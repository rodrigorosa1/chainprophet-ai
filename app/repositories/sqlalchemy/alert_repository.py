from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.models.alert import Alert
from app.schemas.alert_schema import AlertIn, AlertOut
from app.repositories.protocols.ialert_repository import IAlertRepository


class AlertRepository(IAlertRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, alert_data: AlertIn) -> AlertOut:
        alert = Alert(
            user_id=alert_data.user_id,
            active_id=alert_data.active_id,
            condition=alert_data.condition,
            value=alert_data.value,
            currency=alert_data.currency,
            is_active=True,
        )
        self.db.add(alert)
        self.db.commit()

        return alert

    def find_by_id(self, id: UUID) -> AlertOut:
        return self.db.query(Alert).filter(Alert.id == id).first()

    def find_by_user(self, user_id: UUID) -> List[AlertOut]:
        return self.db.query(Alert).filter(Alert.user_id == user_id).all()

    def find_by_active(self) -> List[AlertOut]:
        return (
            self.db.query(Alert)
            .filter(Alert.is_active == True)
            .all()
        )

    def update(self, alert: Alert, alert_data: AlertIn) -> AlertOut:
        alert.condition = alert_data.condition
        alert.value = alert_data.value
        alert.currency = alert_data.currency
        alert.is_active = alert_data.is_active
