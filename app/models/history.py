from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import ModelBase
from sqlalchemy_utils import UUIDType


class History(ModelBase):
    __tablename__ = "histories"

    user_id = Column(UUIDType(binary=False), ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="histories")
