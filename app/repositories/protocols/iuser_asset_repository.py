from typing import List, Protocol
from uuid import UUID

from app.schemas.user_asset_schema import UserAssetOut


class IUserAssetRepository(Protocol):
    def associate_assets(
        self, user_id: UUID, asset_ids: List[UUID]
    ) -> List[UserAssetOut]: ...

    def find_assets_by_user_id(self, user_id: UUID) -> List[UserAssetOut]: ...
    def delete_user_assets(self, user_id: UUID) -> bool: ...
