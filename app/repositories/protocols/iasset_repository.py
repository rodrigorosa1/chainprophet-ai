from typing import List, Protocol

from app.schemas.asset_schema import AssetOut


class IAssetRepository(Protocol):
    def find_all(self) -> List[AssetOut]: ...
