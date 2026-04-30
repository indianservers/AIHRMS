from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user, RequirePermission
from app.models.user import User
from app.models.helpdesk import HelpdeskCategory, HelpdeskTicket, HelpdeskReply

router = APIRouter(prefix="/helpdesk", tags=["HR Helpdesk"])


@router.get("/categories")
def list_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(HelpdeskCategory).filter(HelpdeskCategory.is_active == True).all()


@router.post("/categories", status_code=201)
def create_category(
    name: str,
    sla_hours: int = 24,
    assigned_team: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("helpdesk_manage")),
):
    cat = HelpdeskCategory(name=name, sla_hours=sla_hours, assigned_team=assigned_team)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.post("/tickets", status_code=201)
def create_ticket(
    subject: str,
    description: str,
    category_id: Optional[int] = None,
    priority: str = "Medium",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.employee:
        raise HTTPException(status_code=400, detail="No employee profile")

    # Generate ticket number
    from datetime import datetime
    ticket_number = f"TKT{datetime.now().strftime('%Y%m%d')}{current_user.employee.id:04d}"

    ticket = HelpdeskTicket(
        ticket_number=ticket_number,
        employee_id=current_user.employee.id,
        category_id=category_id,
        subject=subject,
        description=description,
        priority=priority,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/tickets")
def list_tickets(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    assigned_to_me: bool = Query(False),
    my_tickets: bool = Query(False),
    page: int = Query(1, ge=1),
    per_page: int = Query(20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(HelpdeskTicket)
    if my_tickets and current_user.employee:
        q = q.filter(HelpdeskTicket.employee_id == current_user.employee.id)
    if assigned_to_me:
        q = q.filter(HelpdeskTicket.assigned_to == current_user.id)
    if status:
        q = q.filter(HelpdeskTicket.status == status)
    if priority:
        q = q.filter(HelpdeskTicket.priority == priority)
    return q.order_by(HelpdeskTicket.created_at.desc()).offset((page-1)*per_page).limit(per_page).all()


@router.get("/tickets/{ticket_id}")
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = db.query(HelpdeskTicket).filter(HelpdeskTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.put("/tickets/{ticket_id}/status")
def update_ticket_status(
    ticket_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("helpdesk_manage")),
):
    ticket = db.query(HelpdeskTicket).filter(HelpdeskTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket.status = status
    if status in ["Resolved", "Closed"]:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        if status == "Resolved":
            ticket.resolved_at = now
        else:
            ticket.closed_at = now
    db.commit()
    return {"message": f"Ticket {status}"}


@router.put("/tickets/{ticket_id}/assign")
def assign_ticket(
    ticket_id: int,
    assign_to_user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("helpdesk_manage")),
):
    ticket = db.query(HelpdeskTicket).filter(HelpdeskTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket.assigned_to = assign_to_user_id
    ticket.status = "In Progress"
    db.commit()
    return {"message": "Ticket assigned"}


@router.post("/tickets/{ticket_id}/reply", status_code=201)
def add_reply(
    ticket_id: int,
    message: str,
    is_internal: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reply = HelpdeskReply(
        ticket_id=ticket_id,
        user_id=current_user.id,
        message=message,
        is_internal=is_internal,
    )
    db.add(reply)
    db.commit()
    db.refresh(reply)
    return reply


@router.get("/tickets/{ticket_id}/replies")
def get_replies(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(HelpdeskReply).filter(
        HelpdeskReply.ticket_id == ticket_id,
        HelpdeskReply.is_internal == False,
    ).order_by(HelpdeskReply.created_at).all()
