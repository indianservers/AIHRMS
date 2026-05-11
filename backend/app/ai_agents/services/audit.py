from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.ai_agents.models import AiAuditLog
from app.models.user import User


class AiAuditService:
    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        *,
        user: User | None,
        agent_id: int | None,
        module: str,
        action: str,
        input_json: dict[str, Any] | None = None,
        output_json: dict[str, Any] | None = None,
        status: str = "success",
        related_entity_type: str | None = None,
        related_entity_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AiAuditLog:
        row = AiAuditLog(
            user_id=user.id if user else None,
            agent_id=agent_id,
            module=module,
            action=action,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            input_json=input_json,
            output_json=output_json,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(row)
        self.db.flush()
        return row

