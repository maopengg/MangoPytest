# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: D Module Fixtures - D模块构造器 fixtures (User)
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
D Module Fixtures 模块

提供 D模块（基础层）构造器 fixtures：
- user_builder: 用户构造器

D模块是最底层，无依赖
"""

from typing import Generator

import pytest

from auto_tests.demo_project.data_factory.builders import UserBuilder
from auto_tests.demo_project.data_factory.builders.base_builder import BuilderContext


@pytest.fixture
def user_builder(test_token) -> Generator[UserBuilder, None, None]:
    """
    用户构造器 fixture

    返回一个配置好的 UserBuilder 实例
    测试结束后自动清理

    使用示例：
        def test_create_user(user_builder):
            user = user_builder.create(username="test")
            assert user.id is not None
    """
    context = BuilderContext(cascade_cleanup=False, auto_prepare_deps=True)
    builder = UserBuilder(token=test_token, context=context)

    yield builder

    # 自动清理
    builder.cleanup()


# 导出
__all__ = [
    "user_builder",
]
