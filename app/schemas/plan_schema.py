from typing import Optional
from pydantic import BaseModel, ConfigDict
from uuid import UUID


class PlanIn(BaseModel):
    name: str
    daily_amount: Optional[int] = None
    no_limit: bool
    value: float


class PlanOut(PlanIn):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
