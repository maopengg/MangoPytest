"""本地控制台的来源检查与静态资源缓存策略。"""

from urllib.parse import urlsplit
from fastapi import Request
from fastapi.responses import JSONResponse


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
