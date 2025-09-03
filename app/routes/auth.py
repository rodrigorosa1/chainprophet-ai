from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.auth_service import authenticate_user
from app.schemas.auth_schema import LoginIn, TokenOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
def login(login_data: LoginIn, db: Session = Depends(get_db)):
    token = authenticate_user(db, login_data.email, login_data.password)
    return {"access_token": token}