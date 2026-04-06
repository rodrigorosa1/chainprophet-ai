from sqlalchemy import Column, ForeignKey, Float, Boolean, String
from sqlalchemy.orm import relationship

from app.models.base import ModelBase


class ForecastPointEvaluation(ModelBase):
    __tablename__ = "forecast_point_evaluations"

    forecast_point_id = Column(
        ForeignKey("forecast_points.id"),
        nullable=False,
        unique=True,
    )
    forecast_asset_id = Column(
        ForeignKey("forecast_assets.id"),
        nullable=False,
    )

    reference_price = Column(Float(), nullable=True)

    target_price = Column(Float(), nullable=False)
    lower_bound_price = Column(Float(), nullable=False)
    upper_bound_price = Column(Float(), nullable=False)
    actual_price = Column(Float(), nullable=False)

    absolute_error = Column(Float(), nullable=False)
    percentage_error = Column(Float(), nullable=False)

    predicted_direction = Column(String(20), nullable=False)
    actual_direction = Column(String(20), nullable=False)
    direction_correct = Column(Boolean, nullable=False)

    within_forecast_range = Column(Boolean, nullable=False)
    range_deviation_percent = Column(Float(), nullable=False)

    tolerance_percent = Column(Float(), nullable=False)
    evaluation_status = Column(String(30), nullable=False)

    forecast_point = relationship("ForecastPoint", back_populates="evaluation")
    forecast_asset = relationship("ForecastAsset")
