from sqlalchemy import Column, DateTime, String, JSON, Text
from sqlalchemy.sql import func

from app.models.base import ModelBase


class JobExecution(ModelBase):
    __tablename__ = "job_executions"

    job_name = Column(String(150), nullable=False, index=True)
    status = Column(String(30), nullable=False, index=True)
    started_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    finished_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)
