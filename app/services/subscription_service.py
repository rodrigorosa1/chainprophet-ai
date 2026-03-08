from typing import List
from uuid import UUID
from app.constants.exceptions.messages import (
    SubscriptionNotFoundError,
    UserNotFoundError,
    PlanNotFoundError,
)
from app.repositories.protocols.isubscriptionRepository import ISubscriptionRepository
from app.repositories.protocols.iuser_repository import IUserRepository
from app.repositories.protocols.iplan_repository import IPlanRepository
from app.schemas.subscription_schema import SubscriptionIn, SubscriptionOut


class SubscriptionService:
    def __init__(
        self,
        subscription_repo: ISubscriptionRepository,
        user_repo: IUserRepository,
        plan_repo: IPlanRepository,
    ):
        self.subscription_repo = subscription_repo
        self.user_repo = user_repo
        self.plan_repo = plan_repo

    def create(self, subscription_in: SubscriptionIn) -> SubscriptionOut:
        user = self.user_repo.find_by_id(subscription_in.user_id)
        if not user:
            raise ValueError(UserNotFoundError.MESSAGE)

        plan = self.plan_repo.find_by_id(subscription_in.plan_id)
        if not plan:
            raise ValueError(PlanNotFoundError.MESSAGE)

        return self.subscription_repo.create(subscription_in)

    def find_by_id(self, id: UUID) -> SubscriptionOut:
        subscription = self.subscription_repo.find_by_id(id)
        if not subscription:
            raise ValueError(SubscriptionNotFoundError.MESSAGE)

        return subscription

    def find_all(self) -> List[SubscriptionOut]:
        return self.subscription_repo.find_all()

    def update(self, id: UUID, subscription_in: SubscriptionIn) -> SubscriptionOut:
        subscription = self.subscription_repo.find_by_id(id)
        if not subscription:
            raise ValueError(SubscriptionNotFoundError.MESSAGE)

        return self.subscription_repo.update(subscription, subscription_in)

    def delete(self, id: UUID) -> bool:
        subscription = self.subscription_repo.find_by_id(id)
        if not subscription:
            raise ValueError(SubscriptionNotFoundError.MESSAGE)

        return self.subscription_repo.delete(subscription)
