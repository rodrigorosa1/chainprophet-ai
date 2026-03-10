from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship
from app.models.base import ModelBase


class ForecastRequest(ModelBase):
    __tablename__ = "forecast_requests"

    timeframe = Column(String(20), nullable=False)
    horizon_hours = Column(Integer(), nullable=False)
    total_assets = Column(Integer(), nullable=False)
    model_version = Column(String(50), nullable=True)
    request_payload = Column(JSON, nullable=True)
    response_payload = Column(JSON, nullable=True)

    assets = relationship(
        "ForecastAsset", back_populates="forecast_request", cascade="all, delete-orphan"
    )
