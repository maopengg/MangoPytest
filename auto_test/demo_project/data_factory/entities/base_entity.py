# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 实体基类 - 定义实体生命周期和通用行为
# @Time   : 2026-03-31
# @Author : 毛鹏
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
import uuid


class EntityStatus(Enum):
    """实体状态枚举"""
    PENDING = "pending"           # 待处理
    PROCESSING = "processing"     # 处理中
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"             # 失败
    CANCELLED = "cancelled"       # 已取消
    DELETED = "deleted"           # 已删除


@dataclass
class BaseEntity(ABC):
    """
    实体基类
    
    所有实体的父类，定义通用的属性和行为
    
    Attributes:
        id: 实体唯一标识
        created_at: 创建时间
        updated_at: 更新时间
        status: 实体状态
        metadata: 元数据（扩展信息）
    """
    
    # 核心属性
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    status: str = field(default="pending")
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 内部状态
    _is_dirty: bool = field(default=False, repr=False)  # 是否被修改
    _is_new: bool = field(default=True, repr=False)     # 是否新建
    _original_data: Dict[str, Any] = field(default_factory=dict, repr=False)
    
    def __post_init__(self):
        """初始化后处理"""
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at
        
        # 保存原始数据用于变更追踪
        self._original_data = self.to_dict()
    
    @abstractmethod
    def validate(self) -> bool:
        """
        验证实体数据有效性
        
        @return: 是否有效
        """
        pass
    
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """
        获取实体依赖的其他实体类型
        
        @return: 依赖的实体类型列表
        """
        return []
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        @return: 字典表示
        """
        data = asdict(self)
        # 移除内部字段
        data.pop('_is_dirty', None)
        data.pop('_is_new', None)
        data.pop('_original_data', None)
        return data
    
    def to_api_payload(self) -> Dict[str, Any]:
        """
        转换为API请求体
        
        子类可重写此方法自定义API请求格式
        
        @return: API请求体字典
        """
        return self.to_dict()
    
    def mark_as_saved(self, entity_id: int):
        """
        标记为已保存
        
        @param entity_id: 保存后返回的ID
        """
        self.id = entity_id
        self._is_new = False
        self._is_dirty = False
        self._original_data = self.to_dict()
    
    def mark_as_updated(self):
        """标记为已更新"""
        self.updated_at = datetime.now().isoformat()
        self._is_dirty = True
    
    def mark_as_deleted(self):
        """标记为已删除"""
        self.status = EntityStatus.DELETED.value
        self.updated_at = datetime.now().isoformat()
    
    def is_new(self) -> bool:
        """检查是否为新建实体"""
        return self._is_new
    
    def is_dirty(self) -> bool:
        """检查是否被修改"""
        return self._is_dirty
    
    def get_changes(self) -> Dict[str, Any]:
        """
        获取变更的字段
        
        @return: 变更的字段字典
        """
        current = self.to_dict()
        changes = {}
        
        for key, value in current.items():
            if key not in self._original_data or self._original_data[key] != value:
                changes[key] = value
        
        return changes
    
    def update(self, **kwargs):
        """
        更新实体属性
        
        @param kwargs: 要更新的属性
        """
        for key, value in kwargs.items():
            if hasattr(self, key) and not key.startswith('_'):
                setattr(self, key, value)
        
        self.mark_as_updated()
    
    def generate_uuid(self) -> str:
        """生成唯一标识符"""
        return str(uuid.uuid4())
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id}, status={self.status})>"
