#!/usr/bin/env python3
"""Start the API on the dedicated Pixi port and create runtime paths lazily."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import uvicorn


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from path_config import load_paths  # noqa: E402


def main() -> None:
    paths = load_paths()
    log_dir = paths.runtime_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "api-7773.log"
    pid_file = paths.runtime_root / "api-7773.pid"
    pid_file.write_text(f"{os.getpid()}\n")
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"},
            "access": {"format": "%(asctime)s %(levelname)s %(client_addr)s - \"%(request_line)s\" %(status_code)s"},
        },
        "handlers": {
            "console": {"class": "logging.StreamHandler", "formatter": "default", "stream": "ext://sys.stderr"},
            "file": {"class": "logging.FileHandler", "formatter": "default", "filename": str(log_file)},
            "access_file": {"class": "logging.FileHandler", "formatter": "access", "filename": str(log_file)},
        },
        "loggers": {
            "uvicorn": {"handlers": ["console", "file"], "level": "INFO", "propagate": False},
            "uvicorn.error": {"level": "INFO"},
            "uvicorn.access": {"handlers": ["console", "access_file"], "level": "INFO", "propagate": False},
        },
    }
    try:
        uvicorn.run(
            "phenotype_hpo_score_api:app",
            app_dir=str(SRC_DIR),
            host="0.0.0.0",
            port=7773,
            log_config=log_config,
        )
    finally:
        pid_file.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
