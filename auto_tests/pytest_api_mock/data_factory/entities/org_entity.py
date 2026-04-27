# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 组织实体
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
组织实体模块

定义组织数据结构，支持：
- 组织基本信息
- 预算关联
- 用户关联
- 智能工厂方法
"""

import os
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any

# 添加父目录到路径以确保导入工作
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from core.base import BaseEntity


def uuid_short() -> str:
    """生成短UUID"""
    return str(uuid.uuid4())[:8]


@dataclass
class OrgEntity(BaseEntity):
    """
    组织实体
    
    Attributes:
        id: 组织ID
        name: 组织名称
        code: 组织代码
        parent_id: 父组织ID
        level: 组织层级
        budget_total: 总预算
        budget_used: 已用预算
        status: 状态（active/inactive）
        metadata: 扩展元数据
    """

    # 基础字段
    id: Optional[str] = None
    name: str = ""
    code: str = ""
    parent_id: Optional[str] = None
    level: int = 1

    # 预算字段
    budget_total: float = 0.0
    budget_used: float = 0.0

    # 状态字段
    status: str = "active"  # active, inactive

    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """初始化后处理"""
        if not self.id:
            self.id = f"org_{uuid_short()}"
        if not self.code:
            self.code = f"ORG{self.id[-6:].upper()}"
        if not self.name:
            self.name = f"组织_{self.id[-4:]}"

    # ==================== 业务行为 ====================

    def get_available_budget(self) -> float:
        """获取可用预算"""
        return self.budget_total - self.budget_used

    def has_enough_budget(self, amount: float) -> bool:
        """检查是否有足够预算"""
        return self.get_available_budget() >= amount

    def consume_budget(self, amount: float) -> bool:
        """消耗预算"""
        if not self.has_enough_budget(amount):
            return False
        self.budget_used += amount
        self.updated_at = datetime.now()
        return True

    def release_budget(self, amount: float):
        """释放预算"""
        self.budget_used = max(0, self.budget_used - amount)
        self.updated_at = datetime.now()

    def activate(self):
        """激活组织"""
        self.status = "active"
        self.updated_at = datetime.now()

    def deactivate(self):
        """停用组织"""
        self.status = "inactive"
        self.updated_at = datetime.now()

    def is_active(self) -> bool:
        """检查是否激活"""
        return self.status == "active"

    # ==================== 智能工厂方法 ====================

    @classmethod
    def with_budget(cls, budget: float, **kwargs) -> "OrgEntity":
        """
        创建带预算的组织
        
        Args:
            budget: 预算金额
            **kwargs: 其他属性
        
        Returns:
            OrgEntity: 组织实体
        """
        return cls(
            budget_total=budget,
            budget_used=0.0,
            **kwargs
        )

    @classmethod
    def parent_org(cls, **kwargs) -> "OrgEntity":
        """
        创建父级组织
        
        Returns:
            OrgEntity: 父级组织实体
        """
        return cls(
            level=1,
            parent_id=None,
            **kwargs
        )

    @classmethod
    def sub_org(cls, parent_id: str, **kwargs) -> "OrgEntity":
        """
        创建子组织
        
        Args:
            parent_id: 父组织ID
            **kwargs: 其他属性
        
        Returns:
            OrgEntity: 子组织实体
        """
        return cls(
            parent_id=parent_id,
            level=2,
            **kwargs
        )

    @classmethod
    def random(cls) -> "OrgEntity":
        """
        随机创建组织
        
        Returns:
            OrgEntity: 随机组织实体
        """
        return cls(
            name=f"组织_{uuid_short()}",
            budget_total=100000.0,
        )

    # ==================== 验证方法 ====================

    def validate(self) -> bool:
        """验证组织数据"""
        if not self.name:
            return False
        if self.budget_total < 0:
            return False
        if self.budget_used < 0 or self.budget_used > self.budget_total:
            return False
        return True

    def get_dependencies(self) -> List[str]:
        """获取依赖的实体类型"""
        return []

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "parent_id": self.parent_id,
            "level": self.level,
            "budget_total": self.budget_total,
            "budget_used": self.budget_used,
            "budget_available": self.get_available_budget(),
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
