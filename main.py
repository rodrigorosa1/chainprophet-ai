import multiprocessing
from fastapi import FastAPI
import uvicorn
from app.core.config import get_settings
from app.routes.users import router as user_router
from app.routes.actives import router as active_router
from app.routes.alerts import router as alert_router
from app.routes.prediction import router as prediction_router


settings = get_settings()

app = FastAPI(title=settings.APP_NAME)

app.include_router(user_router, prefix="/users")
app.include_router(active_router, prefix="/actives")
app.include_router(alert_router, prefix="/alerts")
app.include_router(prediction_router, prefix="/prediction")

if __name__ == "__main__":
    host_process = multiprocessing.Process(
        target=uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True, reload_dirs=["./app", "./tests"])
    )
    host_process.start()
