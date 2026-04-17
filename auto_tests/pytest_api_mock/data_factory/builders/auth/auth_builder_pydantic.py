# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 认证构造器 - Pydantic 版本 (L2 构造器层)
# @Time   : 2026-04-06
# @Author : 毛鹏
"""
认证构造器 - L2 构造器层

接收 L3 Entity，调用 to_api_payload() 后传给 L1
"""

from typing import Any, Dict, Optional

from auto_tests.pytest_api_mock.api_manager import pytest_api_mock
from auto_tests.pytest_api_mock.data_factory.entities.user_pydantic import UserEntity
from core.base import PydanticBuilder


class AuthBuilder(PydanticBuilder[UserEntity]):
    """
    认证构造器 - L2 构造器层

    对应 /auth/login, /auth/register 接口

    使用示例：
        # 使用 Entity 登录
        user = UserEntity.with_credentials("testuser", "password123")
        builder = AuthBuilder()
        token = builder.login(user)

        # 使用 Entity 注册
        user = UserEntity.default()
        result = builder.register(user)
    """

    ENTITY_CLASS = UserEntity

    def __init__(self, token: Optional[str] = None):
        """
        初始化 Builder

        @param token: 认证 token（可选）
        """
        super().__init__(token=token)

    def login(self, entity: UserEntity) -> Optional[str]:
        """
        用户登录

        @param entity: L3 UserEntity（包含 username 和 password）
        @return: token 或 None
        """
        payload = entity.to_login_payload()  # L3 提供
        result = pytest_api_mock.auth.api_login(
            username=payload["username"], password=payload["password"]
        )

        if result.get("code") == 200:
            token = result["data"]["token"]
            self.token = token
            # 更新 entity 的响应字段（映射 user_id -> id）
            response_data = result["data"].copy()
            if "user_id" in response_data and "id" not in response_data:
                response_data["id"] = response_data.pop("user_id")
            entity.update_from_response(response_data)
            return token

        return None

    def register(self, entity: UserEntity) -> Optional[UserEntity]:
        """
        用户注册

        @param entity: L3 UserEntity
        @return: 注册后的 UserEntity（包含 id 等响应字段）
        """
        payload = entity.to_api_payload()  # L3 提供
        result = pytest_api_mock.auth.api_register(**payload)

        if result.get("code") == 200:
            # 更新 entity 的响应字段（映射 user_id -> id）
            response_data = result["data"].copy()
            if "user_id" in response_data and "id" not in response_data:
                response_data["id"] = response_data.pop("user_id")
            entity.update_from_response(response_data)
            self._track_entity(entity)
            return entity

        return None

    def create_entity(self, entity: UserEntity) -> UserEntity:
        """
        创建实体（注册）

        @param entity: L3 UserEntity
        @return: 创建后的 UserEntity
        """
        result = self.register(entity)
        if result is None:
            raise RuntimeError("Failed to register user")
        return result

    def _delete_entity(self, entity: UserEntity) -> None:
        """
        删除实体 - 调用删除用户 API
        
        @param entity: 要删除的用户实体
        """
        if entity.id:
            # 确保设置了 token
            if self.token:
                pytest_api_mock.auth.set_token(self.token)
            pytest_api_mock.user.delete_user(entity.id)
