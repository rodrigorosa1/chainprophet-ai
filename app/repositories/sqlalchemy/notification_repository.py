from sqlalchemy.orm import Session
from app.constants.enums.status_notification_enum import StatusNotificationEnum
from app.models.notification import Notification
from app.repositories.protocols.inotification_repository import INotificationRepository
from app.schemas.notification_schema import NotificationIn, NotificationOut


class NotificationRepository(INotificationRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, notification_data: NotificationIn) -> NotificationOut:
        notification = Notification(
            alert_id=notification_data.alert_id,
            sent_at=notification_data.sent_at,
            channel=notification_data.channel,
            message=notification_data.message,
            status=StatusNotificationEnum.SENDER,
        )
        self.db.add(notification)
        self.db.commit()

        return notification
