from pydantic import BaseModel, ConfigDict
from uuid import UUID
from app.constants.enums.type_notification_enum import TypeNotificationEnum


class UserBase(BaseModel):
    name: str
    email: str
    phone: str
    type_notification: TypeNotificationEnum


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
