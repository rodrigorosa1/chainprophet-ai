from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Header
from app.core.injections import get_api_customer_service, get_forecast_service
from app.schemas.forecast_schema import MultiForecastResponse
import logging
from app.services.api_customer_service import ApiCustomerService
from app.services.forecast_service import ForecastService

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tags: str = "Forecast"


@router.get(
    "/",
    response_model=MultiForecastResponse,
    responses={400: {"description": "Bad request error"}},
    description="Retrieve results of a forecast by active and hours",
    tags=[tags],
)
def get_forecast(
    api_customer_service: Annotated[
        ApiCustomerService, Depends(get_api_customer_service)
    ],
    tickers: str = Query(..., description="BTC-USD,ETH-USD,..."),
    hours: int = Query(24, ge=1, le=48, description="Horizon in hours"),
    x_chainprophet_key: str = Header(..., alias="X-ChainProphet-Key"),
):
    try:
        ticker_list = [
            ticker.strip() for ticker in tickers.split(",") if ticker.strip()
        ]
        return api_customer_service.forecast(
            api_key=x_chainprophet_key, tickers=ticker_list, hours=hours
        )

    except Exception as e:
        logger.error(f"Error in query forecast: {e}")
        raise HTTPException(status_code=400, detail=str(e))
