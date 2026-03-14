from app.core.database import Session
from app.repositories.sqlalchemy.forecast_analysis_repository import (
    ForecastAnalysisRepository,
)
from app.services.forecast_evaluation_service import ForecastEvaluationService


def run() -> dict:
    db = Session()

    try:
        analysis_repository = ForecastAnalysisRepository(db)

        service = ForecastEvaluationService(
            analysis_repository=analysis_repository,
        )

        evaluated = service.evaluate_pending_points(
            tolerance_percent=2.0,
            limit=1000,
        )

        return {
            "status": "success",
            "message": "Forecast points evaluated successfully",
            "evaluated_points": len(evaluated),
            "items": evaluated,
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": "Failed to evaluate forecast points",
            "error": str(exc),
        }
    finally:
        db.close()


if __name__ == "__main__":
    print(run())
