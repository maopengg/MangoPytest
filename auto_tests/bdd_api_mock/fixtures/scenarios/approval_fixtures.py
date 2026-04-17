# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Approval Scenario Fixtures - 审批场景 fixtures
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
Approval Scenario Fixtures 模块

提供预配置的审批场景 fixtures：
- full_approval_scenario: 完整审批流场景
- simple_approval_scenario: 简单审批场景

使用示例：
    def test_full_approval(full_approval_scenario):
        result = full_approval_scenario.execute(amount=50000)
        assert result.success
"""

from typing import Generator

import pytest

from auto_tests.pytest_api_mock.data_factory.scenarios import FullApprovalScenario
from auto_tests.pytest_api_mock.data_factory.scenarios.base_scenario import ScenarioResult


@pytest.fixture
def full_approval_scenario(test_token) -> Generator[FullApprovalScenario, None, None]:
    """
    完整审批流场景 fixture
    
    返回一个配置好的 FullApprovalScenario 实例
    支持 D→C→B→A 四级审批流程
    
    使用示例：
        def test_full_approval(full_approval_scenario):
            result = full_approval_scenario.execute(amount=50000)
            assert result.success
            assert result.get_entity("reimbursement").status == "ceo_approved"
    """
    scenario = FullApprovalScenario(token=test_token)

    yield scenario

    # 自动清理
    scenario.cleanup()


@pytest.fixture
def full_approval_result(full_approval_scenario) -> ScenarioResult:
    """
    完整审批流结果 fixture
    
    返回一个已执行完成的完整审批流结果
    
    使用示例：
        def test_with_approval_result(full_approval_result):
            assert full_approval_result.success
            reimb = full_approval_result.get_entity("reimbursement")
            assert reimb is not None
    """
    result = full_approval_scenario.execute(amount=50000)
    return result


# 导出
__all__ = [
    "full_approval_scenario",
    "full_approval_result",
]
