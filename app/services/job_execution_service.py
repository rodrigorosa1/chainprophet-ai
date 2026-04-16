from app.repositories.protocols.ijob_execution_repository import IJobExecutionRepository
from app.schemas.job_execution_schema import JobExecutionOut


class JobExecutionService:
    def __init__(self, repository: IJobExecutionRepository):
        self.repository = repository

    def start(
        self, job_name: str, metadata_json: dict | None = None
    ) -> JobExecutionOut:
        return self.repository.start(job_name=job_name, metadata_json=metadata_json)

    def success(
        self,
        execution: JobExecutionOut,
        metadata_json: dict | None = None,
    ) -> JobExecutionOut:
        return self.repository.mark_success(
            execution=execution,
            metadata_json=metadata_json,
        )

    def failed(
        self,
        execution: JobExecutionOut,
        error_message: str,
        metadata_json: dict | None = None,
    ) -> JobExecutionOut:
        return self.repository.mark_failed(
            execution=execution,
            error_message=error_message,
            metadata_json=metadata_json,
        )
