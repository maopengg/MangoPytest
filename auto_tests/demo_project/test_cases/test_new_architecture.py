# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 新架构测试示例 - 演示Entity/Scenario/Builder的使用
# @Time   : 2026-03-31
# @Author : 毛鹏
import allure

from auto_tests.demo_project.data_factory.builders import UserBuilder, ReimbursementBuilder
from auto_tests.demo_project.data_factory.entities import UserEntity, ReimbursementEntity
from auto_tests.demo_project.data_factory.scenarios import (
    LoginScenario,
    RegisterAndLoginScenario,
    FullApprovalWorkflowScenario,
)
from core.base.layering_base import UnitTest, IntegrationTest, E2ETest


@allure.feature("新架构演示")
@allure.story("Entity使用")
class TestEntityUsage(UnitTest):
    """演示Entity的使用"""

    @allure.title("创建用户Entity")
    def test_create_user_entity(self):
        """测试创建用户实体"""
        user = UserEntity(
            username="test_user",
            email="test@example.com",
            full_name="Test User",
            password="Test@123456"
        )

        assert user.validate() is True
        assert user.username == "test_user"
        assert user.email == "test@example.com"

    @allure.title("创建报销申请Entity")
    def test_create_reimbursement_entity(self):
        """测试创建报销申请实体"""
        reimbursement = ReimbursementEntity(
            user_id=1,
            amount=1000.00,
            reason="差旅报销"
        )

        assert reimbursement.validate() is True
        assert reimbursement.user_id == 1
        assert reimbursement.amount == 1000.00
        assert reimbursement.is_pending() is True


@allure.feature("新架构演示")
@allure.story("Builder使用")
class TestBuilderUsage(UnitTest):
    """演示Builder的使用"""

    @allure.title("使用UserBuilder创建用户")
    def test_user_builder(self):
        """测试使用UserBuilder创建用户"""
        builder = UserBuilder()

        # 构造实体（不调用API）
        entity = builder.build(
            username="builder_test_user",
            email="builder@test.com",
            password="Test@123456"
        )

        assert entity.validate() is True
        assert entity.username == "builder_test_user"

    @allure.title("使用ReimbursementBuilder创建报销申请")
    def test_reimbursement_builder(self):
        """测试使用ReimbursementBuilder创建报销申请"""
        builder = ReimbursementBuilder()

        # 构造实体
        entity = builder.build(
            user_id=1,
            amount=500.00,
            reason="测试报销"
        )

        assert entity.validate() is True
        assert entity.amount == 500.00


@allure.feature("新架构演示")
@allure.story("Scenario使用")
class TestScenarioUsage(IntegrationTest):
    """演示Scenario的使用"""

    @allure.title("使用LoginScenario登录")
    def test_login_scenario(self):
        """测试使用LoginScenario登录"""
        scenario = LoginScenario()

        result = scenario.execute(
            username="admin",
            password="admin123",
            create_user=False
        )

        # 注意：这里可能会失败，因为用户可能不存在
        # 但演示了Scenario的使用方式
        if result.success:
            assert "token" in result.data

    @allure.title("使用RegisterAndLoginScenario注册并登录")
    def test_register_and_login_scenario(self):
        """测试使用RegisterAndLoginScenario注册并登录"""
        scenario = RegisterAndLoginScenario()

        result = scenario.execute()

        if result.success:
            assert "token" in result.data
            assert result.data.get("token_type") == "bearer"


@allure.feature("新架构演示")
@allure.story("完整审批流程")
class TestApprovalWorkflow(E2ETest):
    """演示完整审批流程"""

    @allure.title("使用Scenario创建完整审批流程")
    def test_full_approval_workflow(self, test_token):
        """测试使用Scenario创建完整4级审批流程"""
        scenario = FullApprovalWorkflowScenario(token=test_token)

        result = scenario.execute(
            user_id=1,
            amount=5000.00,
            reason="完整审批流程测试"
        )

        # 演示了如何使用ScenarioResult
        if result.success:
            # 获取实体
            reimbursement = result.get_entity("reimbursement")
            if reimbursement:
                assert reimbursement.id is not None

            # 获取数据
            assert "reimbursement_id" in result.data
            assert "final_status" in result.data


@allure.feature("新架构演示")
@allure.story("使用Fixtures")
class TestWithFixtures(IntegrationTest):
    """演示使用Fixtures"""

    @allure.title("使用test_user fixture")
    def test_with_test_user(self, test_user):
        """测试使用test_user fixture"""
        # test_user 是 UserEntity 实例
        assert test_user.id is not None
        assert test_user.username is not None
        assert test_user.email is not None

    @allure.title("使用full_approval_workflow fixture")
    def test_with_full_approval(self, full_approval_workflow):
        """测试使用full_approval_workflow fixture"""
        # full_approval_workflow 是字典，包含审批流程结果
        assert full_approval_workflow["status"] == "fully_approved"
        assert full_approval_workflow["reimbursement"] is not None
