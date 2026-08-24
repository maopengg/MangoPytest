from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import json
import mimetypes
from pathlib import Path
from urllib.parse import urlsplit

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.execution import ProjectCatalog
from core.execution.models import FINAL_STATUSES
from core.execution.result_parser import parse_failures
from web_console.collection_service import CollectionService
from web_console.allure_service import AllureResultService
from web_console.config import WebConsoleSettings
from web_console.repository import RunRepository
from web_console.run_service import RunService
from web_console.schemas import CreateRunInput


def create_app(settings: WebConsoleSettings | None = None) -> FastAPI:
    settings = settings or WebConsoleSettings.default()
    catalog = ProjectCatalog(settings.repository_root)
    repository = RunRepository(settings.database_path)
    repository.interrupt_stale()
    collector = CollectionService(settings, catalog)
    runner = RunService(settings, catalog, repository, collector)
    package_root = Path(__file__).resolve().parent
    templates = Jinja2Templates(directory=package_root / "templates")

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        yield
        await runner.shutdown()

    app = FastAPI(title="Mango Pytest Web Console", version="1.0.0", lifespan=lifespan)
    app.state.catalog = catalog
    app.state.repository = repository
    app.state.collector = collector
    app.state.runner = runner
    app.mount("/static", StaticFiles(directory=package_root / "static"), name="static")

    @app.middleware("http")
    async def reject_cross_origin_writes(request: Request, call_next):
        """阻止外部网页通过用户浏览器向本地控制台提交写操作。"""
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            origin = request.headers.get("origin")
            if origin:
                origin_parts = urlsplit(origin)
                allowed_hosts = {request.url.netloc, "127.0.0.1", "localhost"}
                if origin_parts.hostname not in allowed_hosts or origin_parts.port != request.url.port:
                    return JSONResponse({"detail": "拒绝跨来源写操作"}, status_code=403)
        response = await call_next(request)
        if request.url.path.startswith("/static/"):
            # The console is a local development tool. Always revalidate its
            # CSS/JS so an already-running server does not expose stale UI.
            response.headers["Cache-Control"] = "no-cache, must-revalidate"
        return response

    @app.get("/", response_class=HTMLResponse)
    async def dashboard(request: Request):
        return templates.TemplateResponse(request, "dashboard.html", {})

    @app.get("/projects/{project_id}", response_class=HTMLResponse)
    async def project_page(request: Request, project_id: str):
        try:
            project = catalog.get(project_id, require_enabled=False)
        except ValueError as exc:
            raise HTTPException(404, str(exc)) from exc
        profiles = catalog.environment_profiles(project_id)
        return templates.TemplateResponse(
            request, "project.html",
            {"project": project, "profiles": profiles, "has_prod": any(item["id"] == "prod" for item in profiles)},
        )

    @app.get("/runs/{run_id}", response_class=HTMLResponse)
    async def run_page(request: Request, run_id: str):
        if not repository.get(run_id):
            raise HTTPException(404, "执行记录不存在")
        return templates.TemplateResponse(request, "run_detail.html", {"run_id": run_id})

    @app.get("/api/projects")
    async def projects():
        result = []
        for project in catalog.all():
            collection = collector.read(project.id)
            latest = repository.list(limit=1, project=project.id)
            result.append({
                "id": project.id, "name": project.name, "kind": project.kind,
                "enabled": project.enabled, "reason": project.reason,
                "environments": catalog.environment_profiles(project.id),
                "case_count": collection["count"], "collected": collection["collected"],
                "latest": latest[0] if latest else None,
            })
        return result

    @app.post("/api/projects/{project_id}/collect")
    async def collect(project_id: str):
        try:
            return await collector.collect(project_id)
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
        except RuntimeError as exc:
            raise HTTPException(500, str(exc)) from exc

    @app.get("/api/projects/{project_id}/tree")
    async def project_tree(project_id: str):
        try:
            catalog.get(project_id, require_enabled=False)
            return collector.tree(project_id)
        except ValueError as exc:
            raise HTTPException(404, str(exc)) from exc

    @app.get("/api/projects/{project_id}/cases")
    async def cases(project_id: str, file: str = "", mark: str = "", q: str = ""):
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

    @app.get("/api/projects/{project_id}/source")
    async def source(project_id: str, path: str = Query(...)):
        try:
            return {"path": path, "content": collector.source(project_id, path)}
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc

    @app.post("/api/runs", status_code=201)
    async def create_run(data: CreateRunInput):
        try:
            return runner.create(data)
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc

    @app.get("/api/runs")
    async def runs(
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        project: str = "",
        status: str = "",
    ):
        return repository.list(limit=limit, offset=offset, project=project, status=status)

    @app.get("/api/runs/{run_id}")
    async def run_detail(run_id: str):
        record = repository.get(run_id)
        if not record:
            raise HTTPException(404, "执行记录不存在")
        return record

    @app.post("/api/runs/{run_id}/cancel")
    async def cancel_run(run_id: str):
        try:
            return await runner.cancel(run_id)
        except ValueError as exc:
            raise HTTPException(404, str(exc)) from exc

    @app.post("/api/runs/{run_id}/rerun", status_code=201)
    async def rerun(run_id: str):
        record = repository.get(run_id)
        if not record:
            raise HTTPException(404, "执行记录不存在")
        data = CreateRunInput.model_validate({
            "project": record["project"], "environment": record["environment"],
            "target": {"type": record["target_kind"], "id": record["target"]},
            "options": record["options"],
            "runtime_overrides": record["runtime_overrides"],
            "production_confirmation": record["project"] if record["environment"] == "prod" else "",
        })
        return runner.create(data)

    @app.get("/api/runs/{run_id}/events")
    async def events(request: Request, run_id: str):
        record = repository.get(run_id)
        if not record:
            raise HTTPException(404, "执行记录不存在")
        event_path = Path(record["artifact_dir"]) / "events.ndjson"

        async def stream():
            position = 0
            while True:
                if event_path.is_file():
                    with event_path.open(encoding="utf-8") as source_file:
                        source_file.seek(position)
                        for line in source_file:
                            payload = line.rstrip("\n")
                            yield f"data: {payload}\n\n"
                        position = source_file.tell()
                current = repository.get(run_id)
                if current and current["status"] in {item.value for item in FINAL_STATUSES}:
                    yield f"event: end\ndata: {json.dumps({'status': current['status']})}\n\n"
                    break
                if await request.is_disconnected():
                    break
                yield ": keepalive\n\n"
                await asyncio.sleep(0.5)
        return StreamingResponse(stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})

    @app.get("/api/runs/{run_id}/failures")
    async def failures(run_id: str):
        record = repository.get(run_id)
        if not record:
            raise HTTPException(404, "执行记录不存在")
        return parse_failures(Path(record["artifact_dir"]) / "junit.xml")

    @app.get("/api/runs/{run_id}/allure")
    async def allure_report(run_id: str):
        record = repository.get(run_id)
        if not record:
            raise HTTPException(404, "执行记录不存在")
        return AllureResultService(Path(record["artifact_dir"])).report()

    @app.get("/api/runs/{run_id}/artifacts")
    async def artifacts(run_id: str):
        record = repository.get(run_id)
        if not record:
            raise HTTPException(404, "执行记录不存在")
        root = Path(record["artifact_dir"]).resolve()
        if not root.is_dir():
            return []
        return [
            {"path": path.relative_to(root).as_posix(), "size": path.stat().st_size}
            for path in sorted(root.rglob("*")) if path.is_file()
        ][:2000]

    @app.get("/api/runs/{run_id}/preview/{artifact_path:path}")
    async def preview_artifact(run_id: str, artifact_path: str):
        record = repository.get(run_id)
        if not record:
            raise HTTPException(404, "执行记录不存在")
        root = Path(record["artifact_dir"]).resolve()
        candidate = (root / artifact_path).resolve()
        if not candidate.is_relative_to(root) or not candidate.is_file():
            raise HTTPException(404, "产物不存在")
        return FileResponse(candidate, media_type=mimetypes.guess_type(candidate.name)[0] or "application/octet-stream")

    @app.get("/api/runs/{run_id}/artifacts/{artifact_path:path}")
    async def artifact(run_id: str, artifact_path: str):
        record = repository.get(run_id)
        if not record:
            raise HTTPException(404, "执行记录不存在")
        root = Path(record["artifact_dir"]).resolve()
        candidate = (root / artifact_path).resolve()
        if not candidate.is_relative_to(root) or not candidate.is_file():
            raise HTTPException(404, "产物不存在")
        return FileResponse(candidate, filename=candidate.name)

    return app
