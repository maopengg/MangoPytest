# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 场景定义层 - 业务流程封装
# @Time   : 2026-03-31
# @Author : 毛鹏

"""
场景定义层

职责：
1. 封装业务流程（多个步骤的组合）
2. 管理实体间的依赖关系
3. 提供场景执行结果

使用示例：
    from auto_test.demo_project.data_factory.scenarios import FullApprovalWorkflowScenario
    
    scenario = FullApprovalWorkflowScenario(token="xxx")
    result = scenario.execute(user_id=1, amount=1000.00)
    
    if result.success:
        reimbursement = result.get_entity("reimbursement")
        print(f"审批流程完成，报销ID: {reimbursement.id}")
"""

from .base_scenario import BaseScenario, ScenarioResult
from .login import LoginScenario, RegisterAndLoginScenario
from .reimbursement import (
    CreateReimbursementScenario,
    FullApprovalWorkflowScenario,
    RejectionWorkflowScenario,
)

__all__ = [
    # 基类
    "BaseScenario",
    "ScenarioResult",
    # 登录场景
    "LoginScenario",
    "RegisterAndLoginScenario",
    # 报销审批场景
    "CreateReimbursementScenario",
    "FullApprovalWorkflowScenario",
    "RejectionWorkflowScenario",
]
