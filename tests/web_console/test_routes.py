"""通过真实路由验证任务、事件流、报告和产物边界。"""

import json
import time

from fastapi.testclient import TestClient

from web_console.app import create_app
from .factories import seed_run


def test_reports_events_and_artifacts_share_the_same_run(console_settings, tmp_path):
    app = create_app(console_settings)
    directory = seed_run(app.state.services, console_settings)
    app.state.services.repository.update(
        "run-example", runtime_overrides_json=json.dumps({"AI_API_KEY": "sk-1234567890abcdef"})
    )
    outside = tmp_path / "outside.txt"
    outside.write_text("outside")
    (directory / "outside-link.txt").symlink_to(outside)
    with TestClient(app) as client:
        detail = client.get("/api/runs/run-example").json()
        projects = client.get("/api/projects").json()
        latest = next(project for project in projects if project["id"] == "sample_ui")["latest"]
        cancelled = client.post("/api/runs/run-example/cancel").json()
        for record in (detail, latest, cancelled):
            assert record["runtime_overrides"]["AI_API_KEY"] == "sk-1********cdef"
        assert app.state.services.repository.get("run-example")["runtime_overrides"]["AI_API_KEY"] == "sk-1234567890abcdef"
        report = client.get("/api/runs/run-example/allure").json()
        assert report["summary"]["total"] == 1
        assert report["tests"][0]["name"] == "UI-001 验证提交操作"
        assert client.get("/api/runs/run-example/ai-healing").json() == {"available": False}
        assert client.get("/api/runs/run-example/failures").json() == []
        artifacts = client.get("/api/runs/run-example/artifacts").json()
        assert "example.txt" in {item["path"] for item in artifacts}
        assert client.get("/api/runs/run-example/preview/example.txt").text == "example artifact"
        download = client.get("/api/runs/run-example/artifacts/example.txt")
        assert download.status_code == 200
        assert "attachment" in download.headers["content-disposition"]
        assert client.get("/api/runs/run-example/artifacts/outside-link.txt").status_code == 404
        assert client.get("/api/runs/run-example/preview/%2e%2e%2foutside.txt").status_code == 404
        events = client.get("/api/runs/run-example/events")
        assert "example output" in events.text
        assert 'event: end\ndata: {"status": "passed"}' in events.text
        for suffix in ("allure", "failures", "ai-healing", "artifacts", "events"):
            assert client.get(f"/api/runs/missing/{suffix}").status_code == 404


def wait_for_run(client, run_id, *, status=None):
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        record = client.get(f"/api/runs/{run_id}").json()
        if record["status"] == status or record["status"] in {
            "passed", "failed", "error", "cancelled", "interrupted",
        }:
            return record
        time.sleep(0.05)
    raise AssertionError(f"执行记录未完成：{record}")


def test_collect_execute_and_rerun_temporary_project(
    console_settings, repository_root, monkeypatch,
):
    monkeypatch.setenv("PYTHONPATH", str(repository_root))
    monkeypatch.setenv("MANGO_PYTEST_RUNTIME_DIR", str(console_settings.runtime_root))
    with TestClient(create_app(console_settings)) as client:
        collected = client.post("/api/projects/sample_api/collect")
        assert collected.status_code == 200, collected.text
        assert collected.json()["count"] == 1
        cases = client.get("/api/projects/sample_api/cases", params={"q": "test_ok"}).json()
        assert len(cases) == 1
        tree = client.get("/api/projects/sample_api/tree").json()
        assert any(item["path"] == "test_sample.py" and item["executable"] for item in tree)
        created = client.post("/api/runs", json={"project": "sample_api"})
        assert created.status_code == 201, created.text
        run_id = created.json()["id"]
        result = wait_for_run(client, run_id)
        assert result["status"] == "passed", result
        assert result["total"] == result["passed"] == 1
        assert "event: end" in client.get(f"/api/runs/{run_id}/events").text
        rerun = client.post(f"/api/runs/{run_id}/rerun")
        assert rerun.status_code == 201
        assert rerun.json()["id"] != run_id
        assert wait_for_run(client, rerun.json()["id"])["status"] == "passed"


def test_cancel_running_subprocess(console_settings, repository_root, monkeypatch):
    monkeypatch.setenv("PYTHONPATH", str(repository_root))
    monkeypatch.setenv("MANGO_PYTEST_RUNTIME_DIR", str(console_settings.runtime_root))
    project = console_settings.repository_root / "auto_tests/sample_api"
    (project / "test_sample.py").write_text(
        "import time\ndef test_wait():\n    time.sleep(30)\n"
    )
    with TestClient(create_app(console_settings)) as client:
        created = client.post("/api/runs", json={"project": "sample_api"}).json()
        running = wait_for_run(client, created["id"], status="running")
        assert running["status"] == "running", running
        cancelled = client.post(f"/api/runs/{created['id']}/cancel")
        assert cancelled.status_code == 200
        assert cancelled.json()["status"] == "cancelled"
