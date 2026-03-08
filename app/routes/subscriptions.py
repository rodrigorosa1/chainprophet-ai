from typing import Annotated, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from app.core.injections import get_subscription_service
from app.repositories.dependencies.auth import get_current_user
from app.schemas.subscription_schema import SubscriptionIn, SubscriptionOut
from app.schemas.user_schema import UserOut
from app.services.subscription_service import SubscriptionService
import logging

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post(
    "/", response_model=SubscriptionOut, responses={400: {"description": "Bad Request"}}
)
def create(
    subscription_in: SubscriptionIn,
    subscription_service: Annotated[
        SubscriptionService, Depends(get_subscription_service)
    ],
):
    try:
        subscription = subscription_service.create(subscription_in)
        return SubscriptionOut.model_validate(subscription)

    except Exception as e:
        logger.error(f"Error in register user: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{id}",
    response_model=SubscriptionOut,
    responses={400: {"description": "Bad Request"}},
)
def find_by_id(
    id: UUID,
    subscription_service: Annotated[
        SubscriptionService, Depends(get_subscription_service)
    ],
    current_user: Annotated[UserOut, Depends(get_current_user)],
):
    try:
        subscription = subscription_service.find_by_id(id)
        return SubscriptionOut.model_validate(subscription)

    except Exception as e:
        logger.error(f"Error in query plan: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/",
    response_model=List[SubscriptionOut],
    responses={400: {"description": "Bad Request"}},
)
def find_all(
    plan_service: Annotated[SubscriptionService, Depends(get_subscription_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)] = None,
):
    try:
        plans = plan_service.find_all()
        return [SubscriptionOut.model_validate(x) for x in plans]

    except Exception as e:
        logger.error(f"Error in query plans: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.patch(
    "/{id}",
    response_model=SubscriptionOut,
    responses={400: {"description": "Bad Request"}},
)
def update(
    id: UUID,
    subscription_in: SubscriptionIn,
    subscription_service: Annotated[
        SubscriptionService, Depends(get_subscription_service)
    ],
    current_user: Annotated[UserOut, Depends(get_current_user)],
):
    try:
        subscription = subscription_service.update(id, subscription_in)
        return SubscriptionOut.model_validate(subscription)

    except Exception as e:
        logger.error(f"Error in update plan: {e}")
        raise HTTPException(status_code=400, detail=str(e))
