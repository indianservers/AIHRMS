from typing import List, Optional

from pydantic import BaseModel


class IndustryTargetBase(BaseModel):
    name: str
    slug: str
    headline: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: str = "blue"
    sort_order: int = 0


class IndustryTargetCreate(IndustryTargetBase):
    pass


class IndustryTargetUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    headline: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class IndustryTargetSchema(IndustryTargetBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class FeatureCatalogBase(BaseModel):
    module: str
    name: str
    description: Optional[str] = None
    is_highlight: bool = False
    sort_order: int = 0


class FeatureCatalogCreate(FeatureCatalogBase):
    plan_id: Optional[int] = None


class FeatureCatalogUpdate(BaseModel):
    plan_id: Optional[int] = None
    module: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_highlight: Optional[bool] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class FeatureCatalogSchema(FeatureCatalogBase):
    id: int
    plan_id: Optional[int] = None
    is_active: bool

    class Config:
        from_attributes = True


class FeaturePlanBase(BaseModel):
    code: str
    name: str
    tagline: Optional[str] = None
    strength: Optional[str] = None
    sort_order: int = 0


class FeaturePlanCreate(FeaturePlanBase):
    pass


class FeaturePlanUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    tagline: Optional[str] = None
    strength: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class FeaturePlanSchema(FeaturePlanBase):
    id: int
    is_active: bool
    features: List[FeatureCatalogSchema] = []

    class Config:
        from_attributes = True
