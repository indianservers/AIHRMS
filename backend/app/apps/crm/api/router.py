from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from math import ceil
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import asc, desc, or_
from sqlalchemy.inspection import inspect as sa_inspect
from sqlalchemy.orm import Session
from sqlalchemy.sql.sqltypes import Boolean, Date, DateTime, Integer, Numeric

from app.apps.crm.models import (
    CRMActivity,
    CRMCallLog,
    CRMCompany,
    CRMContact,
    CRMCustomField,
    CRMCustomFieldValue,
    CRMDeal,
    CRMEmailLog,
    CRMLead,
    CRMMeeting,
    CRMNote,
    CRMOwner,
    CRMPipeline,
    CRMPipelineStage,
    CRMProduct,
    CRMQuotation,
    CRMTask,
    CRMTeam,
    CRMTerritory,
)
from app.core.deps import RequirePermission, get_db
from app.models.company import Branch
from app.models.employee import Employee
from app.models.user import User

router = APIRouter(prefix="/crm", tags=["CRM"])


class CRMRecordPayload(BaseModel):
    model_config = ConfigDict(extra="allow")


class Resource:
    def __init__(
        self,
        model: type,
        *,
        required: tuple[str, ...],
        search: tuple[str, ...],
        default_sort: str = "created_at",
        aliases: tuple[str, ...] = (),
        soft_delete: bool = True,
        owner_field: str | None = "owner_user_id",
    ) -> None:
        self.model = model
        self.required = required
        self.search = search
        self.default_sort = default_sort
        self.aliases = aliases
        self.soft_delete = soft_delete
        self.owner_field = owner_field


RESOURCES: dict[str, Resource] = {
    "leads": Resource(CRMLead, required=("first_name", "full_name"), search=("full_name", "email", "phone", "company_name", "source", "status", "rating")),
    "contacts": Resource(CRMContact, required=("first_name", "full_name"), search=("full_name", "email", "phone", "job_title", "lifecycle_stage", "source")),
    "companies": Resource(CRMCompany, required=("name",), search=("name", "industry", "email", "phone", "city", "account_type", "status"), aliases=("accounts",)),
    "deals": Resource(CRMDeal, required=("name", "pipeline_id", "stage_id"), search=("name", "description", "status", "lead_source"), aliases=("opportunities",)),
    "pipelines": Resource(CRMPipeline, required=("name",), search=("name", "description"), owner_field=None),
    "pipeline-stages": Resource(CRMPipelineStage, required=("pipeline_id", "name"), search=("name", "color"), owner_field=None),
    "activities": Resource(CRMActivity, required=("activity_type", "subject"), search=("activity_type", "subject", "description", "status", "priority")),
    "notes": Resource(CRMNote, required=("body",), search=("body",), owner_field="author_user_id"),
    "tasks": Resource(CRMTask, required=("title",), search=("title", "description", "status", "priority")),
    "calls": Resource(CRMCallLog, required=("direction", "phone_number", "call_time"), search=("direction", "phone_number", "outcome", "notes"), aliases=("call-logs",)),
    "emails": Resource(CRMEmailLog, required=("subject", "to_email"), search=("subject", "body", "from_email", "to_email", "direction"), aliases=("email-logs",)),
    "meetings": Resource(CRMMeeting, required=("title", "start_time", "end_time"), search=("title", "description", "location", "status")),
    "quotations": Resource(CRMQuotation, required=("quote_number", "issue_date", "expiry_date"), search=("quote_number", "status", "currency", "terms", "notes")),
    "products": Resource(CRMProduct, required=("name",), search=("name", "sku", "category", "description", "status"), aliases=("products-services",)),
    "territories": Resource(CRMTerritory, required=("name",), search=("name", "code", "country", "state", "city", "status")),
    "owners": Resource(CRMOwner, required=("full_name", "email"), search=("full_name", "email", "phone", "role", "status"), aliases=("users",), owner_field=None),
    "teams": Resource(CRMTeam, required=("name",), search=("name", "team_type", "description", "status")),
    "custom-fields": Resource(CRMCustomField, required=("entity", "field_key", "label"), search=("entity", "field_key", "label", "field_type"), owner_field=None),
    "custom-field-values": Resource(CRMCustomFieldValue, required=("custom_field_id", "entity", "record_id"), search=("entity", "value_text"), owner_field=None),
}

for key, resource in list(RESOURCES.items()):
    for alias in resource.aliases:
        RESOURCES[alias] = resource

RESERVED_QUERY_KEYS = {
    "page",
    "per_page",
    "search",
    "q",
    "sort_by",
    "sort_order",
    "include_deleted",
    "owner_id",
}


