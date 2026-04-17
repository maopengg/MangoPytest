# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 用户构造器 - 使用Entity的新版本
# @Time   : 2026-03-31
# @Author : 毛鹏
import uuid
from typing import Optional, List

from core.base import BaseBuilder
from ...entities.user import UserEntity
from ...registry import register_builder
from ....api_manager import bdd_api_mock


@register_builder("user")
class UserBuilder(BaseBuilder[UserEntity]):
    """
    用户构造器

    使用Entity进行数据构造和API调用
    """

    def __init__(
        self,
        token: str = None,
        context=None,
        strategy=None,
        parent_builders=None,
        factory=None,
    ):
        super().__init__(
            token=token,
            context=context,
            strategy=strategy,
            parent_builders=parent_builders,
            factory=factory,
        )
        # 设置token到API模块 - 使用全局token
        if token:
            bdd_api_mock.set_token(token)

    def build(
        self,
        username: str = None,
        email: str = None,
        full_name: str = None,
        password: str = None,
        role: str = "user",
    ) -> UserEntity:
        """
        构造用户实体（不调用API）

        @param username: 用户名
        @param email: 邮箱
        @param full_name: 全名
        @param password: 密码
        @param role: 角色
        @return: 用户实体
        """
        uid = uuid.uuid4().hex[:8]
        return UserEntity(
            username=username or f"test_user_{uid}",
            email=email or f"test_{uid}@example.com",
            full_name=full_name or f"Test User {uid}",
            password=password or "Test@123456",
            role=role,
        )

    def create(self, entity: UserEntity = None, **kwargs) -> Optional[UserEntity]:
        """
        创建用户（调用API）

        @param entity: 实体实例（不传则使用kwargs构造）
        @param kwargs: 构造参数
        @return: 创建后的实体
        """
        if entity is None:
            entity = self.build(**kwargs)

        if not entity.validate():
            return None

        result = bdd_api_mock.auth.api_register(
            username=entity.username,
            email=entity.email,
            full_name=entity.full_name,
            password=entity.password,
        )

        if result.get("code") == 200:
            data = result["data"]
            created_entity = UserEntity.from_api_response(data)
            self._register_created(created_entity)
            return created_entity

        return None

    def get_by_id(self, user_id: int) -> Optional[UserEntity]:
        """
        根据ID获取用户

        @param user_id: 用户ID
        @return: 用户实体
        """
        result = bdd_api_mock.user.get_user_by_id(user_id)

        if result.get("code") == 200:
            data = result["data"]
            return UserEntity.from_api_response(data)

        return None

    def update(self, entity: UserEntity) -> Optional[UserEntity]:
        """
        更新用户

        @param entity: 实体实例
        @return: 更新后的实体
        """
        result = bdd_api_mock.user.update_user(
            user_id=entity.id, **entity.to_api_payload()
        )

        if result.get("code") == 200:
            data = result["data"]
            return UserEntity.from_api_response(data)

        return None

    def delete(self, entity: UserEntity = None, user_id: int = None) -> bool:
        """
        删除用户

        @param entity: 实体实例（可选）
        @param user_id: 用户ID（可选，与entity二选一）
        @return: 是否删除成功
        """
        delete_id = user_id if user_id is not None else (entity.id if entity else None)
        if delete_id is None:
            return False

        result = bdd_api_mock.user.delete_user(delete_id)

        if result.get("code") == 200:
            if entity:
                entity.mark_as_deleted()
            return True

        return False

    def get_all(self) -> List[UserEntity]:
        """
        获取所有用户

        @return: 用户实体列表
        """
        # 确保设置了 token - 使用全局token
        if self.token:
            bdd_api_mock.set_token(self.token)
        result = bdd_api_mock.user.get_users()

        if result.get("code") == 200:
            data_list = result["data"]
            return [UserEntity.from_api_response(d) for d in data_list]

        return []
