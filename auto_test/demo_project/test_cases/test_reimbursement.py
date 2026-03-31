# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 报销申请模块测试 - D级模块 (基础层)
# @Time   : 2026-03-31
# @Author : 毛鹏
import pytest

from auto_test.demo_project.api_manager import demo_project
from auto_test.demo_project.fixtures.conftest import *
from models.api_model import ApiDataModel, RequestModel


class TestReimbursementAPI:
    """
    报销申请API测试类 - D级模块测试
    测试 /reimbursements 接口
    """

    def test_create_reimbursement(self, api_client, reimbursement_builder):
        """测试创建报销申请"""
        # 使用数据工厂创建报销申请数据
        reimbursement_data = reimbursement_builder.build(
            user_id=1,
            amount=500.00,
            reason="测试报销"
        )

        # 构造API请求
        api_data = ApiDataModel(
            request=RequestModel(
                url="/reimbursements",
                method="POST",
                headers={"Authorization": f"Bearer {api_client.token}"},
                json_data=reimbursement_data
            )
        )

        # 调用API
        result = demo_project.reimbursement.create_reimbursement(api_data)

        # 验证结果
        assert result.response is not None
        assert result.response.json()["code"] == 200
        assert result.response.json()["data"]["status"] == "pending"
        assert result.response.json()["data"]["amount"] == 500.00

    def test_create_reimbursement_invalid_amount(self, api_client):
        """测试创建报销申请 - 金额无效"""
        api_data = ApiDataModel(
            request=RequestModel(
                url="/reimbursements",
                method="POST",
                headers={"Authorization": f"Bearer {api_client.token}"},
                json_data={
                    "user_id": 1,
                    "amount": -100.00,
                    "reason": "无效金额测试"
                }
            )
        )

        result = demo_project.reimbursement.create_reimbursement(api_data)

        assert result.response is not None
        assert result.response.json()["code"] == 400

    def test_get_reimbursements(self, api_client, created_reimbursement):
        """测试获取报销申请列表"""
        api_data = ApiDataModel(
            request=RequestModel(
                url="/reimbursements",
                method="GET",
                headers={"Authorization": f"Bearer {api_client.token}"}
            )
        )

        result = demo_project.reimbursement.get_reimbursements(api_data)

        assert result.response is not None
        assert result.response.json()["code"] == 200
        assert isinstance(result.response.json()["data"], list)

    def test_get_reimbursement_by_id(self, api_client, created_reimbursement):
        """测试根据ID获取报销申请"""
        reimbursement_id = created_reimbursement["id"]

        api_data = ApiDataModel(
            request=RequestModel(
                url="/reimbursements",
                method="GET",
                headers={"Authorization": f"Bearer {api_client.token}"},
                params={"id": reimbursement_id}
            )
        )

        result = demo_project.reimbursement.get_reimbursement_by_id(api_data)

        assert result.response is not None
        assert result.response.json()["code"] == 200
        assert result.response.json()["data"]["id"] == reimbursement_id

    def test_update_reimbursement(self, api_client, pending_reimbursement):
        """测试更新报销申请（pending状态）"""
        reimbursement_id = pending_reimbursement["id"]

        api_data = ApiDataModel(
            request=RequestModel(
                url="/reimbursements",
                method="PUT",
                headers={"Authorization": f"Bearer {api_client.token}"},
                params={"reimbursement_id": reimbursement_id},
                json_data={
                    "user_id": 1,
                    "amount": 800.00,
                    "reason": "更新后的报销原因"
                }
            )
        )

        result = demo_project.reimbursement.update_reimbursement(api_data)

        assert result.response is not None
        assert result.response.json()["code"] == 200
        assert result.response.json()["data"]["amount"] == 800.00

    def test_delete_reimbursement(self, api_client, reimbursement_builder):
        """测试删除报销申请"""
        # 创建一个新的报销申请用于删除测试
        reimbursement = reimbursement_builder.create(
            user_id=1,
            amount=100.00,
            reason="删除测试"
        )
        reimbursement_id = reimbursement["id"]

        api_data = ApiDataModel(
            request=RequestModel(
                url="/reimbursements",
                method="DELETE",
                headers={"Authorization": f"Bearer {api_client.token}"},
                params={"reimbursement_id": reimbursement_id}
            )
        )

        result = demo_project.reimbursement.delete_reimbursement(api_data)

        assert result.response is not None
        assert result.response.json()["code"] == 200


class TestReimbursementBuilder:
    """
    报销申请Builder测试类
    测试数据工厂功能
    """

    def test_builder_create(self, reimbursement_builder):
        """测试Builder创建报销申请"""
        reimbursement = reimbursement_builder.create(
            user_id=1,
            amount=1000.00,
            reason="Builder测试"
        )

        assert reimbursement is not None
        assert reimbursement["id"] is not None
        assert reimbursement["status"] == "pending"
        assert reimbursement["amount"] == 1000.00

    def test_builder_get_by_id(self, reimbursement_builder, created_reimbursement):
        """测试Builder根据ID获取"""
        reimbursement_id = created_reimbursement["id"]
        fetched = reimbursement_builder.get_by_id(reimbursement_id)

        assert fetched is not None
        assert fetched["id"] == reimbursement_id

    def test_builder_update(self, reimbursement_builder, pending_reimbursement):
        """测试Builder更新"""
        reimbursement_id = pending_reimbursement["id"]

        updated = reimbursement_builder.update(
            reimbursement_id,
            {"user_id": 1, "amount": 1500.00, "reason": "更新测试"}
        )

        assert updated is not None
        assert updated["amount"] == 1500.00

    def test_builder_is_pending(self, reimbursement_builder, pending_reimbursement):
        """测试Builder检查pending状态"""
        assert reimbursement_builder.is_pending(pending_reimbursement["id"]) is True

    def test_builder_get_status(self, reimbursement_builder, created_reimbursement):
        """测试Builder获取状态"""
        status = reimbursement_builder.get_status(created_reimbursement["id"])
        assert status == "pending"
