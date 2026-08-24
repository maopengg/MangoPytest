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
        assert [item["id"] for item in pytest_api["environments"]] == ["test"]
        dashboard_html = client.get("/").text
        assert 'id="global-api-loading"' in dashboard_html
        assert "loadProjects(this)" in dashboard_html
        assert "loadRuns(true,this)" in dashboard_html
        assert client.get("/projects/pytest_api").status_code == 200
        project_script = client.get("/static/app.js").text
        assert "const RUN_PAGE_SIZE=20" in project_script
        assert "function setupRunInfiniteScroll()" in project_script
        assert "function beginApiLoading()" in project_script
        assert "function setButtonLoading(button,loading,label='加载中')" in project_script
        assert "offset=${runsOffset}" in project_script
        assert "selectedFileExecutionKind" in project_script
        assert "(c.name||'').toLowerCase().includes(q)" in project_script
        assert "c.markers||[]" in project_script
        console_styles = client.get("/static/app.css").text
        assert ".case-detail-head{position:sticky;top:0" in console_styles
        assert ".report-shell{overflow:clip}" in console_styles
        assert ".report-anchor{height:100vh;height:100dvh}" in console_styles
        assert ".report-shell.is-pinned{position:fixed;top:0" in console_styles
        assert ".report-shell>#tab-cases.active{display:flex;flex-direction:column}" in console_styles
        assert ".allure-layout{position:static;top:auto;height:auto" in console_styles
        assert ".report-shell.is-pinned .allure-case-list" in console_styles
        assert "function setupReportSticky()" in project_script
        assert "function setupProjectExplorerSticky()" in project_script
        assert "function selectInitialProjectFile(tree)" in project_script
        assert "await selectInitialProjectFile(tree)" in project_script
        assert "renderCaseCards" not in project_script
        assert "shell.classList.toggle('is-pinned'" in project_script
        assert "renderCollapsibleSection('完整执行步骤'" in project_script
        assert "renderCollapsibleSection('其他附件'" in project_script
        assert "renderCollapsibleSection('Fixture 前后置'" in project_script
        assert "renderLogSection(e.logs)" in project_script
        assert "function renderLogSection(items=[])" in project_script
        assert "function groupUiOperations(items=[])" in project_script
        assert "function renderUiOperations(items=[])" in project_script
        assert "renderUiOperations(e.operations)" in project_script
        assert "element_reference:'元素引用'" in project_script
        assert "match_count:'匹配数量'" in project_script
        assert "function renderCollapsibleSection(title,content,count=0,open=false)" in project_script
        assert "activeRunProjectKind=run.project_kind||''" in project_script
        assert "function renderAuxiliaryApiSection(requests=[],responses=[])" in project_script
        assert "不代表该用例属于 API 自动化" in project_script
        assert "onclick=\"filterEvidence('all',this)\"" in project_script
        assert "function filterEvidence(kind,button)" in project_script
        assert "data-evidence-kind=\"${kind}\"" in project_script
        assert "function scrollRunToTop()" in project_script
        assert "function allureHierarchyParts(item,mode)" in project_script
        assert "function buildAllureSuiteTree(items,mode)" in project_script
        assert "function renderAllureTreeNode(node,depth,expandAll)" in project_script
        assert "function revealAllureCaseRow(id)" in project_script
        run_template = (repository_root / "web_console" / "templates" / "run_detail.html").read_text()
        assert 'class="result-grid"' not in run_template
        assert 'id="back-to-top"' in run_template
        assert 'class="report-anchor"' in run_template
        assert 'id="allure-group-mode"' in run_template
        assert '<option value="behavior" selected>' in run_template
        assert '<option value="suite">' in run_template
        project_template = (repository_root / "web_console" / "templates" / "project.html").read_text()
        assert 'class="explorer-anchor"' in project_template
        assert 'class="project-title-line"' in project_template
        assert "setupProjectExplorerSticky()" in project_template
        assert 'id="back-to-top"' in project_template
        assert ".allure-case-list{flex:1 1 auto;min-height:0;max-height:none;overflow-y:hidden" in console_styles
        assert ".allure-case-detail{height:100%;min-height:0;overflow-y:hidden" in console_styles
        assert ".report-shell.is-pinned .allure-case-list,.report-shell.is-pinned .allure-case-detail" in console_styles
        assert client.get("/api/runs/not-found/allure").status_code == 404
        assert client.get("/api/projects/pytest_api/source", params={"path": "../../AGENTS.md"}).status_code == 400
        assert client.post(
            "/api/projects/simple_api/collect", headers={"Origin": "https://attacker.example"}
        ).status_code == 403
        assert client.post("/api/runs", json={
            "project": "simple_api", "environment": "prod", "production_confirmation": "simple_api",
            "target": {"type": "project", "id": ""}, "options": {},
        }).status_code == 400
        assert client.post("/api/runs", json={
            "project": "simple_api", "environment": "test",
            "target": {"type": "project", "id": ""},
            "runtime_overrides": {"PYTHONPATH": "/tmp/unsafe"}, "options": {},
        }).status_code == 400
