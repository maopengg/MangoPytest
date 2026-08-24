import json

from web_console.allure_service import AllureResultService


def write_json(path, value) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def test_allure_report_contains_cases_steps_fixtures_and_safe_attachments(tmp_path) -> None:
    results = tmp_path / "allure-results"
    results.mkdir()
    (results / "request.txt").write_text("token=top-secret request body", encoding="utf-8")
    (results / "case.json").write_text('{"case_id":"API-001","name":"test_login"}', encoding="utf-8")
    (results / "response.json").write_text('{"status":401,"body":{"code":"INVALID"}}', encoding="utf-8")
    write_json(results / "case-result.json", {
        "uuid": "case-1", "historyId": "history-1", "name": "登录失败", "fullName": "tests.auth#test_login",
        "status": "failed", "start": 1000, "stop": 1250,
        "statusDetails": {"message": "expected 200", "trace": "password=unsafe\nassert 500 == 200"},
        "labels": [
            {"name": "parentSuite", "value": "tests.auth"}, {"name": "suite", "value": "test_login"},
            {"name": "epic", "value": "API 自动化"},
            {"name": "feature", "value": "登录"},
            {"name": "story", "value": "密码认证"},
            {"name": "tag", "value": "negative"},
        ],
        "parameters": [{"name": "username", "value": "AUTO_USER"}],
        "steps": [{"name": "发送登录请求", "status": "passed", "start": 1010, "stop": 1100}],
        "attachments": [
            {"name": "request", "source": "request.txt", "type": "text/plain"},
            {"name": "Case 信息", "source": "case.json", "type": "application/json"},
            {"name": "响应信息", "source": "response.json", "type": "application/json"},
        ],
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
    assert case["epic"] == "API 自动化"
    assert case["story"] == "密码认证"
    assert case["steps"][0]["name"] == "发送登录请求"
    assert case["fixtures"]["befores"][0]["name"] == "api_client"
    assert "top-secret" in case["attachments"][0]["content"]
    assert "unsafe" in case["status_details"]["trace"]
    assert case["evidence"]["case"][0]["data"]["case_id"] == "API-001"
    assert case["evidence"]["responses"][0]["data"]["status"] == 401


def test_allure_report_handles_missing_results(tmp_path) -> None:
    assert AllureResultService(tmp_path).report()["available"] is False


def test_allure_report_infers_feature_for_legacy_unclassified_case(tmp_path) -> None:
    results = tmp_path / "allure-results"
    results.mkdir()
    write_json(results / "case-result.json", {
        "uuid": "case-1", "name": "旧版简单 API 用例",
        "fullName": "test_cases.simple_api.test_simple_api#test_create_run",
        "status": "passed", "start": 1000, "stop": 1100,
        "labels": [{"name": "suite", "value": "test_simple_api"}],
    })

    case = AllureResultService(tmp_path).report()["tests"][0]
    assert case["feature"] == "Simple API"


def test_allure_report_prefers_stderr_when_pytest_log_is_duplicated(tmp_path) -> None:
    results = tmp_path / "allure-results"
    results.mkdir()
    (results / "log.txt").write_text("DEBUG test.py:10 request -> 200", encoding="utf-8")
    (results / "stderr.txt").write_text("[DEBUG] request -> 200", encoding="utf-8")
    write_json(results / "case-result.json", {
        "uuid": "case-1", "name": "重复日志", "status": "passed", "start": 1000, "stop": 1100,
        "attachments": [
            {"name": "log", "source": "log.txt", "type": "text/plain"},
            {"name": "stderr", "source": "stderr.txt", "type": "text/plain"},
        ],
    })

    logs = AllureResultService(tmp_path).report()["tests"][0]["evidence"]["logs"]
    assert [item["name"] for item in logs] == ["stderr"]
    assert logs[0]["content"] == "[DEBUG] request -> 200"


def test_allure_report_extracts_data_lineage(tmp_path) -> None:
    results = tmp_path / "allure-results"
    results.mkdir()
    graph = {"version": 1, "nodes": [{"id": "factory-1"}], "edges": []}
    (results / "lineage.json").write_text(json.dumps(graph), encoding="utf-8")
    write_json(results / "case-result.json", {
        "uuid": "case-1", "name": "数据工厂用例", "status": "passed", "start": 1000, "stop": 1100,
        "attachments": [
            {"name": "数据血缘", "source": "lineage.json", "type": "application/json"},
        ],
    })

    lineage = AllureResultService(tmp_path).report()["tests"][0]["evidence"]["lineage"]
    assert lineage[0]["data"] == graph


def test_allure_report_preserves_response_step_and_fixture_phase(tmp_path) -> None:
    results = tmp_path / "allure-results"
    results.mkdir()
    (results / "created.json").write_text('{"status":201}', encoding="utf-8")
    (results / "deleted.json").write_text('{"status":200}', encoding="utf-8")
    write_json(results / "case-result.json", {
        "uuid": "case-1", "name": "隔离运行", "status": "passed", "start": 1000, "stop": 1100,
        "steps": [{
            "name": "HTTP POST /api/v1/test-runs", "status": "passed", "start": 1000, "stop": 1050,
            "attachments": [{"name": "响应信息", "source": "created.json", "type": "application/json"}],
        }],
    })
    write_json(results / "fixture-container.json", {
        "children": ["case-1"], "afters": [{
            "name": "HTTP DELETE /api/v1/test-runs/run-1", "status": "passed", "start": 1100, "stop": 1150,
            "attachments": [{"name": "响应信息", "source": "deleted.json", "type": "application/json"}],
        }],
    })

    responses = AllureResultService(tmp_path).report()["tests"][0]["evidence"]["responses"]
    assert [(item["context"], item["phase"]) for item in responses] == [
        ("HTTP POST /api/v1/test-runs", ""),
        ("HTTP DELETE /api/v1/test-runs/run-1", "清理"),
    ]
