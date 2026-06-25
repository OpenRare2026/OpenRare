"""Protocol definition for module health checks."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class CheckResult:
    name: str
    status: str  # "ok" | "warn" | "error"
    message: str

    def is_ok(self) -> bool:
        return self.status == "ok"

    def is_error(self) -> bool:
        return self.status == "error"

    def is_warn(self) -> bool:
        return self.status == "warn"


def worst_status(results: List[CheckResult]) -> str:
    statuses = {r.status for r in results}
    if "error" in statuses:
        return "error"
    if "warn" in statuses:
        return "warn"
    return "ok"
