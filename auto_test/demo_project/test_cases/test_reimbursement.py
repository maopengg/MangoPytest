# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 报销申请模块测试 - 新架构版本 (D级模块)
# @Time   : 2026-04-01
# @Author : 毛鹏
"""
报销申请模块测试 - 使用新架构特性：
- UnitTest/IntegrationTest 分层基类
- Fixture 分层结构 (reimbursement_builder, created_reimbursement)
- test_context 上下文管理
- 场景层依赖声明
"""

import allure

from core.base.layering_base import UnitTest, IntegrationTest


@allure.feature("报销申请")
@allure.story("创建报销申请")
class TestCreateReimbursement(UnitTest):
    """创建报销申请测试 - D级模块"""

    @allure.title("正常创建报销申请 - 使用Builder")
    def test_create_reimbursement_with_builder(self, reimbursement_builder, test_context):
        """测试使用Builder创建报销申请"""
        reimbursement = reimbursement_builder.create(
            user_id=1,
            amount=500.00,
            reason="测试报销"
        )

        assert reimbursement is not None
        assert reimbursement.id is not None
        assert reimbursement.status == "pending"
        assert reimbursement.amount == 500.00

        test_context.set("reimbursement", reimbursement)

    @allure.title("创建报销申请 - 使用Fixture")
    def test_create_reimbursement_with_fixture(self, created_reimbursement):
        """测试使用created_reimbursement fixture"""
        assert created_reimbursement is not None
        assert created_reimbursement.id is not None
        assert created_reimbursement.status == "pending"

    @allure.title("创建报销申请 - 使用API Client")
    def test_create_reimbursement_with_api(self, authenticated_client):
        """测试使用API Client创建报销申请"""
        result = authenticated_client.reimbursement.create_reimbursement(
            user_id=1,
            amount=1000.00,
            reason="API测试报销"
        )

        assert result["code"] == 200
        assert result["data"]["status"] == "pending"
        assert result["data"]["amount"] == 1000.00

    @allure.title("创建报销申请 - 金额无效")
    def test_create_reimbursement_invalid_amount(self, authenticated_client):
        """测试创建报销申请 - 金额无效"""
        result = authenticated_client.reimbursement.create_reimbursement(
            user_id=1,
            amount=-100.00,
            reason="无效金额测试"
        )

        assert result["code"] == 400

    @allure.title("创建报销申请 - 零金额")
    def test_create_reimbursement_zero_amount(self, authenticated_client):
        """测试创建报销申请 - 零金额"""
        result = authenticated_client.reimbursement.create_reimbursement(
            user_id=1,
            amount=0,
            reason="零金额测试"
        )

        assert result["code"] == 400

    @allure.title("创建报销申请 - 大金额")
    def test_create_reimbursement_large_amount(self, reimbursement_builder, test_context):
        """测试创建大金额报销申请"""
        reimbursement = reimbursement_builder.create(
            user_id=1,
            amount=99999.99,
            reason="大金额测试"
        )

        assert reimbursement is not None
        assert reimbursement.amount == 99999.99

        test_context.set("reimbursement", reimbursement)

    @allure.title("批量创建报销申请")
    def test_create_multiple_reimbursements(self, reimbursement_builder, test_context):
        """测试批量创建报销申请"""
        reimbursements = []

        for i in range(3):
            reimbursement = reimbursement_builder.create(
                user_id=1,
                amount=100.00 * (i + 1),
                reason=f"批量测试报销 {i + 1}"
            )
            assert reimbursement is not None
            reimbursements.append(reimbursement)
            test_context.set(f"reimbursement_{i}", reimbursement)

        assert len(reimbursements) == 3

        # 验证ID各不相同
        ids = [r.id for r in reimbursements]
        assert len(set(ids)) == 3

        test_context.set("reimbursements", reimbursements)


