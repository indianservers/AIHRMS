import csv
import io
import re
from datetime import date
from sqlalchemy.orm import Session
from app.models.employee import Employee
from app.models.payroll import (
    EmployeeStatutoryProfile,
    PayrollRecord,
    PayrollStatutoryContributionLine,
    ProfessionalTaxSlab,
)


def _employee_name(emp: Employee) -> str:
    return " ".join(part for part in [emp.first_name, emp.last_name] if part).strip()


def _lines_for_run(db: Session, payroll_run_id: int, component: str):
    return (
        db.query(PayrollStatutoryContributionLine)
        .join(PayrollRecord, PayrollRecord.id == PayrollStatutoryContributionLine.payroll_record_id)
        .join(Employee, Employee.id == PayrollRecord.employee_id)
        .filter(
            PayrollRecord.payroll_run_id == payroll_run_id,
            PayrollStatutoryContributionLine.component == component,
        )
        .all()
    )


def _profile(db: Session, employee_id: int) -> EmployeeStatutoryProfile | None:
    return db.query(EmployeeStatutoryProfile).filter(EmployeeStatutoryProfile.employee_id == employee_id).first()


def _write_csv(header: list[str], rows: list[list[object]]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(header)
    writer.writerows(rows)
    return output.getvalue()


def generate_pf_ecr(db: Session, payroll_run_id: int) -> tuple[str, list[dict]]:
    errors: list[dict] = []
    rows: list[list[object]] = []
    for i, c in enumerate(_lines_for_run(db, payroll_run_id, "PF"), start=2):
        emp = c.payroll_record.employee if c.payroll_record else db.query(Employee).get(c.employee_id)
        statutory = _profile(db, emp.id) if emp else None
        uan = (statutory.uan if statutory and statutory.uan else getattr(emp, "uan_number", None) or "").strip()
        if not uan or len(uan) != 12 or not uan.isdigit():
            errors.append({"row": i, "field": "UAN", "error": f"Invalid UAN for {_employee_name(emp)}"})
        epf_wages = min(float(c.wage_base or 0), 15000)
        eps_wages = min(epf_wages, 15000)
        epf_contrib = round(epf_wages * 0.12, 2)
        eps_contrib = round(eps_wages * 0.0833, 2)
        rows.append([
            uan,
            _employee_name(emp),
            float(c.wage_base or 0),
            epf_wages,
            eps_wages,
            epf_wages,
            epf_contrib,
            eps_contrib,
            round(epf_contrib - eps_contrib, 2),
            0,
            0,
        ])
    header = [
        "UAN", "Member Name", "Gross Wages", "EPF Wages", "EPS Wages",
        "EDLI Wages", "EPF Contribution", "EPS Contribution",
        "EPF EPS Diff", "NCP Days", "Refund of Advances",
    ]
    return _write_csv(header, rows), errors


def generate_esi_return(db: Session, payroll_run_id: int) -> tuple[str, list[dict]]:
    errors: list[dict] = []
    rows: list[list[object]] = []
    for i, c in enumerate(_lines_for_run(db, payroll_run_id, "ESI"), start=2):
        emp = c.payroll_record.employee if c.payroll_record else db.query(Employee).get(c.employee_id)
        statutory = _profile(db, emp.id) if emp else None
        wages = float(c.wage_base or 0)
        if wages > 21000:
            continue
        ip_number = (statutory.esi_ip_number if statutory and statutory.esi_ip_number else getattr(emp, "esic_number", None) or "").strip()
        if not ip_number:
            errors.append({"row": i, "field": "IP Number", "error": f"Missing ESI IP number for {_employee_name(emp)}"})
        rows.append([ip_number, _employee_name(emp), int(c.payroll_record.paid_days or 0), wages, round(wages * 0.0075, 2)])
    return _write_csv(["IP Number", "IP Name", "No of Days", "Total Wages", "ESI Contribution"], rows), errors


def generate_pt_challan(db: Session, payroll_run_id: int, state: str) -> tuple[str, list[dict]]:
    errors: list[dict] = []
    rows: list[list[object]] = []
    records = db.query(PayrollRecord).join(Employee).filter(PayrollRecord.payroll_run_id == payroll_run_id).all()
    for i, record in enumerate(records, start=2):
        emp = record.employee
        gross = float(record.gross_salary or 0)
        slab = (
            db.query(ProfessionalTaxSlab)
            .filter(
                ProfessionalTaxSlab.state == state,
                ProfessionalTaxSlab.salary_from <= gross,
                ProfessionalTaxSlab.is_active.is_(True),
            )
            .filter((ProfessionalTaxSlab.salary_to.is_(None)) | (ProfessionalTaxSlab.salary_to >= gross))
            .order_by(ProfessionalTaxSlab.salary_from.desc())
            .first()
        )
        amount = float(slab.employee_amount if slab else record.professional_tax or 0)
        if not emp.pan_number:
            errors.append({"row": i, "field": "PAN", "error": f"Missing PAN for {_employee_name(emp)}"})
        rows.append([_employee_name(emp), emp.pan_number or "", gross, amount, f"{record.payroll_run.month}/{record.payroll_run.year}"])
    return _write_csv(["Employee Name", "PAN", "Gross Salary", "PT Amount", "Period"], rows), errors


def generate_tds_24q(db: Session, payroll_run_id: int, quarter: int, year: int) -> tuple[str, list[dict]]:
    errors: list[dict] = []
    rows: list[list[object]] = []
    pan_re = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
    records = db.query(PayrollRecord).join(Employee).filter(PayrollRecord.payroll_run_id == payroll_run_id).all()
    start_month = (quarter - 1) * 3 + 1
    period_from = date(year, start_month, 1).isoformat()
    period_to = date(year, start_month + 2, 28).isoformat()
    for i, record in enumerate(records, start=2):
        emp = record.employee
        pan = (emp.pan_number or "").strip().upper()
        if not pan_re.match(pan):
            errors.append({"row": i, "field": "PAN", "error": f"Invalid PAN for {_employee_name(emp)}"})
        rows.append([pan, _employee_name(emp), float(record.tds or 0), float(record.gross_salary or 0), period_from, period_to])
    return _write_csv(["Employee PAN", "Employee Name", "Total TDS Deducted", "Total Income Paid", "Period From", "Period To"], rows), errors
