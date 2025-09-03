import enum


class StatusNotificationEnum(enum.Enum):
    SENDER: str = "SENDER"
    WAITING: str = "WAITING"
    ERROR: str = "ERROR"
