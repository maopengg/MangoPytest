"""
操作符实现 - DAL 表达式操作符的具体实现

对应 Java: DAL-java 中的各种 Checker 和 Operator 类
"""

import re
from typing import Any, Tuple, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from .ast_nodes import ObjectLiteral, ArrayLiteral


@dataclass
class CompareResult:
    """比较结果"""
    success: bool
    expected: str
    actual: str
    message: str = ""


class Operators:
    """
    DAL 操作符实现类
    
    提供所有 DAL 表达式的操作符实现
    支持自定义操作符注册
    """
    
    # 自定义操作符注册表
    _custom_operators: dict = {}
    
    @classmethod
    def register(cls, name: str, func=None):
        """
        注册自定义操作符
        
        可以作为装饰器使用：
            >>> @Operators.register("~=")
            ... def fuzzy_match(actual, expected):
            ...     return CompareResult(success=...)
        
        也可以直接调用：
            >>> Operators.register("~=", fuzzy_match)
        
        Args:
            name: 操作符名称
            func: 操作符函数，接收 (actual, expected) 参数，返回 CompareResult
        """
        def decorator(f):
            cls._custom_operators[name] = f
            return f
        
        if func is not None:
            return decorator(func)
        return decorator
    
    @classmethod
    def get_custom(cls, name: str):
        """获取自定义操作符"""
        return cls._custom_operators.get(name)
    
    @classmethod
    def list_custom(cls):
        """列出所有自定义操作符"""
        return list(cls._custom_operators.keys())
    
    @classmethod
    def unregister(cls, name: str):
        """注销自定义操作符"""
        if name in cls._custom_operators:
            del cls._custom_operators[name]
    
    @classmethod
    def clear_custom(cls):
        """清除所有自定义操作符"""
        cls._custom_operators.clear()
    
    # ==================== 相等性操作符 ====================
    
    @staticmethod
    def strict_equal(actual: Any, expected: Any) -> CompareResult:
        """
        = 严格相等操作符
        
        要求类型和值都完全相同
        但对于数字和字符串，如果字符串表示的数字相同，也视为相等
        
        Args:
            actual: 实际值
            expected: 期望值
            
        Returns:
            比较结果
        """
        # 处理 ObjectLiteral 类型（从 DAL 表达式解析的期望对象）
        if hasattr(expected, '__class__') and expected.__class__.__name__ == 'ObjectLiteral':
            return Operators._compare_object_literal(actual, expected, strict=True)
        
        # 处理 ArrayLiteral 类型
        if hasattr(expected, '__class__') and expected.__class__.__name__ == 'ArrayLiteral':
            return Operators._compare_array_literal(actual, expected, strict=True)
        
        # 处理 RegexLiteral 类型（正则匹配）
        if hasattr(expected, '__class__') and expected.__class__.__name__ == 'RegexLiteral':
            import re
            pattern = expected.value if hasattr(expected, 'value') else str(expected)
            if re.search(pattern, str(actual)):
                return CompareResult(success=True, expected=f"/{pattern}/", actual=str(actual))
            else:
                return CompareResult(
                    success=False,
                    expected=f"/{pattern}/",
                    actual=str(actual),
                    message=f"Value does not match pattern /{pattern}/"
                )
        
        # 类型检查 - 严格模式：int 和 float 视为不同类型
        # 但对于数字和字符串，如果字符串表示的数字相同，也视为相等
        if type(actual) != type(expected):
            # 处理数字和字符串的互转
            if isinstance(actual, str) and isinstance(expected, (int, float)):
                # 实际是字符串，期望是数字：尝试将字符串转为数字比较
                try:
                    if '.' in actual:
                        actual_as_num = float(actual)
                    else:
                        actual_as_num = int(actual)
                    if actual_as_num == expected:
                        return CompareResult(success=True, expected=repr(expected), actual=repr(actual))
                except ValueError:
                    pass
            elif isinstance(actual, (int, float)) and isinstance(expected, str):
                # 实际是数字，期望是字符串：尝试将数字转为字符串比较
                if str(actual) == expected:
                    return CompareResult(success=True, expected=repr(expected), actual=repr(actual))
            
            return CompareResult(
                success=False,
                expected=f"{type(expected).__name__} ({expected!r})",
                actual=f"{type(actual).__name__} ({actual!r})",
                message=f"Type mismatch: expected {type(expected).__name__}, got {type(actual).__name__}"
            )
        
        # 值检查
        if actual != expected:
            return CompareResult(
                success=False,
                expected=repr(expected),
                actual=repr(actual),
                message=f"Value mismatch"
            )
        
        return CompareResult(success=True, expected=repr(expected), actual=repr(actual))
    
    @staticmethod
    def _compare_object_literal(actual: Any, expected: Any, strict: bool = False) -> CompareResult:
        """比较对象字面量和实际对象"""
        # 实际值必须是字典类型
        if not isinstance(actual, dict):
            return CompareResult(
                success=False,
                expected=f"object ({expected!r})",
                actual=f"{type(actual).__name__} ({actual!r})",
                message=f"Type mismatch: expected object, got {type(actual).__name__}"
            )
        
        # 获取期望对象的属性
        from .ast_nodes import ObjectLiteral
        if isinstance(expected, ObjectLiteral):
            expected_props = {prop.key: prop.value for prop in expected.properties}
            is_strict = expected.strict
        else:
            return CompareResult(
                success=False,
                expected="object",
                actual=type(expected).__name__,
                message="Invalid expected value type"
            )
        
        # 严格模式：检查是否有额外的字段
        if is_strict or strict:
            for key in actual.keys():
                if key not in expected_props:
                    return CompareResult(
                        success=False,
                        expected=f"object with keys {list(expected_props.keys())}",
                        actual=f"object with extra key '{key}'",
                        message=f"Extra field '{key}' found in actual object"
                    )
        
        # 检查每个期望的属性
        for key, expected_value in expected_props.items():
            if key not in actual:
                return CompareResult(
                    success=False,
                    expected=f"property '{key}'",
                    actual="missing",
                    message=f"Property '{key}' not found"
                )
            
            actual_value = actual[key]
            
            # 递归比较属性值
            if hasattr(expected_value, '__class__') and expected_value.__class__.__name__ in ('ObjectLiteral', 'ArrayLiteral'):
                result = Operators._compare_object_literal(actual_value, expected_value, strict) if expected_value.__class__.__name__ == 'ObjectLiteral' else Operators._compare_array_literal(actual_value, expected_value, strict)
                if not result.success:
                    return result
            else:
                # 获取期望的原始值
                if hasattr(expected_value, 'value'):
                    expected_raw = expected_value.value
                else:
                    expected_raw = expected_value
                
                if actual_value != expected_raw:
                    return CompareResult(
                        success=False,
                        expected=f"{key} = {expected_raw!r}",
                        actual=f"{key} = {actual_value!r}",
                        message=f"Property '{key}' mismatch"
                    )
        
        return CompareResult(success=True, expected=str(expected), actual=str(actual))
    
    @staticmethod
    def _compare_array_literal(actual: Any, expected: Any, strict: bool = False) -> CompareResult:
        """比较数组字面量和实际数组"""
        # 实际值必须是列表类型
        if not isinstance(actual, list):
            return CompareResult(
                success=False,
                expected=f"array ({expected!r})",
                actual=f"{type(actual).__name__} ({actual!r})",
                message=f"Type mismatch: expected array, got {type(actual).__name__}"
            )
        
        # 获取期望数组的元素
        from .ast_nodes import ArrayLiteral
        if isinstance(expected, ArrayLiteral):
            expected_elements = expected.elements
            is_strict = expected.strict
        else:
            return CompareResult(
                success=False,
                expected="array",
                actual=type(expected).__name__,
                message="Invalid expected value type"
            )
        
        # 严格模式：检查数组长度
        if is_strict or strict:
            if len(actual) != len(expected_elements):
                return CompareResult(
                    success=False,
                    expected=f"array of length {len(expected_elements)}",
                    actual=f"array of length {len(actual)}",
                    message=f"Array length mismatch"
                )
        
        # 检查每个元素
        for i, expected_elem in enumerate(expected_elements):
            if i >= len(actual):
                return CompareResult(
                    success=False,
                    expected=f"element [{i}]",
                    actual="missing",
                    message=f"Element [{i}] not found"
                )
            
            actual_elem = actual[i]
            
            # 递归比较元素
            if hasattr(expected_elem, '__class__') and expected_elem.__class__.__name__ in ('ObjectLiteral', 'ArrayLiteral'):
                result = Operators._compare_object_literal(actual_elem, expected_elem, strict) if expected_elem.__class__.__name__ == 'ObjectLiteral' else Operators._compare_array_literal(actual_elem, expected_elem, strict)
                if not result.success:
                    return result
            else:
                # 获取期望的原始值
                if hasattr(expected_elem, 'value'):
                    expected_raw = expected_elem.value
                else:
                    expected_raw = expected_elem
                
                if actual_elem != expected_raw:
                    return CompareResult(
                        success=False,
                        expected=f"[{i}] = {expected_raw!r}",
                        actual=f"[{i}] = {actual_elem!r}",
                        message=f"Element [{i}] mismatch"
                    )
        
        return CompareResult(success=True, expected=str(expected), actual=str(actual))
    
    @staticmethod
    def loose_match(actual: Any, expected: Any) -> CompareResult:
        """
        : 宽容匹配操作符
        
        值相等即可，类型可以转换
        
        Args:
            actual: 实际值
            expected: 期望值
            
        Returns:
            比较结果
        """
        # 数字类型互相兼容
        if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
            if actual == expected:
                return CompareResult(success=True, expected=str(expected), actual=str(actual))
        
        # 字符串匹配（数字转字符串时去掉 .0）
        actual_str = str(actual)
        expected_str = str(expected)
        # 处理 123.0 -> 123 的情况
        if isinstance(actual, float) and actual == int(actual):
            actual_str = str(int(actual))
        if isinstance(expected, float) and expected == int(expected):
            expected_str = str(int(expected))
        if actual_str == expected_str:
            return CompareResult(success=True, expected=expected_str, actual=actual_str)
        
        return CompareResult(
            success=False,
            expected=repr(expected),
            actual=repr(actual),
            message=f"Value does not match"
        )
    
    @staticmethod
    def not_equal(actual: Any, expected: Any) -> CompareResult:
        """
        != 不等于操作符
        
        Args:
            actual: 实际值
            expected: 期望值
            
        Returns:
            比较结果
        """
        if actual == expected:
            return CompareResult(
                success=False,
                expected=f"!= {repr(expected)}",
                actual=repr(actual),
                message=f"Values should not be equal"
            )
        return CompareResult(success=True, expected=f"!= {repr(expected)}", actual=repr(actual))
    
    # ==================== 比较操作符 ====================
    
    @staticmethod
    def greater_than(actual: Any, expected: Any) -> CompareResult:
        """> 大于操作符"""
        try:
            if actual > expected:
                return CompareResult(success=True, expected=f"> {expected}", actual=str(actual))
            return CompareResult(
                success=False,
                expected=f"> {expected}",
                actual=str(actual),
                message=f"{actual} is not greater than {expected}"
            )
        except TypeError:
            return CompareResult(
                success=False,
                expected=f"> {expected}",
                actual=str(actual),
                message=f"Cannot compare {type(actual).__name__} with {type(expected).__name__}"
            )
    
    @staticmethod
    def less_than(actual: Any, expected: Any) -> CompareResult:
        """< 小于操作符"""
        try:
            if actual < expected:
                return CompareResult(success=True, expected=f"< {expected}", actual=str(actual))
            return CompareResult(
                success=False,
                expected=f"< {expected}",
                actual=str(actual),
                message=f"{actual} is not less than {expected}"
            )
        except TypeError:
            return CompareResult(
                success=False,
                expected=f"< {expected}",
                actual=str(actual),
                message=f"Cannot compare {type(actual).__name__} with {type(expected).__name__}"
            )
    
    @staticmethod
    def greater_equal(actual: Any, expected: Any) -> CompareResult:
        """>= 大于等于操作符"""
        try:
            if actual >= expected:
                return CompareResult(success=True, expected=f">= {expected}", actual=str(actual))
            return CompareResult(
                success=False,
                expected=f">= {expected}",
                actual=str(actual),
                message=f"{actual} is not greater than or equal to {expected}"
            )
        except TypeError:
            return CompareResult(
                success=False,
                expected=f">= {expected}",
                actual=str(actual),
                message=f"Cannot compare {type(actual).__name__} with {type(expected).__name__}"
            )
    
    @staticmethod
    def less_equal(actual: Any, expected: Any) -> CompareResult:
        """<= 小于等于操作符"""
        try:
            if actual <= expected:
                return CompareResult(success=True, expected=f"<= {expected}", actual=str(actual))
            return CompareResult(
                success=False,
                expected=f"<= {expected}",
                actual=str(actual),
                message=f"{actual} is not less than or equal to {expected}"
            )
        except TypeError:
            return CompareResult(
                success=False,
                expected=f"<= {expected}",
                actual=str(actual),
                message=f"Cannot compare {type(actual).__name__} with {type(expected).__name__}"
            )
    
    # ==================== 逻辑操作符 ====================
    
    @staticmethod
    def logical_and(left: bool, right: bool) -> bool:
        """and 逻辑与操作符"""
        return left and right
    
    @staticmethod
    def logical_or(left: bool, right: bool) -> bool:
        """or 逻辑或操作符"""
        return left or right
    
    @staticmethod
    def logical_not(operand: bool) -> bool:
        """not 逻辑非操作符"""
        return not operand
    
    # ==================== 算术操作符 ====================
    
    @staticmethod
    def add(left: Any, right: Any) -> Any:
        """+ 加法操作符"""
        return left + right
    
    @staticmethod
    def subtract(left: Any, right: Any) -> Any:
        """- 减法操作符"""
        return left - right
    
    @staticmethod
    def multiply(left: Any, right: Any) -> Any:
        """* 乘法操作符"""
        return left * right
    
    @staticmethod
    def divide(left: Any, right: Any) -> Any:
        """/ 除法操作符"""
        return left / right
    
    @staticmethod
    def positive(operand: Any) -> Any:
        """+ 正号操作符"""
        return +operand
    
    @staticmethod
    def negative(operand: Any) -> Any:
        """- 负号操作符"""
        return -operand
    
    # ==================== 正则操作符 ====================
    
    @staticmethod
    def regex_match(actual: str, pattern: str) -> CompareResult:
        """
        /pattern/ 正则匹配操作符
        
        Args:
            actual: 实际字符串
            pattern: 正则表达式模式
            
        Returns:
            比较结果
        """
        try:
            if re.search(pattern, str(actual)):
                return CompareResult(success=True, expected=f"/{pattern}/", actual=str(actual))
            return CompareResult(
                success=False,
                expected=f"/{pattern}/",
                actual=str(actual),
                message=f"String does not match pattern /{pattern}/"
            )
        except re.error as e:
            return CompareResult(
                success=False,
                expected=f"/{pattern}/",
                actual=str(actual),
                message=f"Invalid regex pattern: {e}"
            )
    
    # ==================== 对象/列表操作 ====================
    
    @staticmethod
    def get_property(obj: Any, property_name: str) -> Any:
        """
        获取对象属性
        
        Args:
            obj: 对象
            property_name: 属性名
            
        Returns:
            属性值
            
        Raises:
            AttributeError: 属性不存在（对象类型）
            KeyError: 键不存在（字典类型）
        """
        if obj is None:
            raise AttributeError(f"Cannot get property '{property_name}' from null")
        
        # 特殊属性：size（列表/字典长度）
        if property_name == "size":
            return Operators.get_size(obj)
        
        # 字典类型
        if isinstance(obj, dict):
            if property_name not in obj:
                raise KeyError(f"Property '{property_name}' not found in object")
            return obj[property_name]
        
        # 对象类型
        if hasattr(obj, property_name):
            return getattr(obj, property_name)
        
        raise AttributeError(f"Property '{property_name}' not found in {type(obj).__name__}")
    
    @staticmethod
    def get_index(obj: Any, index: Any) -> Any:
        """
        获取列表/数组索引
        
        Args:
            obj: 列表或对象
            index: 索引值
            
        Returns:
            索引处的值
            
        Raises:
            IndexError: 索引越界
            TypeError: 类型错误
        """
        if obj is None:
            raise TypeError(f"Cannot index null")
        
        # 列表类型
        if isinstance(obj, list):
            if not isinstance(index, int):
                raise TypeError(f"List index must be integer, got {type(index).__name__}")
            if index < 0 or index >= len(obj):
                raise IndexError(f"List index {index} out of range [0, {len(obj)})")
            return obj[index]
        
        # 字典类型（字符串索引）
        if isinstance(obj, dict):
            if index not in obj:
                raise KeyError(f"Key '{index}' not found in object")
            return obj[index]
        
        raise TypeError(f"Cannot index {type(obj).__name__}")
    
    @staticmethod
    def get_size(obj: Any) -> int:
        """
        获取对象大小
        
        Args:
            obj: 对象
            
        Returns:
            大小（列表长度或对象键数量）
        """
        if obj is None:
            return 0
        if isinstance(obj, list):
            return len(obj)
        if isinstance(obj, dict):
            return len(obj)
        if isinstance(obj, str):
            return len(obj)
        return 0
    
    @staticmethod
    def get_keys(obj: Any) -> list:
        """
        获取对象的所有键
        
        Args:
            obj: 对象
            
        Returns:
            键列表
        """
        if isinstance(obj, dict):
            return list(obj.keys())
        return []
    
    @staticmethod
    def check_exists(obj: Any, property_name: str) -> bool:
        """
        检查属性是否存在
        
        Args:
            obj: 对象
            property_name: 属性名
            
        Returns:
            是否存在
        """
        if obj is None:
            return False
        if isinstance(obj, dict):
            return property_name in obj
        return hasattr(obj, property_name)


# ==================== 便捷函数 ====================

def compare(operator: str, actual: Any, expected: Any) -> CompareResult:
    """
    根据操作符进行比较
    
    支持内置操作符和自定义操作符
    
    Args:
        operator: 操作符字符串 (=, :, !=, >, <, >=, <=, 或自定义操作符)
        actual: 实际值
        expected: 期望值
        
    Returns:
        比较结果
    """
    ops = {
        "=": Operators.strict_equal,
        ":": Operators.loose_match,
        "!=": Operators.not_equal,
        ">": Operators.greater_than,
        "<": Operators.less_than,
        ">=": Operators.greater_equal,
        "<=": Operators.less_equal,
    }
    
    # 检查是否是内置操作符
    if operator in ops:
        return ops[operator](actual, expected)
    
    # 检查是否是自定义操作符
    custom_op = Operators.get_custom(operator)
    if custom_op is not None:
        return custom_op(actual, expected)
    
    raise ValueError(f"Unknown operator: {operator}")
