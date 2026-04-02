# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 预算实体
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
预算实体模块

定义预算数据结构，支持：
- 预算分配和管理
- 组织关联
- 预算消耗追踪
- 智能工厂方法
"""

import os
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List, Dict, Any

from .base_entity import BaseEntity


def uuid_short() -> str:
    """生成短UUID"""
    return str(uuid.uuid4())[:8]


@dataclass
class BudgetEntity(BaseEntity):
    """
    预算实体
    
    Attributes:
        id: 预算ID
        org_id: 组织ID
        year: 预算年度
        total_amount: 总预算金额
        used_amount: 已用金额
        reserved_amount: 预留金额
        category: 预算类别
        status: 状态（active/frozen/expired）
        metadata: 扩展元数据
    """

    # 基础字段
    id: Optional[str] = None
    org_id: Optional[str] = None
    year: int = field(default_factory=lambda: datetime.now().year)

    # 金额字段
    total_amount: float = 0.0
    used_amount: float = 0.0
    reserved_amount: float = 0.0

    # 分类和状态
    category: str = "general"  # general, project, operation, marketing
    status: str = "active"  # active, frozen, expired

    # 时间范围
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """初始化后处理"""
        if not self.id:
            self.id = f"budget_{uuid_short()}"

        # 设置默认时间范围
        if not self.start_date:
            self.start_date = date(self.year, 1, 1)
        if not self.end_date:
            self.end_date = date(self.year, 12, 31)

    # ==================== 业务行为 ====================

    def get_available_amount(self) -> float:
        """获取可用预算"""
        return self.total_amount - self.used_amount - self.reserved_amount

    def get_usage_rate(self) -> float:
        """获取预算使用率"""
        if self.total_amount == 0:
            return 0.0
        return (self.used_amount / self.total_amount) * 100

    def has_enough_budget(self, amount: float) -> bool:
        """检查是否有足够预算"""
        return self.get_available_amount() >= amount

    def consume(self, amount: float) -> bool:
        """
        消耗预算
        
        Args:
            amount: 消耗金额
        
        Returns:
            bool: 是否成功
        """
        if not self.has_enough_budget(amount):
            return False

        self.used_amount += amount
        self.updated_at = datetime.now()
        return True

    def reserve(self, amount: float) -> bool:
        """
        预留预算
        
        Args:
            amount: 预留金额
        
        Returns:
            bool: 是否成功
        """
        if not self.has_enough_budget(amount):
            return False

        self.reserved_amount += amount
        self.updated_at = datetime.now()
        return True

    def release_reservation(self, amount: float):
        """释放预留预算"""
        self.reserved_amount = max(0, self.reserved_amount - amount)
        self.updated_at = datetime.now()

    def transfer_from_reservation(self, amount: float) -> bool:
        """将预留转为已用"""
        if self.reserved_amount < amount:
            return False

        self.reserved_amount -= amount
        self.used_amount += amount
        self.updated_at = datetime.now()
        return True

    def freeze(self):
        """冻结预算"""
        self.status = "frozen"
        self.updated_at = datetime.now()

    def unfreeze(self):
        """解冻预算"""
        if self.status == "frozen":
            self.status = "active"
            self.updated_at = datetime.now()

    def expire(self):
        """设置预算过期"""
        self.status = "expired"
        self.updated_at = datetime.now()

    def is_active(self) -> bool:
        """检查是否激活"""
        return self.status == "active"

    def is_frozen(self) -> bool:
        """检查是否冻结"""
        return self.status == "frozen"

    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.status == "expired":
            return True
        if self.end_date and date.today() > self.end_date:
            return True
        return False

    # ==================== 智能工厂方法 ====================

    @classmethod
    def for_org(cls, org_id: str, amount: float, **kwargs) -> "BudgetEntity":
        """
        为组织创建预算
        
        Args:
            org_id: 组织ID
            amount: 预算金额
            **kwargs: 其他属性
        
        Returns:
            BudgetEntity: 预算实体
        """
        return cls(
            org_id=org_id,
            total_amount=amount,
            used_amount=0.0,
            reserved_amount=0.0,
            **kwargs
        )

    @classmethod
    def annual(cls, year: int, amount: float, **kwargs) -> "BudgetEntity":
        """
        创建年度预算
        
        Args:
            year: 年度
            amount: 预算金额
            **kwargs: 其他属性
        
        Returns:
            BudgetEntity: 预算实体
        """
        return cls(
            year=year,
            total_amount=amount,
            start_date=date(year, 1, 1),
            end_date=date(year, 12, 31),
            **kwargs
        )

    @classmethod
    def project_budget(cls, project_name: str, amount: float, **kwargs) -> "BudgetEntity":
        """
        创建项目预算
        
        Args:
            project_name: 项目名称
            amount: 预算金额
            **kwargs: 其他属性
        
        Returns:
            BudgetEntity: 预算实体
        """
        return cls(
            category="project",
            total_amount=amount,
            metadata={"project_name": project_name, **kwargs.get("metadata", {})},
            **{k: v for k, v in kwargs.items() if k != "metadata"}
        )

    @classmethod
    def with_high_amount(cls, amount: float = 1000000.0, **kwargs) -> "BudgetEntity":
        """
        创建高额度预算
        
        Args:
            amount: 预算金额（默认100万）
            **kwargs: 其他属性
        
        Returns:
            BudgetEntity: 预算实体
        """
        return cls(
            total_amount=amount,
            **kwargs
        )

    @classmethod
    def random(cls) -> "BudgetEntity":
        """
        随机创建预算
        
        Returns:
            BudgetEntity: 随机预算实体
        """
        import random
        return cls(
            total_amount=random.choice([50000, 100000, 200000, 500000]),
            category=random.choice(["general", "project", "operation", "marketing"]),
        )

    # ==================== 验证方法 ====================

    def validate(self) -> bool:
        """验证预算数据"""
        if self.total_amount < 0:
            return False
        if self.used_amount < 0:
            return False
        if self.reserved_amount < 0:
            return False
        if self.used_amount + self.reserved_amount > self.total_amount:
            return False
        if self.year < 2000 or self.year > 2100:
            return False
        return True

    def get_dependencies(self) -> List[str]:
        """获取依赖的实体类型"""
        if self.org_id:
            return ["OrgEntity"]
        return []

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "org_id": self.org_id,
            "year": self.year,
            "total_amount": self.total_amount,
            "used_amount": self.used_amount,
            "reserved_amount": self.reserved_amount,
            "available_amount": self.get_available_amount(),
            "usage_rate": self.get_usage_rate(),
            "category": self.category,
            "status": self.status,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
