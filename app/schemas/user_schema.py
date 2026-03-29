from typing import Optional
from pydantic import BaseModel, ConfigDict
from uuid import UUID

from app.schemas.plan_schema import PlanOut


class UserBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    api_key: Optional[str] = None
    provider_customer_id: Optional[str] = None
    plan: Optional[PlanOut] = None
    active: Optional[bool] = None


class UserIn(UserBase):
    password: str
    plan_id: Optional[UUID] = None


class UserOut(UserBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
