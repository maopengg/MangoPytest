"""跨仓库校验必须发现目录和初始化文件遗漏，业务例外不得遮蔽公共文件。"""
import json
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def repositories(tmp_path):
    roots = [tmp_path / "local", tmp_path / "upstream"]
    for root in roots:
        root.mkdir()
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        (root / ".gitignore").write_text("runtime/\n.venv/\n__pycache__/\n")
        (root / "core").mkdir()
        (root / "auto_tests/api").mkdir(parents=True)
        (root / "core/__init__.py").write_text('"""公共包。"""\n')
    return roots


def check(repositories):
    script = Path(__file__).resolve().parents[2] / "scripts/check_framework_alignment.py"
    result = subprocess.run(
        [sys.executable, str(script), "--root", str(repositories[0]), "--upstream", str(repositories[1])],
        capture_output=True, text=True, check=False,
    )
    return result.returncode, json.loads(result.stdout)


@pytest.mark.parametrize("difference", ["empty_directory", "init_content", "shared_init", "untracked", "file_kind", "executable", "shared_workbook", "registry_function"])
def test_alignment_rejects_public_structure_and_content_drift(repositories, difference):
    local, upstream = repositories
    if difference == "empty_directory":
        (local / "core/extra/nested").mkdir(parents=True)
    elif difference == "init_content":
        (local / "core/__init__.py").write_text('"""不同内容。"""\n')
    elif difference == "shared_init":
        (local / "auto_tests/other").mkdir(parents=True)
        (local / "auto_tests/other/__init__.py").touch()
    elif difference == "untracked":
        (local / "core/new.py").touch()
    elif difference == "file_kind":
        (local / "core/alias.py").symlink_to("__init__.py")
        (upstream / "core/alias.py").write_bytes((local / "core/__init__.py").read_bytes())
    elif difference == "executable":
        (local / "core/__init__.py").chmod(0o755)
    elif difference == "shared_workbook":
        for root in repositories:
            (root / "core/sources/workbooks/mock_ui").mkdir(parents=True)
            (root / "core/sources/workbooks/mock_ui/elements.xlsx").write_bytes(b"sample")
        (local / "core/sources/workbooks/mock_ui/elements.xlsx").write_bytes(b"changed")
    else:
        for root in repositories:
            (root / "auto_tests").mkdir(exist_ok=True)
            (root / "auto_tests/project_registry.py").write_text("DEFAULT_PROJECT = 'sample'\ndef enabled_projects():\n    return ()\n")
        (local / "auto_tests/project_registry.py").write_text("DEFAULT_PROJECT = 'company'\ndef enabled_projects():\n    return ('unexpected',)\n")
    code, report = check(repositories)
    assert code == 1, report


def test_alignment_accepts_explicit_business_and_ignored_runtime(repositories):
    local, _ = repositories
    (local / "auto_tests/api/qfei_contract_api").mkdir()
    (local / "auto_tests/api/qfei_contract_api/case.py").write_text("business = True\n")
    (local / "runtime/cache").mkdir(parents=True)
    (local / "runtime/cache/output.txt").write_text("local state")
    code, report = check(repositories)
    assert code == 0, report
    assert report["compared_init_files"] == 1
