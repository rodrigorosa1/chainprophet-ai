from sqlalchemy import Column, Enum, String
from sqlalchemy.orm import relationship
from app.constants.enums.type_notification_enum import TypeNotificationEnum
from app.models.base import ModelBase


class User(ModelBase):
    __tablename__ = "users"

    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    phone = Column(String(100), nullable=False)
    type_notification = Column(Enum(TypeNotificationEnum), nullable=False)

    alerts = relationship("Alert", back_populates="user")
    investiments = relationship("Investiment", back_populates="user")
