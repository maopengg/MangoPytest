# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 部门审批模块测试 - C级模块 (依赖D级)
# @Time   : 2026-03-31
# @Author : 毛鹏

import allure

from auto_tests.bdd_api_mock.api_manager import bdd_api_mock
from core.base.layering_base import UnitTest, IntegrationTest


@allure.feature("部门审批")
@allure.story("部门审批API")
class TestDeptApprovalAPI(IntegrationTest):
    """
    部门审批API测试类 - C级模块测试
    测试 /dept-approvals 接口
    依赖D级：Reimbursement
    """

    @allure.title("创建部门审批 - 正常通过")
    def test_create_dept_approval(
        self, authenticated_client, pending_reimbursement, dept_manager_id
    ):
        """测试创建部门审批 - 依赖D级报销申请"""
        reimbursement_id = (
            pending_reimbursement.id
            if hasattr(pending_reimbursement, "id")
            else pending_reimbursement["id"]
        )

        bdd_api_mock.dept_approval.set_token(authenticated_client.token)
        result = bdd_api_mock.dept_approval.create_dept_approval(
            reimbursement_id=reimbursement_id,
            approver_id=dept_manager_id,
            status="approved",
            comment="部门审批通过",
        )

        assert result is not None
        assert result["code"] == 200
        assert result["data"]["status"] == "approved"

    @allure.title("创建部门审批 - 报销申请不存在")
    def test_create_dept_approval_without_reimbursement(
        self, api_client, dept_manager_id
    ):
        """测试创建部门审批 - 报销申请不存在"""
        # 使用全局token设置
        if hasattr(api_client, "token") and api_client.token:
            bdd_api_mock.dept_approval.set_token(api_client.token)
        result = bdd_api_mock.dept_approval.create_dept_approval(
            reimbursement_id=99999,
            approver_id=dept_manager_id,
            status="approved",
            comment="测试",
        )

        assert result is not None
        assert result["code"] == 404

    @allure.title("创建部门审批 - 报销申请已处理")
    def test_create_dept_approval_already_processed(
        self, api_client, dept_approved_reimbursement, dept_manager_id
    ):
        """测试创建部门审批 - 报销申请已处理"""
        if hasattr(dept_approved_reimbursement, "id"):
            reimbursement_id = dept_approved_reimbursement.id
        else:
            reimbursement_id = dept_approved_reimbursement["reimbursement"]["id"]

        bdd_api_mock.dept_approval.set_token(api_client.token)
        result = bdd_api_mock.dept_approval.create_dept_approval(
            reimbursement_id=reimbursement_id,
            approver_id=dept_manager_id,
            status="approved",
            comment="重复审批",
        )

        assert result is not None
        assert result["code"] == 400

    @allure.title("获取部门审批列表")
    def test_get_dept_approvals(self, api_client, dept_approved_reimbursement):
        """测试获取部门审批列表"""
        bdd_api_mock.dept_approval.set_token(api_client.token)
        result = bdd_api_mock.dept_approval.get_dept_approvals()

        assert result is not None
        assert result["code"] == 200

    @allure.title("根据报销申请ID获取部门审批")
    def test_get_dept_approvals_by_reimbursement(
        self, api_client, dept_approved_reimbursement
    ):
        """测试根据报销申请ID获取部门审批"""
        if hasattr(dept_approved_reimbursement, "id"):
            reimbursement_id = dept_approved_reimbursement.id
        else:
            reimbursement_id = dept_approved_reimbursement["reimbursement"]["id"]

        bdd_api_mock.dept_approval.set_token(api_client.token)
        result = bdd_api_mock.dept_approval.get_dept_approval_by_id(
            approval_id=reimbursement_id
        )

        assert result is not None
        assert result["code"] == 200


@allure.feature("部门审批")
@allure.story("部门审批Builder")
class TestDeptApprovalBuilder(UnitTest):
    """
    部门审批Builder测试类
    测试数据工厂功能
    """

    @allure.title("Builder创建部门审批")
    def test_builder_create(self, dept_approval_builder, pending_reimbursement):
        """测试Builder创建部门审批"""
        approval = dept_approval_builder.create(
            reimbursement_id=pending_reimbursement["id"],
            status="approved",
            comment="测试审批",
        )

        assert approval is not None
        assert approval.id is not None
        assert approval.status == "approved"

    @allure.title("Builder快捷通过方法")
    def test_builder_approve(self, dept_approval_builder, pending_reimbursement):
        """测试Builder快捷通过方法"""
        approval = dept_approval_builder.approve(pending_reimbursement["id"])

        assert approval is not None
        assert approval.status == "approved"

    @allure.title("Builder快捷拒绝方法")
    def test_builder_reject(self, dept_approval_builder, pending_reimbursement):
        """测试Builder快捷拒绝方法"""
        approval = dept_approval_builder.reject(
            pending_reimbursement["id"], comment="不符合规定"
        )

        assert approval is not None
        assert approval.status == "rejected"

    @allure.title("Builder根据报销申请获取审批")
    def test_builder_get_by_reimbursement(
        self, dept_approval_builder, dept_approved_reimbursement
    ):
        """测试Builder根据报销申请获取审批"""
        reimbursement_id = dept_approved_reimbursement["reimbursement"]["id"]
        approval = dept_approval_builder.get_by_reimbursement(reimbursement_id)

        assert approval is not None
        assert approval.reimbursement_id == reimbursement_id

    @allure.title("Builder检查是否可以创建")
    def test_builder_can_create(self, dept_approval_builder, pending_reimbursement):
        """测试Builder检查是否可以创建"""
        can_create = dept_approval_builder.can_create(pending_reimbursement["id"])
        assert can_create is True

    @allure.title("Builder检查已处理申请无法创建")
    def test_builder_cannot_create_processed(
        self, dept_approval_builder, dept_approved_reimbursement
    ):
        """测试Builder检查已处理申请无法创建"""
        reimbursement_id = dept_approved_reimbursement["reimbursement"]["id"]
        can_create = dept_approval_builder.can_create(reimbursement_id)
        assert can_create is False
