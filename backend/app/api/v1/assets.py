from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, RequirePermission
from app.models.asset import Asset, AssetAssignment, AssetCategory
from app.models.user import User
from app.schemas.asset import (
    AssetAssignmentCreate,
    AssetAssignmentSchema,
    AssetCategoryCreate,
    AssetCategorySchema,
    AssetCreate,
    AssetSchema,
    AssetUpdate,
)

router = APIRouter(prefix="/assets", tags=["Asset Management"])


@router.get("/categories", response_model=list[AssetCategorySchema])
def list_categories(db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("asset_view"))):
    return db.query(AssetCategory).order_by(AssetCategory.name).all()


@router.post("/categories", response_model=AssetCategorySchema, status_code=status.HTTP_201_CREATED)
def create_category(data: AssetCategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("asset_manage"))):
    category = AssetCategory(**data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/", response_model=list[AssetSchema])
def list_assets(
    search: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("asset_view")),
):
    query = db.query(Asset)
    if search:
        like = f"%{search}%"
        query = query.filter((Asset.name.ilike(like)) | (Asset.asset_tag.ilike(like)) | (Asset.serial_number.ilike(like)))
    if status_filter:
        query = query.filter(Asset.status == status_filter)
    return query.order_by(Asset.created_at.desc()).limit(200).all()


@router.post("/", response_model=AssetSchema, status_code=status.HTTP_201_CREATED)
def create_asset(data: AssetCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("asset_manage"))):
    asset = Asset(**data.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@router.put("/{asset_id}", response_model=AssetSchema)
def update_asset(asset_id: int, data: AssetUpdate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("asset_manage"))):
    asset = db.get(Asset, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(asset, key, value)
    db.commit()
    db.refresh(asset)
    return asset


@router.post("/assignments", response_model=AssetAssignmentSchema, status_code=status.HTTP_201_CREATED)
def assign_asset(data: AssetAssignmentCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("asset_manage"))):
    assignment = AssetAssignment(**data.model_dump(), assigned_by=current_user.id)
    asset = db.get(Asset, data.asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    asset.status = "Assigned"
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.put("/assignments/{assignment_id}/return", response_model=AssetAssignmentSchema)
def return_asset(assignment_id: int, condition_at_return: Optional[str] = None, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("asset_manage"))):
    from datetime import date
    assignment = db.get(AssetAssignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    assignment.returned_date = date.today()
    assignment.condition_at_return = condition_at_return
    assignment.is_active = False
    assignment.asset.status = "Available"
    db.commit()
    db.refresh(assignment)
    return assignment
