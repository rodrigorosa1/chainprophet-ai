from fastapi import APIRouter, Query
from app.services.prediction_service import forecast_prices

router = APIRouter()


@router.get("/")
def predict_price(ticker: str = Query(...), days: int = Query(7, ge=1, le=30)):
    """
    Previsão de preços usando Prophet para os próximos N dias.
    """
    return forecast_prices(ticker, days)
