from pydantic import BaseModel, ConfigDict
from uuid import UUID
from app.constants.enums.condition_enum import ConditionEnum


class AlertBase(BaseModel):
    active_id: UUID
    user_id: UUID
    condition: ConditionEnum
    value: float
    currency: str


class AlertIn(AlertBase):
    pass


class AlertOut(AlertBase):
    id: UUID
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
