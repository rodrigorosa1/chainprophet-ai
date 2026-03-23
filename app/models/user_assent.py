from sqlalchemy import Column, ForeignKey, String, Text, Float, DateTime
from sqlalchemy.orm import relationship

from app.models.base import ModelBase


class UserAsset(ModelBase):
    __tablename__ = "user_assets"

    user_id = Column(ForeignKey("users.id"), nullable=False)
    asset_id = Column(ForeignKey("assets.id"), nullable=False)

    user = relationship("User", back_populates="assets")
    asset = relationship("Asset", back_populates="users")
