"""
AST 节点定义 - DAL 表达式语法树节点

对应 Java: DAL-java 中的 Expression 类层次结构
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple, Dict


class ASTNode(ABC):
    """AST 节点基类"""
    
    def __repr__(self):
        return f"{self.__class__.__name__}()"


class Expression(ASTNode):
    """表达式基类"""
    pass


# ==================== 字面量 ====================

@dataclass
class Literal(Expression):
    """字面量节点"""
    value: Any
    
    def __repr__(self):
        return f"Literal({self.value!r})"


@dataclass
class NumberLiteral(Literal):
    """数字字面量"""
    
    def __post_init__(self):
        # 将字符串转换为数字
        if isinstance(self.value, str):
            if '.' in self.value:
                self.value = float(self.value)
            else:
                self.value = int(self.value)
    
    def __repr__(self):
        return f"NumberLiteral({self.value})"


@dataclass
class StringLiteral(Literal):
    """字符串字面量"""
    
    def __repr__(self):
        return f"StringLiteral({self.value!r})"


@dataclass
class BooleanLiteral(Literal):
    """布尔字面量"""
    value: bool
    
    def __repr__(self):
        return f"BooleanLiteral({self.value})"


@dataclass
class NullLiteral(Literal):
    """Null 字面量"""
    value: None = None
    
    def __repr__(self):
        return "NullLiteral()"


@dataclass
class RegexLiteral(Literal):
    """正则表达式字面量"""
    
    def __repr__(self):
        return f"RegexLiteral(/{self.value}/)"


# ==================== 标识符和访问 ====================

@dataclass
class Identifier(Expression):
    """标识符节点"""
    name: str
    
    def __repr__(self):
        return f"Identifier({self.name!r})"


@dataclass
class PropertyAccess(Expression):
    """属性访问节点：obj.property"""
    object: Expression
    property: str
    
    def __repr__(self):
        return f"PropertyAccess({self.object}, {self.property!r})"


@dataclass
class IndexAccess(Expression):
    """索引访问节点：obj[index]"""
    object: Expression
    index: Expression
    
    def __repr__(self):
        return f"IndexAccess({self.object}, {self.index})"


@dataclass
class MetaAccess(Expression):
    """元数据访问节点：obj::meta"""
    object: Expression
    meta_name: str
    
    def __repr__(self):
        return f"MetaAccess({self.object}, {self.meta_name!r})"


# ==================== 复合字面量 ====================

@dataclass
class ObjectProperty:
    """对象属性定义"""
    key: str
    value: Expression
    operator: str = ":"  # ":" 或 "="
    optional: bool = False  # 是否有 ? 标记
    
    def __repr__(self):
        opt = "?" if self.optional else ""
        return f"ObjectProperty({self.key!r}{opt} {self.operator} {self.value})"


@dataclass
class ObjectLiteral(Expression):
    """对象字面量节点：{ prop: value }"""
    properties: List[ObjectProperty]
    strict: bool = False  # 是否是 ={...} 严格模式
    
    def __repr__(self):
        mode = "=" if self.strict else ""
        return f"ObjectLiteral({mode}{{{', '.join(repr(p) for p in self.properties)}}})"


@dataclass
class ArrayLiteral(Expression):
    """数组字面量节点：[ value1, value2 ]"""
    elements: List[Expression]
    strict: bool = False  # 是否是 =[...] 严格模式
    
    def __repr__(self):
        mode = "=" if self.strict else ""
        return f"ArrayLiteral({mode}[{', '.join(repr(e) for e in self.elements)}])"


# ==================== 表格 ====================

@dataclass
class TableExpression(Expression):
    """表格表达式节点"""
    headers: List[str]
    rows: List[List[Expression]]
    strict: bool = False  # 是否是 =|...| 严格模式
    sort_by: Optional[str] = None  # 排序列
    sort_desc: bool = False  # 是否降序
    skip: int = 0  # 跳过行数
    row_header: bool = False  # 第一列是否为行标题
    transpose: bool = False  # 是否转置
    
    def __repr__(self):
        mode = "=" if self.strict else ""
        options = []
        if self.sort_by:
            order = "desc" if self.sort_desc else "asc"
            options.append(f"sort={self.sort_by}:{order}")
        if self.skip:
            options.append(f"skip={self.skip}")
        if self.row_header:
            options.append("row_header")
        if self.transpose:
            options.append("transpose")
        opts = f"[{', '.join(options)}]" if options else ""
        return f"TableExpression({mode}|{self.headers}|{opts}, {len(self.rows)} rows)"


# ==================== 操作符 ====================

@dataclass
class BinaryOp(Expression):
    """二元操作符节点"""
    left: Expression
    operator: str  # =, :, !=, >, <, >=, <=, and, or, +, -, *, /
    right: Expression
    
    def __repr__(self):
        return f"BinaryOp({self.left} {self.operator} {self.right})"


@dataclass
class UnaryOp(Expression):
    """一元操作符节点"""
    operator: str  # not, !, +, -
    operand: Expression
    
    def __repr__(self):
        return f"UnaryOp({self.operator} {self.operand})"


# ==================== 存在性检查 ====================

@dataclass
class ExistsCheck(Expression):
    """存在性检查节点：prop? 或 prop?:"""
    expression: Expression
    optional: bool = False  # 是否是 ?:（可选）
    
    def __repr__(self):
        opt = ":" if self.optional else ""
        return f"ExistsCheck({self.expression}?{opt})"


@dataclass
class NotExistsCheck(Expression):
    """不存在检查节点：!prop"""
    expression: Expression
    
    def __repr__(self):
        return f"NotExistsCheck(!{self.expression})"


# ==================== Schema ====================

@dataclass
class SchemaExpression(Expression):
    """Schema 验证节点：is SchemaName"""
    schema_name: str
    base: Optional[Expression] = None  # which 子句
    
    def __repr__(self):
        if self.base:
            return f"SchemaExpression(is {self.schema_name} which {self.base})"
        return f"SchemaExpression(is {self.schema_name})"


# ==================== 通配符 ====================

@dataclass
class Wildcard(Expression):
    """通配符节点"""
    level: int = 1  # 1: *, 2: **, 3: ***
    
    def __repr__(self):
        return f"Wildcard({'*' * self.level})"


# ==================== 工具函数 ====================

def dump_ast(node: ASTNode, indent: int = 0) -> str:
    """
    打印 AST 结构（用于调试）
    
    Args:
        node: AST 节点
        indent: 缩进级别
        
    Returns:
        格式化的 AST 字符串
        
    Example:
        >>> expr = BinaryOp(Literal(1), "+", Literal(2))
        >>> print(dump_ast(expr))
        BinaryOp
          left: Literal(1)
          operator: '+'
          right: Literal(2)
    """
    spaces = "  " * indent
    result = f"{spaces}{node.__class__.__name__}"
    
    if hasattr(node, '__dataclass_fields__'):
        for field_name in node.__dataclass_fields__:
            if field_name.startswith('_'):
                continue
            value = getattr(node, field_name)
            if isinstance(value, ASTNode):
                result += f"\n{spaces}  {field_name}:\n{dump_ast(value, indent + 2)}"
            elif isinstance(value, list):
                if value:
                    result += f"\n{spaces}  {field_name}:"
                    for item in value:
                        if isinstance(item, ASTNode):
                            result += f"\n{dump_ast(item, indent + 2)}"
                        else:
                            result += f"\n{spaces}    - {item!r}"
                else:
                    result += f"\n{spaces}  {field_name}: []"
            else:
                result += f"\n{spaces}  {field_name}: {value!r}"
    
    return result
