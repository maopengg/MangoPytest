"""
Schema 验证系统 - DAL 的 Schema 定义和验证

对应 Java: DAL-java 中的 Schema 验证功能
"""

import re
from typing import Any, Callable, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class SchemaValidationResult:
    """Schema 验证结果"""
    success: bool
    message: str = ""


class SchemaRegistry:
    """
    Schema 注册表
    
    管理所有可用的 Schema 验证器
    """
    
    def __init__(self):
        self._schemas: Dict[str, Callable[[Any], SchemaValidationResult]] = {}
        self._register_builtin()
    
    def _register_builtin(self):
        """注册内置 Schema"""
        
        # AlmostNow - 验证时间戳是否接近当前时间（±5秒）
        @self.register("AlmostNow")
        def almost_now(value: Any) -> SchemaValidationResult:
            """验证时间戳是否接近当前时间（±5秒）"""
            try:
                if isinstance(value, (int, float)):
                    value = datetime.fromtimestamp(value)
                elif isinstance(value, str):
                    # 尝试解析 ISO 格式
                    value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                elif not isinstance(value, datetime):
                    return SchemaValidationResult(
                        success=False,
                        message=f"Expected datetime, got {type(value).__name__}"
                    )
                
                now = datetime.now()
                diff = abs((value - now).total_seconds())
                
                if diff < 5:
                    return SchemaValidationResult(success=True)
                else:
                    return SchemaValidationResult(
                        success=False,
                        message=f"Time difference is {diff:.2f}s, expected < 5s"
                    )
            except Exception as e:
                return SchemaValidationResult(
                    success=False,
                    message=f"Invalid datetime format: {e}"
                )
        
        # Instant - 验证是否为合法的时间戳格式
        @self.register("Instant")
        def is_instant(value: Any) -> SchemaValidationResult:
            """验证是否为合法的时间戳格式"""
            try:
                if isinstance(value, datetime):
                    return SchemaValidationResult(success=True)
                elif isinstance(value, (int, float)):
                    # Unix 时间戳
                    datetime.fromtimestamp(value)
                    return SchemaValidationResult(success=True)
                elif isinstance(value, str):
                    # ISO 格式
                    datetime.fromisoformat(value.replace('Z', '+00:00'))
                    return SchemaValidationResult(success=True)
                else:
                    return SchemaValidationResult(
                        success=False,
                        message=f"Expected datetime or timestamp, got {type(value).__name__}"
                    )
            except Exception as e:
                return SchemaValidationResult(
                    success=False,
                    message=f"Invalid instant format: {e}"
                )
        
        # NotEmpty - 验证非空
        @self.register("NotEmpty")
        def not_empty(value: Any) -> SchemaValidationResult:
            """验证非空"""
            if value is None:
                return SchemaValidationResult(
                    success=False,
                    message="Value is None"
                )
            if isinstance(value, (str, list, dict)):
                if len(value) == 0:
                    return SchemaValidationResult(
                        success=False,
                        message=f"{type(value).__name__} is empty"
                    )
            return SchemaValidationResult(success=True)
        
        # NotNull - 验证非 null
        @self.register("NotNull")
        def not_null(value: Any) -> SchemaValidationResult:
            """验证非 null"""
            if value is None:
                return SchemaValidationResult(
                    success=False,
                    message="Value is null"
                )
            return SchemaValidationResult(success=True)
        
        # Positive - 验证正数
        @self.register("Positive")
        def positive(value: Any) -> SchemaValidationResult:
            """验证正数"""
            try:
                num = float(value)
                if num > 0:
                    return SchemaValidationResult(success=True)
                else:
                    return SchemaValidationResult(
                        success=False,
                        message=f"Expected positive number, got {num}"
                    )
            except (ValueError, TypeError):
                return SchemaValidationResult(
                    success=False,
                    message=f"Expected number, got {type(value).__name__}"
                )
        
        # Negative - 验证负数
        @self.register("Negative")
        def negative(value: Any) -> SchemaValidationResult:
            """验证负数"""
            try:
                num = float(value)
                if num < 0:
                    return SchemaValidationResult(success=True)
                else:
                    return SchemaValidationResult(
                        success=False,
                        message=f"Expected negative number, got {num}"
                    )
            except (ValueError, TypeError):
                return SchemaValidationResult(
                    success=False,
                    message=f"Expected number, got {type(value).__name__}"
                )
        
        # NonNegative - 验证非负数
        @self.register("NonNegative")
        def non_negative(value: Any) -> SchemaValidationResult:
            """验证非负数"""
            try:
                num = float(value)
                if num >= 0:
                    return SchemaValidationResult(success=True)
                else:
                    return SchemaValidationResult(
                        success=False,
                        message=f"Expected non-negative number, got {num}"
                    )
            except (ValueError, TypeError):
                return SchemaValidationResult(
                    success=False,
                    message=f"Expected number, got {type(value).__name__}"
                )
        
        # ValidEmail - 验证邮箱格式
        @self.register("ValidEmail")
        def valid_email(value: Any) -> SchemaValidationResult:
            """验证邮箱格式"""
            if not isinstance(value, str):
                return SchemaValidationResult(
                    success=False,
                    message=f"Expected string, got {type(value).__name__}"
                )
            
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if re.match(pattern, value):
                return SchemaValidationResult(success=True)
            else:
                return SchemaValidationResult(
                    success=False,
                    message=f"Invalid email format: {value}"
                )
        
        # ValidURL - 验证 URL 格式
        @self.register("ValidURL")
        def valid_url(value: Any) -> SchemaValidationResult:
            """验证 URL 格式"""
            if not isinstance(value, str):
                return SchemaValidationResult(
                    success=False,
                    message=f"Expected string, got {type(value).__name__}"
                )
            
            pattern = r'^https?://[^\s/$.?#].[^\s]*$'
            if re.match(pattern, value, re.IGNORECASE):
                return SchemaValidationResult(success=True)
            else:
                return SchemaValidationResult(
                    success=False,
                    message=f"Invalid URL format: {value}"
                )
        
        # ValidUUID - 验证 UUID 格式
        @self.register("ValidUUID")
        def valid_uuid(value: Any) -> SchemaValidationResult:
            """验证 UUID 格式"""
            if not isinstance(value, str):
                return SchemaValidationResult(
                    success=False,
                    message=f"Expected string, got {type(value).__name__}"
                )
            
            pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
            if re.match(pattern, value, re.IGNORECASE):
                return SchemaValidationResult(success=True)
            else:
                return SchemaValidationResult(
                    success=False,
                    message=f"Invalid UUID format: {value}"
                )
        
        # String - 验证字符串类型
        @self.register("String")
        def is_string(value: Any) -> SchemaValidationResult:
            """验证字符串类型"""
            if isinstance(value, str):
                return SchemaValidationResult(success=True)
            else:
                return SchemaValidationResult(
                    success=False,
                    message=f"Expected string, got {type(value).__name__}"
                )
        
        # Number - 验证数字类型
        @self.register("Number")
        def is_number(value: Any) -> SchemaValidationResult:
            """验证数字类型"""
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return SchemaValidationResult(success=True)
            else:
                return SchemaValidationResult(
                    success=False,
                    message=f"Expected number, got {type(value).__name__}"
                )
        
        # Integer - 验证整数类型
        @self.register("Integer")
        def is_integer(value: Any) -> SchemaValidationResult:
            """验证整数类型"""
            if isinstance(value, int) and not isinstance(value, bool):
                return SchemaValidationResult(success=True)
            else:
                return SchemaValidationResult(
                    success=False,
                    message=f"Expected integer, got {type(value).__name__}"
                )
        
        # Boolean - 验证布尔类型
        @self.register("Boolean")
        def is_boolean(value: Any) -> SchemaValidationResult:
            """验证布尔类型"""
            if isinstance(value, bool):
                return SchemaValidationResult(success=True)
            else:
                return SchemaValidationResult(
                    success=False,
                    message=f"Expected boolean, got {type(value).__name__}"
                )
        
        # Array - 验证列表类型
        @self.register("Array")
        def is_array(value: Any) -> SchemaValidationResult:
            """验证列表类型"""
            if isinstance(value, list):
                return SchemaValidationResult(success=True)
            else:
                return SchemaValidationResult(
                    success=False,
                    message=f"Expected array, got {type(value).__name__}"
                )
        
        # Object - 验证对象类型
        @self.register("Object")
        def is_object(value: Any) -> SchemaValidationResult:
            """验证对象类型"""
            if isinstance(value, dict):
                return SchemaValidationResult(success=True)
            else:
                return SchemaValidationResult(
                    success=False,
                    message=f"Expected object, got {type(value).__name__}"
                )
    
    def register(self, name: str):
        """
        装饰器：注册 Schema
        
        Args:
            name: Schema 名称
            
        Example:
            >>> registry = SchemaRegistry()
            >>> @registry.register("MySchema")
            ... def my_schema(value):
            ...     return SchemaValidationResult(success=True)
        """
        def decorator(func: Callable[[Any], SchemaValidationResult]):
            self._schemas[name] = func
            return func
        return decorator
    
    def validate(self, name: str, value: Any) -> SchemaValidationResult:
        """
        验证值是否符合 Schema
        
        Args:
            name: Schema 名称
            value: 要验证的值
            
        Returns:
            SchemaValidationResult: 验证结果
            
        Raises:
            ValueError: 如果 Schema 不存在
        """
        if name not in self._schemas:
            raise ValueError(f"Unknown schema: {name}")
        return self._schemas[name](value)
    
    def get_validator(self, name: str) -> Optional[Callable[[Any], SchemaValidationResult]]:
        """
        获取 Schema 验证器
        
        Args:
            name: Schema 名称
            
        Returns:
            验证器函数，如果不存在则返回 None
        """
        return self._schemas.get(name)
    
    def list_schemas(self) -> list:
        """
        列出所有可用的 Schema
        
        Returns:
            Schema 名称列表
        """
        return list(self._schemas.keys())


# 全局 Schema 注册表
_global_registry = SchemaRegistry()


def register_schema(name: str):
    """
    装饰器：注册 Schema 到全局注册表
    
    Example:
        >>> @register_schema("CustomSchema")
        ... def custom_schema(value):
        ...     return SchemaValidationResult(success=value > 0)
    """
    return _global_registry.register(name)


def validate_schema(name: str, value: Any) -> SchemaValidationResult:
    """
    使用全局注册表验证 Schema
    
    Args:
        name: Schema 名称
        value: 要验证的值
        
    Returns:
        SchemaValidationResult: 验证结果
    """
    return _global_registry.validate(name, value)


def get_schema_validator(name: str) -> Optional[Callable[[Any], SchemaValidationResult]]:
    """
    从全局注册表获取 Schema 验证器
    
    Args:
        name: Schema 名称
        
    Returns:
        验证器函数，如果不存在则返回 None
    """
    return _global_registry.get_validator(name)


def list_schemas() -> list:
    """
    列出全局注册表中所有可用的 Schema
    
    Returns:
        Schema 名称列表
    """
    return _global_registry.list_schemas()
