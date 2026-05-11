from __future__ import annotations

from sqlalchemy.orm import Session

from app.ai_agents.models import AiAgent, AiAgentTool
from app.ai_agents.services.registry import AiAgentRegistryService
from app.ai_agents.tools.definitions import ALL_TOOL_DEFINITIONS, AiToolDefinition


class AiToolRegistryService:
    def __init__(self, db: Session):
        self.db = db

    def all_tools(self) -> list[AiToolDefinition]:
        return list(ALL_TOOL_DEFINITIONS)

    def get_tool(self, tool_name: str) -> AiToolDefinition | None:
        return next((tool for tool in ALL_TOOL_DEFINITIONS if tool.tool_name == tool_name), None)

    def ensure_seed_data(self) -> None:
        AiAgentRegistryService(self.db).ensure_seed_data()
        agents = {agent.code: agent for agent in self.db.query(AiAgent).all()}
        for definition in ALL_TOOL_DEFINITIONS:
            for agent_code in definition.allowed_agent_codes:
                agent = agents.get(agent_code)
                if not agent:
                    continue
                row = (
                    self.db.query(AiAgentTool)
                    .filter(AiAgentTool.agent_id == agent.id, AiAgentTool.tool_name == definition.tool_name)
                    .first()
                )
                if not row:
                    row = AiAgentTool(agent_id=agent.id, tool_name=definition.tool_name, input_schema_json=definition.input_schema)
                    self.db.add(row)
                row.tool_description = definition.description
                row.input_schema_json = definition.input_schema
                row.module = definition.module
                row.permission_required = definition.required_permission
                row.risk_level = definition.risk_level
                row.requires_approval = definition.requires_approval
                row.is_active = True
        self.db.flush()

    def is_active_for_agent(self, tool_name: str, agent_code: str) -> bool:
        agent = self.db.query(AiAgent).filter(AiAgent.code == agent_code).first()
        if not agent:
            return False
        row = self.db.query(AiAgentTool).filter(AiAgentTool.agent_id == agent.id, AiAgentTool.tool_name == tool_name).first()
        return bool(row and row.is_active and agent.is_active)