def _columns(model: type) -> dict[str, Any]:
    return {column.key: column for column in sa_inspect(model).columns}


def _snake(value: str) -> str:
    output = []
    for index, char in enumerate(value):
        if char.isupper() and index > 0:
            output.append("_")
        output.append(char.lower())
    return "".join(output).replace("-", "_")


def _normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {_snake(key): value for key, value in payload.items()}


def _coerce_value(column: Any, value: Any) -> Any:
    if value == "":
        return None
    column_type = column.type
    try:
        if isinstance(column_type, Integer) and value is not None:
            return int(value)
        if isinstance(column_type, Numeric) and value is not None:
            return Decimal(str(value))
        if isinstance(column_type, Boolean) and value is not None:
            if isinstance(value, bool):
                return value
            return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}
        if isinstance(column_type, DateTime) and isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        if isinstance(column_type, Date) and not isinstance(column_type, DateTime) and isinstance(value, str):
            return date.fromisoformat(value[:10])
    except (TypeError, ValueError, ArithmeticError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid value for {column.key}") from exc
    return value


def _organization_id(db: Session, user: User) -> int:
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    if employee and employee.branch_id:
        branch = db.query(Branch).filter(Branch.id == employee.branch_id).first()
        if branch:
            return branch.company_id
    return 1


def _get_resource(entity: str) -> Resource:
    resource = RESOURCES.get(entity)
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown CRM entity: {entity}")
    return resource


def _base_query(db: Session, resource: Resource, organization_id: int, include_deleted: bool = False):
    model = resource.model
    columns = _columns(model)
    query = db.query(model)
    if "organization_id" in columns:
        query = query.filter(model.organization_id == organization_id)
    if not include_deleted and "deleted_at" in columns:
        query = query.filter(model.deleted_at.is_(None))
    return query


def _apply_filters(query, resource: Resource, request: Request, owner_id: int | None):
    model = resource.model
    columns = _columns(model)
    if owner_id is not None and resource.owner_field and resource.owner_field in columns:
        query = query.filter(getattr(model, resource.owner_field) == owner_id)

    for key, value in request.query_params.items():
        if key in RESERVED_QUERY_KEYS or value in {"", "all"}:
            continue
        column_key = _snake(key)
        if column_key in columns:
            query = query.filter(getattr(model, column_key) == _coerce_value(columns[column_key], value))
    return query


def _apply_search(query, resource: Resource, search: str | None):
    if not search:
        return query
    model = resource.model
    clauses = []
    for key in resource.search:
        if hasattr(model, key):
            clauses.append(getattr(model, key).ilike(f"%{search}%"))
    return query.filter(or_(*clauses)) if clauses else query


def _serialize(record: Any) -> dict[str, Any]:
    item: dict[str, Any] = {}
    for column in sa_inspect(record.__class__).columns:
        value = getattr(record, column.key)
        if isinstance(value, datetime):
            value = value.isoformat()
        elif isinstance(value, date):
            value = value.isoformat()
        elif isinstance(value, Decimal):
            value = float(value)
        item[column.key] = value

    aliases = {
        "organization_id": "organizationId",
        "owner_user_id": "ownerId",
        "author_user_id": "authorId",
        "created_by_user_id": "createdBy",
        "updated_by_user_id": "updatedBy",
        "created_at": "createdAt",
        "updated_at": "updatedAt",
        "deleted_at": "deletedAt",
    }
    for source, target in aliases.items():
        if source in item:
            item[target] = item[source]
    return item


def _validate_and_build(resource: Resource, payload: dict[str, Any], partial: bool = False) -> dict[str, Any]:
    data = _normalize_payload(payload)
    columns = _columns(resource.model)
    unknown = sorted(key for key in data if key not in columns and key not in {"owner_id", "created_by", "updated_by", "organization_id"})
    if unknown:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Unsupported field(s): {', '.join(unknown)}")

    missing = [field for field in resource.required if not partial and data.get(field) in {None, ""}]
    if missing:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Missing required field(s): {', '.join(missing)}")

    if "owner_id" in data and resource.owner_field:
        data[resource.owner_field] = data.pop("owner_id")
    if "created_by" in data:
        data["created_by_user_id"] = data.pop("created_by")
    if "updated_by" in data:
        data["updated_by_user_id"] = data.pop("updated_by")

    return {key: _coerce_value(columns[key], value) for key, value in data.items() if key in columns}


def _get_record(db: Session, resource: Resource, record_id: int, organization_id: int, include_deleted: bool = False):
    record = _base_query(db, resource, organization_id, include_deleted).filter(resource.model.id == record_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CRM record not found")
    return record


RELATED_RESOURCE_BY_FIELD = {
    "company_id": "companies",
    "contact_id": "contacts",
    "deal_id": "deals",
    "lead_id": "leads",
    "pipeline_id": "pipelines",
    "stage_id": "pipeline-stages",
    "custom_field_id": "custom-fields",
    "converted_contact_id": "contacts",
    "converted_company_id": "companies",
    "converted_deal_id": "deals",
}


def _validate_related_records(db: Session, data: dict[str, Any], organization_id: int) -> None:
    for field, resource_name in RELATED_RESOURCE_BY_FIELD.items():
        record_id = data.get(field)
        if not record_id:
            continue
        related = _get_resource(resource_name)
        _get_record(db, related, int(record_id), organization_id, include_deleted=False)


@router.get("/module-info")
def module_info() -> dict[str, Any]:
    return {
        "key": "crm",
        "name": "VyaparaCRM",
        "status": "installed",
        "modules": sorted(key for key in RESOURCES if key not in {"accounts", "opportunities", "products-services", "call-logs", "email-logs", "users"}),
    }


@router.get("/{entity}")
def list_records(
    entity: str,
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    search: str | None = None,
    q: str | None = None,
    sort_by: str | None = None,
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    include_deleted: bool = False,
    owner_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("crm_view", "crm_manage", "crm_admin")),
):
    resource = _get_resource(entity)
    organization_id = _organization_id(db, current_user)
    query = _base_query(db, resource, organization_id, include_deleted)
    query = _apply_filters(query, resource, request, owner_id)
    query = _apply_search(query, resource, search or q)
    total = query.count()

    columns = _columns(resource.model)
    sort_key = sort_by or resource.default_sort
    if sort_key not in columns:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Cannot sort by {sort_key}")
    sort_column = getattr(resource.model, sort_key)
    query = query.order_by(asc(sort_column) if sort_order == "asc" else desc(sort_column))
    rows = query.offset((page - 1) * per_page).limit(per_page).all()

    return {
        "items": [_serialize(row) for row in rows],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": ceil(total / per_page) if total else 0,
    }


@router.get("/{entity}/{record_id}")
def get_record(
    entity: str,
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("crm_view", "crm_manage", "crm_admin")),
):
    resource = _get_resource(entity)
    record = _get_record(db, resource, record_id, _organization_id(db, current_user))
    return _serialize(record)


