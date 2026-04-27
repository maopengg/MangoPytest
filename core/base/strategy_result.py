# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 策略执行结果
# @Time   : 2026-04-04
# @Author : 毛鹏
"""
策略执行结果模块

定义策略执行的结果数据结构
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .base_entity import BaseEntity


@dataclass
class StrategyResult:
    """策略执行结果"""
    success: bool
    entity: Optional['BaseEntity'] = None
    entities: Optional[List['BaseEntity']] = None
    raw_data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    @property
    def data(self) -> Optional[Dict[str, Any]]:
        """获取原始数据"""
        return self.raw_data

    def get_entity(self) -> Optional['BaseEntity']:
        """获取单个实体"""
        return self.entity

    def get_entities(self) -> List['BaseEntity']:
        """获取实体列表"""
        return self.entities or []
