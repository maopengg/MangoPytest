# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 登录场景
# @Time   : 2026-03-31
# @Author : 毛鹏
import hashlib

import requests

from .base_scenario import BaseScenario, ScenarioResult
from ..entities.user import UserEntity


class LoginScenario(BaseScenario):
    """
    登录场景

    封装用户登录的完整流程：
    1. 创建用户（可选）
    2. 执行登录
    3. 获取token

    使用示例：
        scenario = LoginScenario()
        result = scenario.execute(username="test", password="123456")
        token = result.data.get("token")
    """

    def __init__(self, token: str = None, factory=None):
        super().__init__(token, factory)
        self._host = "http://localhost:8003"

    def _post(self, path: str, json_data: dict) -> dict:
        """
        发送POST请求

        @param path: API路径
        @param json_data: JSON数据
        @return: 响应字典
        """
        url = f"{self._host}/{path.lstrip('/')}"
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        try:
            response = requests.post(url, json=json_data, headers=headers, timeout=30)
            return response.json()
        except Exception as e:
            return {"code": 500, "message": str(e), "data": None}

    def execute(
            self, username: str, password: str, create_user: bool = False, email: str = None
    ) -> ScenarioResult:
        """
        执行登录场景

        @param username: 用户名
        @param password: 密码
        @param create_user: 是否先创建用户
        @param email: 邮箱（创建用户时使用）
        @return: 场景执行结果
        """
        result = ScenarioResult()

        # 1. 如果需要，先创建用户
        if create_user:
            user_entity = UserEntity(
                username=username,
                email=email or f"{username}@example.com",
                full_name=f"User {username}",
                password=password,
            )

            if not user_entity.validate():
                result.add_error("用户数据验证失败")
                return result

            # 调用API创建用户
            response = self._post("/auth/register", user_entity.to_api_payload())

            if response.get("code") == 200:
                user_data = response.get("data", {})
                user_entity.mark_as_saved(user_data.get("id"))
                self.register_entity(user_entity)
                result.add_entity("user", user_entity)
            else:
                result.add_error(f"用户创建失败: {response.get('message')}")
                return result

        # 2. 执行登录（密码需要MD5加密）
        password_md5 = hashlib.md5(password.encode()).hexdigest()
        response = self._post(
            "/auth/login", {"username": username, "password": password_md5}
        )

        if response.get("code") == 200:
            login_data = response.get("data", {})
            result.data = {
                "token": login_data.get("token") or login_data.get("access_token"),
                "token_type": login_data.get("token_type", "bearer"),
                "expires_in": login_data.get("expires_in", 3600),
            }
            result.message = "登录成功"
        else:
            result.add_error(f"登录失败: {response.get('message')}")

        return result


class RegisterAndLoginScenario(BaseScenario):
    """
    注册并登录场景

    封装完整的注册+登录流程
    """

    def execute(
            self, username: str = None, password: str = None, email: str = None
    ) -> ScenarioResult:
        """
        执行注册并登录场景

        @param username: 用户名（不传则自动生成）
        @param password: 密码（不传则自动生成）
        @param email: 邮箱（不传则自动生成）
        @return: 场景执行结果
        """
        import uuid

        # 生成默认值
        username = username or f"user_{uuid.uuid4().hex[:8]}"
        password = password or "Test@123456"
        email = email or f"{username}@example.com"

        # 使用LoginScenario执行
        login_scenario = LoginScenario(self.token, self.factory)
        return login_scenario.execute(
            username=username, password=password, create_user=True, email=email
        )
