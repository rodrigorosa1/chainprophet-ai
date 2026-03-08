from fastapi import APIRouter, HTTPException, Query
from app.repositories.dependencies.auth import get_current_user
from app.schemas.forecast_schema import MultiForecastResponse
import logging
from app.services.forecast_service import ForecastService

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

forecast_service = ForecastService()


@router.get(
    "/",
    response_model=MultiForecastResponse,
    responses={400: {"description": "Bad request error"}},
    description="Retrieve results of a forecast by active and hours",
)
def get_forecast(
    tickers: str = Query(..., description="BTC-USD,ETH-USD,..."),
    hours: int = Query(24, ge=1, le=168, description="Horizon in hours"),
):
    try:
        ticker_list = [
            ticker.strip() for ticker in tickers.split(",") if ticker.strip()
        ]
        return forecast_service.forecast_prices(tickers=ticker_list, hours=hours)

    except Exception as e:
        logger.error(f"Error in query forecast: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/default-top10",
    response_model=MultiForecastResponse,
    responses={400: {"description": "Bad request error"}},
    description="Retrieve results of a forecast by top10 and hours",
)
def get_default_top10_forecast(
    hours: int = Query(24, ge=1, le=168, description="Horizon in hours"),
):
    try:
        return forecast_service.forecast_default_top10(hours=hours)

    except Exception as e:
        logger.error(f"Error in query forecast top 10: {e}")
        raise HTTPException(status_code=400, detail=str(e))
