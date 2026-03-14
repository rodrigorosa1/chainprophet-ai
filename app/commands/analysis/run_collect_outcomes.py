from app.core.database import Session
from app.repositories.sqlalchemy.forecast_analysis_repository import (
    ForecastAnalysisRepository,
)
from app.services.forecast_outcome_service import ForecastOutcomeService
from app.services.market_data_service import MarketDataService


def run() -> dict:
    db = Session()

    try:
        analysis_repository = ForecastAnalysisRepository(db)
        market_data_service = MarketDataService()

        service = ForecastOutcomeService(
            analysis_repository=analysis_repository,
            market_data_service=market_data_service,
        )

        collected = service.collect_pending_outcomes(limit=1000)

        return {
            "status": "success",
            "message": "Outcomes collected successfully",
            "collected_outcomes": len(collected),
            "items": collected,
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": "Failed to collect forecast outcomes",
            "error": str(exc),
        }
    finally:
        db.close()


if __name__ == "__main__":
    print(run())
