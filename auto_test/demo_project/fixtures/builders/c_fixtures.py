# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: C Module Fixtures - C模块构造器 fixtures (Budget)
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
C Module Fixtures 模块

提供 C模块（预算层）构造器 fixtures：
- budget_builder: 预算构造器

C模块依赖 D模块（Org）
"""

import pytest
from typing import Generator
from auto_test.demo_project.data_factory.builders import BudgetBuilder
from auto_test.demo_project.data_factory.builders.base_builder import BuilderContext


@pytest.fixture
def budget_builder(test_token, default_org) -> Generator[BudgetBuilder, None, None]:
    """
    预算构造器 fixture
    
    返回一个配置好的 BudgetBuilder 实例
    自动关联默认组织
    测试结束后自动清理
    
    使用示例：
        def test_create_budget(budget_builder):
            budget = budget_builder.create(total_amount=100000)
            assert budget.id is not None
    """
    context = BuilderContext(auto_cleanup=True)
    builder = BudgetBuilder(
        token=test_token,
        context=context
    )
    
    yield builder
    
    # 自动清理
    builder.cleanup()


# 导出
__all__ = [
    "budget_builder",
]
