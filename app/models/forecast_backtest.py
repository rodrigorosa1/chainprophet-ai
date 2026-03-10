from sqlalchemy import Column, ForeignKey, Integer, Float
from sqlalchemy.orm import relationship

from app.models.base import ModelBase


class ForecastBacktest(ModelBase):
    __tablename__ = "forecast_backtests"

    forecast_asset_id = Column(
        ForeignKey("forecast_assets.id"), nullable=False, unique=True
    )

    windows_used = Column(Integer(), nullable=False)
    horizon_hours = Column(Integer(), nullable=False)
    mae = Column(Float(), nullable=False)
    rmse = Column(Float(), nullable=False)
    mape_percent = Column(Float(), nullable=False)
    directional_accuracy_percent = Column(Float(), nullable=False)
    quality_score_percent = Column(Float(), nullable=False)

    forecast_asset = relationship("ForecastAsset", back_populates="backtest")
