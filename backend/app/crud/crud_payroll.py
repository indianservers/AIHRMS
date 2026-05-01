from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.payroll import (
    SalaryComponent, SalaryStructure, SalaryStructureComponent,
    EmployeeSalary, PayrollRun, PayrollRecord, PayrollComponent, Reimbursement,
    PayrollVarianceItem
)


def _money(value: Decimal) -> Decimal:
    return (value or Decimal("0")).quantize(Decimal("0.01"))


def get_active_salary(db: Session, employee_id: int) -> Optional[EmployeeSalary]:
    return db.query(EmployeeSalary).filter(
        and_(EmployeeSalary.employee_id == employee_id, EmployeeSalary.is_active == True)
    ).first()


def run_payroll(db: Session, month: int, year: int, run_by_user_id: int) -> PayrollRun:
    from app.models.employee import Employee
    from app.models.attendance import Attendance
    import calendar

    # Create or get existing run
    payroll_run = db.query(PayrollRun).filter(
        and_(PayrollRun.month == month, PayrollRun.year == year)
    ).first()

    if payroll_run and payroll_run.status == "Locked":
        raise ValueError("Payroll is already locked for this period")

    if not payroll_run:
        payroll_run = PayrollRun(
            month=month,
            year=year,
            run_date=date.today(),
            status="Processing",
        )
        db.add(payroll_run)
        db.flush()

    # Get all active employees
    employees = db.query(Employee).filter(Employee.status == "Active").all()
    total_working_days = sum(1 for d in range(1, calendar.monthrange(year, month)[1] + 1)
                             if date(year, month, d).weekday() < 5)  # Mon-Fri

    total_gross = Decimal("0")
    total_deductions = Decimal("0")
    total_net = Decimal("0")

    for emp in employees:
        salary = get_active_salary(db, emp.id)
        if not salary:
            continue

        # Count attendance
        present_days = db.query(Attendance).filter(
            and_(
                Attendance.employee_id == emp.id,
                Attendance.status.in_(["Present", "WFH", "Half-day"]),
                Attendance.attendance_date >= date(year, month, 1),
                Attendance.attendance_date <= date(year, month, calendar.monthrange(year, month)[1]),
            )
        ).count()

        # Simple payroll calculation
        paid_days = min(Decimal(str(present_days)), Decimal(str(total_working_days)))
        lop_days = max(Decimal("0"), Decimal(str(total_working_days)) - paid_days)

        ctc = salary.ctc
        monthly_ctc = ctc / Decimal("12")
        basic = salary.basic or (monthly_ctc * Decimal("0.4"))
        hra = salary.hra or (basic * Decimal("0.5"))
        other_allowances = monthly_ctc - basic - hra

        per_day_salary = monthly_ctc / Decimal(str(total_working_days))
        lop_deduction = per_day_salary * lop_days

        gross = monthly_ctc - lop_deduction

        # PF: 12% of basic
        pf_employee = min(basic * Decimal("0.12"), Decimal("1800"))
        pf_employer = pf_employee

        # Professional tax (simplified)
        pt = Decimal("200") if gross > Decimal("20000") else Decimal("0")

        # ESI: 0.75% employee if gross <= 21000
        esi_employee = gross * Decimal("0.0075") if gross <= Decimal("21000") else Decimal("0")
        esi_employer = gross * Decimal("0.0325") if gross <= Decimal("21000") else Decimal("0")

        approved_reimbursements = db.query(Reimbursement).filter(
            and_(
                Reimbursement.employee_id == emp.id,
                Reimbursement.status == "Approved",
                Reimbursement.payroll_record_id.is_(None),
                Reimbursement.date >= date(year, month, 1),
                Reimbursement.date <= date(year, month, calendar.monthrange(year, month)[1]),
            )
        ).all()
        reimbursement_total = sum((item.amount or Decimal("0")) for item in approved_reimbursements)

        total_ded = pf_employee + esi_employee + pt
        net = gross - total_ded + reimbursement_total

        # AI anomaly detection placeholder
        is_anomaly = False
        anomaly_reason = None
        if net < Decimal("0"):
            is_anomaly = True
            anomaly_reason = "Net salary is negative"

        # Remove existing record for this run
        existing = db.query(PayrollRecord).filter(
            and_(
                PayrollRecord.payroll_run_id == payroll_run.id,
                PayrollRecord.employee_id == emp.id,
            )
        ).first()
        if existing:
            db.delete(existing)
            db.flush()

        record = PayrollRecord(
            payroll_run_id=payroll_run.id,
            employee_id=emp.id,
            working_days=total_working_days,
            present_days=paid_days,
            lop_days=lop_days,
            paid_days=paid_days,
            basic=basic,
            hra=hra,
            da=Decimal("0"),
            ta=Decimal("0"),
            other_allowances=other_allowances,
            gross_salary=gross,
            pf_employee=pf_employee,
            pf_employer=pf_employer,
            esi_employee=esi_employee,
            esi_employer=esi_employer,
            professional_tax=pt,
            tds=Decimal("0"),
            total_deductions=total_ded,
            reimbursements=reimbursement_total,
            net_salary=net,
            is_anomaly=is_anomaly,
            anomaly_reason=anomaly_reason,
        )
        db.add(record)
        db.flush()

        payroll_lines = [
            ("Basic", "Earning", basic),
            ("House Rent Allowance", "Earning", hra),
            ("Other Allowances", "Earning", other_allowances),
            ("LOP Deduction", "Deduction", lop_deduction),
            ("PF Employee", "Deduction", pf_employee),
            ("ESI Employee", "Deduction", esi_employee),
            ("Professional Tax", "Deduction", pt),
            ("PF Employer", "Employer Contribution", pf_employer),
            ("ESI Employer", "Employer Contribution", esi_employer),
        ]
        if reimbursement_total > 0:
            payroll_lines.append(("Approved Reimbursements", "Reimbursement", reimbursement_total))

        for component_name, component_type, amount in payroll_lines:
            if amount and amount != Decimal("0"):
                db.add(PayrollComponent(
                    record_id=record.id,
                    component_name=component_name,
                    component_type=component_type,
                    amount=_money(amount),
                ))

        for reimbursement in approved_reimbursements:
            reimbursement.payroll_record_id = record.id
            reimbursement.status = "Paid"

        total_gross += gross
        total_deductions += total_ded
        total_net += net

    payroll_run.total_gross = total_gross
    payroll_run.total_deductions = total_deductions
    payroll_run.total_net = total_net
    payroll_run.status = "Completed"
    db.commit()
    db.refresh(payroll_run)
    return payroll_run


