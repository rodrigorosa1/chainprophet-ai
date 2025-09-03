import enum


class TypeNotificationEnum(enum.Enum):
    WATTSAPP: str = "WATTSAPP"
    EMAIL: str = "EMAIL"
    TELEGRAM: str = "TELEGRAM"
    ALL: str = "ALL"
