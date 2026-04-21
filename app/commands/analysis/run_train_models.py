import sys

from app.core.database import SessionLocal
from app.repositories.sqlalchemy.job_execution_repository import JobExecutionRepository
from app.services.job_execution_service import JobExecutionService
from app.services.market_data_service import MarketDataService
from app.services.feature_engineering_service import FeatureEngineeringService
from app.services.ml_model_service import MlModelService
from app.services.ml_training_service import MlTrainingService

JOB_NAME = "train_ml_models"


def run() -> dict:
    db = SessionLocal()
    execution = None

    try:
        job_execution_service = JobExecutionService(JobExecutionRepository(db))
        execution = job_execution_service.start(
            job_name=JOB_NAME,
            metadata_json={
                "assets": ["BTC-USD", "ETH-USD"],
                "horizons": [12, 24],
            },
        )

        training_service = MlTrainingService(
            market_data_service=MarketDataService(),
            feature_engineering_service=FeatureEngineeringService(),
            ml_model_service=MlModelService(),
        )

        results = []

        for ticker in ["BTC-USD", "ETH-USD"]:
            for horizon_hours in [12, 24]:
                result = training_service.train_asset_models(
                    ticker=ticker,
                    horizon_hours=horizon_hours,
                )
                results.append(result)

        payload = {
            "status": "success",
            "job_name": JOB_NAME,
            "trained": results,
        }

        job_execution_service.success(
            execution=execution,
            metadata_json=payload,
        )

        return payload

    except Exception as exc:
        error_payload = {
            "status": "failed",
            "job_name": JOB_NAME,
            "error": str(exc),
        }

        if execution is not None:
            job_execution_service.failed(
                execution=execution,
                error_message=str(exc),
                metadata_json=error_payload,
            )

        return error_payload

    finally:
        db.close()


if __name__ == "__main__":
    result = run()

    if result["status"] == "failed":
        sys.exit(1)

    sys.exit(0)
