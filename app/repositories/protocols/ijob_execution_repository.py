from typing import Protocol
from uuid import UUID
from app.models.job_execution import JobExecution


class IJobExecutionRepository(Protocol):
    def start(
        self, job_name: str, metadata_json: dict | None = None
    ) -> JobExecution: ...
    def mark_success(
        self,
        execution: JobExecution,
        metadata_json: dict | None = None,
    ) -> JobExecution: ...
    def mark_failed(
        self,
        execution: JobExecution,
        error_message: str,
        metadata_json: dict | None = None,
    ) -> JobExecution: ...
