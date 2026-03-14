import enum


class CauseCategoryEnum(enum.Enum):
    LOW_FAILURE_PATTERN: str = "low_failure_pattern"
    PARAMETER_MISCALIBRATION: str = "parameter_miscalibration"
    MODEL_UNDERFITTING: str = "model_underfitting"
    FEATURE_GAP: str = "feature_gap"
    MARKET_EVENT: str = "market_event"
    DATA_QUALITY: str = "data_quality"
    UNKNOWN: str = "unknown"
