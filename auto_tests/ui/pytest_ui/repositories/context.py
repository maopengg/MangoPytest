"""pytest_ui Repository 共用的 Test Run 与认证上下文。"""

from __future__ import annotations

import uuid
from typing import Any

from auto_tests.common.mango_mock import HttpProtocolClient, HttpResult
from core.utils import log


class RepositoryContext:
    PASSWORDS = {
        "employee": "password123",
        "dept_manager": "password123",
        "finance_manager": "password123",
        "ceo": "password123",
    }

    def __init__(self, base_url: str, timeout: int = 30):
        self.http = HttpProtocolClient(base_url, timeout=timeout)
        self.run_id = ""
        self.cleanup_token = ""
        self.tokens: dict[str, str] = {}
        self.users: dict[str, dict[str, Any]] = {}
        self.deleted = False

    def ensure_run(self) -> None:
        if self.run_id:
            return
        result = self.http.create_run(
            f"AUTO_PYTEST_UI_{uuid.uuid4().hex[:10]}", ttl_minutes=5
        )
        if result.status_code != 201:
            raise AssertionError(result.body)
        self.run_id = result.data["id"]
        self.cleanup_token = result.data["cleanup_token"]
        log.debug(f"pytest_ui 创建 Test Run: {self.run_id}")

    def login(self, role: str = "employee") -> tuple[str, dict[str, Any]]:
        self.ensure_run()
        if role not in self.PASSWORDS:
            raise KeyError(f"未配置测试角色：{role}")
        if role not in self.tokens:
            result = self.http.login(self.run_id, role, self.PASSWORDS[role])
            if result.status_code != 200:
                raise AssertionError(result.body)
            self.tokens[role] = result.data["access_token"]
            self.users[role] = result.data["user"]
        return self.tokens[role], self.users[role]

    def request_result(
        self,
        method: str,
        path: str,
        *,
        role: str = "employee",
        json_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> HttpResult:
        token, _ = self.login(role)
        return self.http.request(
            method,
            path,
            run_id=self.run_id,
            token=token,
            json_data=json_data,
            headers=headers,
        )

    def request_success(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        result = self.request_result(method, path, **kwargs)
        if result.status_code >= 400:
            raise AssertionError(result.body)
        return result.data

    def close(self) -> None:
        try:
            if self.run_id and not self.deleted:
                result = self.http.delete_run_with_cleanup_token(
                    self.run_id, self.cleanup_token
                )
                if result.status_code in {200, 404}:
                    self.deleted = True
                else:
                    raise AssertionError(
                        f"pytest_ui Test Run 清理失败: {result.body}"
                    )
        finally:
            self.http.close()

