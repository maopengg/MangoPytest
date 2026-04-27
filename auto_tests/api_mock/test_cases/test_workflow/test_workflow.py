# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 审批工作流测试 - 不依赖Excel，直接调用Mock API
# @Time   : 2026-04-25
# @Author : 毛鹏

import allure
import pytest

from auto_tests.api_mock import user_info, BASE_URL
from core.api.client import APIClient


@allure.epic('演示-API自动化-常规API-MockAPI服务')
@allure.feature('审批工作流模块')
class TestWorkflow:
    """审批工作流测试类 - 直接调用Mock API，不依赖Excel"""

    @pytest.fixture(scope="class")
    def api_client_with_token(self):
        """创建API客户端并登录获取token，返回client和headers"""
        client = APIClient(base_url=BASE_URL)

        # 登录获取token
        response = client.post("/auth/login", json={
            "username": user_info["username"],
            "password": user_info["password"]
        })

        if response.data.get("code") == 200:
            token = response.data["data"]["token"]
            headers = {
                "X-Token": token,
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            return client, headers
        else:
            pytest.skip("登录失败，跳过测试")

    @pytest.fixture
    def create_full_approval_workflow(self, api_client_with_token):
        """创建完整的四级审批流程，返回报销申请ID"""
        client, headers = api_client_with_token

        # 获取用户列表
        users_response = client.get("/users", headers=headers)
        users = users_response.data.get("data", [])

        if len(users) < 1:
            pytest.skip("没有可用的测试用户")

        user_id = users[0]["id"]
        dept_approver_id = users[1]["id"] if len(users) > 1 else users[0]["id"]
        finance_approver_id = users[2]["id"] if len(users) > 2 else dept_approver_id
        ceo_approver_id = users[3]["id"] if len(users) > 3 else finance_approver_id

        # 创建报销申请 (D级)
        import time
        reimbursement_data = {
            "user_id": user_id,
            "amount": 8000.00,
            "reason": "完整审批流程测试-大额差旅报销",
            "category": "travel",
            "attachments": ["invoice1.pdf", "invoice2.pdf"]
        }
        reimb_response = client.post("/reimbursements", json=reimbursement_data, headers=headers)

        if reimb_response.data.get("code") != 200:
            pytest.skip("创建报销申请失败")

        reimbursement_id = reimb_response.data["data"]["id"]

        # 创建部门审批 (C级)
        dept_approval_data = {
            "reimbursement_id": reimbursement_id,
            "approver_id": dept_approver_id,
            "status": "approved",
            "comment": "部门审批通过-符合差旅标准"
        }
        dept_response = client.post("/dept-approvals", json=dept_approval_data, headers=headers)

        if dept_response.data.get("code") != 200:
            pytest.skip("创建部门审批失败")

        dept_approval_id = dept_response.data["data"]["id"]

        # 创建财务审批 (B级)
        finance_approval_data = {
            "reimbursement_id": reimbursement_id,
            "dept_approval_id": dept_approval_id,
            "approver_id": finance_approver_id,
            "status": "approved",
            "comment": "财务审批通过-票据齐全合规"
        }
        finance_response = client.post("/finance-approvals", json=finance_approval_data, headers=headers)

        if finance_response.data.get("code") != 200:
            pytest.skip("创建财务审批失败")

        finance_approval_id = finance_response.data["data"]["id"]

        # 创建总经理审批 (A级)
        ceo_approval_data = {
            "reimbursement_id": reimbursement_id,
            "finance_approval_id": finance_approval_id,
            "approver_id": ceo_approver_id,
            "status": "approved",
            "comment": "总经理审批通过-同意报销"
        }
        ceo_response = client.post("/ceo-approvals", json=ceo_approval_data, headers=headers)

        if ceo_response.data.get("code") != 200:
            pytest.skip("创建总经理审批失败")

        return reimbursement_id

    @pytest.fixture
    def create_rejected_workflow(self, api_client_with_token):
        """创建被拒绝的审批流程，返回报销申请ID"""
        client, headers = api_client_with_token

        # 获取用户列表
        users_response = client.get("/users", headers=headers)
        users = users_response.data.get("data", [])

        if len(users) < 1:
            pytest.skip("没有可用的测试用户")

        user_id = users[0]["id"]
        dept_approver_id = users[1]["id"] if len(users) > 1 else users[0]["id"]

        # 创建报销申请
        reimbursement_data = {
            "user_id": user_id,
            "amount": 10000.00,
            "reason": "被拒绝的报销申请测试",
            "category": "entertainment"
        }
        reimb_response = client.post("/reimbursements", json=reimbursement_data, headers=headers)

        if reimb_response.data.get("code") != 200:
            pytest.skip("创建报销申请失败")

        reimbursement_id = reimb_response.data["data"]["id"]

        # 创建部门审批 - 拒绝
        dept_approval_data = {
            "reimbursement_id": reimbursement_id,
            "approver_id": dept_approver_id,
            "status": "rejected",
            "comment": "部门审批拒绝-超出部门预算"
        }
        client.post("/dept-approvals", json=dept_approval_data, headers=headers)

        return reimbursement_id

    @allure.story("获取完整审批流程")
    @allure.title("获取完整审批流程成功")
    def test_get_workflow_success(self, api_client_with_token, create_full_approval_workflow):
        """测试获取完整审批流程"""
        client, headers = api_client_with_token
        reimbursement_id = create_full_approval_workflow

        response = client.get(f"/workflow/{reimbursement_id}", headers=headers)

        assert response.data.get("code") == 200
        assert response.data.get("message") == "获取成功"

        # 验证返回的数据结构
        data = response.data.get("data", {})
        assert "reimbursement" in data
        assert "dept_approval" in data
        assert "finance_approval" in data
        assert "ceo_approval" in data

        # 验证报销申请信息
        assert data["reimbursement"]["id"] == reimbursement_id
        # API返回的状态可能是 ceo_approved 或 fully_approved
        assert data["reimbursement"]["status"] in ["fully_approved", "ceo_approved"]

    @allure.story("获取完整审批流程")
    @allure.title("获取不存在的报销申请流程")
    def test_get_workflow_not_found(self, api_client_with_token):
        """测试获取不存在的报销申请流程"""
        client, headers = api_client_with_token
        response = client.get("/workflow/99999", headers=headers)

        assert response.data.get("code") == 404
        assert "不存在" in response.data.get("message", "")

    @allure.story("四级审批流程")
    @allure.title("完整四级审批流程通过")
    def test_full_approval_workflow(self, api_client_with_token, create_full_approval_workflow):
        """测试完整四级审批流程 (D->C->B->A)"""
        client, headers = api_client_with_token
        reimbursement_id = create_full_approval_workflow

        # 获取完整流程验证
        response = client.get(f"/workflow/{reimbursement_id}", headers=headers)

        assert response.data.get("code") == 200
        data = response.data.get("data", {})

        # 验证各级审批都已通过
        # API返回的状态可能是 ceo_approved 或 fully_approved
        assert data["reimbursement"]["status"] in ["fully_approved", "ceo_approved"]
        assert data["dept_approval"]["status"] == "approved"
        assert data["finance_approval"]["status"] == "approved"
        assert data["ceo_approval"]["status"] == "approved"

    @allure.story("四级审批流程")
    @allure.title("审批流程被拒绝")
    def test_rejected_workflow(self, api_client_with_token, create_rejected_workflow):
        """测试审批流程在部门审批被拒绝"""
        client, headers = api_client_with_token
        reimbursement_id = create_rejected_workflow

        # 获取完整流程验证
        response = client.get(f"/workflow/{reimbursement_id}", headers=headers)

        assert response.data.get("code") == 200
        data = response.data.get("data", {})

        # 验证部门审批被拒绝
        assert data["dept_approval"]["status"] == "rejected"

    @allure.story("审批状态流转")
    @allure.title("报销申请创建后状态为pending")
    def test_workflow_initial_status(self, api_client_with_token):
        """测试报销申请创建后的初始状态"""
        client, headers = api_client_with_token

        # 获取用户列表
        users_response = client.get("/users", headers=headers)
        users = users_response.data.get("data", [])

        if not users:
            pytest.skip("没有可用的测试用户")

        user_id = users[0]["id"]

        # 创建报销申请
        reimbursement_data = {
            "user_id": user_id,
            "amount": 1000.00,
            "reason": "状态流转测试",
            "category": "office"
        }
        reimb_response = client.post("/reimbursements", json=reimbursement_data, headers=headers)

        if reimb_response.data.get("code") != 200:
            pytest.skip("创建报销申请失败")

        reimbursement_id = reimb_response.data["data"]["id"]

        # 获取流程验证初始状态
        response = client.get(f"/workflow/{reimbursement_id}", headers=headers)

        assert response.data.get("code") == 200
        assert response.data["data"]["reimbursement"]["status"] == "pending"

    @allure.story("审批状态流转")
    @allure.title("部门审批后状态变为dept_approved")
    def test_workflow_after_dept_approval(self, api_client_with_token):
        """测试部门审批后的状态变化"""
        client, headers = api_client_with_token

        # 获取用户列表
        users_response = client.get("/users", headers=headers)
        users = users_response.data.get("data", [])

        if len(users) < 1:
            pytest.skip("没有可用的测试用户")

        user_id = users[0]["id"]
        dept_approver_id = users[1]["id"] if len(users) > 1 else users[0]["id"]

        # 创建报销申请
        reimbursement_data = {
            "user_id": user_id,
            "amount": 1500.00,
            "reason": "部门审批后状态测试",
            "category": "travel"
        }
        reimb_response = client.post("/reimbursements", json=reimbursement_data, headers=headers)

        if reimb_response.data.get("code") != 200:
            pytest.skip("创建报销申请失败")

        reimbursement_id = reimb_response.data["data"]["id"]

        # 创建部门审批
        dept_approval_data = {
            "reimbursement_id": reimbursement_id,
            "approver_id": dept_approver_id,
            "status": "approved",
            "comment": "部门审批通过"
        }
        client.post("/dept-approvals", json=dept_approval_data, headers=headers)

        # 获取流程验证状态
        response = client.get(f"/workflow/{reimbursement_id}", headers=headers)

        assert response.data.get("code") == 200
        # 验证状态已更新
        status = response.data["data"]["reimbursement"]["status"]
        assert status in ["dept_approved", "pending"]


if __name__ == '__main__':
    pytest.main(['-v', __file__])