@allure.feature("报销申请")
@allure.story("获取报销申请")
class TestGetReimbursements(UnitTest):
    """获取报销申请测试"""

    @allure.title("获取所有报销申请")
    def test_get_all_reimbursements(self, authenticated_client):
        """测试获取报销申请列表"""
        result = authenticated_client.reimbursement.get_reimbursements()

        assert result["code"] == 200
        assert isinstance(result["data"], list)

    @allure.title("根据ID获取报销申请 - 使用Fixture")
    def test_get_reimbursement_by_id_with_fixture(self, authenticated_client, created_reimbursement):
        """测试根据ID获取报销申请"""
        reimbursement_id = created_reimbursement.id

        result = authenticated_client.reimbursement.get_reimbursement_by_id(reimbursement_id)

        assert result["code"] == 200
        assert result["data"]["id"] == reimbursement_id

    @allure.title("获取不存在的报销申请")
    def test_get_nonexistent_reimbursement(self, authenticated_client):
        """测试获取不存在的报销申请"""
        result = authenticated_client.reimbursement.get_reimbursement_by_id(99999)

        assert result["code"] == 404


@allure.feature("报销申请")
@allure.story("更新报销申请")
class TestUpdateReimbursement(UnitTest):
    """更新报销申请测试"""

    @allure.title("正常更新报销申请 - pending状态")
    def test_update_reimbursement_success(self, authenticated_client, pending_reimbursement, test_context):
        """测试更新pending状态的报销申请"""
        reimbursement_id = pending_reimbursement["id"]

        result = authenticated_client.reimbursement.update_reimbursement(
            reimbursement_id=reimbursement_id,
            user_id=1,
            amount=800.00,
            reason="更新后的报销原因"
        )

        if result.get("code") == 200:
            assert result["data"]["amount"] == 800.00

        test_context.set("result", result)

    @allure.title("更新报销申请 - 使用Builder")
    def test_update_reimbursement_with_builder(self, reimbursement_builder, pending_reimbursement, test_context):
        """测试使用Builder更新报销申请"""
        reimbursement_id = pending_reimbursement["id"]

        # 先获取当前的报销申请
        current = reimbursement_builder.get_by_id(reimbursement_id)
        if current:
            current.amount = 1500.00
            current.reason = "Builder更新测试"
            updated = reimbursement_builder.update(current)

            assert updated is not None
            assert updated.amount == 1500.00

            test_context.set("updated_reimbursement", updated)

    @allure.title("更新不存在的报销申请")
    def test_update_nonexistent_reimbursement(self, authenticated_client):
        """测试更新不存在的报销申请"""
        result = authenticated_client.reimbursement.update_reimbursement(
            reimbursement_id=99999,
            user_id=1,
            amount=500.00,
            reason="不存在的报销"
        )

        assert result["code"] == 404


@allure.feature("报销申请")
@allure.story("删除报销申请")
class TestDeleteReimbursement(UnitTest):
    """删除报销申请测试"""

    @allure.title("正常删除报销申请")
    def test_delete_reimbursement_success(self, authenticated_client, reimbursement_builder):
        """测试正常删除报销申请"""
        # 创建一个新的报销申请用于删除测试
        reimbursement = reimbursement_builder.create(
            user_id=1,
            amount=100.00,
            reason="删除测试"
        )
        reimbursement_id = reimbursement.id

        result = authenticated_client.reimbursement.delete_reimbursement(reimbursement_id)

        assert result["code"] == 200

        # 验证已删除
        get_result = authenticated_client.reimbursement.get_reimbursement_by_id(reimbursement_id)
        assert get_result["code"] == 404

    @allure.title("删除不存在的报销申请")
    def test_delete_nonexistent_reimbursement(self, authenticated_client):
        """测试删除不存在的报销申请"""
        result = authenticated_client.reimbursement.delete_reimbursement(99999)

        assert result["code"] == 404


@allure.feature("报销申请")
@allure.story("报销申请状态管理")
class TestReimbursementStatusManagement(UnitTest):
    """报销申请状态管理测试"""

    @allure.title("验证pending状态")
    def test_verify_pending_status(self, reimbursement_builder, pending_reimbursement):
        """验证pending状态"""
        assert reimbursement_builder.is_pending(pending_reimbursement["id"]) is True

    @allure.title("获取报销申请状态")
    def test_get_reimbursement_status(self, reimbursement_builder, created_reimbursement):
        """测试获取报销申请状态"""
        status = reimbursement_builder.get_status(created_reimbursement.id)
        assert status == "pending"

    @allure.title("新报销申请默认状态")
    def test_new_reimbursement_default_status(self, reimbursement_builder, test_context):
        """测试新报销申请默认状态"""
        reimbursement = reimbursement_builder.create(
            user_id=1,
            amount=500.00,
            reason="状态测试"
        )

        assert reimbursement.status == "pending"

        test_context.set("reimbursement", reimbursement)


