from sqlalchemy import Column, ForeignKey, DateTime, Boolean
from app.models.base import ModelBase
from sqlalchemy.orm import relationship
from app.models.base import ModelBase
from sqlalchemy_utils import UUIDType


class Subscription(ModelBase):
    __tablename__ = "subscriptions"

    user_id = Column(UUIDType(binary=False), ForeignKey("users.id"), nullable=False)
    plan_id = Column(UUIDType(binary=False), ForeignKey("plans.id"), nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    started_at = Column(DateTime, nullable=False)
    canceled_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="subscription")
    plan = relationship("Plan", back_populates="subscriptions")
