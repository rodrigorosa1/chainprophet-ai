import unittest
from unittest.mock import Mock
from uuid import uuid4
import pytest
from app.constants.enums.type_active_enum import TypeActiveEnum
from app.schemas.active_schema import ActiveIn, ActiveOut
from app.services.active_service import ActiveService


class TestActiveService(unittest.TestCase):
    def test_create_active_success(self):
        active_data = ActiveIn(ticker="BTC-USD", name="Bitcoin", type="CRYPTO")

        mock_repo = Mock()
        mock_repo.find_by_ticker.return_value = []
        mock_repo.create.return_value = ActiveOut(
            id=uuid4(),
            ticker="BTC-USD",
            name="Bitcoin",
            type=TypeActiveEnum.CRYPTO,
        )

        service = ActiveService(mock_repo)
        result = service.create(active_data)

        assert isinstance(result, ActiveOut)

        assert result.ticker == active_data.ticker
        assert result.name == active_data.name
        assert result.type == active_data.type
        mock_repo.create.assert_called_once_with(active_data)

    def test_create_active_error_ticker_exists(self):
        active_data = ActiveIn(ticker="BTC-USD", name="Bitcoin", type="CRYPTO")

        mock_repo = Mock()
        mock_repo.find_by_ticker.return_value = ActiveOut(
            id=uuid4(),
            ticker="BTC-USD",
            name="Bitcoin",
            type=TypeActiveEnum.CRYPTO,
        )

        service = ActiveService(mock_repo)
        with pytest.raises(ValueError) as exc_info:
            service.create(active_data)

        assert str(exc_info.value) == "Active already exists"
