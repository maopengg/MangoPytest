# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Allure 集成示例测试
# @Time   : 2026-04-03
# @Author : 毛鹏

"""
Allure 集成示例

展示如何在测试中使用 Allure 集成功能：
1. 使用 @allure_feature/@allure_story 标记
2. 使用 allure_context fixture 自动记录 Context 操作
3. 使用 allure_lineage fixture 自动记录血缘信息
4. 使用 AllureHelper 手动记录步骤和附件
"""

import pytest
from auto_test.demo_project.fixtures.allure_conftest import (
    allure_feature,
    allure_story,
    AllureHelper,
)
from auto_test.demo_project.data_factory.entities import UserEntity, ReimbursementEntity
from auto_test.demo_project.core.allure_integration import allure_step


@allure_feature("用户管理")
@allure_story("用户创建与验证")
class TestUserWithAllure:
    """用户管理相关测试 - 集成 Allure 报告"""

    def test_create_user_with_context(self, allure_context):
        """
        创建用户并验证
        
        测试流程：
        1. 创建管理员用户
        2. 验证用户属性
        3. 验证用户状态
        """
        # 创建用户（自动记录到 Allure）
        user = allure_context.create(
            UserEntity,
            username="admin_user",
            email="admin@example.com",
            role="admin"
        )

        # 验证用户属性（自动记录到 Allure）
        assert user.username == "admin_user"
        assert user.role == "admin"

        # 手动记录步骤
        with allure_step("验证用户状态"):
            assert user.is_active()

    def test_reuse_user_with_context(self, allure_context):
        """
        复用已有用户
        
        测试流程：
        1. 创建用户
        2. 复用用户
        3. 验证复用成功
        """
        # 创建用户
        user1 = allure_context.create(
            UserEntity,
            username="test_user",
            role="user"
        )

        # 复用用户（自动记录到 Allure）
        user2 = allure_context.use(UserEntity, role="user")

        # 验证复用成功
        assert user2 is not None
        assert user2.username == user1.username


@allure_feature("报销管理")
@allure_story("报销流程")
class TestReimbursementWithAllure:
    """报销管理相关测试 - 集成 Allure 报告"""

    def test_create_reimbursement_with_lineage(self, allure_context, allure_lineage):
        """
        创建报销单并追踪血缘
        
        测试流程：
        1. 创建用户
        2. 创建报销单
        3. 验证报销单属性
        4. 血缘信息自动附加到报告
        """
        # 创建用户
        user = allure_context.create(
            UserEntity,
            username="reimbursement_user",
            role="user"
        )

        # 创建报销单
        reimbursement = allure_context.create(
            ReimbursementEntity,
            user_id=user.id,
            amount=1000.00,
            reason="差旅报销"
        )

        # 验证报销单
        assert reimbursement.amount == 1000.00
        assert reimbursement.reason == "差旅报销"

        # 血缘信息自动附加到 Allure 报告

    def test_multiple_operations_with_allure(self, allure_context):
        """
        多个操作的完整流程
        
        测试流程：
        1. 创建多个用户
        2. 创建多个报销单
        3. 验证所有操作
        4. 操作摘要自动附加到报告
        """
        # 创建多个用户
        users = []
        for i in range(3):
            user = allure_context.create(
                UserEntity,
                username=f"user_{i}",
                role="user" if i % 2 == 0 else "manager"
            )
            users.append(user)

        # 创建多个报销单
        reimbursements = []
        for i, user in enumerate(users):
            reimbursement = allure_context.create(
                ReimbursementEntity,
                user_id=user.id,
                amount=1000.00 * (i + 1),
                reason=f"报销 {i+1}"
            )
            reimbursements.append(reimbursement)

        # 验证
        assert len(users) == 3
        assert len(reimbursements) == 3

        # 操作摘要自动附加到 Allure 报告


@allure_feature("高级功能")
@allure_story("手动步骤记录")
class TestManualAllureSteps:
    """手动记录 Allure 步骤的示例"""

    def test_manual_steps(self):
        """
        手动记录测试步骤
        
        展示如何使用 AllureHelper 手动记录步骤和附件
        """
        # 步骤1：准备数据
        with allure_step("准备测试数据"):
            test_data = {
                "username": "test_user",
                "email": "test@example.com",
                "role": "admin"
            }
            AllureHelper.attach_json("测试数据", test_data)

        # 步骤2：执行操作
        with allure_step("执行创建操作"):
            user = UserEntity(**test_data)
            AllureHelper.attach_text("创建结果", f"用户ID: {user.id}")

        # 步骤3：验证结果
        with allure_step("验证结果"):
            assert user.username == "test_user"
            assert user.role == "admin"

    def test_attach_html_report(self):
        """
        附加 HTML 报告
        
        展示如何附加 HTML 格式的报告
        """
        html_report = """
        <table>
            <tr>
                <th>用户名</th>
                <th>角色</th>
                <th>状态</th>
            </tr>
            <tr>
                <td>admin_user</td>
                <td>admin</td>
                <td>active</td>
            </tr>
            <tr>
                <td>normal_user</td>
                <td>user</td>
                <td>active</td>
            </tr>
        </table>
        """

        with allure_step("生成 HTML 报告"):
            AllureHelper.attach_html("用户列表", html_report)

        assert True


# 使用示例：运行测试并生成 Allure 报告
# pytest auto_test/demo_project/test_cases/test_allure_integration.py -v --alluredir=./allure-results
# allure serve ./allure-results
