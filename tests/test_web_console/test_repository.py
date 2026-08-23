import json

from web_console.repository import RunRepository


def test_repository_persists_and_filters_runs(tmp_path) -> None:
    repository = RunRepository(tmp_path / "runs.sqlite3")
    repository.create({
        "id": "run-1", "project": "pytest_api", "project_kind": "api", "environment": "test",
        "target_kind": "project", "target": "", "options_json": json.dumps({"workers": 1}),
        "status": "queued", "created_at": "2026-01-01T00:00:00Z", "artifact_dir": str(tmp_path / "run-1"),
    })
    repository.update("run-1", status="passed", total=3, passed=3)
    record = repository.get("run-1")
    assert record["status"] == "passed"
    assert record["options"] == {"workers": 1}
    assert repository.list(project="pytest_api")[0]["passed"] == 3
