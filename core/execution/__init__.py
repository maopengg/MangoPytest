"""CLI 与 Web 控制台共享的 pytest 执行能力。"""

from core.execution.catalog import ProjectCatalog
from core.execution.command_builder import CommandBuilder
from core.execution.models import ProjectDescriptor, RunCommand, RunOptions, RunStatus, TargetKind

__all__ = ["CommandBuilder", "ProjectCatalog", "ProjectDescriptor", "RunCommand", "RunOptions", "RunStatus", "TargetKind"]
