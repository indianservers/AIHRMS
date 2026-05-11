from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import or_

from app.ai_agents.adapters.base import AiAdapterBase, model_to_dict, not_found
from app.apps.crm.models import CRMActivity, CRMCompany, CRMDeal, CRMLead, CRMNote, CRMTask
from app.models.user import User


class CrmAiAdapter(AiAdapterBase):
    def _query_org(self, model: Any, user: User):
        org_id = self.org_id(user)
        query = self.db.query(model)
        if hasattr(model, "deleted_at"):
            query = query.filter(model.deleted_at == None)
        if not user.is_superuser and hasattr(model, "organization_id"):
            query = query.filter(model.organization_id == org_id)
        return query

    def _get_lead(self, user: User, lead_id: int) -> CRMLead:
        lead = self._query_org(CRMLead, user).filter(CRMLead.id == lead_id).first()
        if not lead:
            not_found("Lead not found or not accessible")
        return lead

    def _get_deal(self, user: User, deal_id: int) -> CRMDeal:
        deal = self._query_org(CRMDeal, user).filter(CRMDeal.id == deal_id).first()
        if not deal:
            not_found("Deal not found or not accessible")
        return deal

    def _get_customer(self, user: User, customer_id: int) -> CRMCompany:
        customer = self._query_org(CRMCompany, user).filter(CRMCompany.id == customer_id).first()
        if not customer:
            not_found("Customer not found or not accessible")
        return customer

    def get_lead_by_id(self, user: User, input: dict[str, Any]) -> dict[str, Any]:
        lead = self._get_lead(user, int(input["lead_id"]))
        return {"lead": model_to_dict(lead)}

    def search_duplicate_leads(self, user: User, input: dict[str, Any]) -> dict[str, Any]:
        query = self._query_org(CRMLead, user)
        conditions = []
        lead_id = input.get("lead_id")
        if lead_id:
            lead = self._get_lead(user, int(lead_id))
            if lead.email:
                conditions.append(CRMLead.email == lead.email)
            if lead.phone:
                conditions.append(CRMLead.phone == lead.phone)
            if lead.company_name:
                conditions.append(CRMLead.company_name.ilike(f"%{lead.company_name}%"))
            query = query.filter(CRMLead.id != lead.id)
        for field, column in (("email", CRMLead.email), ("mobile", CRMLead.phone), ("company_name", CRMLead.company_name)):
            value = input.get(field)
            if value:
                conditions.append(column.ilike(f"%{value}%") if field == "company_name" else column == value)
        if not conditions:
            return {"duplicates": [], "message": "Provide lead_id, email, mobile, or company_name to search duplicates."}
        rows = query.filter(or_(*conditions)).limit(25).all()
        return {"duplicates": [model_to_dict(row) for row in rows], "count": len(rows)}

    def get_lead_activities(self, user: User, input: dict[str, Any]) -> dict[str, Any]:
        lead = self._get_lead(user, int(input["lead_id"]))
        activities = self._query_org(CRMActivity, user).filter(or_(CRMActivity.lead_id == lead.id, (CRMActivity.entity_type == "lead") & (CRMActivity.entity_id == lead.id))).order_by(CRMActivity.created_at.desc()).limit(50).all()
        tasks = self._query_org(CRMTask, user).filter(CRMTask.lead_id == lead.id).order_by(CRMTask.created_at.desc()).limit(50).all()
        notes = self._query_org(CRMNote, user).filter(CRMNote.lead_id == lead.id).order_by(CRMNote.created_at.desc()).limit(50).all()
        return {
            "activities": [model_to_dict(row) for row in activities],
            "tasks": [model_to_dict(row) for row in tasks],
            "notes": [model_to_dict(row) for row in notes],
        }

    def get_overdue_followups(self, user: User, input: dict[str, Any]) -> dict[str, Any]:
        now = datetime.utcnow()
        query = self._query_org(CRMTask, user).filter(CRMTask.due_date != None, CRMTask.due_date < now, CRMTask.completed_at == None)
        if input.get("owner_id"):
            query = query.filter(CRMTask.owner_user_id == int(input["owner_id"]))
        rows = query.order_by(CRMTask.due_date.asc()).limit(100).all()
        return {"followups": [model_to_dict(row) for row in rows], "count": len(rows)}

    def get_deal_by_id(self, user: User, input: dict[str, Any]) -> dict[str, Any]:
        return {"deal": model_to_dict(self._get_deal(user, int(input["deal_id"])))}

    def get_deal_notes(self, user: User, input: dict[str, Any]) -> dict[str, Any]:
        deal = self._get_deal(user, int(input["deal_id"]))
        rows = self._query_org(CRMNote, user).filter(CRMNote.deal_id == deal.id).order_by(CRMNote.created_at.desc()).limit(50).all()
        return {"notes": [model_to_dict(row) for row in rows]}

    def get_deal_activities(self, user: User, input: dict[str, Any]) -> dict[str, Any]:
        deal = self._get_deal(user, int(input["deal_id"]))
        rows = self._query_org(CRMActivity, user).filter(or_(CRMActivity.deal_id == deal.id, (CRMActivity.entity_type == "deal") & (CRMActivity.entity_id == deal.id))).order_by(CRMActivity.created_at.desc()).limit(50).all()
        return {"activities": [model_to_dict(row) for row in rows]}

    def get_customer_by_id(self, user: User, input: dict[str, Any]) -> dict[str, Any]:
        return {"customer": model_to_dict(self._get_customer(user, int(input["customer_id"])))}

    def get_customer_deals(self, user: User, input: dict[str, Any]) -> dict[str, Any]:
        customer = self._get_customer(user, int(input["customer_id"]))
        rows = self._query_org(CRMDeal, user).filter(CRMDeal.company_id == customer.id).order_by(CRMDeal.created_at.desc()).limit(50).all()
        return {"deals": [model_to_dict(row) for row in rows]}

    def get_customer_activities(self, user: User, input: dict[str, Any]) -> dict[str, Any]:
        customer = self._get_customer(user, int(input["customer_id"]))
        rows = self._query_org(CRMActivity, user).filter(or_(CRMActivity.company_id == customer.id, (CRMActivity.entity_type == "customer") & (CRMActivity.entity_id == customer.id), (CRMActivity.entity_type == "account") & (CRMActivity.entity_id == customer.id))).order_by(CRMActivity.created_at.desc()).limit(50).all()
        return {"activities": [model_to_dict(row) for row in rows]}

    def create_followup_task_draft(self, user: User, input: dict[str, Any]) -> dict[str, Any]:
        return {"draft": {**input, "created_by": user.id, "status": "draft", "note": "Draft only. No CRM task has been created."}}

    def propose_lead_update(self, user: User, input: dict[str, Any]) -> dict[str, Any]:
        lead = self._get_lead(user, int(input["lead_id"]))
        return {"proposed_action": {"lead_id": lead.id, "current_status": lead.status, "current_score": lead.lead_score, **input}}

    def draft_crm_message(self, user: User, input: dict[str, Any]) -> dict[str, Any]:
        return {
            "draft": {
                "message_type": input.get("message_type"),
                "purpose": input.get("purpose"),
                "tone": input.get("tone", "professional"),
                "key_points": input.get("key_points", []),
                "body": "",
                "note": "Draft structure only. Message generation and sending are not connected in this step.",
            }
        }
