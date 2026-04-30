from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload

from app.core.deps import RequirePermission, get_db
from app.models.target import FeatureCatalog, FeaturePlan, IndustryTarget
from app.models.user import User
from app.schemas.target import (
    FeatureCatalogCreate,
    FeatureCatalogSchema,
    FeatureCatalogUpdate,
    FeaturePlanCreate,
    FeaturePlanSchema,
    FeaturePlanUpdate,
    IndustryTargetCreate,
    IndustryTargetSchema,
    IndustryTargetUpdate,
)

router = APIRouter(prefix="/targets", tags=["Target Markets and Features"])


@router.get("/industries", response_model=List[IndustryTargetSchema])
def list_industries(
    include_inactive: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("targets_view")),
):
    query = db.query(IndustryTarget)
    if not include_inactive:
        query = query.filter(IndustryTarget.is_active == True)
    return query.order_by(IndustryTarget.sort_order, IndustryTarget.name).all()


@router.post("/industries", response_model=IndustryTargetSchema, status_code=status.HTTP_201_CREATED)
def create_industry(
    data: IndustryTargetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("targets_manage")),
):
    item = IndustryTarget(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/industries/{industry_id}", response_model=IndustryTargetSchema)
def update_industry(
    industry_id: int,
    data: IndustryTargetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("targets_manage")),
):
    item = db.query(IndustryTarget).filter(IndustryTarget.id == industry_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Industry target not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/industries/{industry_id}")
def delete_industry(
    industry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("targets_manage")),
):
    item = db.query(IndustryTarget).filter(IndustryTarget.id == industry_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Industry target not found")
    item.is_active = False
    db.commit()
    return {"message": "Industry target deactivated"}


@router.get("/plans", response_model=List[FeaturePlanSchema])
def list_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("targets_view")),
):
    return (
        db.query(FeaturePlan)
        .options(selectinload(FeaturePlan.features))
        .filter(FeaturePlan.is_active == True)
        .order_by(FeaturePlan.sort_order, FeaturePlan.id)
        .all()
    )


@router.post("/plans", response_model=FeaturePlanSchema, status_code=status.HTTP_201_CREATED)
def create_plan(
    data: FeaturePlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("targets_manage")),
):
    item = FeaturePlan(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/plans/{plan_id}", response_model=FeaturePlanSchema)
def update_plan(
    plan_id: int,
    data: FeaturePlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("targets_manage")),
):
    item = db.query(FeaturePlan).filter(FeaturePlan.id == plan_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Feature plan not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/plans/{plan_id}")
def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("targets_manage")),
):
    item = db.query(FeaturePlan).filter(FeaturePlan.id == plan_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Feature plan not found")
    item.is_active = False
    db.commit()
    return {"message": "Feature plan deactivated"}


@router.get("/features", response_model=List[FeatureCatalogSchema])
def list_features(
    plan_id: Optional[int] = Query(None),
    module: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("targets_view")),
):
    query = db.query(FeatureCatalog).filter(FeatureCatalog.is_active == True)
    if plan_id:
        query = query.filter(FeatureCatalog.plan_id == plan_id)
    if module:
        query = query.filter(FeatureCatalog.module == module)
    return query.order_by(FeatureCatalog.module, FeatureCatalog.sort_order, FeatureCatalog.name).all()


@router.post("/features", response_model=FeatureCatalogSchema, status_code=status.HTTP_201_CREATED)
def create_feature(
    data: FeatureCatalogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("targets_manage")),
):
    item = FeatureCatalog(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/features/{feature_id}", response_model=FeatureCatalogSchema)
def update_feature(
    feature_id: int,
    data: FeatureCatalogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("targets_manage")),
):
    item = db.query(FeatureCatalog).filter(FeatureCatalog.id == feature_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Feature not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/features/{feature_id}")
def delete_feature(
    feature_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("targets_manage")),
):
    item = db.query(FeatureCatalog).filter(FeatureCatalog.id == feature_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Feature not found")
    item.is_active = False
    db.commit()
    return {"message": "Feature deactivated"}
