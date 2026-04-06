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
            target_price = point.target_price
            lower_bound_price = point.lower_bound_price
            upper_bound_price = point.upper_bound_price
            reference_price = self._resolve_reference_price(point)

            result = self._evaluate_point(
                target_price=target_price,
                lower_bound_price=lower_bound_price,
                upper_bound_price=upper_bound_price,
                actual_price=actual_price,
                reference_price=reference_price,
                tolerance_percent=tolerance_percent,
            )

            evaluation = self.analysis_repository.create_evaluation(
                forecast_point_id=point.id,
                forecast_asset_id=point.forecast_asset_id,
                reference_price=reference_price,
                target_price=target_price,
                lower_bound_price=lower_bound_price,
                upper_bound_price=upper_bound_price,
                actual_price=actual_price,
                absolute_error=result["absolute_error"],
                percentage_error=result["percentage_error"],
                predicted_direction=result["predicted_direction"],
                actual_direction=result["actual_direction"],
                direction_correct=result["direction_correct"],
                within_forecast_range=result["within_forecast_range"],
                range_deviation_percent=result["range_deviation_percent"],
                tolerance_percent=result["tolerance_percent"],
                evaluation_status=result["evaluation_status"],
            )

            evaluations.append(
                {
                    "forecast_point_id": str(point.id),
                    "evaluation_id": str(evaluation.id),
                    "asset_symbol": point.forecast_asset.asset_symbol,
                    "target_price": target_price,
                    "lower_bound_price": lower_bound_price,
                    "upper_bound_price": upper_bound_price,
                    "actual_price": actual_price,
                    "absolute_error": result["absolute_error"],
                    "percentage_error": result["percentage_error"],
                    "direction_correct": result["direction_correct"],
                    "within_forecast_range": result["within_forecast_range"],
                    "range_deviation_percent": result["range_deviation_percent"],
                    "evaluation_status": result["evaluation_status"],
                }
            )

        return evaluations

    def _evaluate_point(
        self,
        target_price: float,
        lower_bound_price: float,
        upper_bound_price: float,
        actual_price: float,
        reference_price: float | None,
        tolerance_percent: float = 2.0,
    ) -> dict:
        absolute_error = abs(actual_price - target_price)

        if target_price and target_price != 0:
            percentage_error = abs((actual_price - target_price) / target_price) * 100
        else:
            percentage_error = 0.0

        predicted_direction = self._get_direction(
            reference_price=reference_price,
            target_price=target_price,
        )
        actual_direction = self._get_direction(
            reference_price=reference_price,
            target_price=actual_price,
        )

        direction_correct = predicted_direction == actual_direction
        within_forecast_range = lower_bound_price <= actual_price <= upper_bound_price

        range_deviation_percent = self._calculate_range_deviation_percent(
            actual_price=actual_price,
            lower_bound_price=lower_bound_price,
            upper_bound_price=upper_bound_price,
            target_price=target_price,
        )

        if direction_correct and within_forecast_range:
            evaluation_status = "hit"
        elif direction_correct:
            evaluation_status = "partial_hit"
        else:
            evaluation_status = "miss"

        return {
            "absolute_error": round(absolute_error, 4),
            "percentage_error": round(percentage_error, 4),
            "predicted_direction": predicted_direction,
            "actual_direction": actual_direction,
            "direction_correct": direction_correct,
            "within_forecast_range": within_forecast_range,
            "range_deviation_percent": round(range_deviation_percent, 4),
            "tolerance_percent": tolerance_percent,
            "evaluation_status": evaluation_status,
        }

    def _calculate_range_deviation_percent(
        self,
        actual_price: float,
        lower_bound_price: float,
        upper_bound_price: float,
        target_price: float,
    ) -> float:
        if lower_bound_price <= actual_price <= upper_bound_price:
            return 0.0

        if actual_price < lower_bound_price:
            if target_price == 0:
                return 0.0
            return abs((lower_bound_price - actual_price) / target_price) * 100

        if target_price == 0:
            return 0.0

        return abs((actual_price - upper_bound_price) / target_price) * 100

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
        return first_point.target_price
