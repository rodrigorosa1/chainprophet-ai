import enum


class CauseSummaryEnum(enum.Enum):
    MISSING_REFERENCE_POINT: str = (
        "The direction assessment was compromised by the absence of a reliable "
        "reference point in the relevant portion of the data."
    )

    NO_FAILURE_PATTERN: str = (
        "There is no relevant failure pattern for this asset in this evaluation cycle."
    )

    DIRECTION_MISJUDGMENT: str = (
        "The model is frequently misjudging the direction of the movement, "
        "leading to miscalibration of intervals for this asset or time horizon."
    )

    MAGNITUDE_MISJUDGMENT: str = (
        "The model usually defines the direction but misjudges the magnitude "
        "of the movement due to insufficient occurrences in market variations."
    )

    LOW_SIGNAL_QUALITY: str = (
        "The low quality of the backtest and the high error rate suggest a lack "
        "of relevant signals in the current pipeline."
    )

    EXTREME_MARKET_BEHAVIOR: str = (
        "The asset exhibited behavior far from the predicted curve, possibly "
        "associated with a market event or extreme regime."
    )

    INCONCLUSIVE_FAILURE_PATTERN: str = (
        "The failure pattern was inconclusive with the current rules."
    )
