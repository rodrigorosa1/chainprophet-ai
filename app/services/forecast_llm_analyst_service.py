from app.clients.interfaces.i_ai_client import IAiClient
from app.repositories.sqlalchemy.forecast_ai_report_repository import (
    ForecastAiReportRepository,
)


class ForecastLlmAnalystService:
    def __init__(
        self,
        ai_report_repository: ForecastAiReportRepository,
        ai_client: IAiClient,
    ):
        self.ai_report_repository = ai_report_repository
        self.ai_client = ai_client

    def analyze_pending_diagnostics(self, limit: int = 100) -> list[dict]:
        diagnostics = self.ai_report_repository.find_pending_ai_reports(limit=limit)

        results = []

        for diagnostic in diagnostics:
            payload = self._build_payload(diagnostic)

            try:
                ai_response = self.ai_client.analyze_forecast_failure(payload)
            except Exception as e:
                ai_response = {
                    "analysis_summary": (
                        "Failed to generate analysis with LLM. "
                        "Deterministic diagnostic maintained as fallback."
                    ),
                    "technical_explanation": str(e),
                    "business_explanation": None,
                    "evidence": [],
                    "recommended_actions": diagnostic.recommended_actions or [],
                    "code_review_targets": [],
                    "experiment_suggestions": [],
                    "risk_level": "unknown",
                }

            normalized = self._normalize_response(ai_response, diagnostic)

            report = self.ai_report_repository.create(
                forecast_request_id=diagnostic.forecast_request_id,
                forecast_asset_id=diagnostic.forecast_asset_id,
                diagnostic_id=diagnostic.id,
                analysis_summary=normalized["analysis_summary"],
                technical_explanation=normalized["technical_explanation"],
                business_explanation=normalized["business_explanation"],
                risk_level=normalized["risk_level"],
                evidence=normalized["evidence"],
                recommended_actions=normalized["recommended_actions"],
                code_review_targets=normalized["code_review_targets"],
                experiment_suggestions=normalized["experiment_suggestions"],
                llm_raw_response=ai_response,
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

    def _normalize_response(self, ai_response: dict, diagnostic) -> dict:
        return {
            "analysis_summary": ai_response.get(
                "analysis_summary",
                f"Automated analysis unavailable. Diagnosis maintained {diagnostic.root_cause_category}.",
            ),
            "technical_explanation": ai_response.get("technical_explanation"),
            "business_explanation": ai_response.get("business_explanation"),
            "risk_level": ai_response.get("risk_level", "unknown"),
            "evidence": ai_response.get("evidence", []),
            "recommended_actions": ai_response.get(
                "recommended_actions",
                diagnostic.recommended_actions or [],
            ),
            "code_review_targets": ai_response.get("code_review_targets", []),
            "experiment_suggestions": ai_response.get("experiment_suggestions", []),
        }

    def list_reports(self, limit: int = 50, offset: int = 0) -> list[dict]:
        reports = self.ai_report_repository.find_reports(
            limit=limit,
            offset=offset,
        )

        return [self._serialize_report(report) for report in reports]

    def _serialize_report(self, report) -> dict:
        return {
            "id": str(report.id),
            "forecast_request": self._serialize_forecast_request(
                report.forecast_request
            ),
            "forecast_asset": self._serialize_forecast_asset(report.forecast_asset),
            "diagnostic": self._serialize_diagnostic(report.diagnostic),
            "analysis_summary": report.analysis_summary,
            "technical_explanation": report.technical_explanation,
            "business_explanation": report.business_explanation,
            "risk_level": report.risk_level,
            "evidence": report.evidence,
            "recommended_actions": report.recommended_actions,
            "code_review_targets": report.code_review_targets,
            "experiment_suggestions": report.experiment_suggestions,
            "llm_raw_response": report.llm_raw_response,
        }

    def _serialize_forecast_request(self, forecast_request) -> dict | None:
        if forecast_request is None:
            return None

        return {
            "id": str(forecast_request.id),
            "timeframe": forecast_request.timeframe,
            "horizon_hours": forecast_request.horizon_hours,
            "total_assets": forecast_request.total_assets,
            "model_version": forecast_request.model_version,
            "request_payload": forecast_request.request_payload,
            "response_payload": forecast_request.response_payload,
        }

    def _serialize_forecast_asset(self, forecast_asset) -> dict | None:
        if forecast_asset is None:
            return None

        return {
            "id": str(forecast_asset.id),
            "forecast_request_id": str(forecast_asset.forecast_request_id),
            "asset_name": forecast_asset.asset_name,
            "asset_symbol": forecast_asset.asset_symbol,
            "asset_code": forecast_asset.asset_code,
            "reference_price": forecast_asset.reference_price,
            "reference_datetime": self._format_datetime(
                forecast_asset.reference_datetime
            ),
            "error": forecast_asset.error,
        }

    def _serialize_diagnostic(self, diagnostic) -> dict | None:
        if diagnostic is None:
            return None

        return {
            "id": str(diagnostic.id),
            "forecast_request_id": str(diagnostic.forecast_request_id),
            "forecast_asset_id": str(diagnostic.forecast_asset_id),
            "root_cause_category": diagnostic.root_cause_category,
            "confidence_score": diagnostic.confidence_score,
            "summary": diagnostic.summary,
            "metrics_snapshot": diagnostic.metrics_snapshot,
            "evidence": diagnostic.evidence,
            "recommended_actions": diagnostic.recommended_actions,
        }

    def _format_datetime(self, value):
        if value is None:
            return None

        return value.strftime("%Y-%m-%d %H:%M:%S")
