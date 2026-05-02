from typing import Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.deps import RequirePermission, get_current_user, get_db
from app.models.notification import Notification, NotificationDeliveryLog
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.notification import NotificationCreate, NotificationSchema

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def create_notification(db: Session, data: NotificationCreate) -> Notification:
    notification = Notification(
        user_id=data.user_id,
        title=data.title,
        message=data.message,
        module=data.module,
        event_type=data.event_type,
        related_entity_type=data.related_entity_type,
        related_entity_id=data.related_entity_id,
        action_url=data.action_url,
        priority=data.priority,
    )
    db.add(notification)
    db.flush()

    for channel in data.channels or ["in_app"]:
        db.add(
            NotificationDeliveryLog(
                notification_id=notification.id,
                channel=channel,
                recipient=None,
                status="delivered" if channel == "in_app" else "queued",
            )
        )

    db.commit()
    db.refresh(notification)
    return notification


@router.get("/", response_model=PaginatedResponse[NotificationSchema])
def list_notifications(
    unread_only: bool = Query(False),
    module: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(Notification)
        .options(joinedload(Notification.delivery_logs))
        .filter(Notification.user_id == current_user.id)
    )
    if unread_only:
        query = query.filter(Notification.is_read == False)
    if module:
        query = query.filter(Notification.module == module)

    total = query.count()
    items = (
        query.order_by(Notification.created_at.desc(), Notification.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    import math

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=math.ceil(total / per_page) if total else 0,
    )


@router.get("/unread-count")
def unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = (
        db.query(func.count(Notification.id))
        .filter(Notification.user_id == current_user.id, Notification.is_read == False)
        .scalar()
    )
    return {"unread": count or 0}


@router.post("/", response_model=NotificationSchema, status_code=status.HTTP_201_CREATED)
def create_manual_notification(
    data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("notification_manage")),
):
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return create_notification(db, data)


@router.put("/{notification_id}/read", response_model=NotificationSchema)
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = (
        db.query(Notification)
        .options(joinedload(Notification.delivery_logs))
        .filter(Notification.id == notification_id, Notification.user_id == current_user.id)
        .first()
    )
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(notification)
    return notification


@router.put("/mark-all-read")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).update({"is_read": True, "read_at": datetime.now(timezone.utc)}, synchronize_session=False)
    db.commit()
    return {"message": "Notifications marked as read"}
