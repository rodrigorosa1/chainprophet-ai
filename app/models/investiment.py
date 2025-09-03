from sqlalchemy import Column, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import ModelBase
from sqlalchemy_utils import UUIDType


class Investiment(ModelBase):
    __tablename__ = "investiments"

    active_id = Column(UUIDType(binary=False), ForeignKey("actives.id"), nullable=False)
    user_id = Column(UUIDType(binary=False), ForeignKey("users.id"), nullable=False)
    amount_invested = Column(Float(), nullable=False)
    gain_target_percentain = Column(Float(), nullable=False)
    loss_limit_percent = Column(Float(), nullable=False)

    active = relationship("Active", back_populates="investiment")
    user = relationship("User", back_populates="investiments")
