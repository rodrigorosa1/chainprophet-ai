from typing import Protocol

from app.models.forecast_request import ForecastRequest


class IForecastRepository(Protocol):
    def create(self, forecast_request: ForecastRequest) -> ForecastRequest: ...
    def find_by_id(self, forecast_request_id: str) -> ForecastRequest | None: ...
