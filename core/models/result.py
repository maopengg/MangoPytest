# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Core Result - 结果模型
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
Core Result 模块

提供统一的结果模型
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Generic, TypeVar

T = TypeVar("T")


@dataclass
class Result(Generic[T]):
    """
    结果模型
    
    统一的操作结果封装，支持：
    - 成功/失败状态
    - 数据承载
    - 错误信息
    - 元数据
    
    使用示例：
        # 成功结果
        result = Result.success(data={"id": 1})
        
        # 失败结果
        result = Result.failure("操作失败", error_code=500)
        
        # 检查结果
        if result.is_success:
            data = result.data
        else:
            error = result.error
    """

    success: bool = True
    data: Optional[T] = None
    error: Optional[str] = None
    error_code: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_success(self) -> bool:
        """是否成功"""
        return self.success

    @property
    def is_failure(self) -> bool:
        """是否失败"""
        return not self.success

    @classmethod
    def success(cls, data: Optional[T] = None, **metadata) -> "Result[T]":
        """创建成功结果"""
        return cls(success=True, data=data, metadata=metadata)

    @classmethod
    def failure(
            cls,
            error: str,
            error_code: Optional[int] = None,
            **metadata
    ) -> "Result[T]":
        """创建失败结果"""
        return cls(
            success=False,
            error=error,
            error_code=error_code,
            metadata=metadata
        )

    def map(self, func) -> "Result":
        """映射结果"""
        if self.is_success:
            try:
                new_data = func(self.data)
                return Result.success(new_data)
            except Exception as e:
                return Result.failure(str(e))
        return self

    def on_success(self, func) -> "Result":
        """成功时执行"""
        if self.is_success:
            func(self.data)
        return self

    def on_failure(self, func) -> "Result":
        """失败时执行"""
        if self.is_failure:
            func(self.error, self.error_code)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "error_code": self.error_code,
            "metadata": self.metadata,
        }


__all__ = ["Result"]
