"""全量功能用例的标准化执行结果。"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FunctionalCaseResult:
    case_id: str
    status_code: int = 200
    code: int = 0
    checks: list[bool] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)
