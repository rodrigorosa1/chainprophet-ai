from datetime import datetime
import pandas as pd
from prophet import Prophet
from app.repositories.protocols.iforescat_repository import IForecastRepository
from app.repositories.protocols.ihistory_repository import IHistoryRepository
from app.repositories.protocols.iuser_repository import IUserRepository
from app.services.market_data_service import MarketDataService
from app.services.sentiment_service import SentimentService
from app.services.signal_engine_service import SignalEngineService
from app.services.backtest_service import BacktestService
from app.models.forecast_request import ForecastRequest
from app.models.forecast_asset import ForecastAsset
from app.models.forecast_backtest import ForecastBacktest
from app.models.forecast_point import ForecastPoint


class ForecastService:
    def __init__(
        self,
        forecast_repo: IForecastRepository,
        market_data_service: MarketDataService,
        sentiment_service: SentimentService,
        signal_engine_service: SignalEngineService,
        backtest_service: BacktestService,
        user_repo: IUserRepository,
        history_repo: IHistoryRepository,
    ):
        self.market_data_service = market_data_service
        self.sentiment_service = sentiment_service
        self.signal_engine_service = signal_engine_service
        self.backtest_service = backtest_service
        self.forecast_repo = forecast_repo
        self.user_repo = user_repo
        self.history_repo = history_repo

    def _build_prophet_model(self):
        return Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            changepoint_prior_scale=0.15,
        )

    def _calculate_confidence(
        self,
        row,
        anomaly_score: float,
        sentiment_avg: float,
        volatility: float,
        rsi_value: float,
        trend: dict,
        volume_signal: dict,
        market_regime: dict,
        backtest: dict,
    ) -> float:
        estimated_price = float(row["yhat_adj"])
        lower = float(row["yhat_lower_adj"])
        upper = float(row["yhat_upper_adj"])

        if estimated_price <= 0:
            return 0.0

        interval_width_ratio = (upper - lower) / estimated_price
        relative_volume = volume_signal.get("relative_volume", 1.0)
        direction_confirmation = volume_signal.get("direction_confirmation", 0.0)
        regime_name = market_regime.get("name", "sideways")
        backtest_quality = float(backtest.get("quality_score_percent", 50.0) or 50.0)

        confidence = 82.0
        confidence -= min(interval_width_ratio * 100, 28.0)
        confidence -= min(anomaly_score * 4.0, 18.0)
        confidence -= min(volatility * 400, 18.0)
        confidence += sentiment_avg * 7.0

        if rsi_value >= 75:
            confidence -= 8.0
        elif rsi_value >= 65:
            confidence -= 4.0
        elif rsi_value <= 25:
            confidence -= 6.0
        elif rsi_value <= 35:
            confidence -= 3.0
        else:
            confidence += 2.0

        trend_strength = trend.get("strength", 0.0)
        trend_direction = trend.get("direction", "neutral")

        if trend_direction == "up":
            confidence += min(trend_strength * 100, 7.0)
        elif trend_direction == "down":
            confidence += min(trend_strength * 100, 5.0)
        else:
            confidence -= 2.0

        if direction_confirmation > 0:
            confidence += min(relative_volume * 3.0, 6.0)
        elif direction_confirmation < 0:
            confidence -= min(abs(direction_confirmation) * 6.0, 6.0)

        if regime_name == "bullish":
            confidence += 4.0
        elif regime_name == "bearish":
            confidence += 2.0
        elif regime_name == "high_volatility_bullish":
            confidence += 1.0
        elif regime_name == "high_volatility_bearish":
            confidence -= 2.0
        else:
            confidence -= 1.5

        confidence += ((backtest_quality - 50.0) / 50.0) * 12.0

        confidence = max(5.0, min(95.0, confidence))
        return round(confidence, 2)

    def _forecast_single_asset(self, ticker: str, hours: int = 24) -> dict:
        ticker_obj = self.market_data_service.get_ticker(ticker)
        asset_info = self.market_data_service.get_asset_info(ticker_obj, ticker)

        data = self.market_data_service.get_hourly_history(
            ticker_obj, period="60d", interval="1h"
        )
        df = self.market_data_service.build_prophet_dataframe(data)

        if len(df) < 24 * 14:
            raise ValueError(
                f"Insufficient data for reliable hourly forecasting in {ticker}."
            )

        close_series = data["Close"].dropna()

        anomaly_score = self.signal_engine_service.detect_anomaly_score(
            close_series, lookback_hours=24 * 14
        )

        news_titles = self.market_data_service.get_news_titles(ticker_obj, max_items=25)
        sentiment_avg = self.sentiment_service.score(news_titles)

        volatility = self.signal_engine_service.calculate_volatility(
            close_series, window=24
        )

        rsi_series = self.signal_engine_service.calculate_rsi(close_series, period=14)
        rsi_value = float(rsi_series.iloc[-1]) if not rsi_series.empty else 50.0

        trend = self.signal_engine_service.calculate_trend_strength(
            close_series, short_window=12, long_window=48
        )
        volume_signal = self.signal_engine_service.calculate_volume_signal(
            data, volume_window=24
        )
        market_regime = self.signal_engine_service.detect_market_regime(
            volatility, trend, rsi_value
        )

        backtest = self.backtest_service.run(
            df=df,
            horizon_hours=hours,
            windows=3,
            min_train_points=24 * 14,
            step_hours=12,
        )

        model = self._build_prophet_model()
        model.fit(df)

        future = model.make_future_dataframe(periods=hours, freq="h")
        forecast = model.predict(future)

        base = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(hours).copy()

        sentiment_weight = 0.025
        sentiment_factor = 1.0 + (sentiment_avg * sentiment_weight)

        anomaly_weight = 0.02
        anomaly_penalty = 1.0 - (min(anomaly_score, 10.0) / 10.0) * anomaly_weight

        volatility_weight = 0.03
        volatility_penalty = 1.0 - min(volatility * 15, 1.0) * volatility_weight

        trend_bonus = 1.0
        if trend["direction"] == "up":
            trend_bonus += min(trend["strength"], 0.025)
        elif trend["direction"] == "down":
            trend_bonus -= min(trend["strength"], 0.02)

        volume_factor = 1.0
        if volume_signal["direction_confirmation"] > 0:
            volume_factor += min((volume_signal["relative_volume"] - 1.0) * 0.03, 0.03)
        elif volume_signal["direction_confirmation"] < 0:
            volume_factor -= min(
                abs(volume_signal["direction_confirmation"]) * 0.03, 0.03
            )

        regime_factor = 1.0 + (market_regime["score"] * 0.02)
        backtest_factor = (
            1.0
            + ((float(backtest.get("quality_score_percent", 50.0)) - 50.0) / 100.0)
            * 0.04
        )

        adjusted_factor = (
            sentiment_factor
            * anomaly_penalty
            * volatility_penalty
            * trend_bonus
            * volume_factor
            * regime_factor
            * backtest_factor
        )

        adjusted = base.copy()
        adjusted["yhat_adj"] = (adjusted["yhat"] * adjusted_factor).astype(float)

        widen = (
            1.0 + (min(anomaly_score, 10.0) / 10.0) * 0.10 + min(volatility * 8, 0.20)
        )

        if market_regime["name"] in [
            "high_volatility_bullish",
            "high_volatility_bearish",
        ]:
            widen += 0.05

        if float(backtest.get("quality_score_percent", 50.0)) < 55.0:
            widen += 0.04

        center = adjusted["yhat_adj"]
        lower_dist = (base["yhat"] - base["yhat_lower"]).abs() * widen
        upper_dist = (base["yhat_upper"] - base["yhat"]).abs() * widen

        adjusted["yhat_lower_adj"] = (center - lower_dist).astype(float)
        adjusted["yhat_upper_adj"] = (center + upper_dist).astype(float)

        response = []
        for _, row in adjusted.iterrows():
            confidence_percent = self._calculate_confidence(
                row=row,
                anomaly_score=anomaly_score,
                sentiment_avg=sentiment_avg,
                volatility=volatility,
                rsi_value=rsi_value,
                trend=trend,
                volume_signal=volume_signal,
                market_regime=market_regime,
                backtest=backtest,
            )

            response.append(
                {
                    "datetime": pd.to_datetime(row["ds"]).strftime("%Y-%m-%d %H:%M:%S"),
                    "estimated_price": round(float(row["yhat_adj"]), 2),
                    "confidence_percent": confidence_percent,
                }
            )

        return {
            "asset": asset_info,
            "backtest": backtest,
            "forecast": response,
        }

    def forecast_prices(
        self, api_key: str, tickers: list[str], hours: int = 24
    ) -> dict:
        user = self.user_repo.find_by_api_key(api_key)

        if not user or not user.active:
            raise ValueError("Invalid or inactive API key.")

        results = []

        unique_tickers = []
        seen = set()

        for ticker in tickers:
            normalized = ticker.strip().upper()
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique_tickers.append(normalized)

        for ticker in unique_tickers:
            try:
                result = self._forecast_single_asset(ticker=ticker, hours=hours)
                results.append(result)
            except Exception as e:
                results.append(
                    {
                        "asset": {
                            "name": ticker,
                            "symbol": ticker,
                            "code": ticker.split("-")[0] if "-" in ticker else ticker,
                        },
                        "backtest": {
                            "windows_used": 0,
                            "horizon_hours": hours,
                            "mae": None,
                            "rmse": None,
                            "mape_percent": None,
                            "directional_accuracy_percent": None,
                            "quality_score_percent": 0.0,
                        },
                        "forecast": [],
                        "error": str(e),
                    }
                )

        forecast = {
            "timeframe": "1h",
            "horizon_hours": hours,
            "total_assets": len(results),
            "results": results,
        }

        self.save_forecast_response(response_data=forecast)
        self.history_repo.create(user_id=user.id)

        return forecast

    def save_forecast_response(
        self,
        response_data: dict,
        request_payload: dict | None = None,
        model_version: str | None = None,
    ) -> ForecastRequest:
        forecast_request = ForecastRequest(
            timeframe=response_data["timeframe"],
            horizon_hours=response_data["horizon_hours"],
            total_assets=response_data["total_assets"],
            model_version=model_version,
            request_payload=request_payload,
            response_payload=response_data,
        )

        for result in response_data.get("results", []):
            asset_data = result.get("asset", {})
            backtest_data = result.get("backtest", {})
            forecast_data = result.get("forecast", [])

            forecast_asset = ForecastAsset(
                asset_name=asset_data.get("name"),
                asset_symbol=asset_data.get("symbol"),
                asset_code=asset_data.get("code"),
                error=result.get("error"),
            )

            if backtest_data:
                forecast_backtest = ForecastBacktest(
                    windows_used=backtest_data.get("windows_used"),
                    horizon_hours=backtest_data.get("horizon_hours"),
                    mae=backtest_data.get("mae"),
                    rmse=backtest_data.get("rmse"),
                    mape_percent=backtest_data.get("mape_percent"),
                    directional_accuracy_percent=backtest_data.get(
                        "directional_accuracy_percent"
                    ),
                    quality_score_percent=backtest_data.get("quality_score_percent"),
                )

                forecast_asset.backtest = forecast_backtest

            for point in forecast_data:
                forecast_point = ForecastPoint(
                    forecast_datetime=self._parse_datetime(point.get("datetime")),
                    estimated_price=point.get("estimated_price"),
                    confidence_percent=point.get("confidence_percent"),
                )

                forecast_asset.forecast_points.append(forecast_point)

            forecast_request.assets.append(forecast_asset)

        return self.forecast_repo.create(forecast_request)

    def _parse_datetime(self, value: str | None) -> datetime | None:
        if not value:
            return None

        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
