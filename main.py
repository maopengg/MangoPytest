"""从仓库根目录独立运行任一自动化 Demo。"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

from auto_tests.project_registry import PROJECT_REGISTRY, enabled_projects
from core.execution import CommandBuilder, ProjectCatalog, RunOptions, TargetKind


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(description="运行 Mango Pytest 自动化 Demo")
    parser.add_argument("--project", choices=(*enabled_projects(), "all"), default="pytest_api")
    parser.add_argument(
        "--env",
        choices=("dev", "test", "pre", "prod"),
        default=os.getenv("ENV", "test").lower(),
        help="默认 test；生产环境必须显式指定",
    )
    parser.add_argument("--collect-only", action="store_true")
    parser.add_argument("--list-projects", action="store_true")
    return parser.parse_known_args()


def list_projects() -> None:
    catalog = ProjectCatalog()
    for name, config in PROJECT_REGISTRY.items():
        state = "enabled" if config["enabled"] else f"disabled: {config['reason']}"
        environments = ",".join(catalog.environment_ids(name)) or "-"
        print(f"{name:12} {config['path']:24} {state:36} env={environments}")


def run_project(name: str, env_name: str, collect_only: bool, extra: list[str]) -> int:
    catalog = ProjectCatalog()
    project = catalog.get(name)
    allowed_environments = catalog.environment_ids(name)
    if env_name not in allowed_environments:
        allowed = ", ".join(allowed_environments) or "无"
        raise ValueError(f"项目 {name} 未注册环境 {env_name}；可用环境: {allowed}")
    command = CommandBuilder(sys.executable).build(
        project, env_name, TargetKind.PROJECT, "",
        RunOptions(collect_only=collect_only, extra_args=tuple(arg for arg in extra if arg != "--")),
    )
    print(f"\n[{name}] ENV={env_name} ROOT={project.root}")
    return subprocess.run(command.argv, cwd=command.cwd, env=command.environment, check=False).returncode


def main() -> int:
    args, pytest_args = parse_args()
    if args.list_projects:
        list_projects()
        return 0
    projects = enabled_projects() if args.project == "all" else (args.project,)
    result = 0
    for project in projects:
        try:
            project_result = run_project(
                project, args.env, args.collect_only, pytest_args
            )
        except ValueError as exc:
            print(f"配置错误: {exc}", file=sys.stderr)
            return 2
        result = max(result, project_result)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
