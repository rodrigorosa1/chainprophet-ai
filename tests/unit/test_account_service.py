import unittest
from unittest.mock import Mock
from uuid import uuid4
import pytest
from app.schemas.plan_schema import PlanOut
from app.schemas.user_schema import UserOut
from app.services.account_service import AccountService
from app.schemas.subscription_schema import SubscriptionOut


class TestAccountService(unittest.TestCase):
    def test_overview_success(self):
        user_id = uuid4()
        plan_id = uuid4()

        subscription_out = SubscriptionOut(
            id=uuid4(),
            user_id=user_id,
            plan_id=plan_id,
            active=True,
            started_at="2024-01-01T00:00:00Z",
            canceled_at=None,
            user=UserOut(id=user_id, email="test@example.com", name="Test User"),
            plan=PlanOut(
                id=plan_id, name="Test Plan", no_limit=False, value=9.99, daily_amount=5
            ),
            call_today=5,
        )

        mock_subscription_repo = Mock()
        mock_subscription_repo.find_by_user_id.return_value = subscription_out

        mock_history_repo = Mock()
        mock_history_repo.today_count.return_value = 5

        service = AccountService(
            user_repo=Mock(),
            plan_repo=Mock(),
            subscription_repo=mock_subscription_repo,
            history_repo=mock_history_repo,
        )

        result = service.overview(user_id)

        self.assertEqual(result, subscription_out)

    def test_overview_no_subscription(self):
        user_id = uuid4()

        mock_subscription_repo = Mock()
        mock_subscription_repo.find_by_user_id.return_value = None

        service = AccountService(
            user_repo=None,
            plan_repo=None,
            subscription_repo=mock_subscription_repo,
            history_repo=None,
        )

        with pytest.raises(ValueError) as exc_info:
            service.overview(user_id)

        assert str(exc_info.value) == "No subscription found for the user."
