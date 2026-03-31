# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 审批流场景fixtures
# @Time   : 2026-03-31
# @Author : 毛鹏
import pytest

from auto_test.demo_project.data_factory.scenarios import ApprovalScenarios


@pytest.fixture
def approval_scenarios(api_client) -> ApprovalScenarios:
    """
    审批流场景Fixture
    提供ApprovalScenarios实例用于创建各种审批流程场景

    使用示例:
        def test_with_scenario(approval_scenarios):
            workflow = approval_scenarios.create_full_approval_workflow()
            assert workflow["status"] == "fully_approved"
    """
    scenarios = ApprovalScenarios(token=api_client.token)
    yield scenarios
    # 场景类不负责清理，由各个builder负责


@pytest.fixture
def full_approval_workflow(approval_scenarios) -> dict:
    """
    完整4级审批流程Fixture
    创建D->C->B->A全部通过的审批流程
    """
    return approval_scenarios.create_full_approval_workflow(
        user_id=1,
        amount=5000.00,
        reason="完整审批流程测试",
        approved=True
    )


@pytest.fixture
def dept_rejected_workflow(approval_scenarios) -> dict:
    """
    部门审批拒绝场景Fixture
    创建D->C(rejected)的审批流程
    """
    return approval_scenarios.create_dept_rejected_workflow(
        user_id=1,
        amount=1000.00,
        reason="部门拒绝场景测试",
        comment="不符合报销规定"
    )


@pytest.fixture
def finance_rejected_workflow(approval_scenarios) -> dict:
    """
    财务审批拒绝场景Fixture
    创建D->C->B(rejected)的审批流程
    """
    return approval_scenarios.create_finance_rejected_workflow(
        user_id=1,
        amount=8000.00,
        reason="财务拒绝场景测试",
        comment="超出部门预算"
    )


@pytest.fixture
def ceo_rejected_workflow(approval_scenarios) -> dict:
    """
    总经理审批拒绝场景Fixture
    创建D->C->B->A(rejected)的审批流程
    """
    return approval_scenarios.create_ceo_rejected_workflow(
        user_id=1,
        amount=50000.00,
        reason="总经理拒绝场景测试",
        comment="金额过大，需要特殊审批"
    )


@pytest.fixture
def pending_at_dept(approval_scenarios) -> dict:
    """
    待部门审批场景Fixture
    创建D(created)状态，等待C级审批
    """
    return approval_scenarios.create_pending_at_dept(
        user_id=1,
        amount=500.00,
        reason="待部门审批测试"
    )


@pytest.fixture
def pending_at_finance(approval_scenarios) -> dict:
    """
    待财务审批场景Fixture
    创建D->C(approved)状态，等待B级审批
    """
    return approval_scenarios.create_pending_at_finance(
        user_id=1,
        amount=2000.00,
        reason="待财务审批测试"
    )


@pytest.fixture
def pending_at_ceo(approval_scenarios) -> dict:
    """
    待总经理审批场景Fixture
    创建D->C->B(approved)状态，等待A级审批
    """
    return approval_scenarios.create_pending_at_ceo(
        user_id=1,
        amount=10000.00,
        reason="待总经理审批测试"
    )


@pytest.fixture
def multi_level_workflows(approval_scenarios) -> list:
    """
    多级审批流程集合Fixture
    创建多个不同状态的审批流程用于批量测试
    """
    workflows = []

    # 完整通过流程
    workflows.append(approval_scenarios.create_full_approval_workflow(
        user_id=1, amount=1000.00, reason="流程1-通过"
    ))

    # 部门拒绝流程
    workflows.append(approval_scenarios.create_dept_rejected_workflow(
        user_id=1, amount=2000.00, reason="流程2-部门拒绝"
    ))

    # 财务拒绝流程
    workflows.append(approval_scenarios.create_finance_rejected_workflow(
        user_id=1, amount=3000.00, reason="流程3-财务拒绝"
    ))

    # 总经理拒绝流程
    workflows.append(approval_scenarios.create_ceo_rejected_workflow(
        user_id=1, amount=4000.00, reason="流程4-总经理拒绝"
    ))

    return workflows
