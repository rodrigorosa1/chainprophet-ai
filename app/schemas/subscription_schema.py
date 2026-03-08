from typing import Optional
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from app.schemas.plan_schema import PlanOut
from app.schemas.user_schema import UserOut
from datetime import datetime


class SubscriptionIn(BaseModel):
    user_id: UUID
    plan_id: UUID
    active: Optional[bool] = None


class SubscriptionOut(SubscriptionIn):
    id: UUID
    started_at: datetime
    canceled_at: Optional[datetime] = None
    user: UserOut
    plan: PlanOut

    model_config = ConfigDict(from_attributes=True)
