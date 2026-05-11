from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any

from fastapi import HTTPException
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session

from app.models.user import User


class MissingServiceMethodError(RuntimeError):
    def __init__(self, method: str):
        self.method = method
        super().__init__(method)


class AiAdapterBase:
    def __init__(self, db: Session):
        self.db = db

    def org_id(self, user: User) -> int | None:
        employee = getattr(user, "employee", None)
        return (
            getattr(user, "organization_id", None)
            or getattr(user, "company_id", None)
            or getattr(employee, "organization_id", None)
            or getattr(employee, "company_id", None)
        )

    def missing(self, method: str) -> None:
        raise MissingServiceMethodError(method)


def json_ready(value: Any) -> Any:
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, list):
        return [json_ready(item) for item in value]
    if isinstance(value, dict):
        return {key: json_ready(item) for key, item in value.items()}
    return value


def model_to_dict(row: Any, fields: list[str] | None = None) -> dict[str, Any]:
    if row is None:
        return {}
    if fields is None:
        mapper = inspect(row.__class__)
        fields = [column.key for column in mapper.columns]
    return {field: json_ready(getattr(row, field, None)) for field in fields}


def not_found(message: str) -> None:
    raise HTTPException(status_code=404, detail=message)


def permission_denied(message: str = "Access denied") -> None:
    raise HTTPException(status_code=403, detail=message)
