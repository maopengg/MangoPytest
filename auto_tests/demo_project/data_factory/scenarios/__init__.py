# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 场景定义层 - 业务流程封装（增强版）
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
场景定义层

职责：
1. 封装业务流程（多个步骤的组合）
2. 管理实体间的依赖关系（依赖声明自动解决）
3. 提供场景执行结果
4. 支持变体矩阵（笛卡尔积生成测试用例）
5. 【新增】声明创建的实体
6. 【新增】预期结果验证

使用示例：
from auto_test.demo_project.data_factory.scenarios import FullApprovalScenario
    
    # 基础用法
    scenario = FullApprovalScenario(token="xxx")
    result = scenario.execute(amount=50000)
    
    if result.success:
        reimbursement = result.get_entity("reimbursement")
        print(f"审批流程完成，报销ID: {reimbursement.id}")

变体矩阵示例：
    from auto_test.demo_project.data_factory.scenarios import VariantMatrix, Dimension, Variant
    
    matrix = VariantMatrix([
        Dimension("amount", [
            Variant("small", {"amount": 1000}, 0),
            Variant("large", {"amount": 500000}, 1),
        ]),
    ])
    variants = matrix.generate()
    
快捷方法示例：
    # 执行指定变体
    result = FullApprovalScenario.execute_variant("amount=large,urgency=urgent")
    
    # 执行所有变体
    results = FullApprovalScenario.execute_all_variants()
"""

# 基类
from .base_scenario import (
    BaseScenario,
    ScenarioResult,
    Dependencies,
    Creates  # 【新增】
)
# 登录场景
from .login import LoginScenario, RegisterAndLoginScenario
# 报销审批场景
from .reimbursement import (
    CreateReimbursementScenario,
    FullApprovalWorkflowScenario,
    RejectionWorkflowScenario,
)
# 变体矩阵
from .variant_matrix import (
    VariantMatrix,
    Dimension,
    Variant,
    VariantStatus,
    VariantMatrixResult,
    VariantExecutor,
)

# 【新增】完整审批流场景（使用增强版 BaseScenario）
from .full_approval_scenario import FullApprovalScenario

__all__ = [
    # 基类
    "BaseScenario",
    "ScenarioResult",
    "Dependencies",
    "Creates",  # 【新增】
    # 变体矩阵
    "VariantMatrix",
    "Dimension",
    "Variant",
    "VariantStatus",
    "VariantMatrixResult",
    "VariantExecutor",
    # 登录场景
    "LoginScenario",
    "RegisterAndLoginScenario",
    # 报销审批场景
    "CreateReimbursementScenario",
    "FullApprovalWorkflowScenario",
    "RejectionWorkflowScenario",
    # 【新增】完整审批流场景
    "FullApprovalScenario",
]
