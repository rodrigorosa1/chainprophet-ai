import numpy as np
import pandas as pd

from app.services.feature_engineering_service import FeatureEngineeringService
from app.services.ml_model_service import MlModelService
from app.services.market_data_service import MarketDataService


class MlForecastService:
    def __init__(
        self,
        market_data_service: MarketDataService,
        feature_engineering_service: FeatureEngineeringService,
        ml_model_service: MlModelService,
    ):
        self.market_data_service = market_data_service
        self.feature_engineering_service = feature_engineering_service
        self.ml_model_service = ml_model_service

    def can_forecast(self, ticker: str, horizon_hours: int) -> bool:
        if horizon_hours < 12:
            return False

        return all(
            self.ml_model_service.has_complete_model_set(
                ticker=ticker, horizon_hours=step
            )
            for step in range(1, horizon_hours + 1)
        )

    def forecast_asset(self, ticker: str, horizon_hours: int) -> dict:
        if horizon_hours < 12:
            raise ValueError(
                "The ML engine only supports horizons of 12 hours or more."
            )

        ticker_obj = self.market_data_service.get_ticker(ticker)
        asset_info = self.market_data_service.get_asset_info(ticker_obj, ticker)

        data = self.market_data_service.get_hourly_history(
            ticker_obj=ticker_obj,
            period="120d",
            interval="1h",
        )

        last_close_series = data["Close"].dropna()
        last_price = float(last_close_series.iloc[-1])

        last_dt = pd.to_datetime(data.index[-1])
        if getattr(last_dt, "tzinfo", None) is not None:
            last_dt = last_dt.tz_localize(None)

        feature_columns = self.feature_engineering_service.get_feature_columns()

        forecast_points = []

        for step in range(1, horizon_hours + 1):
            feature_df = self.feature_engineering_service.build_features(
                data=data,
                horizon_hours=step,
            )

            latest_row = feature_df.iloc[-1]
            x_latest = latest_row[feature_columns].to_frame().T

            direction_model = self.ml_model_service.load_model(
                ticker=ticker,
                horizon_hours=step,
                suffix="direction",
            )
            return_model = self.ml_model_service.load_model(
                ticker=ticker,
                horizon_hours=step,
                suffix="return",
            )
            q15_model = self.ml_model_service.load_model(
                ticker=ticker,
                horizon_hours=step,
                suffix="q15",
            )
            q85_model = self.ml_model_service.load_model(
                ticker=ticker,
                horizon_hours=step,
                suffix="q85",
            )

            direction_probability_up = float(
                direction_model.predict_proba(x_latest)[0][1]
            )
            predicted_return = float(return_model.predict(x_latest)[0])
            predicted_return_q15 = float(q15_model.predict(x_latest)[0])
            predicted_return_q85 = float(q85_model.predict(x_latest)[0])

            target_price = round(last_price * (1 + predicted_return), 2)
            lower_bound_price = round(last_price * (1 + predicted_return_q15), 2)
            upper_bound_price = round(last_price * (1 + predicted_return_q85), 2)

            if lower_bound_price > upper_bound_price:
                lower_bound_price, upper_bound_price = (
                    upper_bound_price,
                    lower_bound_price,
                )

            confidence_percent = round(
                max(5.0, min(direction_probability_up * 100.0, 95.0)),
                2,
            )

            forecast_dt = last_dt + pd.Timedelta(hours=step)

            forecast_points.append(
                {
                    "datetime": forecast_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "target_price": target_price,
                    "lower_bound_price": lower_bound_price,
                    "upper_bound_price": upper_bound_price,
                    "confidence_percent": confidence_percent,
                }
            )

        backtest = self._run_backtest(
            ticker=ticker,
            data=data,
            max_horizon_hours=horizon_hours,
        )

        return {
            "asset": asset_info,
            "reference_price": round(last_price, 2),
            "reference_datetime": last_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "backtest": backtest,
            "forecast": forecast_points,
            "error": None,
        }

    def _run_backtest(
        self,
        ticker: str,
        data: pd.DataFrame,
        max_horizon_hours: int,
        windows: int = 3,
        step_hours: int = 12,
        min_train_points: int = 24 * 20,
    ) -> dict:
        feature_columns = self.feature_engineering_service.get_feature_columns()

        if len(data) < (min_train_points + max_horizon_hours + 1):
            return {
                "windows_used": 0,
                "horizon_hours": max_horizon_hours,
                "mae": 0.0,
                "rmse": 0.0,
                "mape_percent": 0.0,
                "directional_accuracy_percent": 0.0,
                "quality_score_percent": 50.0,
            }

        results = []

        last_possible_cutoff = len(data) - max_horizon_hours
        cutoffs = []
        current_cutoff = last_possible_cutoff

        while current_cutoff >= min_train_points and len(cutoffs) < windows:
            cutoffs.append(current_cutoff)
            current_cutoff -= step_hours

        cutoffs = sorted(cutoffs)

        for cutoff in cutoffs:
            errors = []
            direction_hits = []

            for horizon_step in range(1, max_horizon_hours + 1):
                try:
                    sliced_data = data.iloc[: cutoff + horizon_step].copy()

                    feature_df = self.feature_engineering_service.build_features(
                        data=sliced_data,
                        horizon_hours=horizon_step,
                    )

                    if feature_df.empty:
                        continue

                    x_latest = feature_df.iloc[-1][feature_columns].to_frame().T

                    return_model = self.ml_model_service.load_model(
                        ticker=ticker,
                        horizon_hours=horizon_step,
                        suffix="return",
                    )

                    direction_model = self.ml_model_service.load_model(
                        ticker=ticker,
                        horizon_hours=horizon_step,
                        suffix="direction",
                    )

                    predicted_return = float(return_model.predict(x_latest)[0])
                    predicted_direction = int(direction_model.predict(x_latest)[0])

                    reference_price = float(data["Close"].iloc[cutoff - 1])
                    actual_price = float(data["Close"].iloc[cutoff + horizon_step - 1])

                    predicted_price = reference_price * (1 + predicted_return)

                    absolute_error = abs(actual_price - predicted_price)
                    squared_error = (actual_price - predicted_price) ** 2
                    percentage_error = (
                        abs((actual_price - predicted_price) / actual_price) * 100.0
                        if actual_price != 0
                        else 0.0
                    )

                    actual_direction = 1 if actual_price > reference_price else 0

                    errors.append(
                        {
                            "ae": absolute_error,
                            "se": squared_error,
                            "ape": percentage_error,
                        }
                    )
                    direction_hits.append(
                        1 if predicted_direction == actual_direction else 0
                    )

                except Exception:
                    continue

            if not errors:
                continue

            mae = float(np.mean([item["ae"] for item in errors]))
            rmse = float(np.sqrt(np.mean([item["se"] for item in errors])))
            mape_percent = float(np.mean([item["ape"] for item in errors]))
            directional_accuracy_percent = float(np.mean(direction_hits) * 100.0)

            results.append(
                {
                    "mae": mae,
                    "rmse": rmse,
                    "mape_percent": mape_percent,
                    "directional_accuracy_percent": directional_accuracy_percent,
                }
            )

        if not results:
            return {
                "windows_used": 0,
                "horizon_hours": max_horizon_hours,
                "mae": 0.0,
                "rmse": 0.0,
                "mape_percent": 0.0,
                "directional_accuracy_percent": 0.0,
                "quality_score_percent": 50.0,
            }

        mae = float(np.mean([r["mae"] for r in results]))
        rmse = float(np.mean([r["rmse"] for r in results]))
        mape_percent = float(np.mean([r["mape_percent"] for r in results]))
        directional_accuracy_percent = float(
            np.mean([r["directional_accuracy_percent"] for r in results])
        )

        quality_score_percent = self._score_backtest_quality(
            mape_percent=mape_percent,
            directional_accuracy_percent=directional_accuracy_percent,
        )

        return {
            "windows_used": len(results),
            "horizon_hours": max_horizon_hours,
            "mae": round(mae, 4),
            "rmse": round(rmse, 4),
            "mape_percent": round(mape_percent, 4),
            "directional_accuracy_percent": round(directional_accuracy_percent, 2),
            "quality_score_percent": round(quality_score_percent, 2),
        }

    def _score_backtest_quality(
        self,
        mape_percent: float,
        directional_accuracy_percent: float,
    ) -> float:
        mape_score = max(0.0, 100.0 - min(mape_percent * 10.0, 100.0))
        direction_score = max(0.0, min(directional_accuracy_percent, 100.0))
        return (mape_score * 0.65) + (direction_score * 0.35)
