#!/usr/bin/env python3
"""Path-sandbox regression tests for the full pipeline API (issue #17).

Run standalone (no pytest needed):

    python test/test_path_sandbox.py

Each case drives the real FastAPI app through TestClient and asserts that a
request path escaping the configured roots is rejected, while the equivalent
in-sandbox request is still accepted.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

PIPELINE_ROOT = Path(__file__).resolve().parents[1]

# Point the sandbox at a scratch tree before importing the app, so the test
# never touches a real deployment's data directories.
_TMP = tempfile.mkdtemp(prefix="openrare_sandbox_test_")
DATA_ROOT = Path(_TMP) / "data"
JOBS_DIR = Path(_TMP) / "jobs"
OUTSIDE = Path(_TMP) / "outside"
for d in (DATA_ROOT, JOBS_DIR, OUTSIDE):
    d.mkdir(parents=True, exist_ok=True)
# resolve() after mkdir so comparisons match the app's resolved paths
# (on Windows tempfile hands back an 8.3 short path).
DATA_ROOT, JOBS_DIR, OUTSIDE = (d.resolve() for d in (DATA_ROOT, JOBS_DIR, OUTSIDE))

os.environ["FULL_PIPELINE_API_JOBS_DIR"] = str(JOBS_DIR)
os.environ["FULL_PIPELINE_API_OUTPUT_ROOT"] = str(JOBS_DIR)
os.environ["FULL_PIPELINE_API_ALLOWED_ROOTS"] = str(DATA_ROOT)

sys.path.insert(0, str(PIPELINE_ROOT))
from fastapi.testclient import TestClient  # noqa: E402

from complete_pipeline import full_pipeline_api as api  # noqa: E402

SECRET = OUTSIDE / "secret.txt"
SECRET.write_text("patient genome, not yours\n", encoding="utf-8")
IN_SANDBOX_VCF = DATA_ROOT / "sample.vcf"
IN_SANDBOX_VCF.write_text("##fileformat=VCFv4.2\n", encoding="utf-8")

client = TestClient(api.app)
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name} {detail}")
        FAILURES.append(name)


def base_body(**overrides) -> dict:
    body = {"input_vcf": str(IN_SANDBOX_VCF), "dry_run": True}
    body.update(overrides)
    return body


print("\n[1] input_vcf outside the allowed roots is rejected")
r = client.post("/run", json=base_body(input_vcf=str(SECRET)))
check("absolute path outside roots -> 400", r.status_code == 400, r.text[:200])

r = client.post("/run", json=base_body(input_vcf=f"{DATA_ROOT}/../outside/secret.txt"))
check("'..' traversal out of an allowed root -> 400", r.status_code == 400, r.text[:200])

print("\n[2] output_dir cannot escape the output root")
r = client.post("/run", json=base_body(output_dir=str(OUTSIDE / "pwned")))
check("output_dir outside output root -> 400", r.status_code == 400, r.text[:200])
check(
    "no directory was created outside the root",
    not (OUTSIDE / "pwned").exists(),
)

print("\n[3] executable paths are no longer request fields")
fields = set(api.RunRequest.model_fields)
check("java_bin removed from RunRequest", "java_bin" not in fields)
check("beagle_jar removed from RunRequest", "beagle_jar" not in fields)
r = client.post("/run", json=base_body(java_bin="/tmp/evil.sh", beagle_jar="/tmp/evil.jar"))
# Extra keys are ignored by the model; what matters is that neither reaches the command.
if r.status_code in (200, 202):
    job = r.json()["job_id"]
    cmd = " ".join(api.read_status(job)["command"])
    check("--java-bin absent from built command", "--java-bin" not in cmd, cmd)
    check("--beagle-jar absent from built command", "--beagle-jar" not in cmd, cmd)
    check("evil.sh never appears in the command", "evil.sh" not in cmd, cmd)
else:
    check("submitting the removed fields is at least not accepted", r.status_code == 400, r.text[:200])

print("\n[4] other data-path overrides are sandboxed too")
for field in ("ref_dir", "ccre_bed", "ncrna_bed", "genos_evee_db"):
    r = client.post("/run", json=base_body(**{field: str(OUTSIDE)}))
    check(f"{field} outside roots -> 400", r.status_code == 400, r.text[:200])

print("\n[5] job_id cannot walk out of the jobs directory")
for bad in ("../../etc", "..", "not-a-uuid", "0" * 31, "g" * 32):
    r = client.get(f"/jobs/{bad}")
    check(f"job_id={bad!r} -> 404", r.status_code == 404, r.text[:120])

print("\n[6] a legitimate in-sandbox request still works")
r = client.post("/run", json=base_body())
check("in-sandbox submit accepted", r.status_code in (200, 202), r.text[:200])
if r.status_code in (200, 202):
    payload = r.json()
    out = Path(payload["output_dir"]).resolve()
    check("default output_dir lands under the jobs dir", api._is_within(out, JOBS_DIR), str(out))
    r2 = client.post("/run", json=base_body(output_dir=str(JOBS_DIR / "custom_out")))
    check("explicit output_dir inside the root accepted", r2.status_code in (200, 202), r2.text[:200])

print("\n[7] file download cannot be aimed outside the output root")
status_file = JOBS_DIR / ("f" * 32) / "status.json"
status_file.parent.mkdir(parents=True, exist_ok=True)
status_file.write_text(f'{{"status": "succeeded", "output_dir": "{OUTSIDE.as_posix()}"}}', encoding="utf-8")
r = client.get(f"/jobs/{'f' * 32}/files")
check("legacy job pointing outside the root -> 403", r.status_code == 403, r.text[:200])
r = client.get(f"/jobs/{'f' * 32}/files/secret.txt")
check("downloading through such a job -> 403", r.status_code == 403, r.text[:200])
check("secret contents never returned", "not yours" not in r.text)

print()
if FAILURES:
    print(f"{len(FAILURES)} check(s) FAILED: {', '.join(FAILURES)}")
    sys.exit(1)
print("all path-sandbox checks passed")
