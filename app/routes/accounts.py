from typing import Annotated, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from app.core.injections import get_account_service
from app.repositories.dependencies.auth import get_current_user
from app.schemas.subscription_schema import SubscriptionOut
from app.services.account_service import AccountService
import logging


router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tags: str = "Accounts"


@router.get(
    "/overview",
    tags=[tags],
    responses={400: {"description": "Error in account overview"}},
)
def get_overview(
    current_user: Annotated[SubscriptionOut, Depends(get_current_user)],
    account_service: Annotated[AccountService, Depends(get_account_service)],
):
    try:
        overview = account_service.overview(current_user.id)
        return SubscriptionOut.model_validate(overview)

    except Exception as e:
        logger.error(f"Error in get account overview: {e}")
        raise HTTPException(status_code=400, detail=str(e))
