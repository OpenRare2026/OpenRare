"""Shared check helpers — avoid repetitive exists/os.environ boilerplate."""

import os
from pathlib import Path
from doctor.core import CheckResult


def check_path(name: str, path: str | Path, label: str = "") -> CheckResult:
    p = Path(path) if isinstance(path, str) else path
    display = label or str(p)
    if p.exists():
        return CheckResult(name=name, status="ok", message=display)
    return CheckResult(name=name, status="error", message=f"missing: {display}")


def check_env(name: str, var: str) -> CheckResult:
    val = os.environ.get(var)
    if val:
        return CheckResult(name=name, status="ok", message=f"{var} set")
    return CheckResult(name=name, status="error", message=f"missing {var}")


def check_import(name: str, module: str) -> CheckResult:
    try:
        __import__(module)
        return CheckResult(name=name, status="ok", message=f"{module} importable")
    except ImportError as e:
        return CheckResult(name=name, status="error", message=str(e))
