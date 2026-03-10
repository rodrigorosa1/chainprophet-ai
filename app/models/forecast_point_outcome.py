from sqlalchemy import Column, ForeignKey, Float, DateTime, String
from sqlalchemy.orm import relationship

from app.models.base import ModelBase


class ForecastPointOutcome(ModelBase):
    __tablename__ = "forecast_point_outcomes"

    forecast_point_id = Column(
        ForeignKey("forecast_points.id"),
        nullable=False,
        unique=True,
    )
    actual_datetime = Column(DateTime, nullable=False)
    actual_price = Column(Float(), nullable=False)
    price_source = Column(String(50), nullable=True)

    forecast_point = relationship("ForecastPoint", back_populates="outcome")
