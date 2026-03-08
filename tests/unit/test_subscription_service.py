import unittest
from unittest.mock import Mock
from uuid import uuid4
import pytest
from app.services.subscription_service import SubscriptionService
from app.schemas.subscription_schema import SubscriptionIn, SubscriptionOut
from app.schemas.plan_schema import PlanOut
from app.schemas.user_schema import UserOut
from datetime import datetime


class TestSubscriptService(unittest.TestCase):
    def test_create_success(self):
        user = UserOut(
            id=uuid4(),
            name="Anakin Skywalker",
            email="anakin.skywalker@jedi.com",
            phone="5548984863711",
            api_key="W8R9KcQe4ZP0xD7YH1nT2bM5aFJ6L9S",
            provider_customer_id=None,
            active=True,
        )

        plan = PlanOut(
            id=uuid4(),
            name="PLUS",
            daily_amount=None,
            no_limit=True,
            value=9.99,
        )

        subscription_in = SubscriptionIn(user_id=user.id, plan_id=plan.id)

        mock_repo = Mock()
        mock_repo.create.return_value = SubscriptionOut(
            id=uuid4(),
            user_id=user.id,
            plan_id=plan.id,
            active=True,
            started_at=datetime.now(),
            canceled_at=None,
            user=user,
            plan=plan,
        )

        user_mock_repo = Mock()
        user_mock_repo.find_by_id.return_value = user

        plan_mock_repo = Mock()
        plan_mock_repo.find_by_id.return_value = plan

        service = SubscriptionService(mock_repo, user_mock_repo, plan_mock_repo)
        result = service.create(subscription_in)

        self.assertEqual(result.user_id, subscription_in.user_id)
        self.assertEqual(result.plan_id, subscription_in.plan_id)

    def test_create_error_user_not_found(self):
        plan = PlanOut(
            id=uuid4(),
            name="PLUS",
            daily_amount=None,
            no_limit=True,
            value=9.99,
        )

        subscription_in = SubscriptionIn(user_id=uuid4(), plan_id=plan.id)

        user_mock_repo = Mock()
        user_mock_repo.find_by_id.return_value = []

        plan_mock_repo = Mock()
        plan_mock_repo.find_by_id.return_value = plan

        mock_repo = Mock()
        service = SubscriptionService(mock_repo, user_mock_repo, plan_mock_repo)
        with pytest.raises(ValueError) as exc_info:
            service.create(subscription_in)

        assert str(exc_info.value) == "User not found"

    def test_create_error_plan_not_found(self):
        user = UserOut(
            id=uuid4(),
            name="Anakin Skywalker",
            email="anakin.skywalker@jedi.com",
            phone="5548984863711",
            api_key="W8R9KcQe4ZP0xD7YH1nT2bM5aFJ6L9S",
            provider_customer_id=None,
            active=True,
        )

        subscription_in = SubscriptionIn(user_id=user.id, plan_id=uuid4())

        user_mock_repo = Mock()
        user_mock_repo.find_by_id.return_value = user

        plan_mock_repo = Mock()
        plan_mock_repo.find_by_id.return_value = []

        mock_repo = Mock()
        service = SubscriptionService(mock_repo, user_mock_repo, plan_mock_repo)
        with pytest.raises(ValueError) as exc_info:
            service.create(subscription_in)

        assert str(exc_info.value) == "Plan not found"
