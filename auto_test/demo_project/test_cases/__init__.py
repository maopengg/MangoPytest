# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:测试用例层 - 分层架构
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
测试用例分层架构

目录结构：
    test_cases/
    ├── unit/           # 单元测试（60%）- 单接口测试
    │   ├── test_auth.py
    │   ├── test_user.py
    │   └── test_reimbursement.py
    ├── integration/    # 集成测试（30%）- 模块间集成
    │   ├── test_approval_workflow.py
    │   └── test_data_consistency.py
    └── e2e/            # 端到端测试（10%）- 完整业务流程
        └── test_full_business_flow.py

使用示例：
    from auto_test.demo_project.test_cases import UnitTest, IntegrationTest, E2ETest
    
    # 单元测试
    class TestUserAPI(UnitTest):
        def test_create_user(self):
            result = self.api.user.create_user(...)
            self.assert_success(result)
    
    # 集成测试
    class TestApprovalWorkflow(IntegrationTest):
        def test_full_approval(self):
            with self.context() as ctx:
                ctx.create(ReimbursementEntity)
                ctx.action("submit")
                ctx.expect_status("pending")
    
    # 端到端测试
    class TestBusinessFlow(E2ETest):
        def test_complete_flow(self):
            self.run_scenario(FullApprovalWorkflowScenario)
"""

from .base import (
    TestLayer,
    UnitTest,
    IntegrationTest,
    E2ETest,
    TestContext,
    case_data,
    TestCaseResult,
    TestLayerType,
)

__all__ = [
    # 测试分层基类
    "TestLayer",
    "UnitTest",
    "IntegrationTest",
    "E2ETest",
    # 测试上下文
    "TestContext",
    # 装饰器
    "case_data",
    # 结果
    "TestCaseResult",
    # 枚举
    "TestLayerType",
]
