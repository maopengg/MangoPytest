"""控制台的 AI 自愈统计接口。"""

import json
from pathlib import Path

from web_console.config import WebConsoleSettings
from web_console.repository import RunRepository


def _build_settings(tmp_path: Path) -> WebConsoleSettings:
    repository_root = Path(__file__).resolve().parents[2]
    return WebConsoleSettings(
        repository_root=repository_root,
        python_executable=repository_root / ".venv" / "bin" / "python",
        artifacts_root=tmp_path / "artifacts",
        database_path=tmp_path / "web.sqlite3",
    )


def _insert_run(settings: WebConsoleSettings, run_id: str, artifact_dir: Path, tmp_path: Path) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    repository = RunRepository(settings.database_path)
    repository.create({
        "id": run_id, "project": "pytest_ui", "project_kind": "ui", "environment": "test",
        "target_kind": "project", "target": "", "options_json": "{}",
        "runtime_overrides_json": "{}", "status": "passed",
        "created_at": "2026-01-01T00:00:00Z", "artifact_dir": str(artifact_dir),
    })


def _client(settings: WebConsoleSettings):
    import warnings

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore", message="Using `httpx` with `starlette.testclient` is deprecated.*"
        )
        from fastapi.testclient import TestClient

    from web_console.app import create_app

    return TestClient(create_app(settings))


def test_ai_healing_endpoint_merges_worker_summaries(tmp_path: Path) -> None:
    settings = _build_settings(tmp_path)
    artifact_dir = tmp_path / "artifacts" / "reports" / "runs" / "run-1"
    _insert_run(settings, "run-1", artifact_dir, tmp_path)
    (artifact_dir / "ai-healing-summary-gw0.json").write_text(json.dumps({
        "operations": 5, "healed_operations": 2, "healed_successfully": 2,
        "healed_failed": 0, "ai_operations": 1, "ai_healed_successfully": 1,
        "local_healed": 1, "by_source": {"ai_accessibility": 1, "dom_text_candidate": 1},
        "by_element": {"submit-button": 1, "ui-file-input": 1},
        "models": ["glm-4"], "prompt_versions": ["web-snapshot-ref-v7"],
    }), encoding="utf-8")
    (artifact_dir / "ai-healing-summary-gw1.json").write_text(json.dumps({
        "operations": 3, "healed_operations": 1, "healed_successfully": 0,
        "healed_failed": 1, "ai_operations": 0, "ai_healed_successfully": 0,
        "local_healed": 1, "by_source": {"dom_proximity": 1},
        "by_element": {"submit-button": 1}, "models": [], "prompt_versions": [],
    }), encoding="utf-8")

    with _client(settings) as client:
        response = client.get("/api/runs/run-1/ai-healing")

    assert response.status_code == 200
    payload = response.json()
    assert payload["available"] is True
    assert payload["operations"] == 8
    assert payload["healed_operations"] == 3
    assert payload["healed_successfully"] == 2
    assert payload["healed_failed"] == 1
    assert payload["ai_operations"] == 1
    assert payload["local_healed"] == 2
    assert payload["by_element"] == {"submit-button": 2, "ui-file-input": 1}
    assert payload["models"] == ["glm-4"]


def test_ai_healing_endpoint_reports_unavailable_without_summary(tmp_path: Path) -> None:
    settings = _build_settings(tmp_path)
    artifact_dir = tmp_path / "artifacts" / "reports" / "runs" / "run-2"
    _insert_run(settings, "run-2", artifact_dir, tmp_path)

    with _client(settings) as client:
        response = client.get("/api/runs/run-2/ai-healing")
        missing = client.get("/api/runs/not-found/ai-healing")

    assert response.status_code == 200
    assert response.json() == {"available": False}
    assert missing.status_code == 404


def test_run_detail_page_wires_the_ai_healing_panel() -> None:
    """模板与脚本必须保留 AI 统计面板的接线，避免被前端改动悄悄移除。"""

    root = Path(__file__).resolve().parents[2]
    template = (root / "web_console" / "templates" / "run_detail.html").read_text(encoding="utf-8")
    script = (root / "web_console" / "static" / "app.js").read_text(encoding="utf-8")

    assert 'id="ai-healing-panel"' in template
    assert 'id="ai-healing-body"' in template
    assert 'id="ai-healing-state"' in template
    assert "function renderAiHealing(runId)" in script
    assert "renderAiHealing(run.id)" in script
    assert "/api/runs/${runId}/ai-healing" in script
