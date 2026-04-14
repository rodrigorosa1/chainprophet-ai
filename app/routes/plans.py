from typing import Annotated, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from app.core.injections import get_plan_service
from app.repositories.dependencies.auth import get_current_user
from app.schemas.plan_schema import PlanIn, PlanOut
from app.services.plan_service import PlanService
import logging

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tags: str = "Plans"


@router.post(
    "/",
    response_model=PlanOut,
    responses={400: {"description": "Bad request error"}},
    tags=[tags],
)
def create(
    plan_in: PlanIn,
    plan_service: Annotated[PlanService, Depends(get_plan_service)],
    current_user: Annotated[object, Depends(get_current_user)],
):
    try:
        plan = plan_service.create(plan_in)
        return PlanOut.model_validate(plan)

    except Exception as e:
        logger.error(f"Error in register user: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{id}",
    response_model=PlanOut,
    responses={400: {"description": "Bad request error"}},
    description="Retrieve a plan by ID",
    tags=[tags],
)
def find_by_id(
    id: UUID,
    plan_service: Annotated[PlanService, Depends(get_plan_service)],
):
    try:
        plan = plan_service.find_by_id(id)
        return PlanOut.model_validate(plan)

    except Exception as e:
        logger.error(f"Error in query plan: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/",
    response_model=List[PlanOut],
    responses={400: {"description": "Bad request error"}},
    tags=[tags],
)
def find_all(
    plan_service: Annotated[PlanService, Depends(get_plan_service)],
):
    try:
        plans = plan_service.find_all()
        return [PlanOut.model_validate(x) for x in plans]

    except Exception as e:
        logger.error(f"Error in query plans: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.patch(
    "/{id}",
    response_model=PlanOut,
    responses={400: {"description": "Bad request error"}},
    tags=[tags],
)
def update(
    id: UUID,
    plan_in: PlanIn,
    plan_service: Annotated[PlanService, Depends(get_plan_service)],
    current_user: Annotated[object, Depends(get_current_user)],
):
    try:
        plan = plan_service.update(id, plan_in)
        return PlanOut.model_validate(plan)

    except Exception as e:
        logger.error(f"Error in update plan: {e}")
        raise HTTPException(status_code=400, detail=str(e))
