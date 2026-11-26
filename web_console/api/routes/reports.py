"""报告与产物访问接口，文件范围检查由产物服务执行。"""

import mimetypes
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from web_console.api.dependencies import Services

router = APIRouter()


@router.get("/api/runs/{run_id}/failures")
async def failures(services: Services, run_id: str):
    try:
        return services.artifacts.failures(run_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/api/runs/{run_id}/allure")
async def allure_report(services: Services, run_id: str):
    try:
        return services.artifacts.allure(run_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/api/runs/{run_id}/ai-healing")
async def ai_healing(services: Services, run_id: str):
    try:
        return services.artifacts.ai_healing(run_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/api/runs/{run_id}/artifacts")
async def artifacts(services: Services, run_id: str):
    try:
        return services.artifacts.list(run_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/api/runs/{run_id}/preview/{artifact_path:path}")
async def preview_artifact(services: Services, run_id: str, artifact_path: str):
    try:
        candidate = services.artifacts.resolve(run_id, artifact_path)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    return FileResponse(candidate, media_type=mimetypes.guess_type(candidate.name)[0] or "application/octet-stream")


@router.get("/api/runs/{run_id}/artifacts/{artifact_path:path}")
async def artifact(services: Services, run_id: str, artifact_path: str):
    try:
        candidate = services.artifacts.resolve(run_id, artifact_path)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    return FileResponse(candidate, filename=candidate.name)
