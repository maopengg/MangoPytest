"""
DAL 表达式解析器 - 简化版本

支持：
- 隐式根对象访问（以操作符开头）
- 逻辑操作符：and, or, not
- 比较操作符：=, :, !=, >, <, >=, <=
- 属性访问：.property, [index]
- 字面量：对象、数组、表格、字符串、数字、布尔值
"""

from typing import List, Optional
from .lexer import Token, TokenType
from .ast_nodes import (
    Expression, Identifier, StringLiteral, NumberLiteral, BooleanLiteral, NullLiteral,
    BinaryOp, UnaryOp, PropertyAccess, IndexAccess, MetaAccess,
    ObjectLiteral, ObjectProperty, ArrayLiteral, TableExpression, RegexLiteral, ExistsCheck
)


class ParseError(Exception):
    """解析错误"""
    pass


class Parser:
    """递归下降解析器"""
    
    def __init__(self, tokens: List[Token]):
        # 过滤掉 NEWLINE token，但保留 EOF
        self.tokens = [t for t in tokens if t.type != TokenType.NEWLINE]
        self.pos = 0
    
    def parse(self) -> Expression:
        """解析表达式"""
        expr = self._parse_or_expr()
        if not self._is_at_end():
            raise ParseError(f"Unexpected token: {self._peek()}")
        return expr
    
    # ========== 表达式层级 ==========
    
    def _parse_or_expr(self) -> Expression:
        """解析 or 表达式"""
        left = self._parse_and_expr()
        
        while self._match(TokenType.OR):
            right = self._parse_and_expr()
            left = BinaryOp(left, "or", right)
        
        return left
    
    def _parse_and_expr(self) -> Expression:
        """解析 and 表达式"""
        left = self._parse_equality_expr()
        
        while self._match(TokenType.AND) or self._match(TokenType.COMMA):
            right = self._parse_equality_expr()
            left = BinaryOp(left, "and", right)
        
        return left
    
    def _parse_equality_expr(self) -> Expression:
        """解析相等性表达式"""
        left = self._parse_comparison_expr()
        
        while True:
            if self._match(TokenType.EQ):
                right = self._parse_comparison_expr()
                left = BinaryOp(left, "=", right)
            elif self._match(TokenType.COLON):
                if self._check(TokenType.IDENTIFIER):
                    left = self._parse_meta_access(left)
                else:
                    right = self._parse_comparison_expr()
                    left = BinaryOp(left, ":", right)
            elif self._match(TokenType.NE):
                right = self._parse_comparison_expr()
                left = BinaryOp(left, "!=", right)
            else:
                break
        
        return left
    
    def _parse_comparison_expr(self) -> Expression:
        """解析比较表达式"""
        left = self._parse_additive_expr()
        
        while True:
            if self._match(TokenType.GT):
                right = self._parse_additive_expr()
                left = BinaryOp(left, ">", right)
            elif self._match(TokenType.GE):
                right = self._parse_additive_expr()
                left = BinaryOp(left, ">=", right)
            elif self._match(TokenType.LT):
                right = self._parse_additive_expr()
                left = BinaryOp(left, "<", right)
            elif self._match(TokenType.LE):
                right = self._parse_additive_expr()
                left = BinaryOp(left, "<=", right)
            else:
                break
        
        return left
    
    def _parse_additive_expr(self) -> Expression:
        """解析加减表达式"""
        left = self._parse_multiplicative_expr()
        
        while True:
            if self._match(TokenType.PLUS):
                right = self._parse_multiplicative_expr()
                left = BinaryOp(left, "+", right)
            elif self._match(TokenType.MINUS):
                right = self._parse_multiplicative_expr()
                left = BinaryOp(left, "-", right)
            else:
                break
        
        return left
    
    def _parse_multiplicative_expr(self) -> Expression:
        """解析乘除表达式"""
        left = self._parse_unary_expr()
        
        while True:
            if self._match(TokenType.MUL):
                right = self._parse_unary_expr()
                left = BinaryOp(left, "*", right)
            elif self._match(TokenType.DIV):
                right = self._parse_unary_expr()
                left = BinaryOp(left, "/", right)
            else:
                break
        
        return left
    
    def _parse_unary_expr(self) -> Expression:
        """解析一元表达式"""
        if self._match(TokenType.NOT) or self._match(TokenType.BANG):
            operand = self._parse_unary_expr()
            return UnaryOp("not", operand)
        
        if self._match(TokenType.PLUS):
            operand = self._parse_unary_expr()
            return UnaryOp("+", operand)
        
        if self._match(TokenType.MINUS):
            operand = self._parse_unary_expr()
            return UnaryOp("-", operand)
        
        return self._parse_primary_expr()
    
    def _parse_primary_expr(self) -> Expression:
        """解析基本表达式"""
        # 隐式根对象访问（以操作符开头）
        if self._is_implicit_root_start():
            root = Identifier("root")
            return self._parse_implicit_root_access(root)
        
        # 标识符
        if self._match(TokenType.IDENTIFIER):
            name = self._previous().value
            expr = Identifier(name)
            # 继续解析属性链
            return self._parse_property_chain(expr)
        
        # 字符串
        if self._match(TokenType.STRING):
            return StringLiteral(self._previous().value)
        
        # 数字
        if self._match(TokenType.NUMBER):
            value = self._previous().value
            if isinstance(value, int):
                return NumberLiteral(value)
            return NumberLiteral(float(value))
        
        # 布尔值
        if self._match(TokenType.TRUE):
            return BooleanLiteral(True)
        if self._match(TokenType.FALSE):
            return BooleanLiteral(False)
        
        # null
        if self._match(TokenType.NULL):
            return NullLiteral()
        
        # 正则表达式
        if self._match(TokenType.REGEX):
            return RegexLiteral(self._previous().value)
        
        # 数组字面量
        if self._match(TokenType.LBRACKET):
            return self._parse_array_literal(strict=False)
        
        # 对象字面量
        if self._match(TokenType.LBRACE):
            return self._parse_object_literal(strict=False)
        
        # 表格字面量
        if self._match(TokenType.PIPE):
            return self._parse_table_literal(strict=False)
        
        # 括号分组
        if self._match(TokenType.LPAREN):
            expr = self._parse_or_expr()
            self._consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr
        
        raise ParseError(f"Unexpected token: {self._peek()}")
    
    # ========== 隐式根访问 ==========
    
    def _is_implicit_root_start(self) -> bool:
        """检查是否是隐式根访问的开始"""
        return any(self._check(t) for t in [
            TokenType.EQ, TokenType.COLON, TokenType.NE,
            TokenType.GT, TokenType.GE, TokenType.LT, TokenType.LE,
            TokenType.DOT, TokenType.LBRACKET
        ])
    
    def _parse_implicit_root_access(self, root: Identifier) -> Expression:
        """解析隐式根访问"""
        # 属性访问 .property
        if self._match(TokenType.DOT):
            if not self._match(TokenType.IDENTIFIER):
                raise ParseError(f"Expected property name after '.'")
            expr = PropertyAccess(root, self._previous().value)
            return self._parse_property_chain(expr)
        
        # 索引访问 [index]
        if self._check(TokenType.LBRACKET):
            return self._parse_index_access(root)
        
        # 二元操作符 =, :, !=, >, <, >=, <=
        expr = root
        
        while True:
            if self._match(TokenType.EQ):
                right = self._parse_additive_expr()
                expr = BinaryOp(expr, "=", right)
            elif self._match(TokenType.COLON):
                if self._check(TokenType.IDENTIFIER):
                    expr = self._parse_meta_access(expr)
                else:
                    right = self._parse_additive_expr()
                    expr = BinaryOp(expr, ":", right)
            elif self._match(TokenType.NE):
                right = self._parse_additive_expr()
                expr = BinaryOp(expr, "!=", right)
            elif self._match(TokenType.GT):
                right = self._parse_additive_expr()
                expr = BinaryOp(expr, ">", right)
            elif self._match(TokenType.GE):
                right = self._parse_additive_expr()
                expr = BinaryOp(expr, ">=", right)
            elif self._match(TokenType.LT):
                right = self._parse_additive_expr()
                expr = BinaryOp(expr, "<", right)
            elif self._match(TokenType.LE):
                right = self._parse_additive_expr()
                expr = BinaryOp(expr, "<=", right)
            else:
                break
        
        return expr
    
    # ========== 属性链 ==========
    
    def _parse_property_chain(self, expr: Expression) -> Expression:
        """解析属性访问链"""
        while True:
            if self._match(TokenType.DOT):
                if not self._match(TokenType.IDENTIFIER):
                    raise ParseError(f"Expected property name after '.'")
                expr = PropertyAccess(expr, self._previous().value)
            elif self._match(TokenType.LBRACKET):
                index = self._parse_or_expr()
                self._consume(TokenType.RBRACKET, "Expected ']' after index")
                expr = IndexAccess(expr, index)
            elif self._match(TokenType.COLON) and self._check(TokenType.IDENTIFIER):
                # 元数据访问 ::size
                expr = self._parse_meta_access(expr)
            else:
                break
        return expr
    
    def _parse_index_access(self, obj: Expression) -> Expression:
        """解析索引访问"""
        self._advance()  # 消耗 [
        index = self._parse_or_expr()
        self._consume(TokenType.RBRACKET, "Expected ']' after index")
        expr = IndexAccess(obj, index)
        return self._parse_property_chain(expr)
    
    def _parse_meta_access(self, obj: Expression) -> Expression:
        """解析元数据访问 ::property"""
        if not self._match(TokenType.IDENTIFIER):
            raise ParseError(f"Expected metadata property name after '::'")
        return MetaAccess(obj, self._previous().value)
    
    # ========== 字面量 ==========
    
    def _parse_object_literal(self, strict: bool = False) -> ObjectLiteral:
        """解析对象字面量"""
        properties = []
        
        if self._check(TokenType.RBRACE):
            self._advance()
            return ObjectLiteral(properties, strict)
        
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            # 属性名
            if not self._match(TokenType.IDENTIFIER):
                raise ParseError(f"Expected property name")
            key = self._previous().value
            
            # 支持 address.city 这样的属性名
            while self._match(TokenType.DOT):
                if not self._match(TokenType.IDENTIFIER):
                    raise ParseError(f"Expected property name after '.'")
                key += "." + self._previous().value
            
            # 存在性检查标记 ?
            exists_check = False
            optional = False
            if self._match(TokenType.QUESTION):
                exists_check = True
                if self._match(TokenType.COLON):
                    optional = True
            
            # 如果是存在性检查且后面跟着 } 或逗号
            if exists_check and (self._check(TokenType.RBRACE) or self._check(TokenType.COMMA) or self._is_at_end()):
                value = ExistsCheck(Identifier(key), optional)
                operator = ":"
                properties.append(ObjectProperty(key, value, operator, optional))
                if not self._check(TokenType.RBRACE):
                    self._match(TokenType.COMMA)
                continue
            
            # 操作符 : 或 =
            operator = ":"
            if self._match(TokenType.COLON):
                operator = ":"
            elif self._match(TokenType.EQ):
                operator = "="
            
            # 属性值
            value = self._parse_object_value()
            properties.append(ObjectProperty(key, value, operator, optional=False))
            
            if not self._check(TokenType.RBRACE):
                self._match(TokenType.COMMA)
        
        self._consume(TokenType.RBRACE, "Expected '}' after object literal")
        return ObjectLiteral(properties, strict)
    
    def _parse_object_value(self) -> Expression:
        """解析对象属性值（支持裸标识符作为字符串）"""
        # 跳过逗号
        while self._match(TokenType.COMMA):
            pass
        
        if self._check(TokenType.RBRACE) or self._is_at_end():
            return None
        
        # 裸标识符作为字符串
        if self._check(TokenType.IDENTIFIER):
            value = self._peek().value
            self._advance()
            return StringLiteral(value)
        
        return self._parse_or_expr()
    
    def _parse_array_literal(self, strict: bool = False) -> ArrayLiteral:
        """解析数组字面量"""
        elements = []
        
        if self._check(TokenType.RBRACKET):
            self._advance()
            return ArrayLiteral(elements, strict)
        
        while not self._check(TokenType.RBRACKET) and not self._is_at_end():
            element = self._parse_or_expr()
            elements.append(element)
            
            if not self._check(TokenType.RBRACKET):
                self._match(TokenType.COMMA)
        
        self._consume(TokenType.RBRACKET, "Expected ']' after array literal")
        return ArrayLiteral(elements, strict)
    
    def _parse_table_literal(self, strict: bool = False) -> TableExpression:
        """解析表格字面量"""
        headers = []
        rows = []
        
        # 表头
        while not self._check(TokenType.PIPE) and not self._is_at_end():
            if self._match(TokenType.IDENTIFIER):
                headers.append(self._previous().value)
            elif self._match(TokenType.COMMA):
                continue
            else:
                break
        
        if self._check(TokenType.PIPE):
            self._advance()
        
        # 数据行
        while self._check(TokenType.PIPE) or self._match(TokenType.NEWLINE):
            if self._check(TokenType.EOF) or self._is_at_end():
                break
            
            if not self._check(TokenType.PIPE):
                continue
            
            self._advance()  # 消耗 |
            
            row = []
            while not self._check(TokenType.PIPE) and not self._is_at_end():
                cell = self._parse_table_cell()
                if cell:
                    row.append(cell)
                if self._check(TokenType.PIPE):
                    self._advance()
            
            if row:
                rows.append(row)
        
        return TableExpression(headers, rows, strict)
    
    def _parse_table_cell(self) -> Expression:
        """解析表格单元格"""
        while self._match(TokenType.COMMA):
            pass
        
        if self._check(TokenType.PIPE) or self._is_at_end():
            return None
        
        if self._match(TokenType.STRING):
            return StringLiteral(self._previous().value)
        
        # 收集所有 token 直到 |
        tokens = []
        while not self._check(TokenType.PIPE) and not self._is_at_end():
            if self._check(TokenType.COMMA):
                self._advance()
                continue
            token = self._advance()
            tokens.append(token)
        
        if not tokens:
            return None
        
        value = ''.join(t.value for t in tokens)
        return StringLiteral(value)
    
    # ========== 辅助方法 ==========
    
    def _peek(self, offset: int = 0) -> Token:
        """查看当前 token（不消耗）"""
        pos = self.pos + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]  # EOF
        return self.tokens[pos]
    
    def _previous(self) -> Token:
        """获取上一个 token"""
        return self.tokens[self.pos - 1]
    
    def _advance(self) -> Token:
        """消耗当前 token 并返回"""
        if not self._is_at_end():
            self.pos += 1
        return self.tokens[self.pos - 1]
    
    def _is_at_end(self) -> bool:
        """检查是否到达结尾"""
        return self._peek().type == TokenType.EOF
    
    def _check(self, token_type: TokenType) -> bool:
        """检查当前 token 类型"""
        if self._is_at_end():
            return False
        return self._peek().type == token_type
    
    def _match(self, *types: TokenType) -> bool:
        """尝试匹配 token 类型"""
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True
        return False
    
    def _consume(self, token_type: TokenType, message: str) -> Token:
        """消耗指定类型的 token，否则报错"""
        if self._check(token_type):
            return self._advance()
        raise ParseError(f"{message}, got {self._peek()}")


def parse(tokens: List[Token]) -> Expression:
    """解析 token 列表为 AST"""
    parser = Parser(tokens)
    return parser.parse()


def parse_expression(source: str) -> Expression:
    """解析表达式字符串为 AST"""
    from .lexer import tokenize
    tokens = tokenize(source)
    return parse(tokens)
