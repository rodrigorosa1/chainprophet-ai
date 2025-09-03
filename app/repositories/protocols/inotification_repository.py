from typing import Protocol
from app.schemas.notification_schema import NotificationIn, NotificationOut


class INotificationRepository(Protocol):
    def create(self, notification_data: NotificationIn) -> NotificationOut: ...
