from typing import List
from fastapi import APIRouter, Depends, HTTPException
import logging
from app.core.injections import get_active_service
from app.schemas.active_schema import ActiveIn, ActiveOut
from app.services.active_service import ActiveService

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/", response_model=ActiveOut)
def create(
    active_data: ActiveIn, active_service: ActiveService = Depends(get_active_service)
):
    try:
        active = active_service.create(active_data)
        return ActiveOut.model_validate(active)

    except Exception as e:
        logger.error(f"Error in register active: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ActiveOut])
def find_all(active_service: ActiveService = Depends(get_active_service)):
    try:
        actives = active_service.find_all()
        return [ActiveOut.model_validate(x) for x in actives]

    except Exception as e:
        logger.error(f"Error in query active: {e}")
        raise HTTPException(status_code=400, detail=str(e))
