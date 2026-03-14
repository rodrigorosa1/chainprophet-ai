from app.constants.enums.evaluation_status_enum import EvaluationStatusEnum
from app.repositories.sqlalchemy.forecast_analysis_repository import (
    ForecastAnalysisRepository,
)


class ForecastEvaluationService:
    def __init__(self, analysis_repository: ForecastAnalysisRepository):
        self.analysis_repository = analysis_repository

    def evaluate_pending_points(
        self,
        tolerance_percent: float = 2.0,
        limit: int = 100,
    ) -> list[dict]:
        points = self.analysis_repository.find_pending_evaluation_points(limit=limit)

        evaluations = []

        for point in points:
            actual_price = point.outcome.actual_price
            estimated_price = point.estimated_price
            reference_price = self._resolve_reference_price(point)

            result = self._evaluate_point(
                estimated_price=estimated_price,
                actual_price=actual_price,
                reference_price=reference_price,
                tolerance_percent=tolerance_percent,
            )

            evaluation = self.analysis_repository.create_evaluation(
                forecast_point_id=point.id,
                forecast_asset_id=point.forecast_asset_id,
                reference_price=reference_price,
                estimated_price=estimated_price,
                actual_price=actual_price,
                absolute_error=result["absolute_error"],
                percentage_error=result["percentage_error"],
                predicted_direction=result["predicted_direction"],
                actual_direction=result["actual_direction"],
                direction_correct=result["direction_correct"],
                within_tolerance=result["within_tolerance"],
                tolerance_percent=result["tolerance_percent"],
                evaluation_status=result["evaluation_status"],
            )

            evaluations.append(
                {
                    "forecast_point_id": str(point.id),
                    "evaluation_id": str(evaluation.id),
                    "asset_symbol": point.forecast_asset.asset_symbol,
                    "estimated_price": estimated_price,
                    "actual_price": actual_price,
                    "absolute_error": result["absolute_error"],
                    "percentage_error": result["percentage_error"],
                    "direction_correct": result["direction_correct"],
                    "within_tolerance": result["within_tolerance"],
                    "evaluation_status": result["evaluation_status"],
                }
            )

        return evaluations

    def _evaluate_point(
        self,
        estimated_price: float,
        actual_price: float,
        reference_price: float | None,
        tolerance_percent: float = 2.0,
    ) -> dict:
        absolute_error = abs(actual_price - estimated_price)

        if estimated_price and estimated_price != 0:
            percentage_error = (
                abs((actual_price - estimated_price) / estimated_price) * 100
            )
        else:
            percentage_error = 0.0

        predicted_direction = self._get_direction(
            reference_price=reference_price,
            target_price=estimated_price,
        )
        actual_direction = self._get_direction(
            reference_price=reference_price,
            target_price=actual_price,
        )

        direction_correct = predicted_direction == actual_direction
        within_tolerance = percentage_error <= tolerance_percent

        if direction_correct and within_tolerance:
            evaluation_status = EvaluationStatusEnum.HIT.value
        elif direction_correct:
            evaluation_status = EvaluationStatusEnum.PARTIAL_HIT.value
        else:
            evaluation_status = EvaluationStatusEnum.MISS.value

        return {
            "absolute_error": round(absolute_error, 4),
            "percentage_error": round(percentage_error, 4),
            "predicted_direction": predicted_direction,
            "actual_direction": actual_direction,
            "direction_correct": direction_correct,
            "within_tolerance": within_tolerance,
            "tolerance_percent": tolerance_percent,
            "evaluation_status": evaluation_status,
        }

    def _get_direction(
        self,
        reference_price: float | None,
        target_price: float,
    ) -> str:
        if reference_price is None:
            return "unknown"

        if target_price > reference_price:
            return "up"

        if target_price < reference_price:
            return "down"

        return "flat"

    def _resolve_reference_price(self, point) -> float | None:
        forecast_asset = point.forecast_asset

        if getattr(forecast_asset, "reference_price", None) is not None:
            return forecast_asset.reference_price

        sibling_points = sorted(
            forecast_asset.forecast_points,
            key=lambda item: item.forecast_datetime,
        )

        if not sibling_points:
            return None

        first_point = sibling_points[0]
        return first_point.estimated_price
