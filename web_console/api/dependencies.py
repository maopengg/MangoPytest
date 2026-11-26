"""应用装配的服务容器，仅由 HTTP 边界读取。"""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates

from core.execution import ProjectCatalog
from web_console.repositories.runs import RunRepository
from web_console.services.artifacts import ArtifactService
from web_console.services.collection import CollectionService
from web_console.services.events import RunEventService
from web_console.services.runs import RunService


@dataclass(frozen=True)
class ConsoleServices:
    catalog: ProjectCatalog
    repository: RunRepository
    collector: CollectionService
    runner: RunService
    events: RunEventService
    artifacts: ArtifactService
    templates: Jinja2Templates


def get_services(request: Request) -> ConsoleServices:
    return request.app.state.services


Services = Annotated[ConsoleServices, Depends(get_services)]
