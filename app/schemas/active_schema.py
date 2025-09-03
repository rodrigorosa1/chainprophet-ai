from pydantic import BaseModel, ConfigDict
from uuid import UUID


class ActiveBase(BaseModel):
    ticker: str
    name: str
    type: str


class ActiveIn(ActiveBase):
    pass


class ActiveOut(ActiveBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
