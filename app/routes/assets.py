from typing import Annotated, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from app.core.injections import get_asset_service
from app.repositories.dependencies.auth import get_current_user
from app.schemas.asset_schema import AssetOut
from app.services.asset_service import AssetService
import logging


router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tags: str = "Assets"


@router.get(
    "/",
    response_model=List[AssetOut],
    responses={400: {"description": "Bad request error"}},
    description="Retrieve all assets",
    tags=[tags],
)
def find_all(
    asset_service: Annotated[AssetService, Depends(get_asset_service)],
    current_user: Annotated[object, Depends(get_current_user)],
):
    try:
        assets = asset_service.find_all()
        return [AssetOut.model_validate(asset) for asset in assets]

    except Exception as e:
        logger.error(f"Error in query assets: {e}")
        raise HTTPException(status_code=400, detail=str(e))
