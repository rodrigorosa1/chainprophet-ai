from app.services.feature_engineering_service import FeatureEngineeringService
from app.services.ml_model_service import MlModelService
from app.services.market_data_service import MarketDataService


class MlTrainingService:
    def __init__(
        self,
        market_data_service: MarketDataService,
        feature_engineering_service: FeatureEngineeringService,
        ml_model_service: MlModelService,
    ):
        self.market_data_service = market_data_service
        self.feature_engineering_service = feature_engineering_service
        self.ml_model_service = ml_model_service

    def train_asset_models(self, ticker: str, horizon_hours: int) -> dict:
        if horizon_hours < 12:
            raise ValueError(
                "The ML engine only supports horizons of 12 hours or more."
            )

        ticker_obj = self.market_data_service.get_ticker(ticker)
        data = self.market_data_service.get_hourly_history(
            ticker_obj=ticker_obj,
            period="120d",
            interval="1h",
        )

        feature_columns = self.feature_engineering_service.get_feature_columns()
        trained_horizons = []

        for step in range(1, horizon_hours + 1):
            feature_df = self.feature_engineering_service.build_features(
                data=data,
                horizon_hours=step,
            )

            x = feature_df[feature_columns]
            y_direction = feature_df[f"target_direction_{step}h"]
            y_return = feature_df[f"target_return_{step}h"]

            self.ml_model_service.train_direction_model(
                ticker=ticker,
                horizon_hours=step,
                features=x,
                target=y_direction,
            )

            self.ml_model_service.train_return_model(
                ticker=ticker,
                horizon_hours=step,
                features=x,
                target=y_return,
            )

            self.ml_model_service.train_quantile_model(
                ticker=ticker,
                horizon_hours=step,
                features=x,
                target=y_return,
                alpha=0.15,
                suffix="q15",
            )

            self.ml_model_service.train_quantile_model(
                ticker=ticker,
                horizon_hours=step,
                features=x,
                target=y_return,
                alpha=0.85,
                suffix="q85",
            )

            trained_horizons.append(step)

        return {
            "status": "success",
            "ticker": ticker,
            "max_horizon_hours": horizon_hours,
            "trained_horizons": trained_horizons,
        }
