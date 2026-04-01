# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 构造器实现层
# @Time   : 2026-03-31
# @Author : 毛鹏

"""
构造器实现层

职责：
1. 构造实体数据
2. 调用API创建/更新/删除数据
3. 管理实体生命周期
4. 自动清理创建的数据

使用示例：
    from auto_test.demo_project.data_factory.builders import UserBuilder
    
    builder = UserBuilder()
    entity = builder.create(username="test", email="test@example.com")
    
    # 使用实体
    print(entity.id, entity.username)
    
    # 清理
    builder.cleanup()
"""

from .base_builder import BaseBuilder

# 导出具体构造器（延迟导入避免循环依赖）
def __getattr__(name):
    if name == "UserBuilder":
        from .user.user_builder import UserBuilder
        return UserBuilder
    elif name == "ReimbursementBuilder":
        from .reimbursement.reimbursement_builder import ReimbursementBuilder
        return ReimbursementBuilder
    elif name == "DeptApprovalBuilder":
        from .dept_approval.dept_approval_builder import DeptApprovalBuilder
        return DeptApprovalBuilder
    elif name == "FinanceApprovalBuilder":
        from .finance_approval.finance_approval_builder import FinanceApprovalBuilder
        return FinanceApprovalBuilder
    elif name == "CEOApprovalBuilder":
        from .ceo_approval.ceo_approval_builder import CEOApprovalBuilder
        return CEOApprovalBuilder
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    "BaseBuilder",
    "UserBuilder",
    "ReimbursementBuilder",
    "DeptApprovalBuilder",
    "FinanceApprovalBuilder",
    "CEOApprovalBuilder",
]
