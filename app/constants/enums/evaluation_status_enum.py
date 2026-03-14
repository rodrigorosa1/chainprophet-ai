import enum


class EvaluationStatusEnum(enum.Enum):
    HIT: str = "hit"
    PARTIAL_HIT: str = "partial_hit"
    MISS: str = "miss"
