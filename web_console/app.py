"""Web 控制台装配入口：生命周期、服务依赖、HTTP 路由与资源挂载。"""

if __name__ == "__main__":
    # IDE 直接运行文件时先补齐包根目录，再进入同一个 CLI 启动入口。
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from web_console.__main__ import main

    raise SystemExit(main())

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.execution import ProjectCatalog
from web_console.api.dependencies import ConsoleServices
from web_console.api.middleware import reject_cross_origin_writes
from web_console.api.routes import pages, projects, reports, runs
from web_console.config import WebConsoleSettings
from web_console.repositories.runs import RunRepository
from web_console.services.artifacts import ArtifactService
from web_console.services.collection import CollectionService
from web_console.services.runs import RunService


def create_app(settings: WebConsoleSettings | None = None) -> FastAPI:
    settings = settings or WebConsoleSettings.default()
    package_root = Path(__file__).resolve().parent
    catalog = ProjectCatalog(settings.repository_root)
    repository = RunRepository(settings.database_path)
    repository.interrupt_stale()
    collector = CollectionService(settings, catalog)
    runner = RunService(settings, catalog, repository, collector)
    services = ConsoleServices(
        catalog=catalog, repository=repository, collector=collector, runner=runner,
        events=runner.events, artifacts=ArtifactService(repository),
        templates=Jinja2Templates(directory=package_root / "templates"),
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        yield
        await runner.shutdown()

    app = FastAPI(title="Mango Pytest Web Console", version="1.0.0", lifespan=lifespan)
    app.state.services = services
    app.middleware("http")(reject_cross_origin_writes)
    for route in (pages.router, projects.router, runs.router, reports.router):
        app.include_router(route)
    app.mount("/static", StaticFiles(directory=package_root / "static"), name="static")
    return app
