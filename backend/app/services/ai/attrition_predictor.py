"""AI-based employee attrition prediction."""
from typing import List, Optional
import json


def predict_attrition_risk(employee_features: dict) -> dict:
    """
    Predict attrition risk using a simple rule-based model.
    In production, replace with a trained ML model (scikit-learn / XGBoost).
    """
    risk_score = 0
    risk_factors = []
    protective_factors = []

    # Tenure (shorter tenure = higher risk)
    tenure_years = employee_features.get("tenure_years", 2)
    if tenure_years < 1:
        risk_score += 25
        risk_factors.append("Very short tenure (< 1 year)")
    elif tenure_years < 2:
        risk_score += 15
        risk_factors.append("Short tenure (< 2 years)")
    else:
        protective_factors.append(f"Stable tenure ({tenure_years} years)")

    # Recent leave usage (high leave = potential burnout)
    leave_days_used = employee_features.get("leave_days_used_last_quarter", 0)
    if leave_days_used > 10:
        risk_score += 20
        risk_factors.append("High leave usage recently")

    # Performance rating
    rating = employee_features.get("last_performance_rating", 3)
    if rating < 2.5:
        risk_score += 20
        risk_factors.append("Low performance rating")
    elif rating >= 4:
        protective_factors.append("High performance rating")
        risk_score -= 10

    # Salary vs market
    salary_percentile = employee_features.get("salary_market_percentile", 50)
    if salary_percentile < 25:
        risk_score += 20
        risk_factors.append("Below market salary")
    elif salary_percentile > 75:
        protective_factors.append("Competitive salary")
        risk_score -= 5

    # Open helpdesk tickets
    open_tickets = employee_features.get("open_helpdesk_tickets", 0)
    if open_tickets > 3:
        risk_score += 10
        risk_factors.append("Multiple unresolved HR issues")

    # Attendance rate
    attendance_rate = employee_features.get("attendance_rate", 0.9)
    if attendance_rate < 0.75:
        risk_score += 15
        risk_factors.append("Low attendance rate")

    # Normalize score
    risk_score = max(0, min(100, risk_score))

    # Risk level
    if risk_score >= 70:
        risk_level = "High"
    elif risk_score >= 40:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "employee_id": employee_features.get("employee_id"),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "protective_factors": protective_factors,
        "recommendation": _get_recommendation(risk_level, risk_factors),
    }


def _get_recommendation(risk_level: str, risk_factors: List[str]) -> str:
    if risk_level == "High":
        return "Immediate manager conversation recommended. Consider retention package, role enhancement, or career discussion."
    elif risk_level == "Medium":
        return "Schedule a 1:1 check-in. Review compensation and growth opportunities."
    return "Continue regular engagement. Monitor for changes in the risk factors."


async def bulk_attrition_analysis(db, department_id: Optional[int] = None) -> List[dict]:
    """Analyze attrition risk for all employees."""
    from app.models.employee import Employee
    from sqlalchemy.orm import Session
    from datetime import date
    import math

    query = db.query(Employee).filter(Employee.status == "Active")
    if department_id:
        query = query.filter(Employee.department_id == department_id)

    employees = query.all()
    results = []

    for emp in employees:
        tenure_years = 0
        if emp.date_of_joining:
            delta = date.today() - emp.date_of_joining
            tenure_years = delta.days / 365.25

        features = {
            "employee_id": emp.id,
            "tenure_years": round(tenure_years, 1),
            "leave_days_used_last_quarter": 5,  # Would be calculated from attendance
            "last_performance_rating": 3.5,  # Would come from performance module
            "salary_market_percentile": 50,  # Would be from salary benchmarking
            "attendance_rate": 0.9,
            "open_helpdesk_tickets": 0,
        }

        result = predict_attrition_risk(features)
        result["employee_name"] = f"{emp.first_name} {emp.last_name}"
        result["department_id"] = emp.department_id
        results.append(result)

    # Sort by risk score descending
    results.sort(key=lambda x: x["risk_score"], reverse=True)
    return results
