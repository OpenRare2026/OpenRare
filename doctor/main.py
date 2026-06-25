"""doctor CLI — runs all module health checks and prints a summary.

Usage:
    python -m doctor.main
    pixi run doctor
"""

import importlib.util
import sys
from pathlib import Path

from doctor.registry import MODULES
from doctor.core import worst_status
from doctor.report import format_module_line, format_detail

REPO_ROOT = Path(__file__).resolve().parent.parent


def run_module_check(module_name: str, check_relpath: str):
    check_path = REPO_ROOT / check_relpath
    if not check_path.exists():
        return [type("CheckResult", (), {
            "name": "check_file",
            "status": "error",
            "message": f"missing {check_relpath}",
        })()]

    spec = importlib.util.spec_from_file_location(
        f"modules.{module_name}.check", str(check_path)
    )
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:
        return [type("CheckResult", (), {
            "name": "check_import",
            "status": "error",
            "message": f"failed to load check.py: {exc}",
        })()]
    return mod.run_check()


def main():
    print("\n[OpenRare Doctor]\n")

    summary = {"ok": 0, "warn": 0, "error": 0}

    for label, check_path in MODULES.items():
        try:
            results = run_module_check(label, check_path)
        except Exception as exc:
            print(f"✖ {label:<24} (check crashed: {exc})")
            summary["error"] += 1
            continue

        status = worst_status(results)

        if status == "ok":
            summary["ok"] += 1
        elif status == "warn":
            summary["warn"] += 1
        else:
            summary["error"] += 1

        print(format_module_line(label, status))

        if status != "ok":
            print(format_detail(results))
            print()

    print("Summary:")
    print(f"  - {summary['ok']} modules ready")
    print(f"  - {summary['warn']} modules with warnings")
    print(f"  - {summary['error']} modules need attention")
    print()

    return 0 if summary["error"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
