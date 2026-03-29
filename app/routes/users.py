from typing import Annotated, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from app.core.injections import get_user_service
from app.repositories.dependencies.auth import get_current_user
from app.schemas.user_asset_schema import UserAssetOut
from app.schemas.user_schema import UserIn, UserOut
from app.services.user_service import UserService
import logging

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tags: str = "Users"


@router.post(
    "/",
    response_model=UserOut,
    responses={400: {"description": "Bad request error"}},
    tags=[tags],
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
    tags=[tags],
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
    tags=[tags],
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
    tags=[tags],
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


@router.post(
    "/{id}/assets",
    response_model=bool,
    responses={400: {"description": "Bad request error"}},
    tags=[tags],
)
def associate_assets(
    id: UUID,
    asset_ids: List[UUID],
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
):
    try:
        return user_service.associate_assets(id, asset_ids)

    except Exception as e:
        logger.error(f"Error in associate assets to user: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{id}/assets",
    response_model=List[UserAssetOut],
    responses={400: {"description": "Bad request error"}},
    tags=[tags],
)
def find_assets_by_user_id(
    id: UUID,
    user_service: Annotated[UserService, Depends(get_user_service)],
    current_user: Annotated[UserOut, Depends(get_current_user)],
):
    try:
        return user_service.find_assets_by_user_id(id)

    except Exception as e:
        logger.error(f"Error in find assets by user id: {e}")
        raise HTTPException(status_code=400, detail=str(e))
