import datetime
from pydantic import BaseModel, ConfigDict
from uuid import UUID


class NotificationIn(BaseModel):
    alert_id: UUID
    sent_at: datetime
    channel: str
    message: str


class NotificationOut(BaseModel):
    id: UUID
    alert_id: UUID
    sent_at: datetime
    channel: str
    message: str

    model_config = ConfigDict(from_attributes=True)
