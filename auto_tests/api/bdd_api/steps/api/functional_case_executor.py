"""L4：FTAPI-0001～FTAPI-0157 功能场景路由器。"""

from auto_tests.api.bdd_api.data_factory.factories import FunctionalCaseFactory
from auto_tests.api.bdd_api.repos.functional_cases import FunctionalCaseRepository
from auto_tests.api.bdd_api.steps.api.handlers import (
    BusinessHandler,
    FaultWebhookHandler,
    GrpcHandler,
    HttpLabHandler,
    McpHandler,
    SseHandler,
    WebSocketHandler,
)
from core.utils import log


class FunctionalCaseExecutor:
    """仅负责按编号把场景分发给对应业务/协议 Handler。"""

    def __init__(self, repository: FunctionalCaseRepository, factory: FunctionalCaseFactory):
        self.routes = (
            (47, BusinessHandler(repository, factory)._business),
            (79, HttpLabHandler(repository, factory)._http_lab),
            (95, FaultWebhookHandler(repository, factory)._fault_webhook),
            (105, SseHandler(repository, factory)._sse),
            (121, WebSocketHandler(repository, factory)._websocket),
            (139, McpHandler(repository, factory)._mcp),
            (157, GrpcHandler(repository, factory)._grpc),
        )

    def execute(self, case_id: str):
        number = int(case_id.rsplit("-", 1)[1])
        log.info(f"开始执行功能用例: {case_id}")
        for upper_bound, execute in self.routes:
            if number <= upper_bound:
                return execute(case_id, number)
        raise KeyError(f"该执行器不负责跨协议场景: {case_id}")
