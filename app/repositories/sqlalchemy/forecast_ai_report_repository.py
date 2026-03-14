from sqlalchemy.orm import Session, joinedload

from app.models.forecast_asset import ForecastAsset
from app.models.forecast_ai_report import ForecastAiReport
from app.models.forecast_diagnostic import ForecastDiagnostic


class ForecastAiReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_pending_ai_reports(self, limit: int = 100):
        return (
            self.db.query(ForecastDiagnostic)
            .options(
                joinedload(ForecastDiagnostic.forecast_asset).joinedload(
                    ForecastAsset.backtest
                ),
                joinedload(ForecastDiagnostic.forecast_asset).joinedload(
                    ForecastAsset.forecast_request
                ),
                joinedload(ForecastDiagnostic.ai_report),
            )
            .filter(ForecastDiagnostic.ai_report == None)
            .limit(limit)
            .all()
        )

    def create(
        self,
        forecast_request_id: str,
        forecast_asset_id: str,
        diagnostic_id: str,
        analysis_summary: str,
        technical_explanation: str | None = None,
        business_explanation: str | None = None,
        risk_level: str | None = None,
        evidence: list | None = None,
        recommended_actions: list | None = None,
        code_review_targets: list | None = None,
        experiment_suggestions: list | None = None,
        llm_raw_response: dict | None = None,
    ) -> ForecastAiReport:
        try:
            report = ForecastAiReport(
                forecast_request_id=forecast_request_id,
                forecast_asset_id=forecast_asset_id,
                diagnostic_id=diagnostic_id,
                analysis_summary=analysis_summary,
                technical_explanation=technical_explanation,
                business_explanation=business_explanation,
                risk_level=risk_level,
                evidence=evidence,
                recommended_actions=recommended_actions,
                code_review_targets=code_review_targets,
                experiment_suggestions=experiment_suggestions,
                llm_raw_response=llm_raw_response,
            )

            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)

            return report
        except Exception:
            self.db.rollback()
            raise
