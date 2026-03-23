from pydantic import BaseModel, ConfigDict
from uuid import UUID


class UserAssetOut(BaseModel):
    id: UUID
    user_id: UUID
    asset_id: UUID

    model_config = ConfigDict(from_attributes=True)
