from app.agents.forecast_improvement_agent import ForecastImprovementAgent
from app.repositories.sqlalchemy.forecast_ai_report_repository import (
    ForecastAiReportRepository,
)


class ForecastLangChainAnalystService:
    def __init__(
        self,
        ai_report_repository: ForecastAiReportRepository,
        agent: ForecastImprovementAgent,
    ):
        self.ai_report_repository = ai_report_repository
        self.agent = agent

    def analyze_pending_diagnostics(self, limit: int = 100) -> list[dict]:
        diagnostics = self.ai_report_repository.find_pending_ai_reports(limit=limit)

        results = []

        for diagnostic in diagnostics:
            payload = self._build_payload(diagnostic)

            try:
                report_data = self.agent.analyze(payload)
                normalized = report_data.model_dump()
            except Exception as e:
                normalized = self._fallback_response(diagnostic, str(e))

            report = self.ai_report_repository.create(
                forecast_request_id=diagnostic.forecast_request_id,
                forecast_asset_id=diagnostic.forecast_asset_id,
                diagnostic_id=diagnostic.id,
                analysis_summary=normalized["analysis_summary"],
                technical_explanation=normalized["technical_explanation"],
                business_explanation=normalized.get("business_explanation"),
                risk_level=normalized["risk_level"],
                evidence=normalized.get("evidence", []),
                recommended_actions=normalized.get("recommended_actions", []),
                code_review_targets=normalized.get("code_review_targets", []),
                experiment_suggestions=normalized.get("experiment_suggestions", []),
                llm_raw_response=normalized,
            )

            results.append(
                {
                    "forecast_asset_id": str(diagnostic.forecast_asset_id),
                    "diagnostic_id": str(diagnostic.id),
                    "ai_report_id": str(report.id),
                    "asset_symbol": diagnostic.forecast_asset.asset_symbol,
                    "analysis_summary": report.analysis_summary,
                    "risk_level": report.risk_level,
                    "recommended_actions": report.recommended_actions,
                    "code_review_targets": report.code_review_targets,
                }
            )

        return results

    def _build_payload(self, diagnostic) -> dict:
        asset = diagnostic.forecast_asset
        backtest = asset.backtest
        request = asset.forecast_request

        return {
            "asset": {
                "symbol": asset.asset_symbol,
                "name": asset.asset_name,
                "code": asset.asset_code,
            },
            "request_context": {
                "timeframe": request.timeframe if request else None,
                "horizon_hours": request.horizon_hours if request else None,
                "model_version": request.model_version if request else None,
            },
            "backtest": {
                "windows_used": backtest.windows_used if backtest else None,
                "horizon_hours": backtest.horizon_hours if backtest else None,
                "mae": (
                    float(backtest.mae)
                    if backtest and backtest.mae is not None
                    else None
                ),
                "rmse": (
                    float(backtest.rmse)
                    if backtest and backtest.rmse is not None
                    else None
                ),
                "mape_percent": (
                    float(backtest.mape_percent)
                    if backtest and backtest.mape_percent is not None
                    else None
                ),
                "directional_accuracy_percent": (
                    float(backtest.directional_accuracy_percent)
                    if backtest and backtest.directional_accuracy_percent is not None
                    else None
                ),
                "quality_score_percent": (
                    float(backtest.quality_score_percent)
                    if backtest and backtest.quality_score_percent is not None
                    else None
                ),
            },
            "evaluation_summary": diagnostic.metrics_snapshot or {},
            "classifier_result": {
                "root_cause_category": diagnostic.root_cause_category,
                "confidence_score": diagnostic.confidence_score,
                "summary": diagnostic.summary,
                "evidence": diagnostic.evidence or {},
                "recommended_actions": diagnostic.recommended_actions or [],
            },
        }

    def _fallback_response(self, diagnostic, error: str) -> dict:
        return {
            "analysis_summary": "LangChain agent failed. Deterministic diagnostic maintained.",
            "technical_explanation": error,
            "business_explanation": None,
            "root_cause": diagnostic.root_cause_category,
            "risk_level": "medium",
            "evidence": [],
            "recommended_actions": diagnostic.recommended_actions or [],
            "code_review_targets": [],
            "experiment_suggestions": [],
            "should_open_pr": False,
        }
