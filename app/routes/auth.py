from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.auth_service import authenticate_user
from app.schemas.auth_schema import LoginIn, TokenOut
import logging

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/login", response_model=TokenOut)
def login(login_data: LoginIn, db: Session = Depends(get_db)):
    try:
        token = authenticate_user(db, login_data.email, login_data.password)
        return TokenOut.model_validate(token)
    except Exception as e:
        logger.error(f"Error in auth user: {e}")
        raise HTTPException(status_code=400, detail=str(e))
