from typing import List
from uuid import UUID
import datetime
from sqlalchemy.orm import Session
from app.models.subscription import Subscription
from app.repositories.protocols.isubscriptionRepository import ISubscriptionRepository
from app.schemas.subscription_schema import SubscriptionIn, SubscriptionOut


class SubscriptionRepository(ISubscriptionRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, subscription_in: SubscriptionIn) -> SubscriptionOut:
        subscription = Subscription(
            user_id=subscription_in.user_id,
            plan_id=subscription_in.plan_id,
            active=True,
            started_at=datetime.datetime.now(),
        )
        self.db.add(subscription)
        self.db.commit()

        return subscription

    def find_by_id(self, id: UUID) -> SubscriptionOut:
        return self.db.query(Subscription).filter(Subscription.id == id).first()

    def find_all(self) -> List[SubscriptionOut]:
        return self.db.query(Subscription).all()

    def update(
        self, subscription: Subscription, subscription_in: SubscriptionIn
    ) -> SubscriptionOut:
        subscription.active = subscription_in.active

        self.db.add(subscription)
        self.db.commit()

        return subscription

    def delete(self, subscription: Subscription) -> bool:
        self.db.delete(subscription)
        self.db.commit()

        return True
