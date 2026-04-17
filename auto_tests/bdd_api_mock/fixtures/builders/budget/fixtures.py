# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Budget Fixtures - 预算/组织构造器 fixtures
# @Time   : 2026-04-02
# @Author : 毛鹏

"""
Budget Fixtures 模块

提供预算层构造器 fixtures：
- org_builder: 组织构造器
- budget_builder: 预算构造器（依赖org_builder）
"""

from typing import Generator

import pytest

from auto_tests.pytest_api_mock.data_factory.builders.budget import BudgetBuilder
from auto_tests.pytest_api_mock.data_factory.builders.org import OrgBuilder
from core.base import BuilderContext
from auto_tests.pytest_api_mock.data_factory.strategies import MockStrategy


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
