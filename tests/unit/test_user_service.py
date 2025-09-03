import unittest
from unittest.mock import Mock
from uuid import uuid4
import pytest
from app.constants.enums.type_notification_enum import TypeNotificationEnum
from app.services.user_service import UserService
from app.schemas.user_schema import UserIn, UserOut


class TestUserService(unittest.TestCase):
    def test_create_user_success(self):
        user_data = UserIn(
            name="Anakin Skywalker",
            email="anakin.skywalker@jedi.com",
            password="123",
            phone="5548984863711",
            type_notification=TypeNotificationEnum.ALL
        )

        mock_repo = Mock()
        mock_repo.find_by_email.return_value = []
        mock_repo.create.return_value = UserOut(
            id=uuid4(),
            name="Anakin Skywalker",
            email="anakin.skywalker@jedi.com",
            password="123",
            phone="5548984863711",
            type_notification=TypeNotificationEnum.ALL
        )

        service = UserService(mock_repo)
        result = service.create(user_data)

        assert isinstance(result, UserOut)
        assert result.name == user_data.name
        assert result.email == user_data.email
        assert result.phone == user_data.phone
        assert result.type_notification == user_data.type_notification
        mock_repo.create.assert_called_once_with(user_data)


    def test_create_user_error_mail_exists(self):
        user_data = UserIn(
            name="Anakin Skywalker",
            email="anakin.skywalker@jedi.com",
            password="123",
            phone="5548984863711",
            type_notification=TypeNotificationEnum.ALL
        )

        mock_repo = Mock()
        mock_repo.find_by_email.return_value = UserOut(
            id=uuid4(),
            name="Anakin Skywalker",
            email="anakin.skywalker@jedi.com",
            password="123",
            phone="5548984863711",
            type_notification=TypeNotificationEnum.ALL
        )

        service = UserService(mock_repo)
        with pytest.raises(ValueError) as exc_info:
            service.create(user_data)

        assert str(exc_info.value) == "Email already exists"
