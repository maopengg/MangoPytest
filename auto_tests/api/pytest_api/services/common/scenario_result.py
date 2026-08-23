"""Service 层统一返回的可诊断场景结果。"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ScenarioResult:
    checks: dict[str, bool]
    details: dict[str, Any] = field(default_factory=dict)

    def failed_checks(self) -> list[str]:
        return [name for name, passed in self.checks.items() if not passed]
