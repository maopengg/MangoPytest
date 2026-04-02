# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据工厂 - 新架构入口
# @Time   : 2026-03-31
# @Author : 毛鹏

"""
数据工厂 - 新架构

分层架构：
1. entities/     - 实体定义层（数据模型）
2. scenarios/    - 场景定义层（业务流程）
3. builders/     - 构造器实现层（数据构造）
4. strategies/   - 构造策略层（构造方式）

使用示例：
    # 方式1：使用Builder
    from auto_test.demo_project.data_factory.builders import ReimbursementBuilder
    
    builder = ReimbursementBuilder()
    entity = builder.create(user_id=1, amount=100.00)
    
    # 方式2：使用Scenario
    from auto_test.demo_project.data_factory.scenarios import FullApprovalWorkflowScenario
    
    scenario = FullApprovalWorkflowScenario()
    result = scenario.execute(user_id=1, amount=1000.00)
    
    if result.success:
        reimbursement = result.get_entity("reimbursement")
"""

# 导出构造器层
from .builders.base_builder import BaseBuilder
# 导出实体层
from .entities import (
    BaseEntity,
    EntityStatus,
    UserEntity,
    ReimbursementEntity,
    DeptApprovalEntity,
    FinanceApprovalEntity,
    CEOApprovalEntity,
)
# 导出场景层
from .scenarios import (
    BaseScenario,
    ScenarioResult,
    LoginScenario,
    RegisterAndLoginScenario,
    CreateReimbursementScenario,
    FullApprovalWorkflowScenario,
    RejectionWorkflowScenario,
)
# 导出 Context 对象
from .context import Context
from .context_allure import AllureContext, create_allure_context

__all__ = [
    # 实体层
    "BaseEntity",
    "EntityStatus",
    "UserEntity",
    "ReimbursementEntity",
    "DeptApprovalEntity",
    "FinanceApprovalEntity",
    "CEOApprovalEntity",
    # 场景层
    "BaseScenario",
    "ScenarioResult",
    "LoginScenario",
    "RegisterAndLoginScenario",
    "CreateReimbursementScenario",
    "FullApprovalWorkflowScenario",
    "RejectionWorkflowScenario",
    # 构造器层
    "BaseBuilder",
    # Context 对象
    "Context",
    "AllureContext",
    "create_allure_context",
]
