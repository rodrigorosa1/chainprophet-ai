from app.core.database import Session
from app.repositories.sqlalchemy.forecast_analysis_repository import (
    ForecastAnalysisRepository,
)
from app.repositories.sqlalchemy.job_execution_repository import JobExecutionRepository
from app.services.forecast_outcome_service import ForecastOutcomeService
from app.services.forecast_evaluation_service import ForecastEvaluationService
from app.services.forecast_failure_classifier_service import (
    ForecastFailureClassifierService,
)
from app.services.job_execution_service import JobExecutionService
from app.services.market_data_service import MarketDataService

JOB_NAME = "analysis_cycle_full"


def run() -> dict:
    db = Session()

    try:
        job_execution_service = JobExecutionService(JobExecutionRepository(db))
        execution = job_execution_service.start(job_name=JOB_NAME)
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

        job_execution_service.success(execution=execution)

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

        error_payload = {
            "status": "failed",
            "job_name": JOB_NAME,
            "error": str(exc),
        }
        if "execution" in locals():
            job_execution_service.failed(
                execution=execution,
                error_message=str(exc),
            )
        return error_payload

    finally:
        db.close()


if __name__ == "__main__":
    print(run())
