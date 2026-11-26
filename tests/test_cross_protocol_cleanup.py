"""跨协议项目的隔离数据和连接必须在正常/异常清理时正确释放。"""

from importlib import import_module
from unittest.mock import Mock

import pytest


@pytest.fixture(params=[
    "auto_tests.api.bdd_api.repos.cross_protocol.cross_protocol_repo",
    "auto_tests.api.pytest_api.repositories.cross_protocol.cross_protocol_repo",
])
def repository(request, monkeypatch):
    module = import_module(request.param)
    for name in ("HttpProtocolClient", "WebSocketProtocolClient", "SseProtocolClient",
                 "McpProtocolClient", "GrpcProtocolClient"):
        monkeypatch.setattr(module, name, Mock())
    repo = module.CrossProtocolRepository("http://example.test", admin_token="legacy")
    repo.http.create_run.return_value = Mock(
        status_code=201, body={"code": 0},
        data={"id": "run-test", "cleanup_token": "own-cleanup-token"},
    )
    return repo.start()


def test_cleanup_uses_run_token_instead_of_admin(repository):
    repository.http.delete_run_with_cleanup_token.return_value.status_code = 200
    repository.close()
    repository.http.delete_run_with_cleanup_token.assert_called_once_with(
        "run-test", "own-cleanup-token"
    )
    repository.http.delete_run.assert_not_called()
    repository.mcp.close.assert_called_once()
    repository.grpc.close.assert_called_once()
    repository.http.close.assert_called_once()


def test_cleanup_failure_still_closes_all_clients(repository):
    repository.http.delete_run_with_cleanup_token.side_effect = RuntimeError("offline")
    with pytest.raises(RuntimeError, match="offline"):
        repository.close()
    repository.mcp.close.assert_called_once()
    repository.grpc.close.assert_called_once()
    repository.http.close.assert_called_once()
