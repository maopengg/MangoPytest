"""运行记录、任务控制与事件流接口。"""

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from web_console.schemas.runs import CreateRunInput
from web_console.api.presenters import public_run
from web_console.api.dependencies import Services

router = APIRouter()


@router.post("/api/runs", status_code=201)
async def create_run(services: Services, data: CreateRunInput):
    runner = services.runner
    try:
        return public_run(runner.create(data))
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@router.get("/api/runs")
async def runs(services: Services,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    project: str = "",
    status: str = "",
):
    repository = services.repository
    return [
        public_run(item)
        for item in repository.list(limit=limit, offset=offset, project=project, status=status)
    ]


@router.get("/api/runs/{run_id}")
async def run_detail(services: Services, run_id: str):
    repository = services.repository
    record = repository.get(run_id)
    if not record:
        raise HTTPException(404, "执行记录不存在")
    return public_run(record)


@router.post("/api/runs/{run_id}/cancel")
async def cancel_run(services: Services, run_id: str):
    runner = services.runner
    try:
        return public_run(await runner.cancel(run_id))
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.post("/api/runs/{run_id}/rerun", status_code=201)
async def rerun(services: Services, run_id: str):
    repository = services.repository
    runner = services.runner
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
    return public_run(runner.create(data))


@router.get("/api/runs/{run_id}/events")
async def events(services: Services, request: Request, run_id: str):
    try:
        path = services.events.path(run_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    return StreamingResponse(
        services.events.stream(run_id, path, request.is_disconnected),
        media_type="text/event-stream", headers={"Cache-Control": "no-cache"},
    )
