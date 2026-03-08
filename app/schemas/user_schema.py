from typing import Optional
from pydantic import BaseModel, ConfigDict
from uuid import UUID


class UserBase(BaseModel):
    name: str
    email: str
    phone: str
    api_key: Optional[str] = None
    provider_customer_id: Optional[str] = None
    active: Optional[bool] = None


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
