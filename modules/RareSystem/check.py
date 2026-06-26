"""Health checks for the RareSystem full-stack genetic diagnosis module.

Checks: database config, VEP API, LLM config, HPO/PPI/Report API endpoints,
key service imports.
"""

import os
import sys
from pathlib import Path

try:
    from doctor.core import CheckResult
except ImportError:
    from dataclasses import dataclass

    @dataclass
    class CheckResult:
        name: str
        status: str
        message: str


_MODULE_DIR = Path(__file__).resolve().parent


def run_check():
    results = []

    # ── A. Code / import check (backend) ──
    backend_dir = _MODULE_DIR / "backend"
    if not backend_dir.exists():
        results.append(CheckResult(name="code", status="error", message="backend dir missing"))
        return results

    sys.path.insert(0, str(backend_dir))
    try:
        from main import app  # noqa: F401
        results.append(CheckResult(name="code", status="ok", message="backend main importable"))
    except ImportError as e:
        results.append(CheckResult(name="code", status="error", message=str(e)))
    finally:
        if str(backend_dir) in sys.path:
            sys.path.remove(str(backend_dir))

    # ── B. Database (PostgreSQL) ──
    db_url = os.environ.get("DATABASE_URL", "")
    if db_url:
        masked = db_url.replace(db_url.split("@")[0].split("://")[-1].split(":")[0], "***") if "@" in db_url else "***"
        results.append(CheckResult(name="database", status="ok", message=f"DATABASE_URL set ({masked})"))
    else:
        results.append(CheckResult(name="database", status="error", message="missing DATABASE_URL"))

    # ── C. VEP API ──
    vep_url = os.environ.get("VEP_API_BASE_URL", "")
    if vep_url:
        results.append(CheckResult(name="vep_api", status="ok", message=vep_url))
    else:
        results.append(CheckResult(name="vep_api", status="warn", message="VEP_API_BASE_URL not set"))

    vep_enabled = os.environ.get("VEP_ENABLED", "true").lower()
    results.append(CheckResult(name="vep_enabled", status="ok", message=f"VEP_ENABLED={vep_enabled}"))

    # ── D. LLM ──
    llm_key = os.environ.get("LLM_API_KEY", "")
    if llm_key and llm_key not in ("your-api-key-here", ""):
        results.append(CheckResult(name="llm_api_key", status="ok", message="LLM_API_KEY set"))
    else:
        results.append(CheckResult(name="llm_api_key", status="error", message="missing LLM_API_KEY"))

    llm_provider = os.environ.get("LLM_PROVIDER", "openai")
    llm_model = os.environ.get("LLM_MODEL", "gpt-4")
    results.append(CheckResult(name="llm_config", status="ok", message=f"provider={llm_provider}, model={llm_model}"))

    # ── E. Downstream services (optional but recommended) ──
    downstream = [
        ("hpo_api", "HPO_API_BASE_URL"),
        ("phenotype_hpo_api", "PHENOTYPE_HPO_API_BASE_URL"),
        ("ppi_score_api", "PPI_SCORE_API_BASE_URL"),
        ("report_api", "REPORT_API_BASE_URL"),
    ]
    for name, var in downstream:
        val = os.environ.get(var, "")
        if val:
            results.append(CheckResult(name=name, status="ok", message=val))
        else:
            results.append(CheckResult(name=name, status="warn", message=f"{var} not set"))

    # ── F. .env file presence ──
    env_file = _MODULE_DIR / "backend" / ".env"
    if env_file.exists():
        results.append(CheckResult(name="dotenv", status="ok", message=".env file present"))
    else:
        env_example = _MODULE_DIR / "backend" / ".env.example"
        if env_example.exists():
            results.append(CheckResult(
                name="dotenv",
                status="warn",
                message="no .env file; copy from .env.example"
            ))
        else:
            results.append(CheckResult(name="dotenv", status="error", message=".env file missing"))

    # ── G. Python ──
    pyver = f"{sys.version_info.major}.{sys.version_info.minor}"
    if (3, 12) <= sys.version_info < (3, 13):
        results.append(CheckResult(name="python", status="ok", message=f"Python {pyver}"))
    else:
        results.append(CheckResult(name="python", status="warn", message=f"Python {pyver} (3.12 expected)"))

    return results
