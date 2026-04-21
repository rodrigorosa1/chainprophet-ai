from typing import List, Optional
from pydantic import BaseModel


class AssetSchema(BaseModel):
    name: str
    symbol: str
    code: str
    directional: str
    directional_percent_period: float


class BacktestSchema(BaseModel):
    windows_used: int
    horizon_hours: int
    mae: float
    rmse: float
    mape_percent: float
    directional_accuracy_percent: float
    quality_score_percent: float


class ForecastPointSchema(BaseModel):
    datetime: str
    target_price: float
    lower_bound_price: float
    upper_bound_price: float
    confidence_percent: float


class ForecastResultSchema(BaseModel):
    asset: AssetSchema
    reference_price: Optional[float] = None
    reference_datetime: Optional[str] = None
    backtest: BacktestSchema
    forecast: List[ForecastPointSchema]
    error: Optional[str] = None


class MultiForecastResponse(BaseModel):
    timeframe: str
    horizon_hours: int
    total_assets: int
    results: List[ForecastResultSchema]
