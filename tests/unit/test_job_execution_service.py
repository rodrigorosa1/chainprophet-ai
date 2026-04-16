import unittest
from datetime import datetime
from unittest.mock import Mock
from uuid import uuid4
from app.services.job_execution_service import JobExecutionService
from app.schemas.job_execution_schema import JobExecutionOut


class TestJobExecutionService(unittest.TestCase):
    def test_start_success(self):
        mock_repo = Mock()
        mock_repo.start.return_value = JobExecutionOut(
            id=uuid4(),
            job_name="test_job",
            status="running",
            started_at=datetime.now(),
            finished_at=None,
            metadata_json={"key": "value"},
        )

        service = JobExecutionService(mock_repo)
        result = service.start(job_name="test_job", metadata_json={"key": "value"})

        self.assertEqual(result.job_name, "test_job")
        self.assertEqual(result.status, "running")
        self.assertEqual(result.metadata_json, {"key": "value"})

    def test_success_success(self):
        mock_repo = Mock()
        execution = JobExecutionOut(
            id=uuid4(),
            job_name="test_job",
            status="running",
            started_at=datetime.now(),
            finished_at=None,
            metadata_json={"key": "value"},
        )
        mock_repo.mark_success.return_value = JobExecutionOut(
            id=execution.id,
            job_name=execution.job_name,
            status="success",
            started_at=execution.started_at,
            finished_at=datetime.now(),
            metadata_json={"result": "ok"},
        )

        service = JobExecutionService(mock_repo)
        result = service.success(execution=execution, metadata_json={"result": "ok"})

        self.assertEqual(result.status, "success")
        self.assertEqual(result.metadata_json, {"result": "ok"})

    def test_failed_success(self):
        mock_repo = Mock()
        execution = JobExecutionOut(
            id=uuid4(),
            job_name="test_job",
            status="running",
            started_at=datetime.now(),
            finished_at=None,
            metadata_json={"key": "value"},
        )
        mock_repo.mark_failed.return_value = JobExecutionOut(
            id=execution.id,
            job_name=execution.job_name,
            status="failed",
            started_at=execution.started_at,
            finished_at=datetime.now(),
            metadata_json={"error": "something went wrong"},
        )

        service = JobExecutionService(mock_repo)
        result = service.failed(
            execution=execution,
            error_message="something went wrong",
            metadata_json={"error": "something went wrong"},
        )

        self.assertEqual(result.status, "failed")
        self.assertEqual(result.metadata_json, {"error": "something went wrong"})
