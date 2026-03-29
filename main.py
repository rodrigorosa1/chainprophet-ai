import multiprocessing
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.core.config import get_settings
from app.routes.prediction import router as prediction_router
from app.routes.users import router as user_router
from app.routes.auth import router as auth_router
from app.routes.plans import router as plan_router
from app.routes.subscriptions import router as subscription_router
from app.routes.forecast import router as forecast_router
from app.routes.analysis import router as analysis_router
from app.routes.accounts import router as account_router

settings = get_settings()

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
app.include_router(prediction_router, prefix="/prediction")
app.include_router(forecast_router, prefix="/forecast")
app.include_router(analysis_router, prefix="/analysis")
app.include_router(account_router, prefix="/accounts")

if __name__ == "__main__":
    host_process = multiprocessing.Process(
        target=uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=settings.PORT,
            reload=True,
            reload_dirs=["./app", "./tests"],
        )
    )
    host_process.start()
