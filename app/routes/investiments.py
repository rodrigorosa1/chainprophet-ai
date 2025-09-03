from typing import List
from fastapi import APIRouter, Depends, HTTPException
import logging
from app.core.injections import get_investiment_service
from app.schemas.investiment_schema import InvestimentIn, InvestimentOut
from app.services.investiment_service import InvestimentService


router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/", response_model=InvestimentOut)
def create(
    investiment_data: InvestimentIn,
    investiment_service: InvestimentService = Depends(get_investiment_service),
):
    try:
        investiment = investiment_service.create(investiment_data)
        return InvestimentOut.model_validate(investiment)

    except Exception as e:
        logger.error(f"Error in register investiment: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/actives", response_model=List[InvestimentOut])
def find_all(
    investiment_service: InvestimentService = Depends(get_investiment_service),
):
    try:
        investiments = investiment_service.find_by_active()
        return [InvestimentOut.model_validate(x) for x in investiments]

    except Exception as e:
        logger.error(f"Error in query investiments: {e}")
        raise HTTPException(status_code=400, detail=str(e))
