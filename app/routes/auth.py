from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.injections import get_user_service
from app.repositories.dependencies.auth import get_current_user
from app.schemas.user_schema import UserIn, UserOut
from app.services.auth_service import authenticate_user
from app.schemas.auth_schema import LoginIn, TokenOut
import logging

from app.services.user_service import UserService

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tags: str = "Authentication"


@router.post("/login", response_model=TokenOut, tags=[tags])
def login(login_data: LoginIn, db: Session = Depends(get_db)):
    try:
        token = authenticate_user(db, login_data.email, login_data.password)
        return TokenOut.model_validate(token)
    except Exception as e:
        logger.error(f"Error in auth user: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/register",
    response_model=UserOut,
    responses={400: {"description": "Bad request error"}},
    tags=[tags],
)
def register(
    user_in: UserIn, user_service: Annotated[UserService, Depends(get_user_service)]
):
    try:
        user = user_service.register(user_in)
        return UserOut.model_validate(user)

    except Exception as e:
        logger.error(f"Error in register user: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me", tags=[tags])
def get_profile(current_user: Annotated[UserOut, Depends(get_current_user)]):
    return current_user
