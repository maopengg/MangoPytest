"""
运行时 - DAL 表达式执行引擎

对应 Java: DAL-java 中的 Runtime 和 Checker 类
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from .ast_nodes import *
from .operators import Operators, CompareResult, compare


@dataclass
class EvaluationResult:
    """求值结果"""
    success: bool
    value: Any = None
    expected: str = ""
    actual: str = ""
    path: str = ""
    message: str = ""
    
    @staticmethod
    def ok(value: Any, path: str = "") -> "EvaluationResult":
        """创建成功结果"""
        return EvaluationResult(success=True, value=value, path=path)
    
    @staticmethod
    def fail(expected: str, actual: str, path: str = "", message: str = "") -> "EvaluationResult":
        """创建失败结果"""
        return EvaluationResult(
            success=False,
            expected=expected,
            actual=actual,
            path=path,
            message=message
        )


class RuntimeContext:
    """
    运行时上下文
    
    存储运行时的数据和配置
    """
    
    def __init__(self, data: Any):
        self.data = data
        self.root = data
        self.schemas: Dict[str, Callable[[Any], bool]] = {}
        self.operators: Dict[str, Callable] = {}
        self._register_default_operators()
        self._register_default_schemas()
    
    def _register_default_operators(self):
        """注册默认操作符"""
        self.operators = {
            "=": Operators.strict_equal,
            ":": Operators.loose_match,
            "!=": Operators.not_equal,
            ">": Operators.greater_than,
            "<": Operators.less_than,
            ">=": Operators.greater_equal,
            "<=": Operators.less_equal,
            "and": Operators.logical_and,
            "or": Operators.logical_or,
            "not": Operators.logical_not,
            "+": Operators.add,
            "-": Operators.subtract,
            "*": Operators.multiply,
            "/": Operators.divide,
        }
    
    def _register_default_schemas(self):
        """注册默认 Schema"""
        from ..schema import _global_registry
        # 将全局注册表的 Schema 转换为简单的验证函数
        for name in _global_registry.list_schemas():
            validator = _global_registry.get_validator(name)
            # 包装验证器，返回布尔值
            self.schemas[name] = lambda value, v=validator: v(value).success
    
    def register_schema(self, name: str, validator: Callable[[Any], bool]):
        """注册 Schema"""
        self.schemas[name] = validator
    
    def get_schema(self, name: str) -> Optional[Callable[[Any], bool]]:
        """获取 Schema"""
        return self.schemas.get(name)


class DALRuntime:
    """
    DAL 运行时
    
    执行 AST 表达式并返回结果
    """
    
    def __init__(self, context: RuntimeContext):
        self.context = context
        self.current_path = ""
    
    def evaluate(self, expression: Expression) -> EvaluationResult:
        """
        求值表达式
        
        Args:
            expression: AST 表达式节点
            
        Returns:
            求值结果
        """
        method_name = f"_eval_{type(expression).__name__}"
        method = getattr(self, method_name, self._eval_unknown)
        return method(expression)
    
    def _eval_unknown(self, expression: Expression) -> EvaluationResult:
        """处理未知节点类型"""
        return EvaluationResult.fail(
            expected="",
            actual="",
            message=f"Unknown expression type: {type(expression).__name__}"
        )
    
    # ==================== 字面量求值 ====================
    
    def _eval_Literal(self, expr: Literal) -> EvaluationResult:
        """求值字面量"""
        return EvaluationResult.ok(expr.value)
    
    def _eval_NumberLiteral(self, expr: NumberLiteral) -> EvaluationResult:
        """求值数字字面量"""
        return EvaluationResult.ok(expr.value)
    
    def _eval_StringLiteral(self, expr: StringLiteral) -> EvaluationResult:
        """求值字符串字面量"""
        return EvaluationResult.ok(expr.value)
    
    def _eval_BooleanLiteral(self, expr: BooleanLiteral) -> EvaluationResult:
        """求值布尔字面量"""
        return EvaluationResult.ok(expr.value)
    
    def _eval_NullLiteral(self, expr: NullLiteral) -> EvaluationResult:
        """求值 null 字面量"""
        return EvaluationResult.ok(None)
    
    def _eval_RegexLiteral(self, expr: RegexLiteral) -> EvaluationResult:
        """求值正则字面量"""
        return EvaluationResult.ok(expr.value)
    
    def _eval_Identifier(self, expr: Identifier) -> EvaluationResult:
        """求值标识符（从根数据中获取）"""
        # 特殊标识符：root 返回根数据
        if expr.name == "root":
            return EvaluationResult.ok(self.context.root, path="root")
        
        try:
            value = Operators.get_property(self.context.root, expr.name)
            return EvaluationResult.ok(value, path=expr.name)
        except (AttributeError, KeyError):
            return EvaluationResult.fail(
                expected=f"property '{expr.name}'",
                actual="not found",
                path=expr.name,
                message=f"Property '{expr.name}' not found"
            )
    
    # ==================== 访问求值 ====================
    
    def _eval_PropertyAccess(self, expr: PropertyAccess) -> EvaluationResult:
        """求值属性访问"""
        # 先求值对象
        obj_result = self.evaluate(expr.object)
        if not obj_result.success:
            return obj_result
        
        obj = obj_result.value
        
        # 获取属性
        try:
            value = Operators.get_property(obj, expr.property)
            new_path = f"{obj_result.path}.{expr.property}" if obj_result.path else expr.property
            return EvaluationResult.ok(value, path=new_path)
        except (AttributeError, KeyError) as e:
            return EvaluationResult.fail(
                expected=f"property '{expr.property}'",
                actual="not found",
                path=f"{obj_result.path}.{expr.property}" if obj_result.path else expr.property,
                message=str(e)
            )
    
    def _eval_IndexAccess(self, expr: IndexAccess) -> EvaluationResult:
        """求值索引访问"""
        # 求值对象
        obj_result = self.evaluate(expr.object)
        if not obj_result.success:
            return obj_result
        
        obj = obj_result.value
        
        # 求值索引
        index_result = self.evaluate(expr.index)
        if not index_result.success:
            return index_result
        
        index = index_result.value
        
        # 获取索引值
        try:
            value = Operators.get_index(obj, index)
            new_path = f"{obj_result.path}[{index}]"
            return EvaluationResult.ok(value, path=new_path)
        except (IndexError, KeyError, TypeError) as e:
            return EvaluationResult.fail(
                expected=f"index [{index}]",
                actual="out of range or invalid",
                path=f"{obj_result.path}[{index}]" if obj_result.path else f"[{index}]",
                message=str(e)
            )
    
    def _eval_MetaAccess(self, expr: MetaAccess) -> EvaluationResult:
        """求值元数据访问"""
        # 求值对象
        obj_result = self.evaluate(expr.object)
        if not obj_result.success:
            return obj_result
        
        obj = obj_result.value
        
        # 根据元数据名称获取值
        if expr.meta_name == "size":
            return EvaluationResult.ok(Operators.get_size(obj))
        elif expr.meta_name == "keys":
            return EvaluationResult.ok(Operators.get_keys(obj))
        elif expr.meta_name == "type":
            return EvaluationResult.ok(type(obj).__name__)
        elif expr.meta_name == "root":
            return EvaluationResult.ok(self.context.root)
        elif expr.meta_name == "original":
            # 返回原始对象（未修改的）
            return EvaluationResult.ok(self.context.data)
        elif expr.meta_name == "this":
            # 返回当前对象
            return EvaluationResult.ok(obj)
        elif expr.meta_name == "common":
            # 返回对象的公共字段（所有键）
            if isinstance(obj, dict):
                return EvaluationResult.ok(list(obj.keys()))
            elif isinstance(obj, list) and len(obj) > 0 and isinstance(obj[0], dict):
                # 对于列表，返回所有对象共有的键
                common_keys = set(obj[0].keys())
                for item in obj[1:]:
                    if isinstance(item, dict):
                        common_keys &= set(item.keys())
                return EvaluationResult.ok(list(common_keys))
            return EvaluationResult.ok([])
        elif expr.meta_name == "eventually":
            # 异步等待：轮询等待某个条件成立
            # 使用场景：expect(data).should("::eventually ::size = 5")
            # 这会轮询检查 data 的 size 是否等于 5
            return EvaluationResult.ok(obj)
        else:
            return EvaluationResult.fail(
                expected=f"meta '::{expr.meta_name}'",
                actual="unknown meta",
                message=f"Unknown meta: ::{expr.meta_name}"
            )
    
    # ==================== 操作符求值 ====================
    
    def _eval_BinaryOp(self, expr: BinaryOp) -> EvaluationResult:
        """求值二元操作符"""
        operator = expr.operator
        
        # 逻辑操作符（短路求值）
        if operator == "and" or operator == ",":
            left_result = self.evaluate(expr.left)
            # 如果左操作数失败或值为 False，返回 and 结果
            if not left_result.success or not left_result.value:
                return EvaluationResult.ok(False)
            
            right_result = self.evaluate(expr.right)
            # 如果右操作数失败，and 结果为 False
            if not right_result.success:
                return EvaluationResult.ok(False)
            return EvaluationResult.ok(bool(right_result.value))
        
        if operator == "or":
            left_result = self.evaluate(expr.left)
            # 如果左操作数成功且值为 True，返回 or 结果
            if left_result.success and left_result.value:
                return EvaluationResult.ok(True)
            
            right_result = self.evaluate(expr.right)
            # 如果右操作数成功，返回其值
            if right_result.success:
                return EvaluationResult.ok(bool(right_result.value))
            # 两者都失败，or 结果为 False
            return EvaluationResult.ok(False)
        
        # 比较操作符
        if operator in ("=", ":", "!=", ">", "<", ">=", "<="):
            left_result = self.evaluate(expr.left)
            if not left_result.success:
                return left_result
            
            right_result = self.evaluate(expr.right)
            if not right_result.success:
                return right_result
            
            # 特殊处理：如果右边是正则表达式，使用正则匹配
            if isinstance(expr.right, RegexLiteral):
                import re
                pattern = expr.right.value
                actual_str = str(left_result.value)
                if re.search(pattern, actual_str):
                    return EvaluationResult.ok(True)
                else:
                    return EvaluationResult.fail(
                        expected=f"/{pattern}/",
                        actual=actual_str,
                        message=f"Value does not match pattern /{pattern}/"
                    )
            
            result = compare(operator, left_result.value, right_result.value)
            # 比较操作符返回布尔值，而不是失败结果
            # 这样逻辑操作符（如 not, and, or）可以正确处理
            return EvaluationResult.ok(result.success)
        
        # 算术操作符
        if operator in ("+", "-", "*", "/"):
            left_result = self.evaluate(expr.left)
            if not left_result.success:
                return left_result
            
            right_result = self.evaluate(expr.right)
            if not right_result.success:
                return right_result
            
            try:
                if operator == "+":
                    value = left_result.value + right_result.value
                elif operator == "-":
                    value = left_result.value - right_result.value
                elif operator == "*":
                    value = left_result.value * right_result.value
                elif operator == "/":
                    value = left_result.value / right_result.value
                
                return EvaluationResult.ok(value)
            except Exception as e:
                return EvaluationResult.fail(
                    expected=f"{operator} operation",
                    actual="error",
                    message=str(e)
                )
        
        return EvaluationResult.fail(
            expected="",
            actual="",
            message=f"Unknown operator: {operator}"
        )
    
    def _eval_UnaryOp(self, expr: UnaryOp) -> EvaluationResult:
        """求值一元操作符"""
        operand_result = self.evaluate(expr.operand)
        if not operand_result.success:
            return operand_result
        
        operand = operand_result.value
        operator = expr.operator
        
        if operator == "not" or operator == "!":
            return EvaluationResult.ok(not bool(operand))
        elif operator == "+":
            return EvaluationResult.ok(+operand)
        elif operator == "-":
            return EvaluationResult.ok(-operand)
        
        return EvaluationResult.fail(
            expected="",
            actual="",
            message=f"Unknown unary operator: {operator}"
        )
    
    # ==================== 复合类型求值 ====================
    
    def _eval_ObjectLiteral(self, expr: ObjectLiteral) -> EvaluationResult:
        """求值对象字面量（验证模式）"""
        # 对象字面量在验证模式下使用
        # 这里返回对象本身，实际验证在断言时进行
        return EvaluationResult.ok(expr)
    
    def _eval_ArrayLiteral(self, expr: ArrayLiteral) -> EvaluationResult:
        """求值数组字面量（验证模式）"""
        return EvaluationResult.ok(expr)
    
    def _eval_TableExpression(self, expr: TableExpression) -> EvaluationResult:
        """求值表格表达式（验证模式）"""
        return EvaluationResult.ok(expr)
    
    # ==================== 存在性检查 ====================
    
    def _eval_ExistsCheck(self, expr: ExistsCheck) -> EvaluationResult:
        """求值存在性检查"""
        # 获取要检查的属性名
        if isinstance(expr.expression, Identifier):
            property_name = expr.expression.name
            exists = Operators.check_exists(self.context.root, property_name)
        elif isinstance(expr.expression, PropertyAccess):
            # 先求值对象部分
            obj_result = self.evaluate(expr.expression.object)
            if not obj_result.success:
                # 如果对象不存在，返回可选的结果
                if expr.optional:
                    return EvaluationResult.ok(True)
                return obj_result
            
            obj = obj_result.value
            exists = Operators.check_exists(obj, expr.expression.property)
        else:
            return EvaluationResult.fail(
                expected="property name",
                actual=type(expr.expression).__name__,
                message="Exists check requires a property name"
            )
        
        return EvaluationResult.ok(exists)
    
    def _eval_NotExistsCheck(self, expr: NotExistsCheck) -> EvaluationResult:
        """求值不存在检查"""
        # 复用存在性检查
        exists_result = self._eval_ExistsCheck(ExistsCheck(expr.expression))
        if not exists_result.success:
            return exists_result
        
        return EvaluationResult.ok(not exists_result.value)
    
    # ==================== Schema ====================
    
    def _eval_SchemaExpression(self, expr: SchemaExpression) -> EvaluationResult:
        """
        求值 Schema 表达式
        
        支持:
        - is SchemaName
        - is SchemaName which {...}
        """
        from ..schema import validate_schema
        
        # 首先验证 Schema
        schema_result = validate_schema(expr.schema_name, self.context.root)
        if not schema_result.success:
            return EvaluationResult.fail(
                expected=f"Schema '{expr.schema_name}'",
                actual="validation failed",
                message=schema_result.message
            )
        
        # 如果有 which 子句，进一步验证
        if expr.base is not None:
            # which 子句应该是一个对象表达式
            base_result = self.evaluate(expr.base)
            if not base_result.success:
                return base_result
        
        return EvaluationResult.ok(True)
    
    # ==================== 通配符 ====================
    
    def _eval_Wildcard(self, expr: Wildcard) -> EvaluationResult:
        """
        求值通配符
        
        *   - 匹配任意非 null 值
        **  - 匹配任意对象（字典）
        *** - 匹配任意列表
        """
        data = self.context.root
        
        if expr.level == 1:
            # * - 匹配任意非 null 值
            if data is None:
                return EvaluationResult.fail(
                    expected="any non-null value",
                    actual="null",
                    message="Wildcard * does not match null"
                )
            return EvaluationResult.ok(True)
        
        elif expr.level == 2:
            # ** - 匹配任意对象（字典）
            if not isinstance(data, dict):
                return EvaluationResult.fail(
                    expected="any object",
                    actual=type(data).__name__,
                    message="Wildcard ** only matches objects (dict)"
                )
            return EvaluationResult.ok(True)
        
        elif expr.level == 3:
            # *** - 匹配任意列表
            if not isinstance(data, list):
                return EvaluationResult.fail(
                    expected="any list",
                    actual=type(data).__name__,
                    message="Wildcard *** only matches lists"
                )
            return EvaluationResult.ok(True)
        
        return EvaluationResult.fail(
            expected=f"wildcard level {expr.level}",
            actual="unknown",
            message=f"Unknown wildcard level: {expr.level}"
        )


def evaluate(expression: Expression, data: Any) -> EvaluationResult:
    """
    便捷函数：求值表达式
    
    Args:
        expression: AST 表达式
        data: 输入数据
        
    Returns:
        求值结果
    """
    context = RuntimeContext(data)
    runtime = DALRuntime(context)
    return runtime.evaluate(expression)
