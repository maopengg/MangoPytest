# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Core Base Model - 基础模型
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
Core Base Model 模块

提供基础的数据模型类
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json


@dataclass
class BaseModel:
    """
    基础模型类
    
    所有数据模型的基类，提供：
    - 字典转换
    - JSON 序列化
    - 字段验证
    
    使用示例：
        @dataclass
        class User(BaseModel):
            name: str
            age: int
        
        user = User(name="test", age=25)
        data = user.to_dict()
        json_str = user.to_json()
    """
    
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    def to_json(self, indent: Optional[int] = None) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict(), indent=indent, default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseModel":
        """从字典创建实例"""
        # 过滤掉不存在的字段
        valid_fields = {f for f in cls.__dataclass_fields__}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)
    
    @classmethod
    def from_json(cls, json_str: str) -> "BaseModel":
        """从 JSON 字符串创建实例"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def update(self, **kwargs):
        """更新字段"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
    
    def validate(self) -> bool:
        """验证数据（子类可重写）"""
        return True
    
    def __repr__(self) -> str:
        """字符串表示"""
        fields = [f"{k}={v!r}" for k, v in self.to_dict().items()]
        return f"{self.__class__.__name__}({', '.join(fields)})"


__all__ = ["BaseModel"]