def calculate_payroll_variance(db: Session, payroll_run_id: int) -> List[PayrollVarianceItem]:
    import calendar

    run = db.query(PayrollRun).filter(PayrollRun.id == payroll_run_id).first()
    if not run:
        raise ValueError("Payroll run not found")

    previous_month = 12 if run.month == 1 else run.month - 1
    previous_year = run.year - 1 if run.month == 1 else run.year
    previous_run = db.query(PayrollRun).filter(
        PayrollRun.month == previous_month,
        PayrollRun.year == previous_year,
    ).first()

    db.query(PayrollVarianceItem).filter(PayrollVarianceItem.payroll_run_id == payroll_run_id).delete()
    db.flush()

    items: List[PayrollVarianceItem] = []
    records = db.query(PayrollRecord).filter(PayrollRecord.payroll_run_id == payroll_run_id).all()
    for record in records:
        previous_record = None
        if previous_run:
            previous_record = db.query(PayrollRecord).filter(
                PayrollRecord.payroll_run_id == previous_run.id,
                PayrollRecord.employee_id == record.employee_id,
            ).first()

        previous_gross = previous_record.gross_salary if previous_record else Decimal("0")
        previous_net = previous_record.net_salary if previous_record else Decimal("0")
        current_gross = record.gross_salary or Decimal("0")
        current_net = record.net_salary or Decimal("0")
        gross_delta = current_gross - previous_gross
        net_delta = current_net - previous_net
        gross_delta_percent = (gross_delta / previous_gross * Decimal("100")) if previous_gross else Decimal("0")
        net_delta_percent = (net_delta / previous_net * Decimal("100")) if previous_net else Decimal("0")

        reasons = []
        severity = "Info"
        if not previous_record:
            reasons.append("No previous month payroll record")
        if current_net < 0:
            severity = "Critical"
            reasons.append("Net salary is negative")
        elif abs(gross_delta_percent) >= Decimal("25") or abs(net_delta_percent) >= Decimal("25"):
            severity = "High"
            reasons.append("Payroll changed by 25% or more")
        elif abs(gross_delta_percent) >= Decimal("10") or abs(net_delta_percent) >= Decimal("10"):
            severity = "Medium"
            reasons.append("Payroll changed by 10% or more")

        item = PayrollVarianceItem(
            payroll_run_id=payroll_run_id,
            employee_id=record.employee_id,
            previous_payroll_record_id=previous_record.id if previous_record else None,
            current_gross=current_gross,
            previous_gross=previous_gross,
            gross_delta=gross_delta,
            gross_delta_percent=gross_delta_percent,
            current_net=current_net,
            previous_net=previous_net,
            net_delta=net_delta,
            net_delta_percent=net_delta_percent,
            severity=severity,
            reason="; ".join(reasons) if reasons else "Within configured variance threshold",
        )
        db.add(item)
        items.append(item)

    db.commit()
    for item in items:
        db.refresh(item)
    return items


