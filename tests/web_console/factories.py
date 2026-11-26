"""控制台测试使用的临时执行记录，不装配任何业务项目。"""

import json


def seed_run(services, settings, run_id="run-example"):
    directory = settings.runtime_root / "reports/runs" / run_id
    directory.mkdir(parents=True, exist_ok=True)
    services.repository.create({
        "id": run_id, "project": "sample_ui", "project_kind": "ui", "environment": "test",
        "target_kind": "project", "target": "", "options_json": "{}",
        "runtime_overrides_json": "{}", "status": "passed", "total": 1, "passed": 1,
        "created_at": "2026-01-01T00:00:00Z", "artifact_dir": str(directory),
    })
    results = directory / "allure-results"
    results.mkdir()
    (results / "example-result.json").write_text(json.dumps({
        "uuid": "case-example", "name": "UI-001 验证提交操作", "status": "passed",
        "fullName": "sample.test_submit", "start": 1000, "stop": 1200,
        "labels": [{"name": "epic", "value": "示例产品"},
                   {"name": "feature", "value": "表单"}],
    }, ensure_ascii=False))
    (directory / "example.txt").write_text("example artifact", encoding="utf-8")
    services.events.write(services.repository.get(run_id), "log", "example output")
    return directory
