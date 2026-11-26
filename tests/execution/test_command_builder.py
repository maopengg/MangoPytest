from pathlib import Path

import pytest

from core.execution.command_builder import CommandBuilder
from core.execution.models import ProjectDescriptor, RunOptions, TargetKind


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
