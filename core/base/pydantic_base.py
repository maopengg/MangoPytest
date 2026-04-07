# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Pydantic 实体基类 - 新五层架构
# @Time   : 2026-04-06
# @Author : 毛鹏
"""
Pydantic 实体基类模块 - 新五层架构

L3 实体层使用 Pydantic BaseModel，提供：
1. 强类型数据验证
2. to_api_payload() 方法序列化为 Dict
3. 业务逻辑方法
4. 工厂方法

使用示例：
    from core.base.pydantic_base import PydanticEntity
    
    class OrderEntity(PydanticEntity):
        order_id: str = ""  # 响应字段
        product_id: int = Field(default=1001, gt=0)  # 请求字段
        
        def to_api_payload(self) -> Dict[str, Any]:
            return {"product_id": self.product_id}
"""

from abc import abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, ClassVar

from pydantic import BaseModel, Field, ConfigDict


class PydanticEntity(BaseModel):
    """
    Pydantic 实体基类 - L3 实体层
    
    所有 L3 Entity 的父类，使用 Pydantic 进行数据验证
    
    Attributes:
        id: 实体唯一标识（响应字段，创建后填充）
        created_at: 创建时间（响应字段）
        updated_at: 更新时间（响应字段）
        status: 实体状态（响应字段）
    """
    
    model_config = ConfigDict(
        validate_assignment=True,  # 赋值时验证
        extra='allow',  # 允许额外字段
        populate_by_name=True,  # 允许通过字段名填充
    )
    
    # 核心属性（响应字段，创建后由后端填充）
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    status: str = "pending"
    
    # 元数据
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def model_post_init(self, __context: Any) -> None:
        """初始化后处理"""
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at
    
    @abstractmethod
    def to_api_payload(self) -> Dict[str, Any]:
        """
        转换为 API 请求体 - 必须由子类实现
        
        这是 L3 → L2 → L1 数据流的关键方法
        只返回创建/更新所需的字段，不包含响应字段（id, created_at 等）
        
        @return: API 请求体字典
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典（包含所有字段）
        
        @return: 完整字典表示
        """
        return self.model_dump()
    
    def get(self, key: str, default: Any = None) -> Any:
        """字典风格读取属性（兼容旧用例）"""
        return getattr(self, key, default)
    
    def update_from_response(self, response: Dict[str, Any]) -> None:
        """
        从 API 响应更新实体字段
        
        L2 Builder 调用 API 后，使用此方法更新 Entity 的响应字段
        
        @param response: API 响应数据
        """
        for key, value in response.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def from_response(cls, response: Dict[str, Any]) -> "PydanticEntity":
        """
        从 API 响应创建实体
        
        @param response: API 响应数据
        @return: 实体实例
        """
        return cls(**response)
