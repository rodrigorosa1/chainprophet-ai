from pydantic import BaseModel, ConfigDict
from uuid import UUID


class AssetOut(BaseModel):
    id: UUID
    name: str
    symbol: str
    code: str

    model_config = ConfigDict(from_attributes=True)
