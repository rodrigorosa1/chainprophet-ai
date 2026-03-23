from typing import List

from app.repositories.protocols.iasset_repository import IAssetRepository
from app.schemas.asset_schema import AssetOut


class AssetService:
    def __init__(self, asset_repo: IAssetRepository):
        self.asset_repo = asset_repo

    def find_all(self) -> List[AssetOut]:
        return self.asset_repo.find_all()
