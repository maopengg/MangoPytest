"""为一个测试场景组合独立业务 Repository。"""

from typing import Any

from .context import RepositoryContext
from .domains import (
    AuthRepository,
    ClaimRepository,
    OrderRepository,
    ReviewRepository,
    TestRunRepository,
)


class MangoMockRepositories:
    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        run_name_prefix: str = "AUTO_UI",
    ):
        self.context = RepositoryContext(base_url, timeout, run_name_prefix)
        self.test_runs = TestRunRepository(self.context)
        self.auth = AuthRepository(self.context)
        self.orders = OrderRepository(self.context)
        self.claims = ClaimRepository(self.context)
        self.reviews = ReviewRepository(self.context)

    @property
    def run_id(self) -> str:
        return self.context.run_id

    @property
    def cleanup_token(self) -> str:
        return self.context.cleanup_token

    @property
    def deleted(self) -> bool:
        return self.context.deleted

    @deleted.setter
    def deleted(self, value: bool) -> None:
        self.context.deleted = value

    def login(self, role: str = "employee"):
        return self.auth.login(role)

    def request(self, method: str, path: str, **kwargs: Any):
        return self.context.request_success(method, path, **kwargs)

    def close(self) -> None:
        self.context.close()
