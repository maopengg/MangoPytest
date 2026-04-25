# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 部门审批测试 - 不依赖Excel，直接调用Mock API
# @Time   : 2026-04-25
# @Author : 毛鹏

import allure
import pytest

from auto_tests.api_mock import user_info, BASE_URL
from core.api.client import APIClient


@allure.epic('演示-API自动化-常规API-MockAPI服务')
@allure.feature('部门审批模块(C级)')
class TestDeptApproval:
    """部门审批测试类 - 直接调用Mock API，不依赖Excel"""

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
    def create_test_reimbursement(self, api_client_with_token):
        """创建测试报销申请，返回报销申请ID"""
        client, headers = api_client_with_token

        # 获取用户列表
        users_response = client.get("/users", headers=headers)
        users = users_response.data.get("data", [])

        if not users:
            pytest.skip("没有可用的测试用户")

        user_id = users[0]["id"]

        # 创建报销申请
        import time
        reimbursement_data = {
            "user_id": user_id,
            "amount": 1000.00,
            "reason": "部门审批测试报销",
            "category": "travel"
        }
        response = client.post("/reimbursements", json=reimbursement_data, headers=headers)

        if response.data.get("code") == 200:
            return response.data["data"]["id"], user_id
        else:
            pytest.skip("创建报销申请失败")

    @pytest.fixture
    def get_approver_id(self, api_client_with_token):
        """获取审批人ID（使用第二个用户或第一个用户）"""
        client, headers = api_client_with_token

        users_response = client.get("/users", headers=headers)
        users = users_response.data.get("data", [])

        if len(users) >= 2:
            return users[1]["id"]
        elif len(users) == 1:
            return users[0]["id"]
        else:
            pytest.skip("没有可用的审批人")

    @allure.story("创建部门审批")
    @allure.title("部门审批通过成功")
    def test_create_dept_approval_approved(self, api_client_with_token, create_test_reimbursement, get_approver_id):
        """测试创建部门审批通过"""
        client, headers = api_client_with_token
        reimbursement_id, _ = create_test_reimbursement

        approval_data = {
            "reimbursement_id": reimbursement_id,
            "approver_id": get_approver_id,
            "status": "approved",
            "comment": "部门审批通过-符合公司规定"
        }
        response = client.post("/dept-approvals", json=approval_data, headers=headers)

        assert response.data.get("code") == 200
        assert response.data.get("message") == "部门审批创建成功"
        assert response.data["data"]["status"] == "approved"
        assert "id" in response.data["data"]

    @allure.story("创建部门审批")
    @allure.title("部门审批拒绝成功")
    def test_create_dept_approval_rejected(self, api_client_with_token, create_test_reimbursement, get_approver_id):
        """测试创建部门审批拒绝"""
        client, headers = api_client_with_token
        reimbursement_id, _ = create_test_reimbursement

        approval_data = {
            "reimbursement_id": reimbursement_id,
            "approver_id": get_approver_id,
            "status": "rejected",
            "comment": "部门审批拒绝-金额超出预算"
        }
        response = client.post("/dept-approvals", json=approval_data, headers=headers)

        assert response.data.get("code") == 200
        assert response.data["data"]["status"] == "rejected"

    @allure.story("创建部门审批")
    @allure.title("创建部门审批-缺少必填字段")
    def test_create_dept_approval_missing_fields(self, api_client_with_token):
        """测试创建部门审批缺少必填字段"""
        client, headers = api_client_with_token

        # 缺少reimbursement_id字段
        approval_data = {
            "approver_id": 1,
            "status": "approved"
        }

        from core.exceptions import ApiError
        with pytest.raises(ApiError) as exc_info:
            client.post("/dept-approvals", json=approval_data, headers=headers)

        assert "422" in str(exc_info.value)

    @allure.story("获取部门审批列表")
    @allure.title("获取所有部门审批列表")
    def test_get_all_dept_approvals(self, api_client_with_token):
        """测试获取所有部门审批列表"""
        client, headers = api_client_with_token
        response = client.get("/dept-approvals", headers=headers)

        assert response.data.get("code") == 200
        assert response.data.get("message") == "获取成功"
        assert isinstance(response.data.get("data"), list)

    @allure.story("获取部门审批列表")
    @allure.title("按报销申请ID筛选部门审批")
    def test_get_dept_approvals_by_reimbursement(self, api_client_with_token, create_test_reimbursement, get_approver_id):
        """测试按报销申请ID筛选部门审批"""
        client, headers = api_client_with_token
        reimbursement_id, _ = create_test_reimbursement

        # 先创建一个部门审批
        approval_data = {
            "reimbursement_id": reimbursement_id,
            "approver_id": get_approver_id,
            "status": "approved",
            "comment": "测试筛选"
        }
        client.post("/dept-approvals", json=approval_data, headers=headers)

        # 按报销申请ID筛选
        response = client.get("/dept-approvals", params={"reimbursement_id": reimbursement_id}, headers=headers)

        assert response.data.get("code") == 200
        # 验证返回的数据都是指定报销申请的审批
        for item in response.data.get("data", []):
            assert item["reimbursement_id"] == reimbursement_id


if __name__ == '__main__':
    pytest.main(['-v', __file__])
