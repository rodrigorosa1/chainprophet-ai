from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from app.schemas.user_schema import UserOut


class HistoryOut(BaseModel):
    id: UUID
    user_id: UUID
    created_at: Optional[datetime] = None

    user: UserOut

    model_config = ConfigDict(from_attributes=True)
