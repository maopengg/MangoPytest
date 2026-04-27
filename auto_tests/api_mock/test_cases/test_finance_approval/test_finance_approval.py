# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 财务审批测试 - 不依赖Excel，直接调用Mock API
# @Time   : 2026-04-25
# @Author : 毛鹏

import allure
import pytest

from auto_tests.api_mock import user_info, BASE_URL
from core.api.client import APIClient


@allure.epic('演示-API自动化-常规API-MockAPI服务')
@allure.feature('财务审批模块(B级)')
class TestFinanceApproval:
    """财务审批测试类 - 直接调用Mock API，不依赖Excel"""

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
    def create_test_dept_approval(self, api_client_with_token):
        """创建测试部门审批，返回报销申请ID、部门审批ID和审批人ID"""
        client, headers = api_client_with_token

        # 获取用户列表
        users_response = client.get("/users", headers=headers)
        users = users_response.data.get("data", [])

        if not users:
            pytest.skip("没有可用的测试用户")

        user_id = users[0]["id"]
        approver_id = users[1]["id"] if len(users) > 1 else users[0]["id"]

        # 创建报销申请
        import time
        reimbursement_data = {
            "user_id": user_id,
            "amount": 2000.00,
            "reason": "财务审批测试报销",
            "category": "office"
        }
        reimb_response = client.post("/reimbursements", json=reimbursement_data, headers=headers)

        if reimb_response.data.get("code") != 200:
            pytest.skip("创建报销申请失败")

        reimbursement_id = reimb_response.data["data"]["id"]

        # 创建部门审批
        dept_approval_data = {
            "reimbursement_id": reimbursement_id,
            "approver_id": approver_id,
            "status": "approved",
            "comment": "部门审批通过"
        }
        dept_response = client.post("/dept-approvals", json=dept_approval_data, headers=headers)

        if dept_response.data.get("code") != 200:
            pytest.skip("创建部门审批失败")

        dept_approval_id = dept_response.data["data"]["id"]

        return reimbursement_id, dept_approval_id, approver_id

    @allure.story("创建财务审批")
    @allure.title("财务审批通过成功")
    def test_create_finance_approval_approved(self, api_client_with_token, create_test_dept_approval):
        """测试创建财务审批通过"""
        client, headers = api_client_with_token
        reimbursement_id, dept_approval_id, approver_id = create_test_dept_approval

        # 使用不同的审批人（如果可能）
        users_response = client.get("/users", headers=headers)
        users = users_response.data.get("data", [])
        finance_approver_id = users[2]["id"] if len(users) > 2 else approver_id

        approval_data = {
            "reimbursement_id": reimbursement_id,
            "dept_approval_id": dept_approval_id,
            "approver_id": finance_approver_id,
            "status": "approved",
            "comment": "财务审批通过-票据齐全"
        }
        response = client.post("/finance-approvals", json=approval_data, headers=headers)

        assert response.data.get("code") == 200
        assert response.data.get("message") == "财务审批创建成功"
        assert response.data["data"]["status"] == "approved"
        assert "id" in response.data["data"]

    @allure.story("创建财务审批")
    @allure.title("财务审批拒绝成功")
    def test_create_finance_approval_rejected(self, api_client_with_token, create_test_dept_approval):
        """测试创建财务审批拒绝"""
        client, headers = api_client_with_token
        reimbursement_id, dept_approval_id, approver_id = create_test_dept_approval

        users_response = client.get("/users", headers=headers)
        users = users_response.data.get("data", [])
        finance_approver_id = users[2]["id"] if len(users) > 2 else approver_id

        approval_data = {
            "reimbursement_id": reimbursement_id,
            "dept_approval_id": dept_approval_id,
            "approver_id": finance_approver_id,
            "status": "rejected",
            "comment": "财务审批拒绝-票据不合规"
        }
        response = client.post("/finance-approvals", json=approval_data, headers=headers)

        assert response.data.get("code") == 200
        assert response.data["data"]["status"] == "rejected"

    @allure.story("创建财务审批")
    @allure.title("创建财务审批-缺少必填字段")
    def test_create_finance_approval_missing_fields(self, api_client_with_token):
        """测试创建财务审批缺少必填字段"""
        client, headers = api_client_with_token

        # 缺少dept_approval_id字段
        approval_data = {
            "reimbursement_id": 1,
            "approver_id": 1,
            "status": "approved"
        }

        from core.exceptions import ApiError
        with pytest.raises(ApiError) as exc_info:
            client.post("/finance-approvals", json=approval_data, headers=headers)

        assert "422" in str(exc_info.value)

    @allure.story("获取财务审批列表")
    @allure.title("获取所有财务审批列表")
    def test_get_all_finance_approvals(self, api_client_with_token):
        """测试获取所有财务审批列表"""
        client, headers = api_client_with_token
        response = client.get("/finance-approvals", headers=headers)

        assert response.data.get("code") == 200
        assert response.data.get("message") == "获取成功"
        assert isinstance(response.data.get("data"), list)

    @allure.story("获取财务审批列表")
    @allure.title("按报销申请ID筛选财务审批")
    def test_get_finance_approvals_by_reimbursement(self, api_client_with_token, create_test_dept_approval):
        """测试按报销申请ID筛选财务审批"""
        client, headers = api_client_with_token
        reimbursement_id, dept_approval_id, approver_id = create_test_dept_approval

        # 先创建一个财务审批
        users_response = client.get("/users", headers=headers)
        users = users_response.data.get("data", [])
        finance_approver_id = users[2]["id"] if len(users) > 2 else approver_id

        approval_data = {
            "reimbursement_id": reimbursement_id,
            "dept_approval_id": dept_approval_id,
            "approver_id": finance_approver_id,
            "status": "approved",
            "comment": "测试筛选"
        }
        client.post("/finance-approvals", json=approval_data, headers=headers)

        # 按报销申请ID筛选
        response = client.get("/finance-approvals", params={"reimbursement_id": reimbursement_id}, headers=headers)

        assert response.data.get("code") == 200
        # 验证返回的数据都是指定报销申请的审批
        for item in response.data.get("data", []):
            assert item["reimbursement_id"] == reimbursement_id


if __name__ == '__main__':
    pytest.main(['-v', __file__])
