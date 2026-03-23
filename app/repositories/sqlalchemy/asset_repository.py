from typing import List
from sqlalchemy.orm import Session
from app.models.asset import Asset
from app.repositories.protocols.iasset_repository import IAssetRepository
from app.schemas.asset_schema import AssetOut


class AssetRepository(IAssetRepository):
    def __init__(self, db: Session):
        self.db = db

    def find_all(self) -> List[AssetOut]:
        return self.db.query(Asset).all()
