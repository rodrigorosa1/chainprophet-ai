from fastapi import APIRouter, Depends, HTTPException
from app.core.injections import get_user_service
from app.repositories.dependencies.auth import get_current_user
from app.schemas.user_schema import UserIn, UserOut
from app.services.user_service import UserService
import logging

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/register", response_model=UserOut)
def create(user_data: UserIn, user_service: UserService = Depends(get_user_service)):
    try:
        user = user_service.create(user_data)
        return UserOut.model_validate(user)

    except Exception as e:
        logger.error(f"Error in register user: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me")
def get_profile(current_user: UserOut = Depends(get_current_user)):
    return current_user
