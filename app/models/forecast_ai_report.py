from sqlalchemy import Column, ForeignKey, String, JSON
from sqlalchemy.orm import relationship

from app.models.base import ModelBase


class ForecastAiReport(ModelBase):
    __tablename__ = "forecast_ai_reports"

    forecast_request_id = Column(
        ForeignKey("forecast_requests.id"),
        nullable=False,
    )
    forecast_asset_id = Column(
        ForeignKey("forecast_assets.id"),
        nullable=False,
        unique=True,
    )
    diagnostic_id = Column(
        ForeignKey("forecast_diagnostics.id"),
        nullable=False,
        unique=True,
    )

    analysis_summary = Column(String(1000), nullable=False)
    technical_explanation = Column(String(2000), nullable=True)
    business_explanation = Column(String(2000), nullable=True)
    risk_level = Column(String(20), nullable=True)

    evidence = Column(JSON, nullable=True)
    recommended_actions = Column(JSON, nullable=True)
    code_review_targets = Column(JSON, nullable=True)
    experiment_suggestions = Column(JSON, nullable=True)
    llm_raw_response = Column(JSON, nullable=True)

    forecast_asset = relationship("ForecastAsset")
    forecast_request = relationship("ForecastRequest")
    diagnostic = relationship("ForecastDiagnostic", back_populates="ai_report")
