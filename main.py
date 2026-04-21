from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
import uvicorn
import logging

from app.core.config import get_settings
from app.routes.users import router as user_router
from app.routes.auth import router as auth_router
from app.routes.plans import router as plan_router
from app.routes.subscriptions import router as subscription_router
from app.routes.forecast import router as forecast_router
from app.routes.analysis import router as analysis_router
from app.routes.accounts import router as account_router

import app.commands.analysis.run_train_models as run_train_models
import app.commands.analysis.run_forecast_prices as run_forecast_prices
import app.commands.analysis.run_full_analysis_cycle as run_full_analysis_cycle

settings = get_settings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/users")
app.include_router(auth_router, prefix="/auth")
app.include_router(plan_router, prefix="/plans")
app.include_router(subscription_router, prefix="/subscriptions")
app.include_router(forecast_router, prefix="/forecast")
app.include_router(analysis_router, prefix="/analysis")
app.include_router(account_router, prefix="/account")


@app.on_event("startup")
@repeat_every(seconds=43200, wait_first=False)
def scheduled_run_train_ml_models() -> None:
    logger.info("starting scheduled job: train_ml_models")
    result = run_train_models.run()
    logger.info(f"scheduled job finished: train_ml_models | result={result}")


@app.on_event("startup")
@repeat_every(seconds=3600, wait_first=True)
def scheduled_run_forecast_prices() -> None:
    logger.info("starting scheduled job: forecast_prices")
    result = run_forecast_prices.run()
    logger.info(f"scheduled job finished: forecast_prices | result={result}")


@app.on_event("startup")
@repeat_every(seconds=86400, wait_first=True)
def scheduled_run_full_analysis_cycle() -> None:
    logger.info("starting scheduled job: full_analysis_cycle")
    result = run_full_analysis_cycle.run()
    logger.info(f"scheduled job finished: full_analysis_cycle | result={result}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        reload_dirs=["./app", "./tests"],
    )
