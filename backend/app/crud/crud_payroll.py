from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.payroll import (
    SalaryComponent, SalaryStructure, SalaryStructureComponent,
    EmployeeSalary, PayrollRun, PayrollRecord, PayrollComponent, Reimbursement
)


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

        total_ded = pf_employee + esi_employee + pt
        net = gross - total_ded

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
            net_salary=net,
            is_anomaly=is_anomaly,
            anomaly_reason=anomaly_reason,
        )
        db.add(record)
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


def get_payslip(db: Session, employee_id: int, month: int, year: int) -> Optional[PayrollRecord]:
    return db.query(PayrollRecord).join(PayrollRun).filter(
        and_(
            PayrollRecord.employee_id == employee_id,
            PayrollRun.month == month,
            PayrollRun.year == year,
        )
    ).first()
