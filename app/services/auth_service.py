from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import create_access_token
from fastapi import HTTPException, status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()

    if not user or not pwd_context.verify(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas"
        )

    token_data = {
        "sub": str(user.id),
        "name": user.name,
        "email": user.email,
    }

    token = create_access_token(
        data=token_data,
        expires_delta=None,
    )

    return token
