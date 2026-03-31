from app.constants.enums.cause_category_enum import CauseCategoryEnum
from app.constants.enums.cause_summary_enum import CauseSummaryEnum
from app.repositories.sqlalchemy.forecast_analysis_repository import (
    ForecastAnalysisRepository,
)


class ForecastFailureClassifierService:
    def __init__(self, analysis_repository: ForecastAnalysisRepository):
        self.analysis_repository = analysis_repository

    def classify_pending_assets(self, limit: int = 100) -> list[dict]:
        assets = self.analysis_repository.find_assets_pending_diagnostic(limit=limit)

        results = []

        for asset in assets:
            evaluations = self.analysis_repository.find_asset_evaluations(asset.id)

            if not evaluations:
                continue

            classification = self._classify_asset(asset, evaluations)

            diagnostic = self.analysis_repository.create_diagnostic(
                forecast_request_id=asset.forecast_request_id,
                forecast_asset_id=asset.id,
                root_cause_category=classification["root_cause_category"],
                confidence_score=classification["confidence_score"],
                summary=classification["summary"],
                metrics_snapshot=classification["metrics_snapshot"],
                evidence=classification["evidence"],
                recommended_actions=classification["recommended_actions"],
            )

            results.append(
                {
                    "forecast_asset_id": str(asset.id),
                    "diagnostic_id": str(diagnostic.id),
                    "asset_symbol": asset.asset_symbol,
                    "root_cause_category": diagnostic.root_cause_category,
                    "confidence_score": diagnostic.confidence_score,
                    "summary": diagnostic.summary,
                    "recommended_actions": diagnostic.recommended_actions,
                }
            )

        return results

    def _classify_asset(self, asset, evaluations: list) -> dict:
        total = len(evaluations)
        miss_count = sum(1 for item in evaluations if item.evaluation_status == "miss")
        partial_hit_count = sum(
            1 for item in evaluations if item.evaluation_status == "partial_hit"
        )
        hit_count = sum(1 for item in evaluations if item.evaluation_status == "hit")

        direction_errors = sum(1 for item in evaluations if not item.direction_correct)
        unknown_direction = sum(
            1 for item in evaluations if item.predicted_direction == "unknown"
        )

        avg_percentage_error = (
            sum(item.percentage_error for item in evaluations) / total
        )
        avg_absolute_error = sum(item.absolute_error for item in evaluations) / total

        miss_ratio = miss_count / total
        direction_error_ratio = direction_errors / total
        hit_ratio = hit_count / total

        backtest = getattr(asset, "backtest", None)
        backtest_quality = float(backtest.quality_score_percent) if backtest else None
        backtest_directional = (
            float(backtest.directional_accuracy_percent) if backtest else None
        )
        backtest_mape = float(backtest.mape_percent) if backtest else None

        metrics_snapshot = {
            "total_points": total,
            "hit_count": hit_count,
            "partial_hit_count": partial_hit_count,
            "miss_count": miss_count,
            "hit_ratio": round(hit_ratio, 4),
            "miss_ratio": round(miss_ratio, 4),
            "direction_error_ratio": round(direction_error_ratio, 4),
            "avg_percentage_error": round(avg_percentage_error, 4),
            "avg_absolute_error": round(avg_absolute_error, 4),
            "backtest_quality_score_percent": backtest_quality,
            "backtest_directional_accuracy_percent": backtest_directional,
            "backtest_mape_percent": backtest_mape,
        }

        if unknown_direction / total > 0.4:
            return {
                "root_cause_category": CauseCategoryEnum.DATA_QUALITY.value,
                "confidence_score": 0.82,
                "summary": CauseSummaryEnum.MISSING_REFERENCE_POINT.value,
                "metrics_snapshot": metrics_snapshot,
                "evidence": {
                    "unknown_direction_ratio": round(unknown_direction / total, 4),
                },
                "recommended_actions": [
                    "Save the actual reference price at the time the forecast is generated.",
                    "Validate that all assets have a base context for direction calculation.",
                ],
            }

        if miss_ratio <= 0.20 and avg_percentage_error <= 2.0:
            return {
                "root_cause_category": CauseCategoryEnum.LOW_FAILURE_PATTERN.value,
                "confidence_score": 0.88,
                "summary": CauseSummaryEnum.NO_FAILURE_PATTERN.value,
                "metrics_snapshot": metrics_snapshot,
                "evidence": {
                    "miss_ratio": round(miss_ratio, 4),
                    "avg_percentage_error": round(avg_percentage_error, 4),
                },
                "recommended_actions": [
                    "Maintain continuous monitoring.",
                    "Monitor regime changes if volatility increases.",
                ],
            }

        if direction_error_ratio >= 0.60 and miss_ratio >= 0.60:
            return {
                "root_cause_category": CauseCategoryEnum.PARAMETER_MISCALIBRATION.value,
                "confidence_score": 0.79,
                "summary": CauseSummaryEnum.DIRECTION_MISJUDGMENT.value,
                "metrics_snapshot": metrics_snapshot,
                "evidence": {
                    "direction_error_ratio": round(direction_error_ratio, 4),
                    "miss_ratio": round(miss_ratio, 4),
                },
                "recommended_actions": [
                    "Review the forecast horizon for this asset.",
                    "Test different changepoint and seasonality parameters in Prophet.",
                    "Separate configuration by asset instead of using generic parameters.",
                ],
            }

        if direction_error_ratio < 0.35 and avg_percentage_error >= 3.5:
            return {
                "root_cause_category": CauseCategoryEnum.MODEL_UNDERFITTING.value,
                "confidence_score": 0.76,
                "summary": CauseSummaryEnum.MAGNITUDE_MISJUDGMENT.value,
                "metrics_snapshot": metrics_snapshot,
                "evidence": {
                    "direction_error_ratio": round(direction_error_ratio, 4),
                    "avg_percentage_error": round(avg_percentage_error, 4),
                },
                "recommended_actions": [
                    "Increase sensitivity to recent movements.",
                    "Test additional volatility and volume features.",
                    "Evaluate complementary models for adjusting the predicted magnitude.",
                ],
            }

        if (
            backtest_quality is not None
            and backtest_quality < 50
            and miss_ratio >= 0.50
        ):
            return {
                "root_cause_category": CauseCategoryEnum.FEATURE_GAP.value,
                "confidence_score": 0.72,
                "summary": CauseSummaryEnum.LOW_SIGNAL_QUALITY.value,
                "metrics_snapshot": metrics_snapshot,
                "evidence": {
                    "backtest_quality_score_percent": backtest_quality,
                    "miss_ratio": round(miss_ratio, 4),
                },
                "recommended_actions": [
                    "Add intraday volatility features.",
                    "Increase the relevance of abnormal volume and market regime.",
                    "Evaluate the inclusion of macro context and correlations between assets.",
                ],
            }

        if miss_ratio >= 0.50 and hit_ratio < 0.20 and avg_percentage_error >= 5.0:
            return {
                "root_cause_category": CauseCategoryEnum.MARKET_EVENT.value,
                "confidence_score": 0.61,
                "summary": CauseSummaryEnum.EXTREME_MARKET_BEHAVIOR.value,
                "metrics_snapshot": metrics_snapshot,
                "evidence": {
                    "miss_ratio": round(miss_ratio, 4),
                    "avg_percentage_error": round(avg_percentage_error, 4),
                },
                "recommended_actions": [
                    "To cross this period with market news and events.",
                    "Create an extreme regime detector.",
                    "Apply a reduced confidence fallback during high volatility.",
                ],
            }

        return {
            "root_cause_category": CauseCategoryEnum.UNKNOWN.value,
            "confidence_score": 0.45,
            "summary": CauseSummaryEnum.INCONCLUSIVE_FAILURE_PATTERN.value,
            "metrics_snapshot": metrics_snapshot,
            "evidence": {
                "miss_ratio": round(miss_ratio, 4),
                "direction_error_ratio": round(direction_error_ratio, 4),
                "avg_percentage_error": round(avg_percentage_error, 4),
            },
            "recommended_actions": [
                "Increase the number of evaluated cycles.",
                "Include new classification rules.",
                "Register additional context to enrich the diagnosis.",
            ],
        }
