import warnings

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", message="Using `httpx` with `starlette.testclient` is deprecated.*")
    from fastapi.testclient import TestClient

from web_console.app import create_app
from web_console.config import WebConsoleSettings


def test_project_api_and_pages(tmp_path) -> None:
    repository_root = __import__("pathlib").Path(__file__).resolve().parents[2]
    settings = WebConsoleSettings(
        repository_root=repository_root,
        python_executable=repository_root / ".venv" / "bin" / "python",
        artifacts_root=tmp_path / "artifacts",
        database_path=tmp_path / "web.sqlite3",
    )
    with TestClient(create_app(settings)) as client:
        response = client.get("/api/projects")
        assert response.status_code == 200
        projects = response.json()
        assert {item["id"] for item in projects} >= {"simple_api", "bdd_api", "pytest_api"}
        pytest_api = next(item for item in projects if item["id"] == "pytest_api")
        assert [item["id"] for item in pytest_api["environments"]] == ["dev", "test", "pre", "prod"]
        assert client.get("/").status_code == 200
        assert client.get("/projects/pytest_api").status_code == 200
        assert client.get("/api/projects/pytest_api/source", params={"path": "../../AGENTS.md"}).status_code == 400
        assert client.post(
            "/api/projects/simple_api/collect", headers={"Origin": "https://attacker.example"}
        ).status_code == 403
