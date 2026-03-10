from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.injections import (
    get_forecast_outcome_service,
    get_forecast_evaluation_service,
)
from app.services.forecast_outcome_service import ForecastOutcomeService
from app.services.forecast_evaluation_service import ForecastEvaluationService

router = APIRouter()


@router.post("/collect-outcomes/")
def collect_outcomes(
    outcome_service: Annotated[
        ForecastOutcomeService, Depends(get_forecast_outcome_service)
    ],
    limit: int = Query(100, ge=1, le=1000),
):
    try:
        result = outcome_service.collect_pending_outcomes(limit=limit)
        return {
            "message": "Outcomes collected successfully",
            "total_collected": len(result),
            "items": result,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/evaluate")
def evaluate_forecasts(
    evaluation_service: Annotated[
        ForecastEvaluationService, Depends(get_forecast_evaluation_service)
    ],
    tolerance_percent: float = Query(2.0, ge=0.1, le=100.0),
    limit: int = Query(100, ge=1, le=1000),
):
    try:
        result = evaluation_service.evaluate_pending_points(
            tolerance_percent=tolerance_percent,
            limit=limit,
        )
        return {
            "message": "Forecasts evaluated successfully",
            "total_evaluated": len(result),
            "items": result,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
