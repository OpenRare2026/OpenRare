"""Health checks for the RAG-HPO module.

Checks: API key, CHPO dictionary, embedding model availability, key imports.
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
        sys.path.insert(0, str(_MODULE_DIR / "src"))
        from server import app  # noqa: F401
        results.append(CheckResult(name="code", status="ok", message="server importable"))
    except ImportError as e:
        results.append(CheckResult(name="code", status="error", message=str(e)))
    finally:
        if str(_MODULE_DIR / "src") in sys.path:
            sys.path.remove(str(_MODULE_DIR / "src"))

    # ── B. LLM API key (critical) ──
    api_key = os.environ.get("RAG_HPO_API_KEY", "")
    if api_key and api_key not in ("your-api-key-here", "sk-...", ""):
        results.append(CheckResult(name="api_key", status="ok", message="RAG_HPO_API_KEY set"))
    else:
        results.append(CheckResult(name="api_key", status="error", message="missing RAG_HPO_API_KEY"))

    base_url = os.environ.get("RAG_HPO_BASE_URL", "https://api.groq.com/openai/v1/chat/completions")
    results.append(CheckResult(name="base_url", status="ok", message=base_url))

    model = os.environ.get("RAG_HPO_MODEL", "llama3-groq-70b-8192-tool-use-preview")
    results.append(CheckResult(name="model", status="ok", message=model))

    # ── C. Required data files ──
    chpo = _MODULE_DIR / "chpo_dict.csv"
    if chpo.exists():
        results.append(CheckResult(name="chpo_dict", status="ok", message=str(chpo)))
    else:
        results.append(CheckResult(name="chpo_dict", status="error", message=f"missing: {chpo}"))

    prompts = _MODULE_DIR / "system_prompts.json"
    if prompts.exists():
        results.append(CheckResult(name="prompts", status="ok", message=str(prompts)))
    else:
        results.append(CheckResult(name="prompts", status="error", message=f"missing: {prompts}"))

    # ── D. Vector DB files (built via pixi run build-db) ──
    meta_path = os.environ.get("RAG_HPO_META_PATH", f"{_MODULE_DIR}/src/data/hpo_meta.json")
    vec_path = os.environ.get("RAG_HPO_VEC_PATH", f"{_MODULE_DIR}/src/data/hpo_embedded.npz")
    for name, path in [("vector_db_meta", meta_path), ("vector_db_emb", vec_path)]:
        if Path(path).exists():
            results.append(CheckResult(name=name, status="ok", message=path))
        else:
            results.append(CheckResult(
                name=name,
                status="error",
                message=f"missing: {path} — run 'pixi run build-db' first"
            ))

    # ── E. Python ──
    pyver = f"{sys.version_info.major}.{sys.version_info.minor}"
    if sys.version_info >= (3, 10):
        results.append(CheckResult(name="python", status="ok", message=f"Python {pyver}"))
    else:
        results.append(CheckResult(name="python", status="error", message=f"Python {pyver} (>=3.10 required)"))

    return results
