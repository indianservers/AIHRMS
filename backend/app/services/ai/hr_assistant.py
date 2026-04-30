"""AI HR Assistant using Anthropic Claude API."""
import json
from typing import List, Optional
from app.core.config import settings


SYSTEM_PROMPT = """You are an expert HR assistant for a company HRMS system. You help employees and HR managers with:
- HR policies and procedures
- Leave management questions
- Payroll queries
- Attendance policies
- Employee benefits
- Onboarding guidance
- Performance review processes
- General HR compliance questions

Always be professional, empathetic, and helpful. If you don't know something specific about company policy,
say so and suggest they contact HR directly. Keep responses concise and actionable."""


async def get_hr_response(
    message: str,
    conversation_history: Optional[List[dict]] = None,
    company_context: Optional[str] = None,
) -> str:
    if not settings.ANTHROPIC_API_KEY:
        return _get_rule_based_response(message)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        system = SYSTEM_PROMPT
        if company_context:
            system += f"\n\nCompany-specific context:\n{company_context}"

        messages = conversation_history or []
        messages.append({"role": "user", "content": message})

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=system,
            messages=messages,
        )
        return response.content[0].text
    except Exception as e:
        return _get_rule_based_response(message)


def _get_rule_based_response(message: str) -> str:
    message_lower = message.lower()

    if any(word in message_lower for word in ["leave", "vacation", "time off"]):
        return ("Leave requests can be submitted through the Leave Management module. "
                "Go to Leave → Apply Leave, select the leave type, date range, and reason. "
                "Your manager will receive a notification for approval.")

    if any(word in message_lower for word in ["payslip", "salary", "payroll", "pay"]):
        return ("You can view your payslip under Payroll → My Payslips. "
                "Select the month and year to download your payslip. "
                "For salary-related queries, please contact HR.")

    if any(word in message_lower for word in ["attendance", "check-in", "check out"]):
        return ("Use the Attendance module to check-in/check-out daily. "
                "If you missed a check-in, you can submit a regularization request with the reason.")

    if any(word in message_lower for word in ["performance", "review", "appraisal", "goals"]):
        return ("Performance reviews are managed in the Performance module. "
                "You can set your goals, submit self-reviews, and view feedback from your manager.")

    return ("I'm here to help with HR-related queries. You can ask me about leave policies, "
            "payroll, attendance, performance reviews, or any other HR topics.")


async def answer_policy_question(question: str, policy_documents: List[dict]) -> str:
    """Answer questions about company policies using RAG-like approach."""
    if not settings.ANTHROPIC_API_KEY:
        return "Policy Q&A requires AI configuration. Please contact HR for policy details."

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        policy_context = "\n\n".join([
            f"Policy: {p.get('title', '')}\n{p.get('content', '')[:2000]}"
            for p in policy_documents[:5]
        ])

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=f"You are an HR policy assistant. Answer questions based ONLY on the following company policies:\n\n{policy_context}\n\nIf the answer is not in the policies, say so clearly.",
            messages=[{"role": "user", "content": question}],
        )
        return response.content[0].text
    except Exception:
        return "Unable to process policy query at this time. Please contact HR."


async def suggest_helpdesk_reply(ticket_subject: str, ticket_description: str) -> str:
    """Generate AI-suggested reply for a helpdesk ticket."""
    if not settings.ANTHROPIC_API_KEY:
        return _default_helpdesk_reply(ticket_subject)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            system="You are an HR support agent. Generate a professional, empathetic reply to employee helpdesk tickets. Keep it concise and actionable.",
            messages=[{
                "role": "user",
                "content": f"Ticket Subject: {ticket_subject}\n\nDescription: {ticket_description}\n\nGenerate a helpful reply."
            }],
        )
        return response.content[0].text
    except Exception:
        return _default_helpdesk_reply(ticket_subject)


def _default_helpdesk_reply(subject: str) -> str:
    return (f"Thank you for reaching out regarding '{subject}'. "
            "We have received your request and will review it shortly. "
            "Our HR team will get back to you within 24 hours. "
            "If urgent, please contact HR directly.")
