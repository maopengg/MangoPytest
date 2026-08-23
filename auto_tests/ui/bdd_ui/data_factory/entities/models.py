"""BDD UI 前置数据实体。"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RunData:
    run_id: str
    cleanup_token: str
    token: str
    user: dict[str, Any]


@dataclass(frozen=True)
class OrderData:
    id: int
    status: str
    raw: dict[str, Any]


@dataclass(frozen=True)
class ClaimData:
    id: int
    status: str
    raw: dict[str, Any]


@dataclass(frozen=True)
class ReviewData:
    id: int
    status: str
    raw: dict[str, Any]
