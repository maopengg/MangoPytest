# -*- coding: utf-8 -*-
"""
API 客户端 - 从 api_steps 中提取，避免循环导入
"""

import json
import re
from typing import Any, Dict, Optional

import requests

from auto_tests.bdd_api_mock.config import settings


class APIClient:
    """API 客户端"""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.BASE_URL
        self.session = requests.Session()
        self.token = None

    def set_token(self, token: str):
        """设置认证令牌"""
        self.token = token
        self.session.headers["Authorization"] = f"Bearer {token}"
        self.session.headers["X-Token"] = token

    def _prepare_url(self, path: str, created_entity=None) -> str:
        """准备 URL，替换占位符"""
        url = path if path.startswith("http") else f"{self.base_url}{path}"

        # 替换占位符 ${entity.id}
        if created_entity is not None:
            url = re.sub(r"\$\{(\w+)\.id\}", str(created_entity.id), url)

        return url

    def _prepare_body(self, body: Dict, created_entity=None) -> Dict:
        """准备请求体，替换占位符"""
        if created_entity is None:
            return body

        body_str = json.dumps(body)
        body_str = re.sub(r"\$\{(\w+)\.id\}", str(created_entity.id), body_str)
        return json.loads(body_str)

    def get(
        self, path: str, params: Dict = None, created_entity=None
    ) -> Dict[str, Any]:
        """GET 请求"""
        url = self._prepare_url(path, created_entity)
        response = self.session.get(url, params=params)
        return response.json()

    def post(self, path: str, body: Dict = None, created_entity=None) -> Dict[str, Any]:
        """POST 请求"""
        url = self._prepare_url(path, created_entity)
        body = self._prepare_body(body or {}, created_entity)
        response = self.session.post(url, json=body)
        return response.json()

    def put(self, path: str, body: Dict = None, created_entity=None) -> Dict[str, Any]:
        """PUT 请求"""
        url = self._prepare_url(path, created_entity)
        body = self._prepare_body(body or {}, created_entity)
        response = self.session.put(url, json=body)
        return response.json()

    def delete(self, path: str, created_entity=None) -> Dict[str, Any]:
        """DELETE 请求"""
        url = self._prepare_url(path, created_entity)
        response = self.session.delete(url)
        return response.json()
