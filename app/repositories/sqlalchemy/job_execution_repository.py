from datetime import datetime

from sqlalchemy.orm import Session

from app.models.job_execution import JobExecution
from app.schemas.job_execution_schema import JobExecutionOut


class JobExecutionRepository:
    def __init__(self, db: Session):
        self.db = db

    def start(
        self, job_name: str, metadata_json: dict | None = None
    ) -> JobExecutionOut:
        execution = JobExecution(
            job_name=job_name,
            status="running",
            started_at=datetime.utcnow(),
            metadata_json=metadata_json or {},
        )
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        return execution

    def mark_success(
        self,
        execution: JobExecution,
        metadata_json: dict | None = None,
    ) -> JobExecution:
        execution.status = "success"
        execution.finished_at = datetime.utcnow()

        if metadata_json is not None:
            execution.metadata_json = metadata_json

        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        return execution

    def mark_failed(
        self,
        execution: JobExecutionOut,
        error_message: str,
        metadata_json: dict | None = None,
    ) -> JobExecutionOut:
        execution.status = "failed"
        execution.finished_at = datetime.utcnow()
        execution.error_message = error_message

        if metadata_json is not None:
            execution.metadata_json = metadata_json

        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        return execution
