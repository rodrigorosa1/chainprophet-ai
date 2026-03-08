from typing import Annotated, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from app.core.injections import get_user_service
from app.repositories.dependencies.auth import get_current_user
from app.schemas.user_schema import UserIn, UserOut
from app.services.user_service import UserService
import logging

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post(
    "/", response_model=UserOut, responses={400: {"description": "Bad request error"}}
)
def create(
    user_in: UserIn, user_service: Annotated[UserService, Depends(get_user_service)]
):
    try:
        user = user_service.create(user_in)
        return UserOut.model_validate(user)

    except Exception as e:
        logger.error(f"Error in register user: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{id}",
    response_model=UserOut,
    responses={400: {"description": "Bad request error"}},
)
def find_by_id(
    id: UUID,
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
):
    try:
        user = user_service.find_by_id(id)
        return UserOut.model_validate(user)

    except Exception as e:
        logger.error(f"Error in query user: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/",
    response_model=List[UserOut],
    responses={400: {"description": "Bad request error"}},
)
def find_all(
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
):
    try:
        users = user_service.find_all()
        return [UserOut.model_validate(x) for x in users]

    except Exception as e:
        logger.error(f"Error in query user: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.patch(
    "/{id}",
    response_model=UserOut,
    responses={400: {"description": "Bad request error"}},
)
def update(
    id: UUID,
    user_in: UserIn,
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
):
    try:
        user = user_service.update(id, user_in)
        return UserOut.model_validate(user)

    except Exception as e:
        logger.error(f"Error in update user: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me")
def get_profile(current_user: Annotated[UserOut, Depends(get_current_user)]):
    return current_user
