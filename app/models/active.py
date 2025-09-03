from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import relationship
from app.constants.enums.type_active_enum import TypeActiveEnum
from app.models.base import ModelBase


class Active(ModelBase):
    __tablename__ = "actives"

    ticker = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    type = Column(Enum(TypeActiveEnum), nullable=False)

    alert = relationship("Alert", back_populates="active")
    investiment = relationship("Investiment", back_populates="active")
