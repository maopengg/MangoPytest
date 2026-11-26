"""控制台 HTML 页面。"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from web_console.api.dependencies import Services

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def dashboard(services: Services, request: Request):
    templates = services.templates
    return templates.TemplateResponse(request, "pages/dashboard.html", {})


@router.get("/projects/{project_id}", response_class=HTMLResponse)
async def project_page(services: Services, request: Request, project_id: str):
    catalog = services.catalog
    templates = services.templates
    try:
        project = catalog.get(project_id, require_enabled=False)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    profiles = catalog.environment_profiles(project_id)
    return templates.TemplateResponse(
        request, "pages/project.html",
        {"project": project, "profiles": profiles, "has_prod": any(item["id"] == "prod" for item in profiles)},
    )


@router.get("/runs/{run_id}", response_class=HTMLResponse)
async def run_page(services: Services, request: Request, run_id: str):
    repository = services.repository
    templates = services.templates
    if not repository.get(run_id):
        raise HTTPException(404, "执行记录不存在")
    return templates.TemplateResponse(request, "pages/run_detail.html", {"run_id": run_id})
