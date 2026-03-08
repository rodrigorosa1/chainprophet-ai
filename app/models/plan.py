from sqlalchemy import Boolean, Column, Integer, String, Float
from app.models.base import ModelBase
from sqlalchemy.orm import relationship


class Plan(ModelBase):
    __tablename__ = "plans"

    name = Column(String(255), nullable=False)
    daily_amount = Column(Integer(), nullable=True)
    no_limit = Column(Boolean, nullable=False)
    value = Column(Float(), nullable=False)

    subscriptions = relationship("Subscription", back_populates="plan")
