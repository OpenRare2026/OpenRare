"""Human-readable report formatting."""

from doctor.core import CheckResult


def format_module_line(label: str, status: str) -> str:
    if status == "ok":
        icon = "✔"
        suffix = "(ready)"
    elif status == "warn":
        icon = "⚠"
        suffix = "(warnings)"
    else:
        icon = "✖"
        suffix = "(needs attention)"
    return f"{icon} {label:<24} {suffix}"


def format_detail(results: list[CheckResult], indent: int = 4) -> str:
    lines = []
    prefix = " " * indent
    for r in results:
        if r.status == "ok":
            lines.append(f"{prefix}  ok  {r.name}: {r.message}")
        elif r.status == "warn":
            lines.append(f"{prefix} warn {r.name}: {r.message}")
        else:
            lines.append(f"{prefix} FAIL {r.name}: {r.message}")
    return "\n".join(lines)