def get_payslip(db: Session, employee_id: int, month: int, year: int) -> Optional[PayrollRecord]:
    return db.query(PayrollRecord).join(PayrollRun).filter(
        and_(
            PayrollRecord.employee_id == employee_id,
            PayrollRun.month == month,
            PayrollRun.year == year,
        )
    ).first()


def _component_payload(component: PayrollComponent) -> dict:
    return {
        "component_name": component.component_name,
        "component_type": component.component_type,
        "amount": component.amount or Decimal("0"),
    }


def _fallback_components(record: PayrollRecord) -> list[PayrollComponent]:
    values = [
        ("Basic", "Earning", record.basic),
        ("House Rent Allowance", "Earning", record.hra),
        ("Other Allowances", "Earning", record.other_allowances),
        ("PF Employee", "Deduction", record.pf_employee),
        ("ESI Employee", "Deduction", record.esi_employee),
        ("Professional Tax", "Deduction", record.professional_tax),
        ("TDS", "Deduction", record.tds),
        ("Other Deductions", "Deduction", record.other_deductions),
        ("PF Employer", "Employer Contribution", record.pf_employer),
        ("ESI Employer", "Employer Contribution", record.esi_employer),
        ("Reimbursements", "Reimbursement", record.reimbursements),
    ]
    return [
        PayrollComponent(component_name=name, component_type=kind, amount=amount)
        for name, kind, amount in values
        if amount and amount != Decimal("0")
    ]


def build_payslip_payload(db: Session, record: PayrollRecord) -> dict:
    components = list(record.components) or _fallback_components(record)
    earnings = [_component_payload(c) for c in components if c.component_type == "Earning"]
    deductions = [_component_payload(c) for c in components if c.component_type == "Deduction"]
    employer_contributions = [
        _component_payload(c) for c in components if c.component_type == "Employer Contribution"
    ]
    reimbursements = [_component_payload(c) for c in components if c.component_type == "Reimbursement"]

    run = record.payroll_run
    ytd_records = db.query(PayrollRecord).join(PayrollRun).filter(
        PayrollRecord.employee_id == record.employee_id,
        PayrollRun.year == run.year,
        PayrollRun.month <= run.month,
    ).all()
    ytd = {
        "gross_salary": sum((item.gross_salary or Decimal("0")) for item in ytd_records),
        "total_deductions": sum((item.total_deductions or Decimal("0")) for item in ytd_records),
        "net_salary": sum((item.net_salary or Decimal("0")) for item in ytd_records),
        "reimbursements": sum((item.reimbursements or Decimal("0")) for item in ytd_records),
        "employer_contributions": sum(
            (item.pf_employer or Decimal("0")) + (item.esi_employer or Decimal("0"))
            for item in ytd_records
        ),
    }

    return {
        "id": record.id,
        "payroll_run_id": record.payroll_run_id,
        "employee_id": record.employee_id,
        "employee": record.employee,
        "month": run.month,
        "year": run.year,
        "working_days": record.working_days,
        "present_days": record.present_days,
        "lop_days": record.lop_days,
        "paid_days": record.paid_days,
        "gross_salary": record.gross_salary,
        "total_deductions": record.total_deductions,
        "net_salary": record.net_salary,
        "status": record.status,
        "is_anomaly": record.is_anomaly,
        "anomaly_reason": record.anomaly_reason,
        "earnings": earnings,
        "deductions": deductions,
        "employer_contributions": employer_contributions,
        "reimbursements": reimbursements,
        "ytd": ytd,
    }
