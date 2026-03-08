import unittest
from unittest.mock import Mock
from uuid import uuid4
import pytest
from app.services.plan_service import PlanService
from app.schemas.plan_schema import PlanIn, PlanOut


class TestPlanService(unittest.TestCase):
    def test_create_success(self):
        plan_in = PlanIn(
            name="PLUS",
            no_limit=True,
            value=9.99,
        )

        mock_repo = Mock()
        mock_repo.create.return_value = PlanOut(
            id=uuid4(),
            name="PLUS",
            daily_amount=None,
            no_limit=True,
            value=9.99,
        )

        service = PlanService(mock_repo)
        result = service.create(plan_in)

        self.assertEqual(result.name, plan_in.name)
        self.assertEqual(result.no_limit, plan_in.no_limit)
        self.assertEqual(result.value, plan_in.value)

    def test_delete_success(self):
        mock_repo = Mock()
        mock_repo.create.return_value = PlanOut(
            id=uuid4(),
            name="PLUS",
            daily_amount=None,
            no_limit=True,
            value=9.99,
        )

        service = PlanService(mock_repo)
        result = service.delete(uuid4())

        self.assertTrue(result)

    def test_delete_error_plan_not_found(self):
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = []
        service = PlanService(mock_repo)
        with pytest.raises(ValueError) as exc_info:
            service.delete(uuid4())

        assert str(exc_info.value) == "Plan not found"
