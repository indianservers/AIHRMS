from __future__ import annotations

from sqlalchemy.orm import Session

from app.ai_agents.models import AiAgentSetting


class AiAgentSettingsService:
    def __init__(self, db: Session):
        self.db = db

    def list_for_company(self, company_id: int | None) -> list[AiAgentSetting]:
        query = self.db.query(AiAgentSetting)
        if company_id is None:
            query = query.filter(AiAgentSetting.company_id.is_(None))
        else:
            query = query.filter(AiAgentSetting.company_id == company_id)
        return query.all()

    def get_or_create(self, *, agent_id: int, company_id: int | None) -> AiAgentSetting:
        query = self.db.query(AiAgentSetting).filter(AiAgentSetting.agent_id == agent_id)
        if company_id is None:
            query = query.filter(AiAgentSetting.company_id.is_(None))
        else:
            query = query.filter(AiAgentSetting.company_id == company_id)
        setting = query.first()
        if setting:
            return setting
        setting = AiAgentSetting(agent_id=agent_id, company_id=company_id)
        self.db.add(setting)
        self.db.flush()
        return setting
