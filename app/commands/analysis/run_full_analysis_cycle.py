from app.core.database import Session
from app.repositories.sqlalchemy.forecast_analysis_repository import (
    ForecastAnalysisRepository,
)
from app.services.forecast_outcome_service import ForecastOutcomeService
from app.services.forecast_evaluation_service import ForecastEvaluationService
from app.services.forecast_failure_classifier_service import (
    ForecastFailureClassifierService,
)
from app.services.market_data_service import MarketDataService


def run() -> dict:
    db = Session()

    try:
        analysis_repository = ForecastAnalysisRepository(db)
        market_data_service = MarketDataService()

        outcome_service = ForecastOutcomeService(
            analysis_repository=analysis_repository,
            market_data_service=market_data_service,
        )

        evaluation_service = ForecastEvaluationService(
            analysis_repository=analysis_repository,
        )

        classifier_service = ForecastFailureClassifierService(
            analysis_repository=analysis_repository,
        )

        collected = outcome_service.collect_pending_outcomes(limit=1000)
        evaluated = evaluation_service.evaluate_pending_points(
            tolerance_percent=2.0,
            limit=1000,
        )
        classified = classifier_service.classify_pending_assets(limit=1000)

        return {
            "status": "success",
            "message": "Forecast analysis cycle completed successfully",
            "summary": {
                "collected_outcomes": len(collected),
                "evaluated_points": len(evaluated),
                "classified_assets": len(classified),
            },
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": "Forecast analysis cycle failed",
            "error": str(exc),
        }
    finally:
        db.close()


if __name__ == "__main__":
    print(run())
