"""项目与用例收集接口。"""

from fastapi import APIRouter, HTTPException, Query
from web_console.api.dependencies import Services
from web_console.api.presenters import public_run

router = APIRouter()


@router.get("/api/projects")
async def projects(services: Services):
    catalog = services.catalog
    collector = services.collector
    repository = services.repository
    result = []
    for project in catalog.all():
        collection = collector.read(project.id)
        latest = repository.list(limit=1, project=project.id)
        result.append({
            "id": project.id, "name": project.name, "kind": project.kind,
            "enabled": project.enabled, "reason": project.reason,
            "environments": catalog.environment_profiles(project.id),
            "case_count": collection["count"], "collected": collection["collected"],
                "latest": public_run(latest[0]) if latest else None,
        })
    return result


@router.post("/api/projects/{project_id}/collect")
async def collect(services: Services, project_id: str):
    collector = services.collector
    try:
        return await collector.collect(project_id)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(500, str(exc)) from exc


@router.get("/api/projects/{project_id}/tree")
async def project_tree(services: Services, project_id: str):
    catalog = services.catalog
    collector = services.collector
    try:
        catalog.get(project_id, require_enabled=False)
        return collector.tree(project_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/api/projects/{project_id}/cases")
async def cases(services: Services, project_id: str, file: str = "", mark: str = "", q: str = ""):
    catalog = services.catalog
    collector = services.collector
    try:
        catalog.get(project_id, require_enabled=False)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    values = collector.read(project_id)["cases"]
    if file:
        values = [item for item in values if item["file"] == file]
    if mark:
        values = [item for item in values if mark in item["markers"]]
    if q:
        lowered = q.lower()
        values = [
            item for item in values
            if lowered in item["node_id"].lower()
            or lowered in item["case_id"].lower()
            or lowered in item.get("name", "").lower()
            or any(lowered in marker.lower() for marker in item.get("markers", []))
        ]
    return values


@router.get("/api/projects/{project_id}/source")
async def source(services: Services, project_id: str, path: str = Query(...)):
    collector = services.collector
    try:
        return {"path": path, "content": collector.source(project_id, path)}
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
