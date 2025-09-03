from sqlalchemy import Boolean, Column, Enum, Float, ForeignKey, String
from sqlalchemy.orm import relationship
from app.constants.enums.condition_enum import ConditionEnum
from app.models.base import ModelBase
from sqlalchemy_utils import UUIDType


class Alert(ModelBase):
    __tablename__ = "alerts"

    active_id = Column(UUIDType(binary=False), ForeignKey("actives.id"), nullable=False)
    user_id = Column(UUIDType(binary=False), ForeignKey("users.id"), nullable=False)
    condition = Column(Enum(ConditionEnum), nullable=False)
    value = Column(Float(), nullable=False)
    currency = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False)

    active = relationship("Active", back_populates="alert")
    user = relationship("User", back_populates="alerts")
    notifications = relationship("Notification", back_populates="alert")