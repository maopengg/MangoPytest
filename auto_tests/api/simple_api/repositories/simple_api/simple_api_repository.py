"""L2：简单 HTTP 接口 Repository，负责隔离运行与自动清理。"""

from __future__ import annotations

import json
from typing import Any

import httpx

from auto_tests.api.simple_api.data_factory.entities import SimpleApiEntity
from auto_tests.common.mango_mock import HttpProtocolClient
from core.models.api import APIResponse
from core.utils import log


class SimpleApiRepository:
    def __init__(
        self,
        base_url: str,
        admin_token: str,
        entity: SimpleApiEntity,
        timeout: float = 30,
    ):
        self.client = HttpProtocolClient(base_url, timeout=timeout)
        self.admin_token = admin_token
        self.entity = entity
        self.run_id: str | None = None
        self.access_token: str | None = None
        self.create_run_response: APIResponse | None = None

    @staticmethod
    def _wrap(response: httpx.Response) -> APIResponse:
        try:
            body: Any = response.json()
        except json.JSONDecodeError:
            body = {"raw": response.text}
        log.debug(
            f"HTTP {response.request.method} {response.request.url.path} "
            f"-> {response.status_code}"
        )
        return APIResponse(
            status_code=response.status_code,
            data=body,
            headers=dict(response.headers),
            elapsed_ms=response.elapsed.total_seconds() * 1000,
            request_method=response.request.method,
            request_url=str(response.request.url),
        )

    def _request(self, method: str, path: str, **kwargs: Any) -> APIResponse:
        return self._wrap(self.client.request_raw(method, path, **kwargs))

    def create_run(self) -> APIResponse:
        if self.create_run_response is None:
            self.create_run_response = self._request(
                "POST",
                "/api/v1/test-runs",
                json={
                    "name": self.entity.run_name,
                    "tenant_id": self.entity.tenant_id,
                    "ttl_minutes": 5,
                },
            )
            if self.create_run_response.status_code == 201:
                self.run_id = self.create_run_response.data["data"]["id"]
                log.info(f"创建简单 API 隔离 Test Run: {self.run_id}")
        return self.create_run_response

    def _ensure_run(self) -> str:
        self.create_run()
        if not self.run_id:
            raise RuntimeError("创建隔离 Test Run 失败")
        return self.run_id

    def login(self, *, valid_password: bool = True) -> APIResponse:
        response = self._request(
            "POST",
            "/api/v1/auth/login",
            headers={"X-Test-Run-ID": self._ensure_run()},
            json={
                "username": self.entity.username,
                "password": (
                    self.entity.password if valid_password else self.entity.wrong_password
                ),
            },
        )
        if response.status_code == 200:
            self.access_token = response.data["data"]["access_token"]
        return response

    def login_with_nonexistent_run(self) -> APIResponse:
        return self._request(
            "POST",
            "/api/v1/auth/login",
            headers={"X-Test-Run-ID": self.entity.nonexistent_run_id},
            json={
                "username": self.entity.username,
                "password": self.entity.password,
            },
        )

    def login_with_nonexistent_user(self) -> APIResponse:
        return self._request(
            "POST",
            "/api/v1/auth/login",
            headers={"X-Test-Run-ID": self._ensure_run()},
            json={
                "username": self.entity.nonexistent_username,
                "password": self.entity.password,
            },
        )

    def current_user(self, *, authenticated: bool) -> APIResponse:
        headers = {"X-Test-Run-ID": self._ensure_run()}
        if authenticated:
            if not self.access_token:
                self.login()
            headers["Authorization"] = f"Bearer {self.access_token}"
        return self._request("GET", "/api/v1/auth/me", headers=headers)

    def current_user_with_invalid_token(self) -> APIResponse:
        return self._request(
            "GET",
            "/api/v1/auth/me",
            headers={
                "X-Test-Run-ID": self._ensure_run(),
                "Authorization": "Bearer AUTO_INVALID_TOKEN",
            },
        )

    def list_products(self, **params: Any) -> APIResponse:
        if not self.access_token:
            self.login()
        return self._request(
            "GET",
            "/api/v1/products",
            headers={
                "X-Test-Run-ID": self._ensure_run(),
                "Authorization": f"Bearer {self.access_token}",
            },
            params=params,
        )

    def product_payload(self, **overrides: Any) -> dict[str, Any]:
        payload = {
            "sku": self.entity.product_sku,
            "name": self.entity.product_name,
            "price": 12.5,
            "stock": 10,
        }
        payload.update(overrides)
        return payload

    def create_product(self, **overrides: Any) -> APIResponse:
        if not self.access_token:
            self.login()
        return self._request(
            "POST",
            "/api/v1/products",
            headers={
                "X-Test-Run-ID": self._ensure_run(),
                "Authorization": f"Bearer {self.access_token}",
            },
            json=self.product_payload(**overrides),
        )

    def create_duplicate_product(self) -> APIResponse:
        first = self.create_product()
        if first.status_code != 201:
            raise RuntimeError("前置商品创建失败")
        return self.create_product()

    def update_product(self) -> APIResponse:
        created = self.create_product()
        if created.status_code != 201:
            raise RuntimeError("前置商品创建失败")
        product = created.data["data"]
        return self._request(
            "PATCH",
            f"/api/v1/products/{product['id']}",
            headers={
                "X-Test-Run-ID": self._ensure_run(),
                "Authorization": f"Bearer {self.access_token}",
            },
            json={
                "price": self.entity.updated_price,
                "version": product["version"],
            },
        )

    def delete_product(self) -> APIResponse:
        created = self.create_product()
        if created.status_code != 201:
            raise RuntimeError("前置商品创建失败")
        return self._request(
            "DELETE",
            f"/api/v1/products/{created.data['data']['id']}",
            headers={
                "X-Test-Run-ID": self._ensure_run(),
                "Authorization": f"Bearer {self.access_token}",
            },
        )

    def close(self) -> None:
        if self.run_id:
            response = self._request(
                "DELETE",
                f"/api/v1/test-runs/{self.run_id}",
                headers={"X-Admin-Token": self.admin_token},
            )
            if response.status_code != 200:
                log.warning(f"Test Run 清理失败，将由 TTL 回收: {self.run_id}")
        self.client.close()
