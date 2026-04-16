from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from uuid import UUID


class JobExecutionOut(BaseModel):
    id: UUID
    job_name: str
    status: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata_json: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)
