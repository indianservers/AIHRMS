from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import RequirePermission, get_db
from app.models.platform import CustomFieldDefinition, CustomFieldValue
from app.models.user import User
from app.schemas.platform import (
    CustomFieldDefinitionCreate,
    CustomFieldDefinitionSchema,
    CustomFieldValueSchema,
    CustomFieldValueUpsert,
)

router = APIRouter(prefix="/custom-fields", tags=["Custom Fields"])


@router.post("/definitions", response_model=CustomFieldDefinitionSchema, status_code=201)
def create_custom_field_definition(
    data: CustomFieldDefinitionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("settings_manage")),
):
    exists = db.query(CustomFieldDefinition).filter(
        CustomFieldDefinition.module == data.module,
        CustomFieldDefinition.field_key == data.field_key,
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="Custom field key already exists for this module")
    item = CustomFieldDefinition(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/definitions", response_model=List[CustomFieldDefinitionSchema])
def list_custom_field_definitions(
    module: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("settings_view")),
):
    query = db.query(CustomFieldDefinition).filter(CustomFieldDefinition.is_active == True)
    if module:
        query = query.filter(CustomFieldDefinition.module == module)
    return query.order_by(CustomFieldDefinition.module, CustomFieldDefinition.display_order, CustomFieldDefinition.label).all()


@router.put("/values", response_model=CustomFieldValueSchema)
def upsert_custom_field_value(
    data: CustomFieldValueUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("settings_manage")),
):
    definition = db.query(CustomFieldDefinition).filter(CustomFieldDefinition.id == data.definition_id, CustomFieldDefinition.is_active == True).first()
    if not definition:
        raise HTTPException(status_code=404, detail="Custom field definition not found")
    if definition.is_required and not (data.value_text or data.value_json):
        raise HTTPException(status_code=400, detail="Value is required for this custom field")
    item = db.query(CustomFieldValue).filter(
        CustomFieldValue.definition_id == data.definition_id,
        CustomFieldValue.entity_type == data.entity_type,
        CustomFieldValue.entity_id == data.entity_id,
    ).first()
    if not item:
        item = CustomFieldValue(
            definition_id=data.definition_id,
            entity_type=data.entity_type,
            entity_id=data.entity_id,
        )
        db.add(item)
    item.value_text = data.value_text
    item.value_json = data.value_json
    item.updated_by = current_user.id
    db.commit()
    db.refresh(item)
    return item


@router.get("/values", response_model=List[CustomFieldValueSchema])
def list_custom_field_values(
    entity_type: str = Query(...),
    entity_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("settings_view")),
):
    return db.query(CustomFieldValue).filter(
        CustomFieldValue.entity_type == entity_type,
        CustomFieldValue.entity_id == entity_id,
    ).order_by(CustomFieldValue.id).all()
