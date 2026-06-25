"""Health checks for the rare_sort FastAPI module.

This module has zero external dependencies — only code import matters.
"""

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

    # ── A. Code / import check (run from module dir) ──
    sys.path.insert(0, str(_MODULE_DIR))
    try:
        from main import app  # noqa: F401
        results.append(CheckResult(name="code", status="ok", message="main app importable"))
    except ImportError as e:
        results.append(CheckResult(name="code", status="error", message=str(e)))

    try:
        from _core import Contributor  # noqa: F401
        results.append(CheckResult(name="scoring_engine", status="ok", message="_core importable"))
    except ImportError as e:
        results.append(CheckResult(name="scoring_engine", status="error", message=str(e)))

    try:
        from pipeline import run  # noqa: F401
        results.append(CheckResult(name="pipeline", status="ok", message="pipeline importable"))
    except ImportError as e:
        results.append(CheckResult(name="pipeline", status="error", message=str(e)))

    try:
        from dataio import iter_chunks  # noqa: F401
        results.append(CheckResult(name="dataio", status="ok", message="dataio importable"))
    except ImportError as e:
        results.append(CheckResult(name="dataio", status="error", message=str(e)))
    finally:
        if str(_MODULE_DIR) in sys.path:
            sys.path.remove(str(_MODULE_DIR))

    # ── B. Platform compatibility (verified: needs linux-64 or osx-arm64) ──
    import platform as _plat
    machine = _plat.machine()
    system = _plat.system()
    if system == "Linux" or (system == "Darwin" and machine == "arm64"):
        results.append(CheckResult(name="platform", status="ok", message=f"{system} {machine}"))
    else:
        results.append(CheckResult(name="platform", status="warn", message=f"{system} {machine} — untested"))

    # ── C. Python ──
    pyver = f"{sys.version_info.major}.{sys.version_info.minor}"
    if sys.version_info >= (3, 11):
        results.append(CheckResult(name="python", status="ok", message=f"Python {pyver}"))
    else:
        results.append(CheckResult(name="python", status="warn", message=f"Python {pyver} (>=3.11 recommended)"))

    return results
