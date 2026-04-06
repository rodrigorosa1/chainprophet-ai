from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.injections import (
    get_forecast_failure_classifier_service,
    get_forecast_outcome_service,
    get_forecast_evaluation_service,
    get_ml_training_service,
)
from app.services.forecast_failure_classifier_service import (
    ForecastFailureClassifierService,
)
from app.services.forecast_outcome_service import ForecastOutcomeService
from app.services.forecast_evaluation_service import ForecastEvaluationService
from app.core.injections import get_forecast_llm_analyst_service
from app.services.forecast_llm_analyst_service import ForecastLlmAnalystService
from app.services.ml_training_service import MlTrainingService

router = APIRouter()

tags: str = "Analysis"


@router.post("/collect-outcomes/", tags=[tags])
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


@router.post("/evaluate", tags=[tags])
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


@router.post("/classify-failures", tags=[tags])
def classify_failures(
    classifier_service: Annotated[
        ForecastFailureClassifierService,
        Depends(get_forecast_failure_classifier_service),
    ],
    limit: int = Query(100, ge=1, le=1000),
):
    try:
        result = classifier_service.classify_pending_assets(limit=limit)
        return {
            "message": "Failures classified successfully",
            "total_classified": len(result),
            "items": result,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/llm-analyze", tags=[tags])
def llm_analyze_failures(
    analyst_service: Annotated[
        ForecastLlmAnalystService,
        Depends(get_forecast_llm_analyst_service),
    ],
    limit: int = Query(100, ge=1, le=1000),
):
    try:
        result = analyst_service.analyze_pending_diagnostics(limit=limit)
        return {
            "message": "AI reports generated successfully",
            "total_generated": len(result),
            "items": result,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/train-ml", tags=[tags])
def train_ml_models(
    ticker: str = Query(..., description="Example: BTC-USD"),
    hours: int = Query(..., ge=12, description="Minimum 12 hours"),
    training_service: MlTrainingService = Depends(get_ml_training_service),
):
    try:
        return training_service.train_asset_models(
            ticker=ticker.strip().upper(),
            horizon_hours=hours,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
