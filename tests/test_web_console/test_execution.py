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
    override_command = builder.build(
        descriptor, "test", TargetKind.FILE, "test_demo.py", RunOptions(),
        runtime_overrides={"BASE_URL": "http://override.example:8003"},
    )
    assert "test_demo.py" in file_command.argv
    assert "test_demo.py::test_ok" in node_command.argv
    assert node_command.environment["ENV"] == "dev"
    assert node_command.argv[-2:] == ("-n", "2")
    assert override_command.environment["BASE_URL"] == "http://override.example:8003"


def test_command_builder_executes_feature_as_exact_nodes(tmp_path: Path) -> None:
    descriptor = project(tmp_path)
    feature = tmp_path / "features" / "orders.feature"
    feature.parent.mkdir()
    feature.write_text("功能: 订单\n", encoding="utf-8")
    command = CommandBuilder("/usr/bin/python3").build(
        descriptor,
        "test",
        TargetKind.FEATURE,
        "features/orders.feature",
        RunOptions(),
        feature_nodes=(
            "test_demo.py::test_ok[first]",
            "test_demo.py::test_ok[second]",
        ),
    )

    assert command.argv[-2:] == (
        "test_demo.py::test_ok[first]",
        "test_demo.py::test_ok[second]",
    )


def test_command_builder_rejects_feature_without_collected_nodes(tmp_path: Path) -> None:
    descriptor = project(tmp_path)
    feature = tmp_path / "demo.feature"
    feature.write_text("功能: Demo\n", encoding="utf-8")
    with pytest.raises(ValueError, match="没有可执行"):
        CommandBuilder("/usr/bin/python3").build(
            descriptor, "test", TargetKind.FEATURE, "demo.feature", RunOptions()
        )


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
    assert [profile["id"] for profile in profiles] == ["test"]
    assert ProjectCatalog(repository_root).environment_ids("pytest_api") == ("test",)
    test_profile = profiles[0]
    assert test_profile["inherits"] == ""
    assert test_profile["summary"]["BASE_URL"] == "http://43.142.161.61:8003"
    assert all("PASSWORD" not in profile["summary"] for profile in profiles)
    runtime_options = {item["key"]: item for item in test_profile["runtime_options"]}
    assert runtime_options["BASE_URL"]["value"] == "http://43.142.161.61:8003"
    assert runtime_options["MOCK_TIMEOUT"]["value"] == "30"
    assert ProjectCatalog(repository_root).validate_runtime_overrides(
        "pytest_api", {"BASE_URL": "https://temporary.example", "MOCK_TIMEOUT": "60"}
    ) == {"BASE_URL": "https://temporary.example", "MOCK_TIMEOUT": "60"}


def test_catalog_rejects_undeclared_or_invalid_runtime_overrides() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    catalog = ProjectCatalog(repository_root)
    with pytest.raises(ValueError, match="不允许临时覆盖"):
        catalog.validate_runtime_overrides("pytest_api", {"PYTHONPATH": "/tmp/unsafe"})
    with pytest.raises(ValueError, match="http/https"):
        catalog.validate_runtime_overrides("pytest_api", {"BASE_URL": "file:///tmp/mock"})
    with pytest.raises(ValueError, match="超出允许范围"):
        catalog.validate_runtime_overrides("pytest_api", {"MOCK_TIMEOUT": "9999"})
