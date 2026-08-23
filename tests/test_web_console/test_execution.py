from pathlib import Path

import pytest

from core.execution.command_builder import CommandBuilder
from core.execution.catalog import ProjectCatalog
from core.execution.models import ProjectDescriptor, RunOptions, TargetKind
from core.execution.result_parser import parse_failures, parse_junit, status_from_exit_code


def project(tmp_path: Path) -> ProjectDescriptor:
    test_file = tmp_path / "test_demo.py"
    test_file.write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    return ProjectDescriptor("demo", "Demo", "api", tmp_path, True)


def test_command_builder_accepts_project_file_and_node(tmp_path: Path) -> None:
    descriptor = project(tmp_path)
    builder = CommandBuilder("/usr/bin/python3")
    file_command = builder.build(descriptor, "test", TargetKind.FILE, "test_demo.py", RunOptions())
    node_command = builder.build(descriptor, "dev", TargetKind.NODE, "test_demo.py::test_ok", RunOptions(workers=2))
    assert "test_demo.py" in file_command.argv
    assert "test_demo.py::test_ok" in node_command.argv
    assert node_command.environment["ENV"] == "dev"
    assert node_command.argv[-2:] == ("-n", "2")


@pytest.mark.parametrize("target", ["../test_demo.py", "/tmp/test_demo.py", "not_test.py"])
def test_command_builder_rejects_unsafe_target(tmp_path: Path, target: str) -> None:
    descriptor = project(tmp_path)
    with pytest.raises(ValueError):
        CommandBuilder("/usr/bin/python3").build(descriptor, "test", TargetKind.FILE, target, RunOptions())


def test_junit_parser_and_exit_status(tmp_path: Path) -> None:
    report = tmp_path / "junit.xml"
    report.write_text('<testsuites><testsuite tests="5" failures="1" errors="1" skipped="1"/></testsuites>')
    assert parse_junit(report) == {"total": 5, "passed": 2, "failed": 1, "errors": 1, "skipped": 1}
    assert status_from_exit_code(0).value == "passed"
    assert status_from_exit_code(5).value == "error"


def test_junit_failure_details(tmp_path: Path) -> None:
    report = tmp_path / "junit.xml"
    report.write_text(
        '<testsuite tests="1" failures="1"><testcase classname="tests.auth" name="test_login">'
        '<failure message="expected 200">assert 500 == 200</failure></testcase></testsuite>',
        encoding="utf-8",
    )
    assert parse_failures(report) == [{
        "name": "test_login", "classname": "tests.auth",
        "message": "expected 200", "traceback": "assert 500 == 200",
    }]


def test_catalog_discovers_project_environment_profiles() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    profiles = ProjectCatalog(repository_root).environment_profiles("pytest_api")
    assert [profile["id"] for profile in profiles] == ["dev", "test", "pre", "prod"]
    test_profile = next(profile for profile in profiles if profile["id"] == "test")
    assert test_profile["inherits"] == "prod"
    assert test_profile["summary"]["BASE_URL"] == "http://43.142.161.61:8003"
    assert all("PASSWORD" not in profile["summary"] for profile in profiles)
