from app.core.database import SessionLocal
from app.services.ml_training_service import MlTrainingService
from app.services.market_data_service import MarketDataService
from app.services.feature_engineering_service import FeatureEngineeringService
from app.services.ml_model_service import MlModelService


def run():
    db = SessionLocal()

    try:
        service = MlTrainingService(
            market_data_service=MarketDataService(),
            feature_engineering_service=FeatureEngineeringService(),
            ml_model_service=MlModelService(),
        )

        service.train_asset_models("BTC-USD", 24)
        service.train_asset_models("ETH-USD", 24)

        print("Training completed successfully")

    finally:
        db.close()


if __name__ == "__main__":
    run()
