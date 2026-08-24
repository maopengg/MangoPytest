from __future__ import annotations

import os
from pathlib import Path
import re
import shlex

from core.execution.models import ProjectDescriptor, RunCommand, RunOptions, TargetKind

_SAFE_EXPRESSION = re.compile(r"^[\w\s.():\[\]{}'\"=!<>&|,+\-/*]+$", re.UNICODE)


class CommandBuilder:
    def __init__(self, python_executable: Path | str) -> None:
        # 不能 resolve：.venv/bin/python 通常是符号链接，解析后会丢失虚拟环境语义。
        self.python_executable = str(Path(python_executable).absolute())

    def build(self, project: ProjectDescriptor, environment: str, target_kind: TargetKind, target: str,
              options: RunOptions, *, junit_path: Path | None = None, allure_dir: Path | None = None,
              runtime_overrides: dict[str, str] | None = None,
              feature_nodes: tuple[str, ...] = ()) -> RunCommand:
        environment = environment.lower()
        if environment not in {"dev", "test", "pre", "prod"}:
            raise ValueError(f"不支持的环境: {environment}")
        argv = [self.python_executable, "-m", "pytest"]
        resolved_targets = self._validate_targets(project, target_kind, target, feature_nodes)
        argv.extend(resolved_targets)
        if options.collect_only:
            argv.append("--collect-only")
        if options.markers:
            expression = " and ".join(options.markers)
            self._validate_expression(expression, "marker")
            argv.extend(("-m", expression))
        if options.keyword:
            self._validate_expression(options.keyword, "keyword")
            argv.extend(("-k", options.keyword))
        if not 1 <= options.workers <= 16:
            raise ValueError("并发数必须在 1 到 16 之间")
        if options.workers > 1:
            argv.extend(("-n", str(options.workers)))
        if not 0 <= options.reruns <= 10:
            raise ValueError("失败重跑次数必须在 0 到 10 之间")
        if options.reruns:
            argv.extend(("--reruns", str(options.reruns)))
        if not 0 <= options.max_failures <= 1000:
            raise ValueError("失败停止数量必须在 0 到 1000 之间")
        if options.max_failures:
            argv.extend(("--maxfail", str(options.max_failures)))
        if junit_path:
            argv.append(f"--junitxml={junit_path.resolve()}")
        if allure_dir:
            argv.append(f"--alluredir={allure_dir.resolve()}")
        argv.extend(options.extra_args)
        process_env = os.environ.copy()
        process_env["ENV"] = environment
        process_env.update(runtime_overrides or {})
        repository_root = str(project.root.parents[2])
        process_env["PYTHONPATH"] = os.pathsep.join(filter(None, (repository_root, process_env.get("PYTHONPATH", ""))))
        return RunCommand(tuple(argv), project.root, process_env, shlex.join(argv))

    @staticmethod
    def _validate_expression(value: str, label: str) -> None:
        if len(value) > 300 or not _SAFE_EXPRESSION.fullmatch(value):
            raise ValueError(f"{label} 表达式包含不允许的字符")

    @staticmethod
    def _validate_targets(
        project: ProjectDescriptor,
        kind: TargetKind,
        target: str,
        feature_nodes: tuple[str, ...],
    ) -> tuple[str, ...]:
        if kind is TargetKind.PROJECT:
            if target:
                raise ValueError("项目执行不能指定 target")
            return ()
        if not target or "\x00" in target:
            raise ValueError("测试目标不能为空")
        if kind is TargetKind.FEATURE:
            candidate = Path(target)
            if candidate.is_absolute():
                raise ValueError("测试目标必须是项目内相对路径")
            resolved = (project.root / candidate).resolve()
            if (
                not resolved.is_relative_to(project.root)
                or not resolved.is_file()
                or resolved.suffix != ".feature"
            ):
                raise ValueError("Feature 目标不存在或超出项目目录")
            if not feature_nodes:
                raise ValueError("Feature 目标没有可执行的 pytest 节点")
            nodes = tuple(dict.fromkeys(
                CommandBuilder._validate_targets(project, TargetKind.NODE, node, ())[0]
                for node in feature_nodes
            ))
            return nodes
        file_part = target.split("::", 1)[0]
        candidate = Path(file_part)
        if candidate.is_absolute():
            raise ValueError("测试目标必须是项目内相对路径")
        resolved = (project.root / candidate).resolve()
        if not resolved.is_relative_to(project.root) or not resolved.is_file():
            raise ValueError("测试目标不存在或超出项目目录")
        if resolved.suffix != ".py" or not resolved.name.startswith("test_"):
            raise ValueError("只能执行 pytest 测试文件")
        relative = resolved.relative_to(project.root).as_posix()
        if kind is TargetKind.FILE:
            if "::" in target:
                raise ValueError("文件目标不能包含 node ID")
            return (relative,)
        if kind is TargetKind.NODE and "::" in target:
            return (relative + "::" + target.split("::", 1)[1],)
        raise ValueError("单用例目标必须是完整 pytest node ID")
