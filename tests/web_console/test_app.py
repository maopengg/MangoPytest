import warnings
from .assets import read_static_assets, contains
with warnings.catch_warnings():
    warnings.filterwarnings('ignore', message='Using `httpx` with `starlette.testclient` is deprecated.*')
    from fastapi.testclient import TestClient
from web_console.app import create_app

def test_project_api_and_pages(tmp_path, repository_root, console_settings) -> None:
    settings = console_settings
    with TestClient(create_app(settings)) as client:
        response = client.get('/api/projects')
        assert response.status_code == 200
        projects = response.json()
        assert {item['id'] for item in projects} >= {'sample_api', 'sample_bdd', 'sample_secondary_api'}
        sample_secondary_api = next((item for item in projects if item['id'] == 'sample_secondary_api'))
        assert [item['id'] for item in sample_secondary_api['environments']] == ['test']
        dashboard_html = client.get('/').text
        assert 'id="global-api-loading"' in dashboard_html
        assert '/static/css/app.css?v=20261126-1' in dashboard_html
        assert '/static/js/app.js?v=20261126-1' in dashboard_html
        assert 'loadProjects(this)' in dashboard_html
        assert 'loadRuns(true,this)' in dashboard_html
        assert client.get('/projects/sample_secondary_api').status_code == 200
        project_script = '\n'.join(read_static_assets(client, '/static/js/app.js').values())
        assert contains(project_script, 'const RUN_PAGE_SIZE=20')
        assert contains(project_script, 'function setupRunInfiniteScroll()')
        assert contains(project_script, 'function beginApiLoading()')
        assert contains(project_script, "function setButtonLoading(button,loading,label='加载中')")
        assert contains(project_script, 'offset=${runsOffset}')
        assert contains(project_script, 'selectedFileExecutionKind')
        assert contains(project_script, 'selectedFileCollectionState')
        assert contains(project_script, '未被 pytest 收集')
        assert contains(project_script, 'data-collection-state')
        assert contains(project_script, "(c.name||'').toLowerCase().includes(q)")
        assert contains(project_script, 'c.markers||[]')
        style_response = client.get('/static/css/app.css')
        assert style_response.headers['cache-control'] == 'no-cache, must-revalidate'
        console_styles = '\n'.join(read_static_assets(client, '/static/css/app.css').values())
        assert contains(console_styles, '.case-detail-head{position:sticky;top:0')
        assert contains(console_styles, '.report-shell{overflow:clip}')
        assert contains(console_styles, '.report-anchor{height:100vh;height:100dvh}')
        assert contains(console_styles, '.report-shell.is-pinned{position:fixed;top:0')
        assert contains(console_styles, '.report-shell>#tab-cases.active{display:flex;flex-direction:column}')
        assert contains(console_styles, '.allure-layout{position:static;top:auto;height:auto')
        assert contains(console_styles, '.report-shell.is-pinned .allure-case-list')
        assert contains(project_script, 'function setupReportSticky()')
        assert contains(project_script, 'function setupProjectExplorerSticky()')
        assert contains(project_script, 'function selectInitialProjectFile(tree)')
        assert contains(project_script, 'await selectInitialProjectFile(tree)')
        assert not contains(project_script, 'renderCaseCards')
        assert contains(project_script, "shell.classList.toggle('is-pinned'")
        assert contains(project_script, "renderCollapsibleSection('完整执行步骤'")
        assert contains(project_script, "renderCollapsibleSection('其他附件'")
        assert contains(project_script, "renderCollapsibleSection('Fixture 前后置'")
        assert contains(project_script, 'renderLogSection(e.logs)')
        assert contains(project_script, 'function renderLogSection(items=[])')
        assert contains(project_script, 'function groupUiOperations(items=[])')
        assert contains(project_script, 'function renderUiOperations(items=[])')
        assert contains(project_script, 'renderUiOperations(e.operations)')
        assert contains(project_script, 'named=input.named_elements?.[0]?.name')
        assert contains(project_script, "named_elements:'元素仓库信息'")
        assert contains(console_styles, '.ui-operation-detail{display:grid;grid-template-columns:1fr;')
        assert not contains(console_styles, '.ui-operation-detail{display:grid;grid-template-columns:1fr 1fr;')
        assert contains(project_script, "element_reference:'元素引用'")
        assert contains(project_script, "match_count:'匹配数量'")
        assert contains(project_script, 'function renderCollapsibleSection(title,content,count=0,open=false)')
        assert contains(project_script, "projectKind:run.project_kind||''")
        assert contains(project_script, 'function renderAuxiliaryApiSection(requests=[],responses=[])')
        assert contains(project_script, '不代表该用例属于 API 自动化')
        assert contains(project_script, 'onclick="filterEvidence(\'all\',this)"')
        assert contains(project_script, 'function filterEvidence(kind,button)')
        assert contains(project_script, 'data-evidence-kind="${kind}"')
        assert contains(project_script, 'function scrollRunToTop()')
        assert contains(project_script, 'function allureHierarchyParts(item,mode)')
        assert contains(project_script, 'function buildAllureSuiteTree(items,mode)')
        assert contains(project_script, 'function renderAllureTreeNode(node,depth,expandAll)')
        assert contains(project_script, 'function revealAllureCaseRow(id)')
        run_template = (repository_root / 'web_console' / 'templates' / 'pages' / 'run_detail.html').read_text()
        assert 'class="result-grid"' not in run_template
        assert 'id="back-to-top"' in run_template
        assert 'class="report-anchor"' in run_template
        assert 'id="allure-group-mode"' in run_template
        assert '<option value="behavior" selected>' in run_template
        assert '<option value="suite">' in run_template
        project_template = (repository_root / 'web_console' / 'templates' / 'pages' / 'project.html').read_text()
        assert 'class="explorer-anchor"' in project_template
        assert 'class="project-title-line"' in project_template
        assert contains(project_script, 'setupProjectExplorerSticky()')
        assert 'id="back-to-top"' in project_template
        assert contains(console_styles, '.allure-case-list{overflow-y:auto;scrollbar-gutter:stable')
        assert contains(console_styles, '.allure-case-detail{height:100%;min-height:0;overflow-y:hidden')
        assert contains(console_styles, '.file-state.not-collected')
        assert contains(console_styles, '.collection-notice')
        assert contains(console_styles, '.json-row.complex{grid-template-columns:minmax(0,1fr)}')
        assert contains(console_styles, '.json-string{white-space:pre-wrap;overflow-wrap:anywhere;word-break:break-word}')
        assert contains(project_script, "json-row ${complex?'complex':''}")
        assert contains(console_styles, '.report-shell.is-pinned .allure-case-list,.report-shell.is-pinned .allure-case-detail')
        assert client.get('/api/runs/not-found/allure').status_code == 404
        assert client.get('/api/projects/sample_secondary_api/source', params={'path': '../../AGENTS.md'}).status_code == 400
        assert client.post('/api/projects/sample_api/collect', headers={'Origin': 'https://attacker.example'}).status_code == 403
        assert client.post('/api/runs', json={'project': 'sample_api', 'environment': 'prod', 'production_confirmation': 'sample_api', 'target': {'type': 'project', 'id': ''}, 'options': {}}).status_code == 400
        assert client.post('/api/runs', json={'project': 'sample_api', 'environment': 'test', 'target': {'type': 'project', 'id': ''}, 'runtime_overrides': {'PYTHONPATH': '/tmp/unsafe'}, 'options': {}}).status_code == 400
