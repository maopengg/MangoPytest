"""核对目录层级、维护文件、内容与可执行标记；业务例外使用明确路径。"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import stat
import subprocess
from pathlib import Path


BUSINESS_FILES = {
    "README.md",
    "auto_tests/AGENTS.md",
    "auto_tests/project_registry.py",
    "docs/assets/test-cases/MangoMock_API功能测试用例.xlsx",
    "docs/assets/test-cases/MangoMock_UI全元素操作测试用例.xlsx",
}
BUSINESS_DIRECTORIES = (
    "auto_tests/api/simple_api/",
    "auto_tests/api/bdd_api/",
    "auto_tests/api/pytest_api/",
    "auto_tests/api/qfei_contract_api/",
    "auto_tests/api/qfei_contract_pytest/",
    "auto_tests/ui/simple_ui/",
    "auto_tests/ui/bdd_ui/",
    "auto_tests/ui/pytest_ui/",
    "auto_tests/ui/qfei_contract_ui/",
    "auto_tests/common/mango_mock/",
    "auto_tests/common/qfei_contract/",
    "auto_tests/other/sql/",
    "core/sources/workbooks/qfei_contract/",
)


def is_business(name: str) -> bool:
    return name in BUSINESS_FILES or any(
        name == prefix.rstrip("/") or name.startswith(prefix)
        for prefix in BUSINESS_DIRECTORIES
    )


def git_paths(root: Path, *options: str) -> set[str]:
    output = subprocess.check_output(["git", "ls-files", *options, "-z"], cwd=root)
    return {raw.decode("utf-8") for raw in output.split(b"\0") if raw}


def framework_inventory(root: Path) -> tuple[dict[str, dict], set[str]]:
    paths = git_paths(root, "--cached", "--others", "--exclude-standard")
    files = {}
    directories = set()
    for name in sorted(paths):
        if is_business(name):
            continue
        path = root / name
        if not path.exists() and not path.is_symlink():
            continue  # 删除中的文件由两边清单差异体现。
        info = path.lstat()
        link = stat.S_ISLNK(info.st_mode)
        data = os.readlink(path).encode("utf-8") if link else path.read_bytes()
        files[name] = {
            "kind": "symlink" if link else "file",
            "sha256": hashlib.sha256(data).hexdigest(),
            "executable": bool(info.st_mode & 0o111) if not link else False,
        }
        directories.update(parent.as_posix() for parent in Path(name).parents if parent != Path("."))

    # Git 不追踪空目录，另扫实际目录；排除 Git 自身及 Git 忽略的本地状态。
    ignored = {
        name.rstrip("/")
        for name in git_paths(root, "--others", "--ignored", "--exclude-standard", "--directory")
        if name.endswith("/")
    }
    for base, children, _ in os.walk(root, followlinks=False):
        kept = []
        for child in children:
            path = Path(base) / child
            name = path.relative_to(root).as_posix()
            if name == ".git" or name in ignored or is_business(name) or path.is_symlink():
                continue
            directories.add(name)
            kept.append(child)
        children[:] = kept
    return files, directories


def registry_framework_nodes(root: Path) -> list[str]:
    """注册表中仅项目声明与产品工作簿登记可不同，其余公共函数和选项继续比较。"""
    path = root / "auto_tests/project_registry.py"
    if not path.exists():
        return []
    nodes = []
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.ClassDef) and node.name == "ProjectEnum":
            continue
        if isinstance(node, ast.Assign):
            names = {target.id for target in node.targets if isinstance(target, ast.Name)}
            if names & {"DEFAULT_PROJECT", "PROJECT_REGISTRY"}:
                continue
            if all(
                isinstance(target, ast.Subscript)
                and isinstance(target.value, ast.Name)
                and target.value.id == "PRODUCT_WORKBOOKS"
                for target in node.targets
            ):
                continue
        if isinstance(node, ast.ImportFrom) and (
            (node.module == "pathlib" and [a.name for a in node.names] == ["Path"])
            or (node.module == "core.sources.ui_elements" and [a.name for a in node.names] == ["PRODUCT_WORKBOOKS"])
        ):
            continue
        nodes.append(ast.dump(node, include_attributes=False))
    return nodes


def compare_repositories(root: Path, upstream: Path) -> dict:
    local, local_dirs = framework_inventory(root)
    other, other_dirs = framework_inventory(upstream)
    return {
        "local": str(root),
        "upstream": str(upstream),
        "compared_files": len(local.keys() | other.keys()),
        "compared_directories": len(local_dirs | other_dirs),
        "compared_init_files": sum(name.endswith("/__init__.py") or name == "__init__.py" for name in local.keys() | other.keys()),
        "local_only": sorted(local.keys() - other.keys()),
        "upstream_only": sorted(other.keys() - local.keys()),
        "different": sorted(name for name in local.keys() & other.keys() if local[name] != other[name]),
        "local_only_directories": sorted(local_dirs - other_dirs),
        "upstream_only_directories": sorted(other_dirs - local_dirs),
        "registry_common_code_different": registry_framework_nodes(root) != registry_framework_nodes(upstream),
        "business_files": sorted(BUSINESS_FILES),
        "business_directories": list(BUSINESS_DIRECTORIES),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help="本地仓库路径，默认本脚本所在仓库")
    parser.add_argument("--upstream", required=True, type=Path, help="开源或待比对仓库路径")
    args = parser.parse_args()
    result = compare_repositories(args.root.expanduser().resolve(), args.upstream.expanduser().resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(any(result[key] for key in (
        "local_only", "upstream_only", "different", "local_only_directories",
        "upstream_only_directories", "registry_common_code_different",
    )))


if __name__ == "__main__":
    raise SystemExit(main())
