# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: C Module Fixtures - C模块构造器 fixtures (Budget/Org)
# @Time   : 2026-04-02
# @Author : 毛鹏

"""
C Module Fixtures 模块

提供 C模块（预算层）构造器 fixtures：
- org_builder: 组织构造器
- budget_builder: 预算构造器（依赖org_builder）
"""

from typing import Generator

import pytest

from auto_tests.demo_project.data_factory.builders import OrgBuilder, BudgetBuilder
from auto_tests.demo_project.data_factory.builders.base_builder import BuilderContext
from auto_tests.demo_project.data_factory.strategies import MockStrategy


@pytest.fixture
def org_builder(test_token) -> Generator[OrgBuilder, None, None]:
    """组织构造器 fixture"""
    context = BuilderContext(
        strategy=MockStrategy(),
        cascade_cleanup=False,
        auto_prepare_deps=True,
    )
    builder = OrgBuilder(token=test_token, context=context)
    yield builder
    builder.cleanup()


@pytest.fixture
def budget_builder(test_token, org_builder) -> Generator[BudgetBuilder, None, None]:
    """预算构造器 fixture"""
    context = org_builder.context
    builder = BudgetBuilder(
        token=test_token,
        context=context,
        parent_builders={"OrgBuilder": org_builder},
    )
    yield builder
    builder.cleanup()


__all__ = [
    "org_builder",
    "budget_builder",
]
