from app.repositories.protocols.ihistory_repository import IHistoryRepository
from app.repositories.protocols.iuser_repository import IUserRepository
from app.services.forecast_service import ForecastService
from app.services.market_data_service import MarketDataService
from app.services.sentiment_service import SentimentService
from app.services.signal_engine_service import SignalEngineService
from app.services.backtest_service import BacktestService
from app.services.ml_forecast_service import MlForecastService


class ApiCustomerService:
    def __init__(
        self,
        forecast_service: ForecastService,
        market_data_service: MarketDataService,
        sentiment_service: SentimentService,
        signal_engine_service: SignalEngineService,
        backtest_service: BacktestService,
        user_repository: IUserRepository,
        history_repository: IHistoryRepository,
        ml_forecast_service: MlForecastService,
    ):
        self.forecast_service = forecast_service
        self.market_data_service = market_data_service
        self.sentiment_service = sentiment_service
        self.signal_engine_service = signal_engine_service
        self.backtest_service = backtest_service
        self.user_repository = user_repository
        self.history_repository = history_repository
        self.ml_forecast_service = ml_forecast_service

    def forecast(self, api_key: str, tickers: list[str], hours: int) -> dict:
        user = self.user_repository.find_by_api_key(api_key)

        if not user or not user.active:
            raise ValueError("Invalid or inactive API key.")

        forecast = self.forecast_service.forecast_prices(tickers=tickers, hours=hours)

        self.history_repository.create(user_id=user.id)

        return forecast
