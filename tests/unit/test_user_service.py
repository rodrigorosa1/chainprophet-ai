import unittest
from unittest.mock import Mock
from uuid import uuid4
import pytest
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

        service = UserService(mock_repo)
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

        service = UserService(mock_repo)
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

        service = UserService(mock_repo)
        result = service.register_password(uuid4(), "4ZP0xD7YH1n")

        self.assertEqual(result.name, "Anakin Skywalker")
        self.assertEqual(result.email, "anakin.skywalker@jedi.com")
        self.assertEqual(result.phone, "5548984863711")
        self.assertEqual(result.api_key, "W8R9KcQe4ZP0xD7YH1nT2bM5aFJ6L9S")

    def test_register_password_error_user_not_found(self):
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = []

        service = UserService(mock_repo)
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

        service = UserService(mock_repo)
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

        service = UserService(mock_repo)
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
        service = UserService(mock_repo)
        result = service.delete(uuid4())

        self.assertTrue(result)

    def test_delete_error_user_not_found(self):
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = []
        service = UserService(mock_repo)
        with pytest.raises(ValueError) as exc_info:
            service.delete(uuid4())

        assert str(exc_info.value) == "User not found"
