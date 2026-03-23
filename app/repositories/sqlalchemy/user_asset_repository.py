from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.user_assent import UserAsset
from app.repositories.protocols.iuser_asset_repository import IUserAssetRepository
from app.schemas.user_asset_schema import UserAssetOut


class UserAssetRepository(IUserAssetRepository):
    def __init__(self, db: Session):
        self.db = db

    def associate_assets(self, user_id: UUID, asset_ids: List[UUID]) -> bool:
        associations = [
            UserAsset(user_id=user_id, asset_id=asset_id) for asset_id in asset_ids
        ]
        self.db.bulk_save_objects(associations)
        self.db.commit()

        return True

    def find_assets_by_user_id(self, user_id: UUID) -> List[UserAssetOut]:
        return self.db.query(UserAsset).filter(UserAsset.user_id == user_id).all()

    def delete_user_assets(self, user_id: UUID) -> bool:
        self.db.query(UserAsset).filter(UserAsset.user_id == user_id).delete()
        self.db.commit()

        return True
