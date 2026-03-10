from sqlalchemy.orm import Session

from app.models.forecast_request import ForecastRequest
from app.repositories.protocols.iforescat_repository import IForecastRepository


class ForecastRepository(IForecastRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, forecast_request: ForecastRequest) -> ForecastRequest:
        self.db.add(forecast_request)
        self.db.commit()
        self.db.refresh(forecast_request)
        return forecast_request

    def find_by_id(self, forecast_request_id: str) -> ForecastRequest | None:
        return (
            self.db.query(ForecastRequest)
            .filter(ForecastRequest.id == forecast_request_id)
            .first()
        )
