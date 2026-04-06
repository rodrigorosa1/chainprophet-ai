from pydantic import BaseModel
from typing import List, Optional


class AssetResponse(BaseModel):
    name: str
    symbol: str
    code: str


class BacktestResponse(BaseModel):
    windows_used: int
    horizon_hours: int
    mae: Optional[float] = None
    rmse: Optional[float] = None
    mape_percent: Optional[float] = None
    directional_accuracy_percent: Optional[float] = None
    quality_score_percent: float


class ForecastItemResponse(BaseModel):
    datetime: str
    target_price: float
    lower_bound_price: float
    upper_bound_price: float
    confidence_percent: float


class AssetForecastResponse(BaseModel):
    asset: AssetResponse
    backtest: BacktestResponse
    forecast: List[ForecastItemResponse]
    error: Optional[str] = None


class MultiForecastResponse(BaseModel):
    timeframe: str
    horizon_hours: int
    total_assets: int
    results: List[AssetForecastResponse]
