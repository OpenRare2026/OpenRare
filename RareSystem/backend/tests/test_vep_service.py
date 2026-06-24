import os
import tempfile

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from services.vep_service import VEPService, VEPJobInfo, VEPServiceError


@pytest.fixture
def vep_service():
    return VEPService(base_url="http://test-vep:8000", max_retries=3, poll_interval=1)


@pytest.fixture
def tmp_vcf():
    with tempfile.NamedTemporaryFile(suffix=".vcf", delete=False) as f:
        f.write(b"##fileformat=VCFv4.1\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")
        path = f.name
    yield path
    os.unlink(path)


class TestSubmitJob:
    @pytest.mark.asyncio
    async def test_submit_job_success(self, vep_service, tmp_vcf):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "job_id": "test-job-123",
            "status": "queued",
            "created_at": "2026-05-28T10:00:00",
            "updated_at": "2026-05-28T10:00:00",
            "input_filename": "test.vcf",
            "input_bytes": 31030,
            "options": {"hgvs": True},
            "status_url": "/runs/test-job-123",
            "result_url": "/runs/test-job-123/result",
            "log_url": "/runs/test-job-123/log",
            "rows": None,
            "error": None,
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("services.vep_service.httpx.AsyncClient", return_value=mock_client):
            result = await vep_service.submit_job(tmp_vcf, {"hgvs": True})

        assert result.job_id == "test-job-123"
        assert result.status == "queued"
        assert result.input_filename == "test.vcf"
        assert result.result_url == "/runs/test-job-123/result"

    @pytest.mark.asyncio
    async def test_submit_job_connection_error(self, vep_service, tmp_vcf):
        import httpx
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("services.vep_service.httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(httpx.ConnectError):
                await vep_service.submit_job(tmp_vcf)


class TestPollJob:
    @pytest.mark.asyncio
    async def test_poll_job_completed_immediately(self, vep_service):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "job_id": "test-job-123",
            "status": "completed",
            "result_url": "/runs/test-job-123/result",
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("services.vep_service.httpx.AsyncClient", return_value=mock_client):
            result = await vep_service.poll_job("test-job-123")

        assert result.status == "completed"

    @pytest.mark.asyncio
    async def test_poll_job_failed(self, vep_service):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "job_id": "test-job-123",
            "status": "failed",
            "error": "Processing error",
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("services.vep_service.httpx.AsyncClient", return_value=mock_client):
            result = await vep_service.poll_job("test-job-123")

        assert result.status == "failed"
        assert result.error == "Processing error"

    @pytest.mark.asyncio
    async def test_poll_job_timeout(self, vep_service):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "job_id": "test-job-123",
            "status": "running",
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("services.vep_service.httpx.AsyncClient", return_value=mock_client):
            with patch("services.vep_service.asyncio.sleep", new_callable=AsyncMock):
                result = await vep_service.poll_job("test-job-123")

        assert result.status == "timeout"


class TestGetResult:
    @pytest.mark.asyncio
    async def test_get_result_success(self, vep_service):
        mock_response = MagicMock()
        mock_response.text = "col1,col2\nval1,val2"
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("services.vep_service.httpx.AsyncClient", return_value=mock_client):
            result = await vep_service.get_result("/runs/test/result")

        assert "col1,col2" in result


class TestProcessVcf:
    @pytest.mark.asyncio
    async def test_process_vcf_disabled(self):
        with patch("services.vep_service.VEP_ENABLED", False):
            svc = VEPService()
            result = await svc.process_vcf("/tmp/test.vcf")
            assert result is None

    @pytest.mark.asyncio
    async def test_process_vcf_connection_failure(self, vep_service, tmp_vcf):
        import httpx
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("services.vep_service.httpx.AsyncClient", return_value=mock_client):
            result = await vep_service.process_vcf(tmp_vcf)

        assert result is None
