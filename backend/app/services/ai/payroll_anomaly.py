"""AI-based payroll anomaly detection."""
from decimal import Decimal
from typing import List, Optional


def detect_payroll_anomalies(records: List[dict]) -> List[dict]:
    """
    Detect anomalies in payroll records.
    Flags records that deviate significantly from expected values.
    """
    anomalies = []

    if len(records) < 2:
        return anomalies

    # Calculate statistics for comparison
    net_salaries = [float(r.get("net_salary", 0)) for r in records if r.get("net_salary")]
    if not net_salaries:
        return anomalies

    avg_net = sum(net_salaries) / len(net_salaries)
    variance = sum((x - avg_net) ** 2 for x in net_salaries) / len(net_salaries)
    std_dev = variance ** 0.5

    for record in records:
        issues = []
        net = float(record.get("net_salary", 0))
        gross = float(record.get("gross_salary", 0))
        deductions = float(record.get("total_deductions", 0))
        basic = float(record.get("basic", 0))

        # Negative salary
        if net < 0:
            issues.append("Net salary is negative")

        # Zero salary for active employee
        if net == 0 and gross > 0:
            issues.append("Zero net salary detected")

        # Deductions exceed 50% of gross
        if gross > 0 and deductions / gross > 0.5:
            issues.append(f"Deductions are {deductions/gross*100:.0f}% of gross salary")

        # Statistical outlier (>3 sigma)
        if std_dev > 0 and abs(net - avg_net) > 3 * std_dev:
            direction = "high" if net > avg_net else "low"
            issues.append(f"Net salary is statistically {direction} (3+ sigma from mean)")

        # Basic > gross
        if basic > gross:
            issues.append("Basic salary exceeds gross salary")

        # LOP > working days
        lop = float(record.get("lop_days", 0))
        working = float(record.get("working_days", 26) or 26)
        if lop > working:
            issues.append("LOP days exceed working days")

        if issues:
            anomalies.append({
                "payroll_record_id": record.get("id"),
                "employee_id": record.get("employee_id"),
                "anomalies": issues,
                "severity": "High" if len(issues) >= 2 or any("negative" in i for i in issues) else "Medium",
            })

    return anomalies


async def run_anomaly_detection(db, payroll_run_id: int) -> dict:
    """Run anomaly detection on a payroll run and update records."""
    from app.models.payroll import PayrollRecord, PayrollRun
    from sqlalchemy.orm import Session

    run = db.query(PayrollRun).filter(PayrollRun.id == payroll_run_id).first()
    if not run:
        return {"error": "Payroll run not found"}

    records = db.query(PayrollRecord).filter(
        PayrollRecord.payroll_run_id == payroll_run_id
    ).all()

    record_dicts = [
        {
            "id": r.id,
            "employee_id": r.employee_id,
            "net_salary": float(r.net_salary or 0),
            "gross_salary": float(r.gross_salary or 0),
            "total_deductions": float(r.total_deductions or 0),
            "basic": float(r.basic or 0),
            "lop_days": float(r.lop_days or 0),
            "working_days": r.working_days,
        }
        for r in records
    ]

    anomalies = detect_payroll_anomalies(record_dicts)

    # Update records with anomaly flags
    anomaly_map = {a["payroll_record_id"]: a for a in anomalies}
    for record in records:
        if record.id in anomaly_map:
            record.is_anomaly = True
            record.anomaly_reason = "; ".join(anomaly_map[record.id]["anomalies"])
        else:
            record.is_anomaly = False
            record.anomaly_reason = None

    db.commit()

    return {
        "payroll_run_id": payroll_run_id,
        "total_records": len(records),
        "anomalies_found": len(anomalies),
        "anomalies": anomalies,
    }