@allure.feature("报销申请")
@allure.story("报销申请集成测试")
class TestReimbursementIntegration(IntegrationTest):
    """报销申请集成测试"""

    @allure.title("完整报销申请流程")
    def test_complete_reimbursement_flow(self, authenticated_client, reimbursement_builder, test_context):
        """测试完整报销申请流程：创建 -> 查询 -> 更新 -> 删除"""
        # 1. 创建报销申请
        reimbursement = reimbursement_builder.create(
            user_id=1,
            amount=1000.00,
            reason="集成测试报销"
        )
        assert reimbursement is not None
        reimbursement_id = reimbursement.id
        test_context.set("reimbursement", reimbursement)

        # 2. 查询报销申请
        result = authenticated_client.reimbursement.get_reimbursement_by_id(reimbursement_id)
        assert result["code"] == 200
        assert result["data"]["id"] == reimbursement_id

        # 3. 更新报销申请
        update_result = authenticated_client.reimbursement.update_reimbursement(
            reimbursement_id=reimbursement_id,
            user_id=1,
            amount=1500.00,
            reason="更新后的原因"
        )

        if update_result.get("code") == 200:
            assert update_result["data"]["amount"] == 1500.00

        # 4. 删除报销申请
        delete_result = authenticated_client.reimbursement.delete_reimbursement(reimbursement_id)
        assert delete_result["code"] == 200

        # 5. 验证删除
        get_result = authenticated_client.reimbursement.get_reimbursement_by_id(reimbursement_id)
        assert get_result["code"] == 404

    @allure.title("多报销申请查询")
    def test_multiple_reimbursements_query(self, reimbursement_builder, authenticated_client):
        """测试多报销申请查询"""
        # 创建多个报销申请
        reimbursements = []
        for i in range(3):
            reimbursement = reimbursement_builder.create(
                user_id=1,
                amount=100.00 * (i + 1),
                reason=f"批量查询测试 {i + 1}"
            )
            reimbursements.append(reimbursement)

        # 查询所有报销申请
        result = authenticated_client.reimbursement.get_reimbursements()

        assert result["code"] == 200
        assert isinstance(result["data"], list)
        assert len(result["data"]) >= 3


@allure.feature("报销申请")
@allure.story("报销申请Builder功能")
class TestReimbursementBuilderFeatures(UnitTest):
    """报销申请Builder功能测试"""

    @allure.title("Builder创建报销申请")
    def test_builder_create(self, reimbursement_builder, test_context):
        """测试Builder创建报销申请"""
        reimbursement = reimbursement_builder.create(
            user_id=1,
            amount=1000.00,
            reason="Builder测试"
        )

        assert reimbursement is not None
        assert reimbursement.id is not None
        assert reimbursement.status == "pending"
        assert reimbursement.amount == 1000.00

        test_context.set("reimbursement", reimbursement)

    @allure.title("Builder根据ID获取")
    def test_builder_get_by_id(self, reimbursement_builder, created_reimbursement):
        """测试Builder根据ID获取"""
        reimbursement_id = created_reimbursement.id
        fetched = reimbursement_builder.get_by_id(reimbursement_id)

        assert fetched is not None
        assert fetched.id == reimbursement_id

    @allure.title("Builder更新")
    def test_builder_update(self, reimbursement_builder, pending_reimbursement, test_context):
        """测试Builder更新"""
        reimbursement_id = pending_reimbursement["id"]

        current = reimbursement_builder.get_by_id(reimbursement_id)
        if current:
            current.amount = 2000.00
            current.reason = "Builder更新测试"
            updated = reimbursement_builder.update(current)

            assert updated is not None
            assert updated.amount == 2000.00

            test_context.set("updated", updated)
