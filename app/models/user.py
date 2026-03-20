from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from app.models.base import ModelBase


class User(ModelBase):
    __tablename__ = "users"

    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    phone = Column(String(100), nullable=True)
    api_key = Column(String(100), nullable=False)
    provider_customer_id = Column(String(100), nullable=True)
    active = Column(Boolean, nullable=False, default=True)

    subscription = relationship("Subscription", back_populates="user")
    histories = relationship("History", back_populates="user")
