from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AuditLogSchema(BaseModel):
    id: int
    user_id: Optional[int] = None
    method: str
    endpoint: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status_code: Optional[int] = None
    duration_ms: Optional[int] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    action: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
