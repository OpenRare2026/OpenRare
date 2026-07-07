from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

META_PATH_FIELDS = (
    "liftover_path",
    "vcf_path",
    "wide_table_path",
    "gene_disease_path",
    "ppi_path",
    "report_path",
)


def _normalize_slashes(value: str) -> str:
    return value.replace("\\", "/")


def contains_absolute_path(value: str) -> bool:
    text = (value or "").strip()
    if not text:
        return False
    return Path(text).is_absolute()


def normalize_stored_path(
    value: str,
    *,
    root: Path | None = None,
    anchor: Path | None = None,
) -> str:
    """Return a module-root-relative path suitable for JSON / report storage."""
    text = (value or "").strip()
    if not text:
        return ""

    path = Path(text)
    base = (root or PROJECT_ROOT).resolve()

    try:
        if path.is_absolute():
            resolved = path.resolve()
        elif anchor is not None:
            resolved = (anchor.resolve() / path).resolve()
        else:
            return _normalize_slashes(text)

        return _normalize_slashes(str(resolved.relative_to(base)))
    except ValueError:
        if path.is_absolute():
            return _normalize_slashes(str(resolved))
        return _normalize_slashes(text)
    except OSError:
        if path.is_absolute():
            return _normalize_slashes(str(path))
        return path.name or text


def resolve_module_path(value: str, *, root: Path | None = None) -> Path:
    """Resolve a stored or API-relative path to an absolute filesystem path."""
    text = (value or "").strip()
    if not text:
        raise ValueError("Path is empty")

    path = Path(text)
    base = (root or PROJECT_ROOT).resolve()
    if path.is_absolute():
        return path.resolve()
    return (base / path).resolve()


def format_report_path(value: str, *, root: Path | None = None) -> str:
    """Format a filesystem path for human-readable report output."""
    text = (value or "").strip()
    if not text:
        return ""

    path = Path(text)
    base = (root or PROJECT_ROOT).resolve()
    if path.is_absolute():
        try:
            return _normalize_slashes(str(path.resolve().relative_to(base)))
        except ValueError:
            return path.name
    return _normalize_slashes(text)


def assert_no_absolute_paths_in_text(text: str, *, label: str = "report") -> None:
    """Raise if text appears to contain absolute filesystem paths."""
    for line in text.splitlines():
        stripped = line.strip().strip('"')
        if not stripped.startswith("/"):
            continue
        if stripped.startswith("//") or stripped.startswith("http://") or stripped.startswith("https://"):
            continue
        if "/" in stripped[1:]:
            raise ValueError(f"{label} contains absolute path: {stripped[:120]}")
