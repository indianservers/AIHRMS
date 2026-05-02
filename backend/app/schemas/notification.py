from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


NOTIFICATION_CHANNELS = {"in_app", "email", "whatsapp", "push", "sms"}


def normalize_notification_channels(channels: List[str] | None) -> List[str]:
    normalized = []
    for channel in channels or ["in_app"]:
        value = channel.strip().lower()
        if value not in NOTIFICATION_CHANNELS:
            allowed = ", ".join(sorted(NOTIFICATION_CHANNELS))
            raise ValueError(f"Unsupported notification channel '{channel}'. Allowed: {allowed}")
        if value not in normalized:
            normalized.append(value)
    return normalized or ["in_app"]


class NotificationCreate(BaseModel):
    company_id: Optional[int] = None
    user_id: int
    title: str
    message: str
    module: Optional[str] = None
    event_type: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    action_url: Optional[str] = None
    priority: str = "normal"
    channels: List[str] = Field(default_factory=lambda: ["in_app"])

    @field_validator("channels")
    @classmethod
    def validate_channels(cls, value: List[str]) -> List[str]:
        return normalize_notification_channels(value)


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
    company_id: Optional[int] = None
    user_id: int
    title: str
    message: str
    module: Optional[str] = None
    event_type: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    action_url: Optional[str] = None
    priority: str
    channels: List[str] = Field(default_factory=list)
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    delivery_logs: List[NotificationDeliveryLogSchema] = []

    class Config:
        from_attributes = True
