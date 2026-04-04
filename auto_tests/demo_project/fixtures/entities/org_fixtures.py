# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Org Entity Fixtures - 组织实体 fixtures
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
Org Entity Fixtures 模块

提供预配置的组织实体 fixtures：
- default_org: 默认组织
- large_org: 大型组织（高预算）
- small_org: 小型组织（低预算）

使用示例：
    def test_with_org(default_org):
        assert default_org.budget_total > 0
"""

import pytest

from auto_test.demo_project.data_factory.entities.org_entity import OrgEntity


@pytest.fixture
def default_org() -> OrgEntity:
    """
    默认组织 fixture
    
    返回一个预配置的默认组织实体
    """
    return OrgEntity.with_budget(
        budget=1000000,
        name="总公司",
        code="ORG001"
    )


@pytest.fixture
def large_org() -> OrgEntity:
    """
    大型组织 fixture
    
    返回一个预配置的大型组织实体（高预算）
    """
    return OrgEntity.with_budget(
        budget=10000000,
        name="大型研发中心",
        code="ORG002"
    )


@pytest.fixture
def small_org() -> OrgEntity:
    """
    小型组织 fixture
    
    返回一个预配置的小型组织实体（低预算）
    """
    return OrgEntity.with_budget(
        budget=100000,
        name="小型部门",
        code="ORG003"
    )


@pytest.fixture
def dept_org() -> OrgEntity:
    """
    部门组织 fixture
    
    返回一个预配置的部门组织实体
    """
    return OrgEntity.with_budget(
        budget=500000,
        name="研发部门",
        code="DEPT001"
    )


# 导出
__all__ = [
    "default_org",
    "large_org",
    "small_org",
    "dept_org",
]
