"""
语法分析器 - 将 Token 序列解析为 AST

使用递归下降解析器实现
对应 Java: DAL-java 中的 Parser 类
"""

from typing import List, Optional
from .lexer import Token, TokenType
from .ast_nodes import *


class ParseError(Exception):
    """解析错误"""
    pass


class Parser:
    """
    DAL 语法分析器
    
    将 Token 序列解析为 AST（抽象语法树）
    
    语法规则（简化版）：
        expression     → equality
        equality       → comparison ( ( "=" | ":" | "!=" ) comparison )*
        comparison     → term ( ( ">" | ">=" | "<" | "<=" ) term )*
        term           → factor ( ( "+" | "-" | "and" | "&&" | "," ) factor )*
        factor         → unary ( ( "*" | "/" | "or" | "||" ) unary )*
        unary          → ( "not" | "!" | "+" | "-" ) unary | primary
        primary        → literal | identifier | property_access | index_access
                        | object_literal | array_literal | table_literal
                        | "(" expression ")" | schema_check | exists_check
    """
    
    def __init__(self, tokens: List[Token]):
        # 过滤掉 NEWLINE token，但保留 EOF
        self.tokens = [t for t in tokens if t.type != TokenType.NEWLINE]
        self.pos = 0
    
    def parse(self) -> Expression:
        """解析表达式"""
        expr = self._parse_expression()
        if not self._is_at_end():
            raise ParseError(f"Unexpected token: {self._peek()}")
        return expr
    
    def _is_at_end(self) -> bool:
        """检查是否到达 Token 列表末尾"""
        return self._peek().type == TokenType.EOF
    
    def _peek(self, offset: int = 0) -> Token:
        """查看当前位置或偏移位置的 Token"""
        pos = self.pos + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]  # EOF
        return self.tokens[pos]
    
    def _previous(self) -> Token:
        """获取前一个 Token"""
        return self.tokens[self.pos - 1]
    
    def _advance(self) -> Token:
        """前进并返回当前 Token"""
        if not self._is_at_end():
            self.pos += 1
        return self._previous()
    
    def _match(self, *types: TokenType) -> bool:
        """匹配并消耗指定类型的 Token"""
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True
        return False
    
    def _check(self, token_type: TokenType) -> bool:
        """检查当前 Token 是否是指定类型"""
        if self._is_at_end():
            return False
        return self._peek().type == token_type
    
    def _consume(self, token_type: TokenType, message: str) -> Token:
        """消耗指定类型的 Token，否则报错"""
        if self._check(token_type):
            return self._advance()
        raise ParseError(f"{message} at line {self._peek().line}, column {self._peek().column}")
    
    def _parse_expression(self) -> Expression:
        """解析表达式（入口）
        
        支持隐式根对象访问（以操作符开头时，自动添加 root 标识符）
        例如：= 1, > 3, ~ 'hello' 会被解析为 root = 1, root > 3, root ~ 'hello'
        """
        # 检查是否是严格字面量：=[...] 或 ={...}
        if self._check(TokenType.EQ):
            if self._peek(1).type == TokenType.LBRACKET:
                self._advance()  # 消耗 =
                self._advance()  # 消耗 [
                return self._parse_array_literal(strict=True)
            elif self._peek(1).type == TokenType.LBRACE:
                self._advance()  # 消耗 =
                self._advance()  # 消耗 {
                return self._parse_object_literal(strict=True)
            elif self._peek(1).type == TokenType.PIPE:
                self._advance()  # 消耗 =
                # 不要消耗 |，让 _parse_table_literal 来处理
                return self._parse_table_literal(strict=True)
        
        # 检查是否以二元操作符开头（隐式根对象访问）
        if self._is_binary_operator_start():
            # 检查是否是表格字面量 : | ...
            if self._check(TokenType.COLON) and self._peek(1).type == TokenType.PIPE:
                self._advance()  # 消耗 :
                return self._parse_table_literal(strict=False)
            
            # 创建隐式根标识符
            root = Identifier("root")
            # 处理 .property 这样的属性访问
            if self._match(TokenType.DOT):
                if not self._match(TokenType.IDENTIFIER):
                    raise ParseError(f"Expected property name after '.' at line {self._peek().line}")
                expr = PropertyAccess(root, self._previous().value)
                # 继续解析属性链
                expr = self._parse_property_chain(expr)
                # 继续解析 or 链
                return self._parse_or_chain(expr)
            # 处理 [index] 这样的索引访问
            elif self._check(TokenType.LBRACKET):
                expr = self._parse_index_access(root)
                # 继续解析 or 链
                return self._parse_or_chain(expr)
            # 处理其他二元操作符（如 =, > 等）
            # 直接解析 or 链，让 _parse_or_suffix 处理 = 操作符
            return self._parse_or_chain(root)
        
        return self._parse_or_chain(self._parse_equality())
    
    def _parse_or_chain(self, left: Expression) -> Expression:
        """解析 or 操作符链"""
        expr = left
        while self._match(TokenType.OR):
            # or 右侧调用 _parse_equality 以支持 = 操作符
            if self._is_binary_operator_start():
                root = Identifier("root")
                right = self._parse_binary_chain(root)
            else:
                right = self._parse_equality()
            expr = BinaryOp(expr, "or", right)
        return expr
    
    def _parse_index_access(self, obj: Expression) -> Expression:
        """解析索引访问 [index]"""
        self._advance()  # 消耗 [
        index = self._parse_expression()
        self._consume(TokenType.RBRACKET, "Expected ']' after index")
        expr = IndexAccess(obj, index)
        # 继续解析属性链
        return self._parse_property_chain(expr)
    
    def _is_binary_operator_start(self) -> bool:
        """检查当前 token 是否是二元操作符（用于隐式根访问）"""
        binary_ops = [
            TokenType.EQ, TokenType.COLON, TokenType.NE,
            TokenType.GT, TokenType.GE, TokenType.LT, TokenType.LE,
            TokenType.MATCH, TokenType.CONTAINS, TokenType.STARTS,
            TokenType.ENDS, TokenType.IN,
            TokenType.DOT, TokenType.LBRACKET  # 支持 .size 和 [0] 这样的隐式根访问
        ]
        return any(self._check(t) for t in binary_ops)
    
    def _parse_equality(self) -> Expression:
        """解析相等性表达式：=, :, !=, is"""
        expr = self._parse_factor()
        
        while True:
            if self._match(TokenType.EQ):
                right = self._parse_factor()
                expr = BinaryOp(expr, "=", right)
            elif self._match(TokenType.COLON):
                # 检查是否是 :: 元数据访问
                if self._check(TokenType.IDENTIFIER):
                    # 可能是 ::size 等元数据访问
                    expr = self._parse_meta_access(expr)
                else:
                    right = self._parse_factor()
                    expr = BinaryOp(expr, ":", right)
            elif self._match(TokenType.NE):
                right = self._parse_factor()
                expr = BinaryOp(expr, "!=", right)
            elif self._match(TokenType.IS):
                # Schema 检查
                expr = self._parse_schema_check(expr)
            # 比较操作符
            elif self._match(TokenType.GT):
                right = self._parse_factor()
                expr = BinaryOp(expr, ">", right)
            elif self._match(TokenType.GE):
                right = self._parse_factor()
                expr = BinaryOp(expr, ">=", right)
            elif self._match(TokenType.LT):
                right = self._parse_factor()
                expr = BinaryOp(expr, "<", right)
            elif self._match(TokenType.LE):
                right = self._parse_factor()
                expr = BinaryOp(expr, "<=", right)
            else:
                break
        
        return expr
    
    def _parse_binary_chain(self, left: Expression) -> Expression:
        """解析二元操作符链（用于隐式根访问），使用给定的左操作数
        
        处理 =, :, !=, >, <, >=, <= 等操作符
        """
        expr = left
        
        while True:
            # 相等性操作符
            if self._match(TokenType.EQ):
                right = self._parse_factor()
                expr = BinaryOp(expr, "=", right)
            elif self._match(TokenType.COLON):
                # 检查是否是 :: 元数据访问
                if self._check(TokenType.IDENTIFIER):
                    # 可能是 ::size 等元数据访问
                    expr = self._parse_meta_access(expr)
                else:
                    right = self._parse_factor()
                    expr = BinaryOp(expr, ":", right)
            elif self._match(TokenType.NE):
                right = self._parse_factor()
                expr = BinaryOp(expr, "!=", right)
            elif self._match(TokenType.IS):
                # Schema 检查
                expr = self._parse_schema_check(expr)
            # 比较操作符
            elif self._match(TokenType.GT):
                right = self._parse_factor()
                expr = BinaryOp(expr, ">", right)
            elif self._match(TokenType.GE):
                right = self._parse_factor()
                expr = BinaryOp(expr, ">=", right)
            elif self._match(TokenType.LT):
                right = self._parse_factor()
                expr = BinaryOp(expr, "<", right)
            elif self._match(TokenType.LE):
                right = self._parse_factor()
                expr = BinaryOp(expr, "<=", right)
            else:
                break
        
        return expr
    
    def _parse_comparison(self) -> Expression:
        """解析比较表达式：>, >=, <, <= """
        # 检查是否以比较操作符开头（隐式根访问）
        if any(self._check(t) for t in [TokenType.GT, TokenType.GE, TokenType.LT, TokenType.LE]):
            root = Identifier("root")
            return self._parse_binary_chain(root)
        
        expr = self._parse_term()
        return expr
    
    def _parse_term(self) -> Expression:
        """解析加减项：+, -, and, &&, ,"""
        # 检查是否以逻辑操作符开头（隐式根访问）
        if self._check(TokenType.AND):
            root = Identifier("root")
            return self._parse_binary_chain(root)
        
        expr = self._parse_factor()
        
        while True:
            if self._match(TokenType.PLUS):
                right = self._parse_factor()
                expr = BinaryOp(expr, "+", right)
            elif self._match(TokenType.MINUS):
                right = self._parse_factor()
                expr = BinaryOp(expr, "-", right)
            elif self._match(TokenType.AND):
                right = self._parse_factor()
                expr = BinaryOp(expr, "and", right)
            elif self._match(TokenType.COMMA):
                # 逗号作为 and
                right = self._parse_factor()
                expr = BinaryOp(expr, ",", right)
            else:
                break
        
        return expr
    
    def _parse_factor(self) -> Expression:
        """解析因子：*, /, or, ||"""
        # 检查是否以二元操作符开头（隐式根访问）
        if self._is_binary_operator_start():
            root = Identifier("root")
            expr = self._parse_binary_chain(root)
            # 继续解析 or
            return self._parse_or_suffix(expr)
        
        expr = self._parse_unary()
        
        while True:
            if self._match(TokenType.MUL):
                right = self._parse_unary()
                expr = BinaryOp(expr, "*", right)
            elif self._match(TokenType.DIV):
                right = self._parse_unary()
                expr = BinaryOp(expr, "/", right)
            else:
                break
        
        # 解析 or 后缀
        return self._parse_or_suffix(expr)
    
    def _parse_or_suffix(self, left: Expression) -> Expression:
        """解析 or 后缀"""
        expr = left
        
        # 首先处理 =, :, != 等操作符（如果有的话）
        while True:
            if self._match(TokenType.EQ):
                right = self._parse_factor()
                expr = BinaryOp(expr, "=", right)
            elif self._match(TokenType.COLON):
                if self._check(TokenType.IDENTIFIER):
                    expr = self._parse_meta_access(expr)
                else:
                    right = self._parse_factor()
                    expr = BinaryOp(expr, ":", right)
            elif self._match(TokenType.NE):
                right = self._parse_factor()
                expr = BinaryOp(expr, "!=", right)
            elif self._match(TokenType.GT):
                right = self._parse_factor()
                expr = BinaryOp(expr, ">", right)
            elif self._match(TokenType.GE):
                right = self._parse_factor()
                expr = BinaryOp(expr, ">=", right)
            elif self._match(TokenType.LT):
                right = self._parse_factor()
                expr = BinaryOp(expr, "<", right)
            elif self._match(TokenType.LE):
                right = self._parse_factor()
                expr = BinaryOp(expr, "<=", right)
            else:
                break
        
        # 然后处理 or
        while self._match(TokenType.OR):
            # or 右侧递归调用 _parse_or_suffix
            if self._is_binary_operator_start():
                root = Identifier("root")
                right = self._parse_or_suffix(root)
            else:
                right = self._parse_equality()
            expr = BinaryOp(expr, "or", right)
        return expr
    
    def _parse_unary(self) -> Expression:
        """解析一元操作符：not, !, +, -"""
        if self._match(TokenType.NOT, TokenType.BANG):
            operator = "not" if self._previous().type == TokenType.NOT else "!"
            # not 后面可能跟着以操作符开头的表达式
            if self._is_binary_operator_start():
                root = Identifier("root")
                operand = self._parse_binary_chain(root)
                return UnaryOp(operator, operand)
            operand = self._parse_unary()
            return UnaryOp(operator, operand)
        
        if self._match(TokenType.PLUS):
            operand = self._parse_unary()
            return UnaryOp("+", operand)
        
        if self._match(TokenType.MINUS):
            operand = self._parse_unary()
            return UnaryOp("-", operand)
        
        return self._parse_primary()
    
    def _parse_primary(self) -> Expression:
        """解析基本表达式"""
        # 字面量
        if self._match(TokenType.NUMBER):
            return NumberLiteral(self._previous().value)
        
        if self._match(TokenType.STRING):
            return StringLiteral(self._previous().value)
        
        if self._match(TokenType.REGEX):
            return RegexLiteral(self._previous().value)
        
        if self._match(TokenType.TRUE):
            return BooleanLiteral(True)
        
        if self._match(TokenType.FALSE):
            return BooleanLiteral(False)
        
        if self._match(TokenType.NULL):
            return NullLiteral()
        
        # 通配符
        if self._match(TokenType.STAR, TokenType.DOUBLE_STAR, TokenType.TRIPLE_STAR):
            token = self._previous()
            if token.type == TokenType.STAR:
                return Wildcard(1)
            elif token.type == TokenType.DOUBLE_STAR:
                return Wildcard(2)
            else:
                return Wildcard(3)
        
        # 括号表达式
        if self._match(TokenType.LPAREN):
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr
        
        # 对象字面量
        if self._match(TokenType.LBRACE):
            return self._parse_object_literal(strict=False)
        
        # 严格对象字面量 ={...}
        if self._check(TokenType.EQ) and self._peek(1).type == TokenType.LBRACE:
            self._advance()  # 消耗 =
            self._advance()  # 消耗 {
            return self._parse_object_literal(strict=True)
        
        # 数组字面量
        if self._match(TokenType.LBRACKET):
            return self._parse_array_literal(strict=False)
        
        # 严格数组字面量 =[...]
        if self._check(TokenType.EQ) and self._peek(1).type == TokenType.LBRACKET:
            self._advance()  # 消耗 =
            self._advance()  # 消耗 [
            return self._parse_array_literal(strict=True)
        
        # 表格字面量
        if self._match(TokenType.PIPE):
            return self._parse_table_literal(strict=False)
        
        # 严格表格字面量 =|...|
        if self._check(TokenType.EQ) and self._peek(1).type == TokenType.PIPE:
            self._advance()  # 消耗 =
            self._advance()  # 消耗 |
            return self._parse_table_literal(strict=True)
        
        # 标识符或属性访问
        if self._match(TokenType.IDENTIFIER):
            expr = Identifier(self._previous().value)
            # 继续解析属性链
            return self._parse_property_chain(expr)
        
        raise ParseError(f"Unexpected token: {self._peek()} at line {self._peek().line}")
    
    def _parse_property_chain(self, expr: Expression) -> Expression:
        """解析属性访问链：obj.prop1.prop2[index]"""
        while True:
            if self._match(TokenType.DOT):
                # 属性访问 .property
                if not self._match(TokenType.IDENTIFIER):
                    raise ParseError(f"Expected property name after '.' at line {self._peek().line}")
                expr = PropertyAccess(expr, self._previous().value)
            elif self._match(TokenType.LBRACKET):
                # 索引访问 [index]
                index = self._parse_expression()
                self._consume(TokenType.RBRACKET, "Expected ']' after index")
                expr = IndexAccess(expr, index)
            elif self._match(TokenType.QUESTION):
                # 存在性检查 ?
                optional = False
                if self._match(TokenType.COLON):
                    optional = True
                expr = ExistsCheck(expr, optional)
            else:
                break
        
        return expr
    
    def _parse_meta_access(self, expr: Expression) -> Expression:
        """解析元数据访问：obj::meta"""
        # 当前已经消耗了 ::，接下来应该是标识符
        if not self._match(TokenType.IDENTIFIER):
            raise ParseError(f"Expected meta name after '::' at line {self._peek().line}")
        return MetaAccess(expr, self._previous().value)
    
    def _parse_schema_check(self, expr: Expression) -> Expression:
        """解析 Schema 检查：is SchemaName"""
        if not self._match(TokenType.IDENTIFIER):
            raise ParseError(f"Expected schema name after 'is' at line {self._peek().line}")
        schema_name = self._previous().value
        
        # 检查是否有 which 子句
        base = None
        if self._match(TokenType.WHICH):
            base = self._parse_expression()
        
        return SchemaExpression(schema_name, base)
    
    def _parse_object_literal(self, strict: bool = False) -> ObjectLiteral:
        """解析对象字面量：{ prop: value, ... }"""
        properties = []
        
        # 空对象 {}
        if self._check(TokenType.RBRACE):
            self._advance()
            return ObjectLiteral(properties, strict)
        
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            # 解析属性名（支持 address.city 这样的嵌套属性名）
            if not self._match(TokenType.IDENTIFIER):
                raise ParseError(f"Expected property name at line {self._peek().line}")
            key = self._previous().value
            
            # 支持 address.city 这样的属性名
            while self._match(TokenType.DOT):
                if not self._match(TokenType.IDENTIFIER):
                    raise ParseError(f"Expected property name after '.' at line {self._peek().line}")
                key += "." + self._previous().value
            
            # 检查是否存在性检查标记 ?
            exists_check = False
            optional = False
            if self._match(TokenType.QUESTION):
                exists_check = True
                # 检查是否是 ?:（可选标记）
                if self._match(TokenType.COLON):
                    optional = True
            
            # 如果存在性检查且后面跟着 } 或注释，创建存在性检查表达式
            if exists_check and (self._check(TokenType.RBRACE) or self._peek().type in (TokenType.IDENTIFIER, TokenType.NEWLINE, TokenType.COMMA) or self._is_at_end()):
                # 存在性检查：name? 或 name?:
                # 创建一个特殊的标识符来表示存在性检查
                value = ExistsCheck(Identifier(key), optional)
                operator = ":"
                properties.append(ObjectProperty(key, value, operator, optional))
                
                # 检查是否还有更多属性
                if not self._check(TokenType.RBRACE):
                    self._match(TokenType.COMMA)
                continue
            
            # 解析操作符 : 或 =
            operator = ":"
            if self._match(TokenType.COLON):
                operator = ":"
            elif self._match(TokenType.EQ):
                operator = "="
            
            # 解析属性值（在对象字面量中，裸标识符当作字符串）
            value = self._parse_object_value()
            
            # 普通属性（非存在性检查）的 optional 始终为 False
            properties.append(ObjectProperty(key, value, operator, optional=False))
            
            # 检查是否还有更多属性
            if not self._check(TokenType.RBRACE):
                # 逗号是可选的
                self._match(TokenType.COMMA)
        
        self._consume(TokenType.RBRACE, "Expected '}' after object literal")
        return ObjectLiteral(properties, strict)
    
    def _parse_object_value(self) -> Expression:
        """
        解析对象属性值
        
        在对象字面量中，裸标识符（如 PAID、PENDING）被当作字符串值
        """
        # 如果是标识符，直接当作字符串处理
        if self._check(TokenType.IDENTIFIER):
            value = self._peek().value
            self._advance()
            return StringLiteral(value)
        
        # 其他情况使用正常表达式解析
        return self._parse_expression()
    
    def _parse_array_literal(self, strict: bool = False) -> ArrayLiteral:
        """解析数组字面量：[ value1, value2, ... ]"""
        elements = []
        
        # 空数组 []
        if self._check(TokenType.RBRACKET):
            self._advance()
            return ArrayLiteral(elements, strict)
        
        while not self._check(TokenType.RBRACKET) and not self._is_at_end():
            element = self._parse_expression()
            elements.append(element)
            
            # 检查是否还有更多元素
            if not self._check(TokenType.RBRACKET):
                # 逗号是可选的
                self._match(TokenType.COMMA)
        
        self._consume(TokenType.RBRACKET, "Expected ']' after array literal")
        return ArrayLiteral(elements, strict)
    
    def _parse_table_literal(self, strict: bool = False) -> TableExpression:
        """解析表格字面量：| header1 | header2 | ..."""
        headers = []
        rows = []
        
        # 解析表头：| header1 | header2 |
        # 当前 token 应该是 PIPE
        if not self._check(TokenType.PIPE):
            raise ParseError(f"Expected '|' at start of table, got {self._peek()}")
        
        self._advance()  # 消耗第一个 |
        
        # 解析表头单元格
        while not self._check(TokenType.PIPE) and not self._is_at_end():
            if self._match(TokenType.IDENTIFIER):
                headers.append(self._previous().value)
            elif self._match(TokenType.COMMA):
                # 跳过逗号
                continue
            else:
                break
            
            # 消耗单元格后的 |
            if self._check(TokenType.PIPE):
                self._advance()
        
        # 解析数据行
        while True:
            # 跳过换行
            if self._check(TokenType.NEWLINE):
                self._advance()
                continue
            
            # 检查是否是新数据行开始
            if not self._check(TokenType.PIPE):
                break
            
            if self._check(TokenType.EOF):
                break
            
            self._advance()  # 消耗 |
            
            row = []
            while not self._check(TokenType.PIPE) and not self._is_at_end():
                # 解析单元格值（支持复合值如 ORD-001）
                cell = self._parse_table_cell()
                if cell:
                    row.append(cell)
                
                # 消耗单元格后的 |
                if self._check(TokenType.PIPE):
                    self._advance()
            
            if row:
                rows.append(row)
        
        return TableExpression(headers, rows, strict)
    
    def _parse_table_cell(self) -> Expression:
        """
        解析表格单元格值
        
        支持简单的标识符、数字、字符串，以及复合值（如 ORD-001）
        """
        # 跳过空白和逗号
        while self._match(TokenType.COMMA):
            pass
        
        if self._check(TokenType.PIPE) or self._is_at_end():
            return None
        
        # 如果是字符串，直接返回
        if self._match(TokenType.STRING):
            return StringLiteral(self._previous().value)
        
        # 收集单元格中的所有 token（直到遇到 |）
        cell_tokens = []
        while not self._check(TokenType.PIPE) and not self._is_at_end():
            # 跳过逗号
            if self._check(TokenType.COMMA):
                self._advance()
                continue
            
            token = self._advance()
            cell_tokens.append(token)
        
        if not cell_tokens:
            return None
        
        # 将 token 组合成一个字符串值
        cell_value = ''.join(t.value for t in cell_tokens)
        return StringLiteral(cell_value)


def parse(tokens: List[Token]) -> Expression:
    """
    便捷函数：将 Token 列表解析为 AST
    
    Args:
        tokens: Token 列表
        
    Returns:
        AST 根节点
        
    Example:
        >>> from .lexer import tokenize
        >>> tokens = tokenize("1 + 2")
        >>> ast = parse(tokens)
        >>> print(ast)
        BinaryOp(NumberLiteral(1) + NumberLiteral(2))
    """
    parser = Parser(tokens)
    return parser.parse()


def parse_expression(source: str) -> Expression:
    """
    便捷函数：直接从源代码解析为 AST
    
    Args:
        source: DAL 表达式字符串
        
    Returns:
        AST 根节点
        
    Example:
        >>> ast = parse_expression("name = '张三'")
        >>> print(ast)
        BinaryOp(Identifier('name') = StringLiteral('张三'))
    """
    from .lexer import tokenize
    tokens = tokenize(source)
    return parse(tokens)
