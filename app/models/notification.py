from sqlalchemy import Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import relationship
from app.constants.enums.status_notification_enum import StatusNotificationEnum
from app.models.base import ModelBase
from sqlalchemy_utils import UUIDType


class Notification(ModelBase):
    __tablename__ = "notifications"

    alert_id = Column(UUIDType(binary=False), ForeignKey("alerts.id"), nullable=False)
    sent_at = Column(DateTime, nullable=False)
    channel = Column(String(50), nullable=False)
    message = Column(String(50), nullable=False)
    status = Column(Enum(StatusNotificationEnum), nullable=False)

    alert = relationship("Alert", back_populates="notifications")
