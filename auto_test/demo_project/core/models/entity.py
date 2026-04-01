# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Core Entity - 实体基类
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
Core Entity 模块

提供实体基类，支持：
- 唯一标识
- 状态管理
- 生命周期
- 依赖追踪
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from .base import BaseModel


@dataclass
class BaseEntity(BaseModel):
    """
    实体基类
    
    所有业务实体的基类，提供：
    - 唯一标识（id）
    - 状态管理
    - 生命周期方法
    - 依赖追踪
    
    使用示例：
        @dataclass
        class User(BaseEntity):
            username: str
            email: str
        
        user = User(username="test", email="test@example.com")
        user.mark_as_active()
        user.mark_as_deleted()
    """
    
    id: Optional[str] = None
    status: str = "pending"  # pending, active, inactive, deleted
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.id:
            self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """生成唯一标识"""
        prefix = self.__class__.__name__.lower().replace("entity", "")
        return f"{prefix}_{uuid.uuid4().hex[:8]}"
    
    def mark_as_active(self):
        """标记为激活状态"""
        self.status = "active"
        self.updated_at = datetime.now()
    
    def mark_as_inactive(self):
        """标记为非激活状态"""
        self.status = "inactive"
        self.updated_at = datetime.now()
    
    def mark_as_deleted(self):
        """标记为已删除"""
        self.status = "deleted"
        self.updated_at = datetime.now()
    
    def is_active(self) -> bool:
        """检查是否激活"""
        return self.status == "active"
    
    def is_deleted(self) -> bool:
        """检查是否已删除"""
        return self.status == "deleted"
    
    def get_dependencies(self) -> List[str]:
        """
        获取依赖的实体类型（子类可重写）
        
        @return: 依赖的实体类型列表
        """
        return []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = super().to_dict()
        data["is_active"] = self.is_active()
        data["is_deleted"] = self.is_deleted()
        return data
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "BaseEntity":
        """从 API 响应创建实例"""
        return cls.from_dict(data)


__all__ = ["BaseEntity"]
