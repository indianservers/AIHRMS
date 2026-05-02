from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class NotificationCreate(BaseModel):
    user_id: int
    title: str
    message: str
    module: Optional[str] = None
    event_type: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    action_url: Optional[str] = None
    priority: str = "normal"
    channels: List[str] = ["in_app"]


class NotificationDeliveryLogSchema(BaseModel):
    id: int
    notification_id: int
    channel: str
    recipient: Optional[str] = None
    status: str
    provider_message_id: Optional[str] = None
    error_message: Optional[str] = None
    attempted_at: datetime
    delivered_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationSchema(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    module: Optional[str] = None
    event_type: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    action_url: Optional[str] = None
    priority: str
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    delivery_logs: List[NotificationDeliveryLogSchema] = []

    class Config:
        from_attributes = True
