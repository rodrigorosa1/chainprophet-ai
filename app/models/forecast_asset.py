from sqlalchemy import Column, ForeignKey, String, Text, Float, DateTime
from sqlalchemy.orm import relationship

from app.models.base import ModelBase


class ForecastAsset(ModelBase):
    __tablename__ = "forecast_assets"

    forecast_request_id = Column(ForeignKey("forecast_requests.id"), nullable=False)

    asset_name = Column(String(100), nullable=False)
    asset_symbol = Column(String(30), nullable=False)
    asset_code = Column(String(20), nullable=False)

    reference_price = Column(Float(), nullable=True)
    reference_datetime = Column(DateTime, nullable=True)

    error = Column(Text, nullable=True)

    forecast_request = relationship("ForecastRequest", back_populates="assets")

    backtest = relationship(
        "ForecastBacktest",
        back_populates="forecast_asset",
        uselist=False,
        cascade="all, delete-orphan",
    )

    forecast_points = relationship(
        "ForecastPoint", back_populates="forecast_asset", cascade="all, delete-orphan"
    )

    diagnostic = relationship(
        "ForecastDiagnostic",
        back_populates="forecast_asset",
        uselist=False,
        cascade="all, delete-orphan",
    )
