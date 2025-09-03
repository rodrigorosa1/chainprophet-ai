from uuid import UUID
from typing import List
from app.constants.exceptions.messages import AlertNotFoundError
from app.repositories.protocols.ialert_repository import IAlertRepository
from app.schemas.alert_schema import AlertIn, AlertOut


class AlertService:
    def __init__(self, alert_repo: IAlertRepository):
        self.alert_repo = alert_repo

    def create(self, alert_data: AlertIn) -> AlertOut:
        return self.alert_repo.create(alert_data)

    def find_by_id(self, id: UUID) -> AlertOut:
        alert = self.alert_repo.find_by_id(id)
        if not alert:
            raise ValueError(AlertNotFoundError.MESSAGE)

        return alert

    def find_by_user(self, user_id: UUID) -> List[AlertOut]:
        return self.alert_repo.find_by_user(user_id)

    def find_by_active(self, user_id: UUID) -> List[AlertOut]:
        return self.alert_repo.find_by_active(user_id)

    def update(self, id: UUID, alert_data: AlertIn) -> AlertOut:
        alert = self.alert_repo.find_by_id(id)
        if not alert:
            raise ValueError(AlertNotFoundError.MESSAGE)

        return self.alert_repo.update(alert, alert_data)
