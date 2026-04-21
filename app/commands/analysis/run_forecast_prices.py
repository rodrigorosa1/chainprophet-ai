import argparse
import os
import sys

from app.core.database import SessionLocal
from app.repositories.sqlalchemy.forecast_repository import ForecastRepository
from app.repositories.sqlalchemy.history_repository import HistoryRepository
from app.repositories.sqlalchemy.job_execution_repository import JobExecutionRepository
from app.repositories.sqlalchemy.user_repository import UserRepository
from app.services.backtest_service import BacktestService
from app.services.feature_engineering_service import FeatureEngineeringService
from app.services.forecast_service import ForecastService
from app.services.job_execution_service import JobExecutionService
from app.services.market_data_service import MarketDataService
from app.services.ml_forecast_service import MlForecastService
from app.services.ml_model_service import MlModelService
from app.services.sentiment_service import SentimentService
from app.services.signal_engine_service import SignalEngineService

JOB_NAME = "forecast_prices"
DEFAULT_TICKERS = ["BTC-USD", "ETH-USD"]
DEFAULT_HOURS = 24


def _build_forecast_service(db) -> ForecastService:
    market_data_service = MarketDataService()

    ml_forecast_service = MlForecastService(
        market_data_service=market_data_service,
        feature_engineering_service=FeatureEngineeringService(),
        ml_model_service=MlModelService(),
    )

    return ForecastService(
        ForecastRepository(db),
        market_data_service,
        SentimentService(),
        SignalEngineService(),
        BacktestService(),
        UserRepository(db),
        HistoryRepository(db),
        ml_forecast_service,
    )


def _normalize_tickers(tickers: list[str] | str | None) -> list[str]:
    if tickers is None:
        return DEFAULT_TICKERS

    if isinstance(tickers, str):
        tickers = tickers.split(",")

    return [ticker.strip() for ticker in tickers if ticker.strip()]


def run(
    tickers: list[str] | str | None = None,
    hours: int = DEFAULT_HOURS,
) -> dict:
    db = SessionLocal()
    execution = None

    ticker_list = _normalize_tickers(tickers)
    request_metadata = {
        "tickers": ticker_list,
        "hours": hours,
    }

    try:
        job_execution_service = JobExecutionService(JobExecutionRepository(db))
        execution = job_execution_service.start(
            job_name=JOB_NAME,
            metadata_json=request_metadata,
        )
        forecast_service = _build_forecast_service(db)
        forecast = forecast_service.generate_forecast(
            tickers=ticker_list,
            hours=hours,
        )

        payload = {
            "status": "success",
            "job_name": JOB_NAME,
            "message": "Forecast prices generated successfully",
            "tickers": ticker_list,
            "hours": hours,
            "total_assets": forecast.get("total_assets", 0),
            "forecast": forecast,
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
            "message": "Failed to generate forecast prices",
            "tickers": ticker_list,
            "hours": hours,
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


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run ForecastService.forecast_prices and save the job execution."
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="TraderX API key. Defaults to X_TRADERX_API_KEY or TRADERX_API_KEY.",
    )
    parser.add_argument(
        "--tickers",
        default=",".join(DEFAULT_TICKERS),
        help="Comma-separated ticker list, for example BTC-USD,ETH-USD.",
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=DEFAULT_HOURS,
        help="Forecast horizon in hours.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()

    result = run(
        tickers=args.tickers,
        hours=args.hours,
    )

    if result["status"] == "failed":
        sys.exit(1)

    sys.exit(0)