@router.post("/{entity}", status_code=status.HTTP_201_CREATED)
def create_record(
    entity: str,
    payload: CRMRecordPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("crm_manage", "crm_admin")),
):
    resource = _get_resource(entity)
    data = _validate_and_build(resource, payload.model_dump(), partial=False)
    organization_id = _organization_id(db, current_user)
    columns = _columns(resource.model)
    if "organization_id" in columns:
        data["organization_id"] = organization_id
    _validate_related_records(db, data, organization_id)
    if resource.owner_field and resource.owner_field in columns and not data.get(resource.owner_field):
        data[resource.owner_field] = current_user.id
    if "author_user_id" in columns and not data.get("author_user_id"):
        data["author_user_id"] = current_user.id
    if "created_by_user_id" in columns:
        data["created_by_user_id"] = current_user.id
    if "updated_by_user_id" in columns:
        data["updated_by_user_id"] = current_user.id

    record = resource.model(**data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return _serialize(record)


@router.patch("/{entity}/{record_id}")
def update_record(
    entity: str,
    record_id: int,
    payload: CRMRecordPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("crm_manage", "crm_admin")),
):
    resource = _get_resource(entity)
    organization_id = _organization_id(db, current_user)
    record = _get_record(db, resource, record_id, organization_id)
    data = _validate_and_build(resource, payload.model_dump(exclude_unset=True), partial=True)
    columns = _columns(resource.model)
    if "organization_id" in data and data["organization_id"] != organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot move CRM records across organizations")
    _validate_related_records(db, data, organization_id)
    for key, value in data.items():
        if key not in {"id", "organization_id", "created_at", "created_by_user_id"}:
            setattr(record, key, value)
    if "updated_by_user_id" in columns:
        record.updated_by_user_id = current_user.id
    if "updated_at" in columns:
        record.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(record)
    return _serialize(record)


@router.delete("/{entity}/{record_id}")
def delete_record(
    entity: str,
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("crm_manage", "crm_admin")),
):
    resource = _get_resource(entity)
    record = _get_record(db, resource, record_id, _organization_id(db, current_user), include_deleted=True)
    columns = _columns(resource.model)
    if resource.soft_delete and "deleted_at" in columns:
        record.deleted_at = datetime.now(timezone.utc)
        if "updated_by_user_id" in columns:
            record.updated_by_user_id = current_user.id
    else:
        db.delete(record)
    db.commit()
    return {"message": "CRM record deleted"}
