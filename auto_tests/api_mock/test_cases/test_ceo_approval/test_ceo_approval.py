# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 总经理审批测试 - 不依赖Excel，直接调用Mock API
# @Time   : 2026-04-25
# @Author : 毛鹏

import allure
import pytest

from auto_tests.api_mock import user_info, BASE_URL
from core.api.client import APIClient


@allure.epic('演示-API自动化-常规API-MockAPI服务')
@allure.feature('总经理审批模块(A级)')
class TestCeoApproval:
    """总经理审批测试类 - 直接调用Mock API，不依赖Excel"""

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
    def create_test_finance_approval(self, api_client_with_token):
        """创建测试财务审批，返回报销申请ID、财务审批ID和审批人ID"""
        client, headers = api_client_with_token

        # 获取用户列表
        users_response = client.get("/users", headers=headers)
        users = users_response.data.get("data", [])

        if not users:
            pytest.skip("没有可用的测试用户")

        user_id = users[0]["id"]
        dept_approver_id = users[1]["id"] if len(users) > 1 else users[0]["id"]
        finance_approver_id = users[2]["id"] if len(users) > 2 else dept_approver_id

        # 创建报销申请
        import time
        reimbursement_data = {
            "user_id": user_id,
            "amount": 5000.00,
            "reason": "总经理审批测试报销-大额",
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
        dept_response = client.post("/dept-approvals", json=dept_approval_data, headers=headers)

        if dept_response.data.get("code") != 200:
            pytest.skip("创建部门审批失败")

        dept_approval_id = dept_response.data["data"]["id"]

        # 创建财务审批
        finance_approval_data = {
            "reimbursement_id": reimbursement_id,
            "dept_approval_id": dept_approval_id,
            "approver_id": finance_approver_id,
            "status": "approved",
            "comment": "财务审批通过"
        }
        finance_response = client.post("/finance-approvals", json=finance_approval_data, headers=headers)

        if finance_response.data.get("code") != 200:
            pytest.skip("创建财务审批失败")

        finance_approval_id = finance_response.data["data"]["id"]

        return reimbursement_id, finance_approval_id, finance_approver_id

    @allure.story("创建总经理审批")
    @allure.title("总经理审批通过成功")
    def test_create_ceo_approval_approved(self, api_client_with_token, create_test_finance_approval):
        """测试创建总经理审批通过"""
        client, headers = api_client_with_token
        reimbursement_id, finance_approval_id, _ = create_test_finance_approval

        # 使用CEO审批人（如果可能，使用不同的用户）
        users_response = client.get("/users", headers=headers)
        users = users_response.data.get("data", [])
        ceo_approver_id = users[3]["id"] if len(users) > 3 else users[0]["id"]

        approval_data = {
            "reimbursement_id": reimbursement_id,
            "finance_approval_id": finance_approval_id,
            "approver_id": ceo_approver_id,
            "status": "approved",
            "comment": "总经理审批通过-同意报销"
        }
        response = client.post("/ceo-approvals", json=approval_data, headers=headers)

        assert response.data.get("code") == 200
        assert response.data.get("message") == "总经理审批创建成功"
        assert response.data["data"]["status"] == "approved"
        assert "id" in response.data["data"]

    @allure.story("创建总经理审批")
    @allure.title("总经理审批拒绝成功")
    def test_create_ceo_approval_rejected(self, api_client_with_token, create_test_finance_approval):
        """测试创建总经理审批拒绝"""
        client, headers = api_client_with_token
        reimbursement_id, finance_approval_id, _ = create_test_finance_approval

        users_response = client.get("/users", headers=headers)
        users = users_response.data.get("data", [])
        ceo_approver_id = users[3]["id"] if len(users) > 3 else users[0]["id"]

        approval_data = {
            "reimbursement_id": reimbursement_id,
            "finance_approval_id": finance_approval_id,
            "approver_id": ceo_approver_id,
            "status": "rejected",
            "comment": "总经理审批拒绝-金额过大"
        }
        response = client.post("/ceo-approvals", json=approval_data, headers=headers)

        assert response.data.get("code") == 200
        assert response.data["data"]["status"] == "rejected"

    @allure.story("创建总经理审批")
    @allure.title("创建总经理审批-缺少必填字段")
    def test_create_ceo_approval_missing_fields(self, api_client_with_token):
        """测试创建总经理审批缺少必填字段"""
        client, headers = api_client_with_token

        # 缺少finance_approval_id字段
        approval_data = {
            "reimbursement_id": 1,
            "approver_id": 1,
            "status": "approved"
        }

        from core.exceptions import ApiError
        with pytest.raises(ApiError) as exc_info:
            client.post("/ceo-approvals", json=approval_data, headers=headers)

        assert "422" in str(exc_info.value)

    @allure.story("获取总经理审批列表")
    @allure.title("获取所有总经理审批列表")
    def test_get_all_ceo_approvals(self, api_client_with_token):
        """测试获取所有总经理审批列表"""
        client, headers = api_client_with_token
        response = client.get("/ceo-approvals", headers=headers)

        assert response.data.get("code") == 200
        assert response.data.get("message") == "获取成功"
        assert isinstance(response.data.get("data"), list)

    @allure.story("获取总经理审批列表")
    @allure.title("按报销申请ID筛选总经理审批")
    def test_get_ceo_approvals_by_reimbursement(self, api_client_with_token, create_test_finance_approval):
        """测试按报销申请ID筛选总经理审批"""
        client, headers = api_client_with_token
        reimbursement_id, finance_approval_id, _ = create_test_finance_approval

        # 先创建一个总经理审批
        users_response = client.get("/users", headers=headers)
        users = users_response.data.get("data", [])
        ceo_approver_id = users[3]["id"] if len(users) > 3 else users[0]["id"]

        approval_data = {
            "reimbursement_id": reimbursement_id,
            "finance_approval_id": finance_approval_id,
            "approver_id": ceo_approver_id,
            "status": "approved",
            "comment": "测试筛选"
        }
        client.post("/ceo-approvals", json=approval_data, headers=headers)

        # 按报销申请ID筛选
        response = client.get("/ceo-approvals", params={"reimbursement_id": reimbursement_id}, headers=headers)

        assert response.data.get("code") == 200
        # 验证返回的数据都是指定报销申请的审批
        for item in response.data.get("data", []):
            assert item["reimbursement_id"] == reimbursement_id


if __name__ == '__main__':
    pytest.main(['-v', __file__])
