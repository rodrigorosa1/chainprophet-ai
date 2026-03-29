from uuid import UUID
from app.repositories.protocols.iplan_repository import IPlanRepository
from app.repositories.protocols.isubscriptionRepository import ISubscriptionRepository
from app.repositories.protocols.iuser_repository import IUserRepository
from app.repositories.protocols.ihistory_repository import IHistoryRepository
from app.schemas.subscription_schema import SubscriptionOut


class AccountService:
    def __init__(
        self,
        user_repo: IUserRepository,
        plan_repo: IPlanRepository,
        subscription_repo: ISubscriptionRepository,
        history_repo: IHistoryRepository,
    ):
        self.user_repository = user_repo
        self.plan_repository = plan_repo
        self.subscription_repository = subscription_repo
        self.history_repository = history_repo

    def overview(self, user_id: UUID) -> SubscriptionOut:
        subscription = self.subscription_repository.find_by_user_id(user_id)

        if not subscription:
            raise ValueError("No subscription found for the user.")

        subscription.call_today = self.history_repository.today_count(user_id)

        return subscription
