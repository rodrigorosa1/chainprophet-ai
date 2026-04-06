from fastapi import Depends
from app.core.database import get_db
from app.repositories.sqlalchemy.asset_repository import AssetRepository
from app.repositories.sqlalchemy.forecast_analysis_repository import (
    ForecastAnalysisRepository,
)
from app.repositories.sqlalchemy.forecast_repository import ForecastRepository
from app.repositories.sqlalchemy.history_repository import HistoryRepository
from app.repositories.sqlalchemy.plan_repository import PlanRepository
from app.repositories.sqlalchemy.subscription_repository import SubscriptionRepository
from app.repositories.sqlalchemy.user_asset_repository import UserAssetRepository
from app.services.account_service import AccountService
from app.services.asset_service import AssetService
from app.repositories.sqlalchemy.user_repository import UserRepository
from app.services.backtest_service import BacktestService
from app.services.feature_engineering_service import FeatureEngineeringService
from app.services.forecast_evaluation_service import ForecastEvaluationService
from app.services.forecast_outcome_service import ForecastOutcomeService
from app.services.forecast_service import ForecastService
from app.services.market_data_service import MarketDataService
from app.services.ml_forecast_service import MlForecastService
from app.services.ml_model_service import MlModelService
from app.services.ml_training_service import MlTrainingService
from app.services.plan_service import PlanService
from app.services.sentiment_service import SentimentService
from app.services.signal_engine_service import SignalEngineService
from app.services.subscription_service import SubscriptionService
from app.services.user_service import UserService
from app.services.forecast_failure_classifier_service import (
    ForecastFailureClassifierService,
)
from app.repositories.sqlalchemy.forecast_analysis_repository import (
    ForecastAnalysisRepository,
)
from app.clients.openai_client import OpenAiClient
from app.repositories.sqlalchemy.forecast_ai_report_repository import (
    ForecastAiReportRepository,
)
from app.services.forecast_llm_analyst_service import ForecastLlmAnalystService
from sqlalchemy.orm import Session


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    repo = UserRepository(db)
    user_asset_repo = UserAssetRepository(db)
    plan_repo = PlanRepository(db)
    subscription_repo = SubscriptionRepository(db)
    return UserService(repo, user_asset_repo, plan_repo, subscription_repo)


def get_plan_service(db: Session = Depends(get_db)) -> PlanService:
    repo = PlanRepository(db)
    return PlanService(repo)


def get_subscription_service(db: Session = Depends(get_db)) -> SubscriptionService:
    repo = SubscriptionRepository(db)
    user_repo = UserRepository(db)
    plan_repo = PlanRepository(db)
    return SubscriptionService(repo, user_repo, plan_repo)


def get_forecast_service(db: Session = Depends(get_db)) -> ForecastService:
    repo = ForecastRepository(db)
    market_data_service = MarketDataService()
    sentiment_service = SentimentService()
    signal_engine_service = SignalEngineService()
    backtest_service = BacktestService()
    user_repo = UserRepository(db)
    history_repo = HistoryRepository(db)
    ml_forecast_service = get_ml_forecast_service()

    return ForecastService(
        repo,
        market_data_service,
        sentiment_service,
        signal_engine_service,
        backtest_service,
        user_repo,
        history_repo,
        ml_forecast_service,
    )


def get_ml_forecast_service() -> MlForecastService:
    market_data_service = MarketDataService()
    feature_engineering_service = FeatureEngineeringService()
    ml_model_service = MlModelService()

    return MlForecastService(
        market_data_service=market_data_service,
        feature_engineering_service=feature_engineering_service,
        ml_model_service=ml_model_service,
    )


def get_ml_training_service() -> MlTrainingService:
    market_data_service = MarketDataService()
    feature_engineering_service = FeatureEngineeringService()
    ml_model_service = MlModelService()

    return MlTrainingService(
        market_data_service=market_data_service,
        feature_engineering_service=feature_engineering_service,
        ml_model_service=ml_model_service,
    )


def get_forecast_outcome_service(
    db: Session = Depends(get_db),
) -> ForecastOutcomeService:
    analysis_repo = ForecastAnalysisRepository(db)
    market_data_service = MarketDataService()

    return ForecastOutcomeService(
        analysis_repository=analysis_repo,
        market_data_service=market_data_service,
    )


def get_forecast_evaluation_service(
    db: Session = Depends(get_db),
) -> ForecastEvaluationService:
    analysis_repo = ForecastAnalysisRepository(db)

    return ForecastEvaluationService(
        analysis_repository=analysis_repo,
    )


def get_forecast_failure_classifier_service(
    db: Session = Depends(get_db),
) -> ForecastFailureClassifierService:
    analysis_repo = ForecastAnalysisRepository(db)

    return ForecastFailureClassifierService(
        analysis_repository=analysis_repo,
    )


def get_forecast_llm_analyst_service(
    db: Session = Depends(get_db),
) -> ForecastLlmAnalystService:
    ai_report_repository = ForecastAiReportRepository(db)
    ai_client = OpenAiClient()

    return ForecastLlmAnalystService(
        ai_report_repository=ai_report_repository,
        ai_client=ai_client,
    )


def get_asset_service(db: Session = Depends(get_db)) -> AssetService:
    repo = AssetRepository(db)
    return AssetService(repo)


def get_account_service(db: Session = Depends(get_db)) -> AccountService:
    user_repo = UserRepository(db)
    plan_repo = PlanRepository(db)
    subscription_repo = SubscriptionRepository(db)
    history_repo = HistoryRepository(db)

    return AccountService(
        user_repo=user_repo,
        plan_repo=plan_repo,
        subscription_repo=subscription_repo,
        history_repo=history_repo,
    )
