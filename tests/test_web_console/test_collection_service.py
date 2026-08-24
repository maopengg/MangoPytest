import json
from pathlib import Path
from types import SimpleNamespace

from web_console.collection_service import CollectionService
from web_console.pytest_plugin import COLLECTION_SCHEMA_VERSION, _bdd_source


def test_bdd_source_resolves_feature_file_and_scenario_line(tmp_path: Path) -> None:
    test_file = tmp_path / "test_cases" / "grpc" / "test_grpc.py"
    feature_file = tmp_path / "features" / "grpc" / "grpc.feature"
    test_file.parent.mkdir(parents=True)
    feature_file.parent.mkdir(parents=True)
    test_file.write_text("def test_grpc(): pass\n", encoding="utf-8")
    feature_file.write_text("功能: gRPC\n", encoding="utf-8")
    scenario = SimpleNamespace(
        feature=SimpleNamespace(filename=str(feature_file)),
        line_number=7,
        name="FTAPI-0140 调用 UnaryEcho",
    )
    item = SimpleNamespace(obj=SimpleNamespace(__scenario__=scenario), name="test_ftapi_0140")

    assert _bdd_source(item, tmp_path, test_file) == (
        feature_file, 7, "FTAPI-0140 调用 UnaryEcho"
    )


def test_tree_maps_feature_to_exact_feature_execution_target(tmp_path: Path) -> None:
    project_root = tmp_path / "bdd_api"
    feature_file = project_root / "features" / "grpc" / "grpc.feature"
    test_file = project_root / "test_cases" / "grpc" / "test_grpc.py"
    feature_file.parent.mkdir(parents=True)
    test_file.parent.mkdir(parents=True)
    feature_file.write_text("功能: gRPC\n", encoding="utf-8")
    test_file.write_text("def test_ftapi_0140(): pass\n", encoding="utf-8")
    settings = SimpleNamespace(artifacts_root=tmp_path / "artifacts")
    catalog = SimpleNamespace(get=lambda *args, **kwargs: SimpleNamespace(root=project_root))
    service = CollectionService(settings, catalog)
    service.cache_path("bdd_api").parent.mkdir(parents=True)
    service.cache_path("bdd_api").write_text(json.dumps({
        "schema_version": COLLECTION_SCHEMA_VERSION,
        "count": 2,
        "cases": [{
            "file": "features/grpc/grpc.feature",
            "test_file": "test_cases/grpc/test_grpc.py",
            "node_id": "test_cases/grpc/test_grpc.py::test_unary",
        }, {
            "file": "features/grpc/grpc.feature",
            "test_file": "test_cases/grpc/test_grpc.py",
            "node_id": "test_cases/grpc/test_grpc.py::test_stream",
        }],
    }), encoding="utf-8")

    tree = {item["path"]: item for item in service.tree("bdd_api")}
    assert tree["features/grpc/grpc.feature"] == {
        "path": "features/grpc/grpc.feature",
        "count": 2,
        "executable": True,
        "execution_kind": "feature",
        "execution_target": "features/grpc/grpc.feature",
        "type": "feature",
    }
    assert service.feature_nodes("bdd_api", "features/grpc/grpc.feature") == (
        "test_cases/grpc/test_grpc.py::test_unary",
        "test_cases/grpc/test_grpc.py::test_stream",
    )


def test_read_rejects_stale_collection_cache(tmp_path: Path) -> None:
    settings = SimpleNamespace(artifacts_root=tmp_path / "artifacts")
    service = CollectionService(settings, SimpleNamespace())
    service.cache_path("demo").parent.mkdir(parents=True)
    service.cache_path("demo").write_text(
        json.dumps({"schema_version": COLLECTION_SCHEMA_VERSION - 1, "count": 99, "cases": []}),
        encoding="utf-8",
    )

    assert service.read("demo") == {
        "count": 0, "cases": [], "collected": False, "stale": True,
    }
