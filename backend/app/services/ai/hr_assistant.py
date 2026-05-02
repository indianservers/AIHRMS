"""AI HR Assistant with Claude API and HRMS database context."""
from typing import List, Optional

from app.core.config import settings


SYSTEM_PROMPT = """You are an expert HR assistant inside an HRMS system.
You help employees, managers, HR, finance, and admins with leave, attendance,
payroll, documents, benefits, performance, hiring, and operational questions.

Use live HRMS context when available. Do not invent records or policy facts.
If the database context is insufficient, say what is missing and suggest the
right HRMS page or HR owner. Keep responses concise and actionable."""


async def get_hr_response(
    message: str,
    conversation_history: Optional[List[dict]] = None,
    company_context: Optional[str] = None,
    db=None,
    current_user=None,
) -> str:
    db_context = _build_db_context(db, current_user) if db is not None else ""
    if not settings.ANTHROPIC_API_KEY:
        return _get_rule_based_response(message, db_context)

    try:
        import httpx

        system = SYSTEM_PROMPT
        if company_context:
            system += f"\n\nCompany-specific context:\n{company_context}"
        if db_context:
            system += (
                "\n\nLive HRMS database context:\n"
                f"{db_context}\n"
                "Use this context for operational answers. Do not expose sensitive salary, bank, PAN, or Aadhaar data."
            )

        messages = [
            {"role": item.get("role", "user"), "content": item.get("content", "")}
            for item in (conversation_history or [])
            if item.get("role") in {"user", "assistant"} and item.get("content")
        ][-8:]
        messages.append({"role": "user", "content": message})

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": getattr(settings, "ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
                    "max_tokens": 1024,
                    "system": system,
                    "messages": messages,
                },
            )
            response.raise_for_status()
            payload = response.json()

        blocks = payload.get("content") or []
        text = "\n".join(block.get("text", "") for block in blocks if block.get("type") == "text").strip()
        return text or _get_rule_based_response(message, db_context)
    except Exception:
        return _get_rule_based_response(message, db_context)


def _build_db_context(db, current_user) -> str:
    try:
        from sqlalchemy import func
        from app.models.attendance import Attendance
        from app.models.company import Department
        from app.models.employee import Employee
        from app.models.helpdesk import HelpdeskTicket
        from app.models.leave import LeaveRequest
        from app.models.payroll import PayrollRun

        active = db.query(func.count(Employee.id)).filter(Employee.status == "Active").scalar() or 0
        pending_leave = db.query(func.count(LeaveRequest.id)).filter(LeaveRequest.status == "Pending").scalar() or 0
        open_tickets = (
            db.query(func.count(HelpdeskTicket.id))
            .filter(HelpdeskTicket.status.notin_(["Resolved", "Closed"]))
            .scalar()
            or 0
        )
        today_present = db.query(func.count(Attendance.id)).filter(Attendance.status == "Present").scalar() or 0
        latest_run = db.query(PayrollRun).order_by(PayrollRun.id.desc()).first()
        departments = (
            db.query(Department.name, func.count(Employee.id))
            .outerjoin(Employee, Employee.department_id == Department.id)
            .group_by(Department.id, Department.name)
            .limit(10)
            .all()
        )
        lines = [
            f"Active employees: {active}",
            f"Attendance records marked present: {today_present}",
            f"Pending leave requests: {pending_leave}",
            f"Open helpdesk tickets: {open_tickets}",
            f"Latest payroll run: {latest_run.month}/{latest_run.year} status {latest_run.status}" if latest_run else "Latest payroll run: none",
            "Department headcount: " + ", ".join(f"{name or 'Unassigned'}={count}" for name, count in departments),
        ]
        if getattr(current_user, "employee", None):
            emp = current_user.employee
            lines.append(f"Current employee: {emp.employee_id} {emp.first_name} {emp.last_name}, status {emp.status}")
        return "\n".join(lines)
    except Exception:
        return ""


def _get_rule_based_response(message: str, db_context: str = "") -> str:
    message_lower = message.lower()
    context = f"\n\nCurrent HRMS snapshot:\n{db_context}" if db_context else ""

    if any(word in message_lower for word in ["leave", "vacation", "time off"]):
        return (
            "Leave requests can be submitted through Leave. Select the leave type, date range, "
            "and reason; your manager or HR can approve/reject with comments." + context
        )
    if any(word in message_lower for word in ["payslip", "salary", "payroll", "pay"]):
        return (
            "You can view payslips in Payroll. HR/finance can run pre-checks, process payroll, "
            "review variance, approve, publish payslips, and export statutory files." + context
        )
    if any(word in message_lower for word in ["attendance", "check-in", "check out", "check-in"]):
        return (
            "Use Attendance for check-in/out. Missed punches can be corrected through regularization "
            "before payroll attendance inputs are locked." + context
        )
    if any(word in message_lower for word in ["performance", "review", "appraisal", "goals", "okr"]):
        return (
            "Performance supports goals, OKR check-ins, reviews, 360 feedback, competency assessments, "
            "and skill gap reports." + context
        )
    return (
        "I can help with HRMS operations: leave, attendance, payroll, employees, performance, benefits, "
        "documents, and reports." + context
    )


async def answer_policy_question(question: str, policy_documents: List[dict]) -> str:
    if not settings.ANTHROPIC_API_KEY:
        return "Policy Q&A requires AI configuration. Please contact HR for policy details."

    try:
        import httpx

        policy_context = "\n\n".join([
            f"Policy: {p.get('title', '')}\n{p.get('content', '')[:2000]}"
            for p in policy_documents[:5]
        ])
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": getattr(settings, "ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
                    "max_tokens": 1024,
                    "system": f"Answer only from these company policies:\n\n{policy_context}",
                    "messages": [{"role": "user", "content": question}],
                },
            )
            response.raise_for_status()
            payload = response.json()
        return "\n".join(block.get("text", "") for block in payload.get("content", []) if block.get("type") == "text").strip()
    except Exception:
        return "Unable to process policy query at this time. Please contact HR."


async def suggest_helpdesk_reply(ticket_subject: str, ticket_description: str) -> str:
    if not settings.ANTHROPIC_API_KEY:
        return _default_helpdesk_reply(ticket_subject)

    try:
        import httpx

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": getattr(settings, "ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
                    "max_tokens": 512,
                    "system": "Write a professional, empathetic HR helpdesk reply. Keep it concise and actionable.",
                    "messages": [{
                        "role": "user",
                        "content": f"Subject: {ticket_subject}\n\nDescription: {ticket_description}",
                    }],
                },
            )
            response.raise_for_status()
            payload = response.json()
        text = "\n".join(block.get("text", "") for block in payload.get("content", []) if block.get("type") == "text").strip()
        return text or _default_helpdesk_reply(ticket_subject)
    except Exception:
        return _default_helpdesk_reply(ticket_subject)


def _default_helpdesk_reply(subject: str) -> str:
    return (
        f"Thank you for reaching out regarding '{subject}'. We have received your request and "
        "will review it shortly. Our HR team will get back to you within the SLA."
    )
