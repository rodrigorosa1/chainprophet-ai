from fastapi import Depends
from app.core.database import get_db
from app.repositories.sqlalchemy.plan_repository import PlanRepository
from app.repositories.sqlalchemy.subscription_repository import SubscriptionRepository
from app.repositories.sqlalchemy.user_repository import UserRepository
from app.services.plan_service import PlanService
from app.services.subscription_service import SubscriptionService
from app.services.user_service import UserService
from sqlalchemy.orm import Session


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    repo = UserRepository(db)
    return UserService(repo)


def get_plan_service(db: Session = Depends(get_db)) -> PlanService:
    repo = PlanRepository(db)
    return PlanService(repo)


def get_subscription_service(db: Session = Depends(get_db)) -> SubscriptionService:
    repo = SubscriptionRepository(db)
    user_repo = UserRepository(db)
    plan_repo = PlanRepository(db)
    return SubscriptionService(repo, user_repo, plan_repo)
