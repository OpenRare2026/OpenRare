"""Health checks for the pixi_report module.

Checks: API key, local data CSVs, optional Neo4j/Reactome connectivity, key imports.
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

    # ── A. Code / import check ──
    try:
        sys.path.insert(0, str(_MODULE_DIR))
        from api.main import app  # noqa: F401
        results.append(CheckResult(name="code", status="ok", message="api.main importable"))
    except ImportError as e:
        results.append(CheckResult(name="code", status="error", message=str(e)))
    finally:
        if str(_MODULE_DIR) in sys.path:
            sys.path.remove(str(_MODULE_DIR))

    # ── B. LLM API key (critical) ──
    api_key = os.environ.get("LLM_API_KEY", "")
    if api_key and api_key not in ("sk-...", "your-api-key-here", ""):
        results.append(CheckResult(name="api_key", status="ok", message="LLM_API_KEY set"))
    else:
        results.append(CheckResult(name="api_key", status="error", message="missing LLM_API_KEY"))

    llm_base = os.environ.get("LLM_BASE_URL", "")
    llm_model = os.environ.get("LLM_MODEL", "")
    results.append(CheckResult(
        name="llm_config",
        status="ok" if llm_base and llm_model else "warn",
        message=f"base={llm_base}, model={llm_model}" if llm_base else "LLM_BASE_URL or LLM_MODEL not set"
    ))

    # ── C. Local data files ──
    data_checks = [
        ("chictr_data", "data/Chictr/chictr.csv"),
        ("chinadrug_data", "data/ChinaDrug/chinadrugtrials.csv"),
    ]
    for name, relpath in data_checks:
        p = _MODULE_DIR / relpath
        if p.exists():
            results.append(CheckResult(name=name, status="ok", message=str(p)))
        else:
            results.append(CheckResult(name=name, status="error", message=f"missing: {p}"))

    # ── D. Optional: OMIM SQLite ──
    omim_db = os.environ.get("OMIM_DB_PATH", "./data/omim/omim_20250411.sqlite3")
    omim_path = Path(omim_db)
    if omim_path.exists():
        results.append(CheckResult(name="omim_db", status="ok", message=str(omim_path.resolve())))
    else:
        results.append(CheckResult(
            name="omim_db",
            status="warn",
            message=f"OMIM DB not found: {omim_db} (OMIM lookups will be skipped)"
        ))

    # ── E. Optional: Reactome Neo4j ──
    neo4j_uri = os.environ.get("REACTOME_NEO4J_URI", "")
    if neo4j_uri:
        results.append(CheckResult(name="reactome_neo4j", status="ok", message=neo4j_uri))
    else:
        reactome_enabled = os.environ.get("REACTOME_ENABLED", "1")
        if reactome_enabled == "1":
            results.append(CheckResult(
                name="reactome_neo4j",
                status="warn",
                message="REACTOME_NEO4J_URI not set (pathway enrichment will be skipped)"
            ))

    # ── F. Python ──
    pyver = f"{sys.version_info.major}.{sys.version_info.minor}"
    if (3, 11) <= sys.version_info < (3, 13):
        results.append(CheckResult(name="python", status="ok", message=f"Python {pyver}"))
    else:
        results.append(CheckResult(name="python", status="warn", message=f"Python {pyver} (3.11-3.12 expected)"))

    return results
