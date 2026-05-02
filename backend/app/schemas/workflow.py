from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class WorkflowInboxItem(BaseModel):
    id: str
    source: str
    source_id: int
    title: str
    requester_employee_id: Optional[int] = None
    requester_name: Optional[str] = None
    status: str
    priority: str = "Normal"
    submitted_at: Optional[datetime] = None
    action_url: str
    action_label: str
    role_scope: str


class WorkflowInboxSummary(BaseModel):
    total: int
    pending_action: int
    submitted_by_me: int
    by_source: dict[str, int]
    items: list[WorkflowInboxItem]
