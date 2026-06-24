import os
import tempfile

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from services.vep_service import VEPService


VEP_CSV_RESULT = """## VEP output
#Uploaded_variation,Location,Allele,Gene,Feature,Consequence,HGVSc,HGVSp,Impact,SIFT,PolyPhen,CADD_PHRED,gnomADe_AF,CLIN_SIG
1_12345_A_G,1:12345,G,BRCA1,ENST0001,missense_variant,c.123A>G,p.Lys41Arg,MODERATE,deleterious(0.01),probably_damaging(0.95),25.3,0.00001,Uncertain_significance
2_67890_C_T,2:67890,T,TP53,ENST0002,stop_gained,c.678C>T,p.Tyr226*,HIGH,tolerated(0.5),benign(0.1),35.1,0.00005,Pathogenic
"""


@pytest.fixture
def tmp_vcf():
    with tempfile.NamedTemporaryFile(suffix=".vcf", delete=False) as f:
        f.write(b"##fileformat=VCFv4.1\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n1\t12345\t.\tA\tG\t30\tPASS\t.\n2\t67890\t.\tC\tT\t50\tPASS\t.\n")
        path = f.name
    yield path
    os.unlink(path)


class TestFullVEPFlow:
    @pytest.mark.asyncio
    async def test_process_vcf_full_flow(self, tmp_vcf):
        svc = VEPService(base_url="http://test-vep:8000", max_retries=3, poll_interval=1)

        submit_resp = MagicMock()
        submit_resp.json.return_value = {
            "job_id": "job-int-001",
            "status": "queued",
            "result_url": "/runs/job-int-001/result",
            "log_url": "/runs/job-int-001/log",
        }
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.json.return_value = {
            "job_id": "job-int-001",
            "status": "completed",
            "result_url": "/runs/job-int-001/result",
        }
        poll_resp.raise_for_status = MagicMock()

        result_resp = MagicMock()
        result_resp.text = VEP_CSV_RESULT
        result_resp.raise_for_status = MagicMock()

        call_count = {"n": 0}

        async def mock_get(url, **kwargs):
            if "/runs/job-int-001/result" in url:
                return result_resp
            call_count["n"] += 1
            return poll_resp

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=submit_resp)
        mock_client.get = AsyncMock(side_effect=mock_get)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("services.vep_service.httpx.AsyncClient", return_value=mock_client):
            with patch("services.vep_service.VEP_ENABLED", True):
                variants = await svc.process_vcf(tmp_vcf, {"hgvs": True})

        assert variants is not None
        assert len(variants) == 2

        v1 = variants[0]
        assert v1.chromosome == "1"
        assert v1.position == 12345
        assert v1.gene == "BRCA1"
        assert v1.impact == "MODERATE"
        assert v1.hgvs_c == "c.123A>G"
        assert v1.hgvs_p == "p.Lys41Arg"
        assert v1.cadd == 25.3
        assert v1.clinvar_significance == "Uncertain_significance"

        v2 = variants[1]
        assert v2.chromosome == "2"
        assert v2.gene == "TP53"
        assert v2.impact == "HIGH"
        assert v2.clinvar_significance == "Pathogenic"

    @pytest.mark.asyncio
    async def test_process_vcf_job_fails_returns_none(self, tmp_vcf):
        svc = VEPService(base_url="http://test-vep:8000", max_retries=3, poll_interval=1)

        submit_resp = MagicMock()
        submit_resp.json.return_value = {
            "job_id": "job-fail-001",
            "status": "queued",
            "result_url": "/runs/job-fail-001/result",
        }
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.json.return_value = {
            "job_id": "job-fail-001",
            "status": "failed",
            "error": "Out of memory",
        }
        poll_resp.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=submit_resp)
        mock_client.get = AsyncMock(return_value=poll_resp)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("services.vep_service.httpx.AsyncClient", return_value=mock_client):
            with patch("services.vep_service.VEP_ENABLED", True):
                result = await svc.process_vcf(tmp_vcf)

        assert result is None

    @pytest.mark.asyncio
    async def test_process_vcf_timeout_returns_none(self, tmp_vcf):
        svc = VEPService(base_url="http://test-vep:8000", max_retries=3, poll_interval=1)

        submit_resp = MagicMock()
        submit_resp.json.return_value = {
            "job_id": "job-timeout-001",
            "status": "queued",
            "result_url": "/runs/job-timeout-001/result",
        }
        submit_resp.raise_for_status = MagicMock()

        poll_resp = MagicMock()
        poll_resp.json.return_value = {
            "job_id": "job-timeout-001",
            "status": "running",
        }
        poll_resp.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=submit_resp)
        mock_client.get = AsyncMock(return_value=poll_resp)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch("services.vep_service.httpx.AsyncClient", return_value=mock_client):
            with patch("services.vep_service.VEP_ENABLED", True):
                with patch("services.vep_service.asyncio.sleep", new_callable=AsyncMock):
                    result = await svc.process_vcf(tmp_vcf)

        assert result is None
