from __future__ import annotations

from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.ai_agents.adapters.base import MissingServiceMethodError
from app.ai_agents.adapters.crm_ai_adapter import CrmAiAdapter
from app.ai_agents.adapters.cross_module_ai_adapter import CrossModuleAiAdapter
from app.ai_agents.adapters.hrms_ai_adapter import HrmsAiAdapter
from app.ai_agents.adapters.pms_ai_adapter import PmsAiAdapter
from app.ai_agents.models import AiActionApproval, AiAgent, AiConversation
from app.ai_agents.services.audit import AiAuditService
from app.ai_agents.tools.ai_tool_registry_service import AiToolRegistryService
from app.ai_agents.tools.definitions import AiToolDefinition
from app.models.user import User


class AiToolExecutionService:
    def __init__(self, db: Session):
        self.db = db
        self.registry = AiToolRegistryService(db)

    def execute_tool(
        self,
        *,
        user: User,
        agent_code: str,
        tool_name: str,
        input: dict[str, Any],
        conversation_id: int | None = None,
        related_entity_type: str | None = None,
        related_entity_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict[str, Any]:
        agent = self.db.query(AiAgent).filter(AiAgent.code == agent_code).first()
        tool = self.registry.get_tool(tool_name)
        base = {"tool_name": tool_name, "module": tool.module if tool else None, "requires_approval": False, "approval_id": None}

        if not tool:
            return self._fail(user, agent, "CROSS", tool_name, input, "TOOL_NOT_FOUND", "Tool is not registered.", ip_address, user_agent, base)
        if not agent or not agent.is_active:
            return self._fail(user, agent, tool.module, tool_name, input, "AGENT_NOT_FOUND", "Agent is not active or not registered.", ip_address, user_agent, base)
        if agent_code not in tool.allowed_agent_codes:
            return self._fail(user, agent, tool.module, tool_name, input, "TOOL_NOT_ALLOWED", "This agent is not allowed to use the requested tool.", ip_address, user_agent, base)
        if not self.registry.is_active_for_agent(tool_name, agent_code):
            return self._fail(user, agent, tool.module, tool_name, input, "TOOL_INACTIVE", "Tool is not active for this agent.", ip_address, user_agent, base)
        if not self._has_permission(user, tool.required_permission):
            return self._fail(user, agent, tool.module, tool_name, input, "PERMISSION_DENIED", "You do not have permission to use this tool.", ip_address, user_agent, base)

        errors = self._validate_input(tool.input_schema, input)
        if errors:
            result = {**base, "success": False, "error_code": "INVALID_TOOL_INPUT", "message": "Invalid tool input.", "details": errors, "data": None}
            self._audit(user, agent, tool.module, "AI_TOOL_FAILED", tool_name, input, result, "failed", ip_address, user_agent)
            return result

        if tool.requires_approval:
            try:
                proposed_data = self._dispatch(tool, user, input)
            except MissingServiceMethodError as exc:
                result = {**base, "success": False, "error_code": "SERVICE_METHOD_MISSING", "message": "Required existing module service method is not available yet.", "missing_method": exc.method, "data": None}
                self._audit(user, agent, tool.module, "AI_TOOL_FAILED", tool_name, input, result, "failed", ip_address, user_agent, related_entity_type, related_entity_id)
                return result
            except HTTPException as exc:
                code = "PERMISSION_DENIED" if exc.status_code == 403 else "RECORD_NOT_FOUND" if exc.status_code == 404 else "TOOL_EXECUTION_FAILED"
                result = {**base, "success": False, "error_code": code, "message": str(exc.detail), "data": None}
                self._audit(user, agent, tool.module, "AI_TOOL_FAILED", tool_name, input, result, "failed", ip_address, user_agent, related_entity_type, related_entity_id)
                return result
            approval = self._create_approval(user, agent, tool, proposed_data, conversation_id, related_entity_type, related_entity_id)
            result = {
                **base,
                "success": True,
                "requires_approval": True,
                "approval_id": approval.id,
                "data": {"proposed_action": proposed_data},
                "message": "This action requires approval before execution.",
            }
            self._audit(user, agent, tool.module, "AI_TOOL_APPROVAL_CREATED", tool_name, input, result, "success", ip_address, user_agent, related_entity_type, related_entity_id)
            return result

        try:
            data = self._dispatch(tool, user, input)
            result = {**base, "success": True, "data": data, "message": "Tool executed successfully."}
            self._audit(user, agent, tool.module, "AI_TOOL_EXECUTED", tool_name, input, result, "success", ip_address, user_agent, related_entity_type, related_entity_id)
            return result
        except MissingServiceMethodError as exc:
            result = {**base, "success": False, "error_code": "SERVICE_METHOD_MISSING", "message": "Required existing module service method is not available yet.", "missing_method": exc.method, "data": None}
            self._audit(user, agent, tool.module, "AI_TOOL_FAILED", tool_name, input, result, "failed", ip_address, user_agent, related_entity_type, related_entity_id)
            return result
        except HTTPException as exc:
            code = "PERMISSION_DENIED" if exc.status_code == 403 else "RECORD_NOT_FOUND" if exc.status_code == 404 else "TOOL_EXECUTION_FAILED"
            result = {**base, "success": False, "error_code": code, "message": str(exc.detail), "data": None}
            self._audit(user, agent, tool.module, "AI_TOOL_FAILED", tool_name, input, result, "failed", ip_address, user_agent, related_entity_type, related_entity_id)
            return result
        except Exception as exc:
            result = {**base, "success": False, "error_code": "TOOL_EXECUTION_FAILED", "message": str(exc), "data": None}
            self._audit(user, agent, tool.module, "AI_TOOL_FAILED", tool_name, input, result, "failed", ip_address, user_agent, related_entity_type, related_entity_id)
            return result

    def _dispatch(self, tool: AiToolDefinition, user: User, input: dict[str, Any]) -> dict[str, Any]:
        namespace, method_name = tool.executor.split(".", 1)
        adapter = {
            "crm": CrmAiAdapter(self.db),
            "pms": PmsAiAdapter(self.db),
            "hrms": HrmsAiAdapter(self.db),
            "cross": CrossModuleAiAdapter(self.db),
        }[namespace]
        method = getattr(adapter, method_name)
        return method(user, input)

    def _create_approval(
        self,
        user: User,
        agent: AiAgent,
        tool: AiToolDefinition,
        input: dict[str, Any],
        conversation_id: int | None,
        related_entity_type: str | None,
        related_entity_id: str | None,
    ) -> AiActionApproval:
        if conversation_id:
            conversation = self.db.query(AiConversation).filter(AiConversation.id == conversation_id, AiConversation.user_id == user.id).first()
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
        approval = AiActionApproval(
            conversation_id=conversation_id,
            agent_id=agent.id,
            user_id=user.id,
            module=tool.module,
            action_type=tool.action_type or tool.tool_name,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            proposed_action_json={"tool_name": tool.tool_name, "input": input},
            status="pending",
        )
        self.db.add(approval)
        self.db.flush()
        return approval

    def _has_permission(self, user: User, permission: str) -> bool:
        if not permission or user.is_superuser:
            return True
        permissions = {item.name for item in (user.role.permissions if user.role else [])}
        return permission in permissions or "*" in permissions

    def _validate_input(self, input_schema: dict[str, Any], input: dict[str, Any]) -> list[dict[str, Any]]:
        errors: list[dict[str, Any]] = []
        properties = input_schema.get("properties", {})
        for field in input_schema.get("required", []):
            if input.get(field) in (None, ""):
                errors.append({"field": field, "message": "Field is required."})
        for field, value in input.items():
            if field not in properties or value is None:
                continue
            definition = properties[field]
            expected = definition.get("type")
            if expected == "integer":
                try:
                    int(value)
                except (TypeError, ValueError):
                    errors.append({"field": field, "message": "Expected integer."})
            if expected == "array" and not isinstance(value, list):
                errors.append({"field": field, "message": "Expected array."})
            if expected == "object" and not isinstance(value, dict):
                errors.append({"field": field, "message": "Expected object."})
            if definition.get("enum") and value not in definition["enum"]:
                errors.append({"field": field, "message": f"Expected one of: {', '.join(definition['enum'])}."})
        return errors

    def _fail(self, user: User, agent: AiAgent | None, module: str, tool_name: str, input_json: dict[str, Any], error_code: str, message: str, ip_address: str | None, user_agent: str | None, base: dict[str, Any]) -> dict[str, Any]:
        result = {**base, "success": False, "error_code": error_code, "message": message, "data": None}
        self._audit(user, agent, module, "AI_TOOL_FAILED", tool_name, input_json, result, "failed", ip_address, user_agent)
        return result

    def _audit(
        self,
        user: User,
        agent: AiAgent | None,
        module: str,
        action: str,
        tool_name: str,
        input_json: dict[str, Any],
        output_json: dict[str, Any],
        status: str,
        ip_address: str | None,
        user_agent: str | None,
        related_entity_type: str | None = None,
        related_entity_id: str | None = None,
    ) -> None:
        AiAuditService(self.db).log(
            user=user,
            agent_id=agent.id if agent else None,
            module=module,
            action=action,
            input_json={"tool_name": tool_name, "input": input_json},
            output_json=output_json,
            status=status,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
