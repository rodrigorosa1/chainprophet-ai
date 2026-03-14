from app.core.database import Session
from app.repositories.sqlalchemy.forecast_analysis_repository import (
    ForecastAnalysisRepository,
)
from app.services.forecast_failure_classifier_service import (
    ForecastFailureClassifierService,
)


def run() -> dict:
    db = Session()

    try:
        analysis_repository = ForecastAnalysisRepository(db)

        service = ForecastFailureClassifierService(
            analysis_repository=analysis_repository,
        )

        classified = service.classify_pending_assets(limit=1000)

        return {
            "status": "success",
            "message": "Failures classified successfully",
            "classified_assets": len(classified),
            "items": classified,
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": "Failed to classify forecast failures",
            "error": str(exc),
        }
    finally:
        db.close()


if __name__ == "__main__":
    print(run())
