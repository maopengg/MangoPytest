from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class TargetKind(str, Enum):
    PROJECT = "project"
    FILE = "file"
    NODE = "node"


class RunStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    CANCELLED = "cancelled"
    INTERRUPTED = "interrupted"


FINAL_STATUSES = {RunStatus.PASSED, RunStatus.FAILED, RunStatus.ERROR, RunStatus.CANCELLED, RunStatus.INTERRUPTED}


@dataclass(frozen=True, slots=True)
class ProjectDescriptor:
    id: str
    name: str
    kind: str
    root: Path
    enabled: bool
    reason: str = ""


@dataclass(frozen=True, slots=True)
class RunOptions:
    markers: tuple[str, ...] = ()
    keyword: str = ""
    workers: int = 1
    reruns: int = 0
    max_failures: int = 0
    collect_only: bool = False
    extra_args: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RunCommand:
    argv: tuple[str, ...]
    cwd: Path
    environment: dict[str, str]
    display: str
