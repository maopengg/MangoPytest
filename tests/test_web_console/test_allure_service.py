import json

from web_console.allure_service import AllureResultService


def write_json(path, value) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def test_allure_report_contains_cases_steps_fixtures_and_safe_attachments(tmp_path) -> None:
    results = tmp_path / "allure-results"
    results.mkdir()
    (results / "request.txt").write_text("token=top-secret request body", encoding="utf-8")
    write_json(results / "case-result.json", {
        "uuid": "case-1", "historyId": "history-1", "name": "登录失败", "fullName": "tests.auth#test_login",
        "status": "failed", "start": 1000, "stop": 1250,
        "statusDetails": {"message": "expected 200", "trace": "password=unsafe\nassert 500 == 200"},
        "labels": [
            {"name": "parentSuite", "value": "tests.auth"}, {"name": "suite", "value": "test_login"},
            {"name": "feature", "value": "登录"}, {"name": "tag", "value": "negative"},
        ],
        "parameters": [{"name": "username", "value": "AUTO_USER"}],
        "steps": [{"name": "发送登录请求", "status": "passed", "start": 1010, "stop": 1100}],
        "attachments": [{"name": "request", "source": "request.txt", "type": "text/plain"}],
    })
    write_json(results / "fixture-container.json", {
        "children": ["case-1"], "befores": [{"name": "api_client", "status": "passed", "start": 900, "stop": 950}]
    })

    report = AllureResultService(tmp_path).report()
    assert report["summary"] == {
        "total": 1, "passed": 0, "failed": 1, "broken": 0, "skipped": 0, "unknown": 0,
        "start": 1000, "stop": 1250, "duration_ms": 250,
    }
    case = report["tests"][0]
    assert case["feature"] == "登录"
    assert case["steps"][0]["name"] == "发送登录请求"
    assert case["fixtures"]["befores"][0]["name"] == "api_client"
    assert "top-secret" not in case["attachments"][0]["content"]
    assert "unsafe" not in case["status_details"]["trace"]


def test_allure_report_handles_missing_results(tmp_path) -> None:
    assert AllureResultService(tmp_path).report()["available"] is False
