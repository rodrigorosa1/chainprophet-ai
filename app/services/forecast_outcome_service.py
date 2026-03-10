from app.repositories.sqlalchemy.forecast_analysis_repository import (
    ForecastAnalysisRepository,
)
from app.services.market_data_service import MarketDataService


class ForecastOutcomeService:
    def __init__(
        self,
        analysis_repository: ForecastAnalysisRepository,
        market_data_service: MarketDataService,
    ):
        self.analysis_repository = analysis_repository
        self.market_data_service = market_data_service

    def collect_pending_outcomes(self, limit: int = 100) -> list[dict]:
        points = self.analysis_repository.find_pending_outcome_points(limit=limit)
        print(points)

        collected = []

        for point in points:
            asset_symbol = point.forecast_asset.asset_symbol
            forecast_datetime = point.forecast_datetime

            actual_price = self.market_data_service.get_price_by_datetime(
                ticker=asset_symbol,
                target_datetime=forecast_datetime,
                interval="1h",
            )

            if actual_price is None:
                continue

            outcome = self.analysis_repository.create_outcome(
                forecast_point_id=point.id,
                actual_datetime=forecast_datetime,
                actual_price=actual_price,
                price_source="yfinance",
            )

            collected.append(
                {
                    "forecast_point_id": str(point.id),
                    "asset_symbol": asset_symbol,
                    "forecast_datetime": forecast_datetime.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "actual_price": outcome.actual_price,
                }
            )

        return collected
