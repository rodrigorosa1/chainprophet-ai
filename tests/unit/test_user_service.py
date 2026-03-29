import unittest
from unittest.mock import Mock
from uuid import uuid4
import pytest
from app.schemas.user_asset_schema import UserAssetOut
from app.services.user_service import UserService
from app.schemas.user_schema import UserIn, UserOut


class TestUserService(unittest.TestCase):
    def test_create_user_success(self):
        user_data = UserIn(
            name="Anakin Skywalker",
            email="anakin.skywalker@jedi.com",
            password="4ZP0xD7YH1n",
            phone="5548984863711",
        )

        mock_repo = Mock()
        mock_repo.find_by_email.return_value = []
        mock_repo.create.return_value = UserOut(
            id=uuid4(),
            name="Anakin Skywalker",
            email="anakin.skywalker@jedi.com",
            phone="5548984863711",
            api_key="W8R9KcQe4ZP0xD7YH1nT2bM5aFJ6L9S",
            provider_customer_id=None,
            active=True,
        )

        user_asset_repo = Mock()
        plan_repo = Mock()
        subscription_repo = Mock()

        service = UserService(mock_repo, user_asset_repo, plan_repo, subscription_repo)
        result = service.create(user_data)

        self.assertEqual(result.name, user_data.name)
        self.assertEqual(result.email, user_data.email)
        self.assertEqual(result.phone, user_data.phone)

    def test_create_user_error_mail_exists(self):
        user_data = UserIn(
            name="Anakin Skywalker",
            email="anakin.skywalker@jedi.com",
            password="4ZP0xD7YH1n",
            phone="5548984863711",
        )

        mock_repo = Mock()
        mock_repo.find_by_email.return_value = UserOut(
            id=uuid4(),
            name="Anakin Skywalker",
            email="anakin.skywalker@jedi.com",
            phone="5548984863711",
        )

        user_asset_repo = Mock()
        plan_repo = Mock()
        subscription_repo = Mock()
        service = UserService(mock_repo, user_asset_repo, plan_repo, subscription_repo)
        with pytest.raises(ValueError) as exc_info:
            service.create(user_data)

        assert str(exc_info.value) == "Email already exists"

    def test_register_password_success(self):
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = UserOut(
            id=uuid4(),
            name="Anakin Skywalker",
            email="anakin.skywalker@jedi.com",
            phone="5548984863711",
            api_key="W8R9KcQe4ZP0xD7YH1nT2bM5aFJ6L9S",
            provider_customer_id=None,
            active=True,
        )
        mock_repo.register_password.return_value = mock_repo.find_by_id.return_value

        user_asset_repo = Mock()
        plan_repo = Mock()
        subscription_repo = Mock()
        service = UserService(mock_repo, user_asset_repo, plan_repo, subscription_repo)
        result = service.register_password(uuid4(), "4ZP0xD7YH1n")

        self.assertEqual(result.name, "Anakin Skywalker")
        self.assertEqual(result.email, "anakin.skywalker@jedi.com")
        self.assertEqual(result.phone, "5548984863711")
        self.assertEqual(result.api_key, "W8R9KcQe4ZP0xD7YH1nT2bM5aFJ6L9S")

    def test_register_password_error_user_not_found(self):
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = []

        user_asset_repo = Mock()
        plan_repo = Mock()
        subscription_repo = Mock()
        service = UserService(mock_repo, user_asset_repo, plan_repo, subscription_repo)
        with pytest.raises(ValueError) as exc_info:
            service.register_password(uuid4(), "4ZP0xD7YH1n")

        assert str(exc_info.value) == "User not found"

    def test_update_success(self):
        user_data = UserIn(
            name="Anakin Skywalker",
            email="anakin.skywalker@jedi.com",
            password="4ZP0xD7YH1n",
            phone="5548984863711",
            active=True,
        )

        mock_repo = Mock()
        mock_repo.find_by_id.return_value = UserOut(
            id=uuid4(),
            name="Anakin Skywalker",
            email="anakin.skywalker@jedi.com",
            phone="5548984863711",
            api_key="W8R9KcQe4ZP0xD7YH1nT2bM5aFJ6L9S",
            provider_customer_id=None,
            active=True,
        )
        mock_repo.update.return_value = mock_repo.find_by_id.return_value

        user_asset_repo = Mock()
        plan_repo = Mock()
        subscription_repo = Mock()
        service = UserService(mock_repo, user_asset_repo, plan_repo, subscription_repo)
        result = service.update(uuid4(), user_data)

        self.assertEqual(result.name, user_data.name)
        self.assertEqual(result.email, user_data.email)
        self.assertEqual(result.phone, user_data.phone)
        self.assertEqual(result.active, user_data.active)

    def test_update_error_user_not_foud(self):
        user_data = UserIn(
            name="Anakin Skywalker",
            email="anakin.skywalker@jedi.com",
            password="4ZP0xD7YH1n",
            phone="5548984863711",
        )

        mock_repo = Mock()
        mock_repo.find_by_id.return_value = []

        user_asset_repo = Mock()
        plan_repo = Mock()
        subscription_repo = Mock()

        service = UserService(mock_repo, user_asset_repo, plan_repo, subscription_repo)
        with pytest.raises(ValueError) as exc_info:
            service.update(uuid4(), user_data)

        assert str(exc_info.value) == "User not found"

    def test_delete_success(self):
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = UserOut(
            id=uuid4(),
            name="Anakin Skywalker",
            email="anakin.skywalker@jedi.com",
            phone="5548984863711",
            api_key="W8R9KcQe4ZP0xD7YH1nT2bM5aFJ6L9S",
            provider_customer_id=None,
            active=True,
        )
        mock_repo.delete.return_value = True

        user_asset_repo = Mock()
        plan_repo = Mock()
        subscription_repo = Mock()
        service = UserService(mock_repo, user_asset_repo, plan_repo, subscription_repo)
        result = service.delete(uuid4())

        self.assertTrue(result)

    def test_delete_error_user_not_found(self):
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = []
        user_asset_repo = Mock()
        plan_repo = Mock()
        subscription_repo = Mock()
        service = UserService(mock_repo, user_asset_repo, plan_repo, subscription_repo)
        with pytest.raises(ValueError) as exc_info:
            service.delete(uuid4())

        assert str(exc_info.value) == "User not found"

    def test_associate_assets(self):
        user_id = uuid4()
        asset_ids = [uuid4(), uuid4()]

        mock_repo = Mock()
        mock_repo.find_by_id.return_value = UserOut(
            id=user_id,
            name="Anakin Skywalker",
            email="anakin.skywalker@jedi.com",
            phone="5548984863711",
            api_key="W8R9KcQe4ZP0xD7YH1nT2bM5aFJ6L9S",
            provider_customer_id=None,
            active=True,
        )
        user_asset_repo = Mock()
        user_asset_repo.associate_assets.return_value = True
        plan_repo = Mock()
        subscription_repo = Mock()
        service = UserService(mock_repo, user_asset_repo, plan_repo, subscription_repo)
        result = service.associate_assets(user_id, asset_ids)
        self.assertTrue(result)

    def test_associate_assets_user_not_found(self):
        user_id = uuid4()
        asset_ids = [uuid4(), uuid4()]

        mock_repo = Mock()
        mock_repo.find_by_id.return_value = []
        user_asset_repo = Mock()
        plan_repo = Mock()
        subscription_repo = Mock()
        service = UserService(mock_repo, user_asset_repo, plan_repo, subscription_repo)
        with pytest.raises(ValueError) as exc_info:
            service.associate_assets(user_id, asset_ids)

        assert str(exc_info.value) == "User not found"

    def test_find_assets_by_user_id(self):
        user_id = uuid4()
        asset_ids = [uuid4(), uuid4()]

        mock_repo = Mock()
        mock_repo.find_by_id.return_value = UserOut(
            id=user_id,
            name="Anakin Skywalker",
            email="anakin.skywalker@jedi.com",
            phone="5548984863711",
            api_key="W8R9KcQe4ZP0xD7YH1nT2bM5aFJ6L9S",
            provider_customer_id=None,
            active=True,
        )
        user_asset_repo = Mock()
        user_asset_repo.find_assets_by_user_id.return_value = [
            UserAssetOut(id=asset_id, user_id=user_id, asset_id=asset_id)
            for asset_id in asset_ids
        ]
        plan_repo = Mock()
        subscription_repo = Mock()
        service = UserService(mock_repo, user_asset_repo, plan_repo, subscription_repo)
        result = service.find_assets_by_user_id(user_id)
        self.assertEqual(len(result), len(asset_ids))
        for asset_out, asset_id in zip(result, asset_ids):
            self.assertEqual(asset_out.user_id, user_id)
            self.assertEqual(asset_out.asset_id, asset_id)
