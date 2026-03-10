from sqlalchemy import Column, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship

from app.models.base import ModelBase


class ForecastPoint(ModelBase):
    __tablename__ = "forecast_points"

    forecast_asset_id = Column(ForeignKey("forecast_assets.id"), nullable=False)

    forecast_datetime = Column(DateTime, nullable=False)
    estimated_price = Column(Float(), nullable=False)
    confidence_percent = Column(Float(), nullable=False)

    forecast_asset = relationship("ForecastAsset", back_populates="forecast_points")

    outcome = relationship(
        "ForecastPointOutcome",
        back_populates="forecast_point",
        uselist=False,
        cascade="all, delete-orphan",
    )

    evaluation = relationship(
        "ForecastPointEvaluation",
        back_populates="forecast_point",
        uselist=False,
        cascade="all, delete-orphan",
    )
