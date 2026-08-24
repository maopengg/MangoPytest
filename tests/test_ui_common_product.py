from pathlib import Path

from auto_tests.common.mango_mock import HttpResult
from auto_tests.common.mango_mock.repositories import MangoMockRepositories


class FakeHttpClient:
    def __init__(self, base_url: str, timeout: int):
        self.base_url = base_url
        self.timeout = timeout
        self.created_name = ""
        self.closed = False

    def create_run(self, name: str, ttl_minutes: int) -> HttpResult:
        self.created_name = name
        return HttpResult(
            201,
            {"data": {"id": "run-1", "cleanup_token": "cleanup-1"}},
            {},
        )

    def delete_run_with_cleanup_token(
        self, run_id: str, cleanup_token: str
    ) -> HttpResult:
        assert (run_id, cleanup_token) == ("run-1", "cleanup-1")
        return HttpResult(200, {"data": {}}, {})

    def close(self) -> None:
        self.closed = True


def test_ui_demos_share_one_product_workbook():
    workbook_dir = (
        Path(__file__).resolve().parents[1]
        / "core"
        / "sources"
        / "workbooks"
        / "mock_ui"
    )

    assert [file.name for file in workbook_dir.glob("*.xlsx")] == [
        "mock_ui_elements.xlsx"
    ]


def test_common_repository_keeps_project_run_prefix(monkeypatch):
    import auto_tests.common.mango_mock.repositories.context as context_module

    monkeypatch.setattr(context_module, "HttpProtocolClient", FakeHttpClient)
    repositories = MangoMockRepositories(
        "http://mock.local",
        timeout=12,
        run_name_prefix="AUTO_BDD_UI",
    )

    repositories.test_runs.ensure()
    client = repositories.context.http
    assert client.created_name.startswith("AUTO_BDD_UI_")
    assert repositories.run_id == "run-1"

    repositories.close()
    assert repositories.deleted is True
    assert client.closed is True
