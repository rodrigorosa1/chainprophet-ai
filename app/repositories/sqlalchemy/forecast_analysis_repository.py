from datetime import datetime
from sqlalchemy.orm import Session, joinedload

from app.models.forecast_point import ForecastPoint
from app.models.forecast_point_outcome import ForecastPointOutcome
from app.models.forecast_point_evaluation import ForecastPointEvaluation
from app.repositories.protocols.iforecast_analysis_repository import (
    IForecastAnalysisRepository,
)


class ForecastAnalysisRepository(IForecastAnalysisRepository):
    def __init__(self, db: Session):
        self.db = db

    def find_pending_outcome_points(self, limit: int = 100):
        return (
            self.db.query(ForecastPoint)
            .options(
                joinedload(ForecastPoint.forecast_asset),
                joinedload(ForecastPoint.outcome),
            )
            # .filter(ForecastPoint.forecast_datetime <= datetime.utcnow())
            .filter(ForecastPoint.outcome == None)
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
            .filter(ForecastPoint.outcome != None)
            .filter(ForecastPoint.evaluation == None)
            .limit(limit)
            .all()
        )

    def create_outcome(
        self,
        forecast_point_id: str,
        actual_datetime: datetime,
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
    ) -> ForecastPointEvaluation:
        try:
            evaluation = ForecastPointEvaluation(
                forecast_point_id=forecast_point_id,
                forecast_asset_id=forecast_asset_id,
                reference_price=reference_price,
                estimated_price=estimated_price,
                actual_price=actual_price,
                absolute_error=absolute_error,
                percentage_error=percentage_error,
                predicted_direction=predicted_direction,
                actual_direction=actual_direction,
                direction_correct=direction_correct,
                within_tolerance=within_tolerance,
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
