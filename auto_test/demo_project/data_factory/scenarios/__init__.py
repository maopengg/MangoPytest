# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 场景定义层 - 业务流程封装
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
场景定义层

职责：
1. 封装业务流程（多个步骤的组合）
2. 管理实体间的依赖关系
3. 提供场景执行结果
4. 支持变体矩阵（笛卡尔积生成测试用例）

使用示例：
from auto_test.demo_project.data_factory.scenarios import FullApprovalWorkflowScenario
    
    scenario = FullApprovalWorkflowScenario(token="xxx")
result = scenario.execute(user_id=1, amount=1000.00)
    
    if result.success:
        reimbursement = result.get_entity("reimbursement")
        print(f"审批流程完成，报销ID: {reimbursement.id}")

变体矩阵示例：
    from auto_test.demo_project.data_factory.scenarios import VariantMatrix, Dimension
    
    matrix = VariantMatrix(
        dimensions=[
            Dimension("role", ["admin", "user"]),
            Dimension("status", ["active", "locked"])
        ]
    )
    variants = matrix.generate()
"""

# 基类
from .base_scenario import BaseScenario, ScenarioResult

# 变体矩阵
from .variant_matrix import (
    VariantMatrix,
    Dimension,
    Variant,
    VariantStatus,
    VariantMatrixResult,
    VariantExecutor,
    cartesian_product,
    filter_variants,
    group_variants,
)

# 登录场景
from .login import LoginScenario, RegisterAndLoginScenario

# 报销审批场景
from .reimbursement import (
    CreateReimbursementScenario,
    FullApprovalWorkflowScenario,
    RejectionWorkflowScenario,
)

__all__ = [
    # 基类
    "BaseScenario",
    "ScenarioResult",
    # 变体矩阵
    "VariantMatrix",
    "Dimension",
    "Variant",
    "VariantStatus",
    "VariantMatrixResult",
    "VariantExecutor",
    "cartesian_product",
    "filter_variants",
    "group_variants",
    # 登录场景
    "LoginScenario",
    "RegisterAndLoginScenario",
    # 报销审批场景
    "CreateReimbursementScenario",
    "FullApprovalWorkflowScenario",
    "RejectionWorkflowScenario",
]
