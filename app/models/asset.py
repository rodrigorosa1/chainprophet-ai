from sqlalchemy import Column, ForeignKey, String, Text, Float, DateTime
from sqlalchemy.orm import relationship

from app.models.base import ModelBase


class Asset(ModelBase):
    __tablename__ = "assets"

    name = Column(String(100), nullable=False)
    symbol = Column(String(30), nullable=False)
    code = Column(String(20), nullable=False)

    users = relationship(
        "UserAsset", back_populates="asset", cascade="all, delete-orphan"
    )
