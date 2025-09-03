from uuid import UUID
from pydantic import BaseModel, ConfigDict

class InvestimetBase(BaseModel):
    active_id: UUID
    user_id: UUID
    amount_invested: float
    gain_target_percent: float
    loss_limit_percent: float

class InvestimentIn(InvestimetBase):
    pass


class InvestimentOut(InvestimetBase):
    id: UUID
    is_active: bool

    model_config = ConfigDict(from_attributes=True)