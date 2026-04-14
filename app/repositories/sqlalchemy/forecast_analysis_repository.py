from datetime import datetime

from sqlalchemy.orm import Session, joinedload

from app.models.forecast_asset import ForecastAsset
from app.models.forecast_diagnostic import ForecastDiagnostic
from app.models.forecast_point import ForecastPoint
from app.models.forecast_point_outcome import ForecastPointOutcome
from app.models.forecast_point_evaluation import ForecastPointEvaluation


class ForecastAnalysisRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_pending_outcome_points(self, limit: int = 100):
        return (
            self.db.query(ForecastPoint)
            .options(
                joinedload(ForecastPoint.forecast_asset),
                joinedload(ForecastPoint.outcome),
            )
            .filter(ForecastPoint.forecast_datetime <= datetime.utcnow())
            .filter(ForecastPoint.outcome == None)  # noqa: E711
            .limit(limit)
            .all()
        )

    def find_pending_evaluation_points(self, limit: int = 100):
        return (
            self.db.query(ForecastPoint)
            .options(
                joinedload(ForecastPoint.forecast_asset),
                joinedload(ForecastPoint.outcome),
                joinedload(ForecastPoint.evaluation),
            )
            .filter(ForecastPoint.outcome != None)  # noqa: E711
            .filter(ForecastPoint.evaluation == None)  # noqa: E711
            .limit(limit)
            .all()
        )

    def create_outcome(
        self,
        forecast_point_id: str,
        actual_datetime,
        actual_price: float,
        price_source: str | None = None,
    ) -> ForecastPointOutcome:
        try:
            outcome = ForecastPointOutcome(
                forecast_point_id=forecast_point_id,
                actual_datetime=actual_datetime,
                actual_price=actual_price,
                price_source=price_source,
            )

            self.db.add(outcome)
            self.db.commit()
            self.db.refresh(outcome)

            return outcome
        except Exception:
            self.db.rollback()
            raise

    def create_evaluation(
        self,
        forecast_point_id: str,
        forecast_asset_id: str,
        reference_price: float | None,
        target_price: float,
        lower_bound_price: float,
        upper_bound_price: float,
        actual_price: float,
        absolute_error: float,
        percentage_error: float,
        predicted_direction: str,
        actual_direction: str,
        direction_correct: bool,
        within_forecast_range: bool,
        range_deviation_percent: float,
        tolerance_percent: float,
        evaluation_status: str,
    ) -> ForecastPointEvaluation:
        try:
            evaluation = ForecastPointEvaluation(
                forecast_point_id=forecast_point_id,
                forecast_asset_id=forecast_asset_id,
                reference_price=reference_price,
                target_price=target_price,
                lower_bound_price=lower_bound_price,
                upper_bound_price=upper_bound_price,
                actual_price=actual_price,
                absolute_error=absolute_error,
                percentage_error=percentage_error,
                predicted_direction=predicted_direction,
                actual_direction=actual_direction,
                direction_correct=direction_correct,
                within_forecast_range=within_forecast_range,
                range_deviation_percent=range_deviation_percent,
                tolerance_percent=tolerance_percent,
                evaluation_status=evaluation_status,
            )

            self.db.add(evaluation)
            self.db.commit()
            self.db.refresh(evaluation)

            return evaluation
        except Exception:
            self.db.rollback()
            raise

    def find_assets_pending_diagnostic(self, limit: int = 100):
        return (
            self.db.query(ForecastAsset)
            .options(
                joinedload(ForecastAsset.backtest),
                joinedload(ForecastAsset.forecast_request),
                joinedload(ForecastAsset.forecast_points).joinedload(
                    ForecastPoint.evaluation
                ),
            )
            .filter(
                ForecastAsset.forecast_points.any(
                    ForecastPoint.evaluation != None  # noqa: E711
                )
            )
            .filter(ForecastAsset.diagnostic == None)  # noqa: E711
            .limit(limit)
            .all()
        )

    def find_asset_evaluations(self, forecast_asset_id: str):
        return (
            self.db.query(ForecastPointEvaluation)
            .filter(ForecastPointEvaluation.forecast_asset_id == forecast_asset_id)
            .order_by(ForecastPointEvaluation.created_at.asc())
            .all()
        )

    def create_diagnostic(
        self,
        forecast_request_id: str,
        forecast_asset_id: str,
        root_cause_category: str,
        confidence_score: float,
        summary: str,
        metrics_snapshot: dict,
        evidence: dict,
        recommended_actions: list[str],
    ) -> ForecastDiagnostic:
        try:
            diagnostic = ForecastDiagnostic(
                forecast_request_id=forecast_request_id,
                forecast_asset_id=forecast_asset_id,
                root_cause_category=root_cause_category,
                confidence_score=confidence_score,
                summary=summary,
                metrics_snapshot=metrics_snapshot,
                evidence=evidence,
                recommended_actions=recommended_actions,
            )

            self.db.add(diagnostic)
            self.db.commit()
            self.db.refresh(diagnostic)

            return diagnostic
        except Exception:
            self.db.rollback()
            raise
