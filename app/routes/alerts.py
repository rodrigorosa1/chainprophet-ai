from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from app.core.injections import get_alert_service
from app.schemas.alert_schema import AlertIn, AlertOut
from app.services.alert_service import AlertService
import logging

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/", response_model=AlertOut)
def create(
    alert_data: AlertIn, alert_service: AlertService = Depends(get_alert_service)
):
    try:
        alert = alert_service.create(alert_data)
        return AlertOut.model_validate(alert)

    except Exception as e:
        logger.error(f"Error in register alert: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=List[AlertOut])
def find_by_user(
    user_id: UUID, alert_service: AlertService = Depends(get_alert_service)
):
    try:
        alerts = alert_service.find_by_user(user_id)
        return [AlertOut.model_validate(x) for x in alerts]

    except Exception as e:
        logger.error(f"Error in query alert: {e}")
        raise HTTPException(status_code=400, detail=str(e))
