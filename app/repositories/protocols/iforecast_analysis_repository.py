import datetime
from typing import Protocol

from app.models.forecast_diagnostic import ForecastDiagnostic
from app.models.forecast_point_evaluation import ForecastPointEvaluation
from app.models.forecast_point_outcome import ForecastPointOutcome


class IForecastAnalysisRepository(Protocol):
    def find_pending_outcome_points(self, limit: int = 100): ...
    def find_pending_evaluation_points(self, limit: int = 100): ...
    def create_outcome(
        self,
        forecast_point_id: str,
        actual_datetime: datetime,
        actual_price: float,
        price_source: str | None = None,
    ) -> ForecastPointOutcome: ...
    def create_evaluation(
        self,
        forecast_point_id: str,
        forecast_asset_id: str,
        reference_price: float | None,
        estimated_price: float,
        actual_price: float,
        absolute_error: float,
        percentage_error: float,
        predicted_direction: str,
        actual_direction: str,
        direction_correct: bool,
        within_tolerance: bool,
        tolerance_percent: float,
        evaluation_status: str,
    ) -> ForecastPointEvaluation: ...
    def find_assets_pending_diagnostic(self, limit: int = 100): ...
    def find_asset_evaluations(self, forecast_asset_id: str): ...
    def create_diagnostic(
        self,
        forecast_request_id: str,
        forecast_asset_id: str,
        root_cause_category: str,
        confidence_score: float,
        summary: str,
        metrics_snapshot: dict | None = None,
        evidence: dict | None = None,
        recommended_actions: list[str] | None = None,
    ) -> ForecastDiagnostic: ...
