from fastapi import Depends
from app.core.database import get_db
from app.repositories.sqlalchemy.active_repository import ActiveRepository
from app.repositories.sqlalchemy.alert_repository import AlertRepository
from app.repositories.sqlalchemy.investiment_repository import InvestimentRepository
from app.repositories.sqlalchemy.user_repository import UserRepository
from app.services.active_service import ActiveService
from app.services.alert_service import AlertService
from app.services.investiment_service import InvestimentService
from app.services.user_service import UserService
from sqlalchemy.orm import Session


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    repo = UserRepository(db)
    return UserService(repo)


def get_alert_service(db: Session = Depends(get_db)) -> AlertService:
    repo = AlertRepository(db)
    return AlertService(repo)


def get_active_service(db: Session = Depends(get_db)) -> ActiveService:
    repo = ActiveRepository(db)
    return ActiveService(repo)


def get_investiment_service(db: Session = Depends(get_db)) -> InvestimentService:
    repo = InvestimentRepository(db)
    return InvestimentService(repo)