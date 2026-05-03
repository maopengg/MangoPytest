"""
数据访问 API - 使用 DAL 表达式访问数据

对应 Java: DAL-java 中的 Accessors 类
"""

from typing import Any
from .core.lexer import tokenize
from .core.parser import parse
from .core.runtime import DALRuntime, RuntimeContext


class Accessor:
    """
    数据访问器
    
    使用 DAL 表达式从数据中获取值
    
    Example:
        >>> data = {"user": {"name": "张三", "age": 25}}
        >>> get(data).property("user.name").value()
        '张三'
        >>> get(data).property("user.age").value()
        25
    """
    
    def __init__(self, data: Any):
        """
        创建访问器
        
        Args:
            data: 要访问的数据
        """
        self.data = data
        self.expression = ""
    
    def property(self, path: str) -> "Accessor":
        """
        设置属性路径
        
        Args:
            path: 属性路径，如 "user.name" 或 "items[0].id"
            
        Returns:
            self，支持链式调用
        """
        self.expression = path
        return self
    
    def value(self) -> Any:
        """
        获取值
        
        Returns:
            属性值
            
        Raises:
            AttributeError: 属性不存在
            KeyError: 键不存在
        """
        # 将路径转换为 DAL 表达式
        if not self.expression:
            return self.data
        
        # 解析表达式
        tokens = tokenize(self.expression)
        ast = parse(tokens)
        
        # 执行
        context = RuntimeContext(self.data)
        runtime = DALRuntime(context)
        result = runtime.evaluate(ast)
        
        if not result.success:
            if "not found" in result.message:
                raise AttributeError(result.message)
            raise RuntimeError(result.message)
        
        return result.value
    
    def optional(self) -> Any:
        """
        获取值（可选，不存在返回 None）
        
        Returns:
            属性值，不存在返回 None
        """
        try:
            return self.value()
        except (AttributeError, KeyError):
            return None


def get(data: Any) -> Accessor:
    """
    创建数据访问器
    
    Args:
        data: 要访问的数据
        
    Returns:
        Accessor 对象
        
    Example:
        >>> data = {"users": [{"name": "张三"}, {"name": "李四"}]}
        >>> get(data).property("users[0].name").value()
        '张三'
        >>> get(data).property("users.size").value()
        2
    """
    return Accessor(data)
