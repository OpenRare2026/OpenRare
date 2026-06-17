from __future__ import annotations

import shutil
import uuid
from pathlib import Path
from typing import Optional


def resolve_path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    return path.resolve()


def safe_upload_name(filename: str | None) -> str:
    name = Path(filename or "input.vcf").name
    name = name.replace("/", "_").replace("\\", "_")
    if not name or name in {".", ".."}:
        name = "input.vcf"
    return name


def save_upload(upload_file, upload_dir: Path) -> Path:
    upload_dir.mkdir(parents=True, exist_ok=True)
    target = upload_dir / safe_upload_name(upload_file.filename)
    if target.exists():
        stem = target.stem
        suffix = "".join(target.suffixes) or ""
        if suffix and stem.endswith(suffix):
            stem = stem[: -len(suffix)]
        target = upload_dir / f"{stem}.{uuid.uuid4().hex[:8]}{suffix}"
    with target.open("wb") as dst:
        shutil.copyfileobj(upload_file.file, dst)
    return target.resolve()
