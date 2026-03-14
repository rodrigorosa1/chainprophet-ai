from sqlalchemy import Column, ForeignKey, Float, String, JSON
from sqlalchemy.orm import relationship

from app.models.base import ModelBase


class ForecastDiagnostic(ModelBase):
    __tablename__ = "forecast_diagnostics"

    forecast_request_id = Column(
        ForeignKey("forecast_requests.id"),
        nullable=False,
    )
    forecast_asset_id = Column(
        ForeignKey("forecast_assets.id"),
        nullable=False,
        unique=True,
    )

    root_cause_category = Column(String(50), nullable=False)
    confidence_score = Column(Float(), nullable=False)
    summary = Column(String(500), nullable=False)

    metrics_snapshot = Column(JSON, nullable=True)
    evidence = Column(JSON, nullable=True)
    recommended_actions = Column(JSON, nullable=True)

    forecast_asset = relationship("ForecastAsset", back_populates="diagnostic")
    forecast_request = relationship("ForecastRequest")

    ai_report = relationship(
        "ForecastAiReport",
        uselist=False,
        cascade="all, delete-orphan",
    )
