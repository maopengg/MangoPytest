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
    ObjectLiteral, ObjectProperty, ArrayLiteral, TableExpression, RegexLiteral, ExistsCheck,
    SchemaExpression, Wildcard
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
                # 特殊处理：如果左边是 MetaAccess::type，右边是标识符，则转换为字符串字面量
                if isinstance(left, MetaAccess) and left.meta_name == "type" and isinstance(right, Identifier):
                    right = StringLiteral(right.name)
                left = BinaryOp(left, "=", right)
            elif self._match(TokenType.COLON):
                if self._check(TokenType.IDENTIFIER):
                    left = self._parse_meta_access(left)
                else:
                    right = self._parse_comparison_expr()
                    left = BinaryOp(left, ":", right)
            elif self._match(TokenType.NE):
                right = self._parse_comparison_expr()
                # 特殊处理：如果左边是 MetaAccess::type，右边是标识符，则转换为字符串字面量
                if isinstance(left, MetaAccess) and left.meta_name == "type" and isinstance(right, Identifier):
                    right = StringLiteral(right.name)
                left = BinaryOp(left, "!=", right)
            elif self._match(TokenType.CONTAINS):
                # contains 操作符
                right = self._parse_comparison_expr()
                left = BinaryOp(left, "contains", right)
            elif self._match(TokenType.MATCH):
                # match 操作符
                right = self._parse_comparison_expr()
                left = BinaryOp(left, "match", right)
            elif self._match(TokenType.STARTS):
                # starts with 操作符
                if self._match(TokenType.IDENTIFIER) and self._previous().value.lower() == 'with':
                    right = self._parse_comparison_expr()
                    left = BinaryOp(left, "starts with", right)
            elif self._match(TokenType.ENDS):
                # ends with 操作符
                if self._match(TokenType.IDENTIFIER) and self._previous().value.lower() == 'with':
                    right = self._parse_comparison_expr()
                    left = BinaryOp(left, "ends with", right)
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
            value_str = self._previous().value
            # 尝试解析为整数，如果失败则解析为浮点数
            try:
                if '.' in value_str:
                    return NumberLiteral(float(value_str))
                else:
                    return NumberLiteral(int(value_str))
            except ValueError:
                return NumberLiteral(float(value_str))
        
        # 布尔值
        if self._match(TokenType.TRUE):
            return BooleanLiteral(True)
        if self._match(TokenType.FALSE):
            return BooleanLiteral(False)
        
        # null
        if self._match(TokenType.NULL):
            return NullLiteral()
        
        # 通配符 ***, **, *
        if self._match(TokenType.TRIPLE_STAR):
            return Wildcard(3)
        if self._match(TokenType.DOUBLE_STAR):
            return Wildcard(2)
        if self._match(TokenType.STAR):
            return Wildcard(1)
        
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
        # 检查是否是元数据访问 ::property
        if self._check(TokenType.COLON_COLON):
            return True
        # 检查是否是属性访问 .property
        if self._check(TokenType.DOT):
            return True
        # 检查是否是索引访问 [index]（但不是数组字面量）
        if self._check(TokenType.LBRACKET):
            # 检查下一个 token
            next_token = self._peek(1)
            # 如果是 { * ** *** ]，则是数组字面量，不是隐式根访问
            if next_token.type in (TokenType.LBRACE, TokenType.STAR, TokenType.DOUBLE_STAR, TokenType.TRIPLE_STAR, TokenType.RBRACKET):
                return False
            # 其他情况（数字、字符串等）可能是索引访问或数组字面量
            # 临时前进到 [ 后面，使用 _is_array_literal_start 来判断
            self._advance()  # 跳过 [
            is_array = self._is_array_literal_start()
            self.pos -= 1  # 回退到 [
            if is_array:
                return False
            return True
        # 检查是否是二元操作符
        return any(self._check(t) for t in [
            TokenType.EQ, TokenType.COLON, TokenType.NE,
            TokenType.GT, TokenType.GE, TokenType.LT, TokenType.LE
        ])
    
    def _parse_implicit_root_access(self, root: Identifier) -> Expression:
        """解析隐式根访问"""
        expr = root

        # 元数据访问 ::property
        if self._match(TokenType.COLON_COLON):
            if not self._match(TokenType.IDENTIFIER):
                raise ParseError(f"Expected property name after '::'")
            expr = MetaAccess(root, self._previous().value)
            expr = self._parse_property_chain(expr)
            # 继续处理可能的二元操作符
            return self._parse_binary_after_property_chain(expr)

        # 属性访问 .property
        if self._match(TokenType.DOT):
            if not self._match(TokenType.IDENTIFIER):
                raise ParseError(f"Expected property name after '.'")
            expr = PropertyAccess(root, self._previous().value)
            expr = self._parse_property_chain(expr)
            # 继续处理可能的二元操作符
            return self._parse_binary_after_property_chain(expr)

        # 索引访问 [index] 或数组字面量 [value1, value2]
        if self._check(TokenType.LBRACKET):
            # 检查是否是数组字面量 [{
            if self._peek(1).type == TokenType.LBRACE:
                # 数组字面量，不消耗 [，让上层处理
                pass
            else:
                # 检查是索引访问还是数组字面量
                # 向前看：如果 [expr] 后面跟着 , 或 ] 和另一个值，则是数组字面量
                if self._is_array_literal_start():
                    # 数组字面量，不消耗 [，让上层处理
                    pass
                else:
                    expr = self._parse_index_access(root)
                    # 继续处理可能的二元操作符
                    return self._parse_binary_after_property_chain(expr)

        # 二元操作符 =, :, !=, >, <, >=, <=
        while True:
            if self._match(TokenType.EQ):
                # 检查是否是数组字面量 =[...
                if self._check(TokenType.LBRACKET):
                    self._advance()  # 消耗 [
                    right = self._parse_array_literal(strict=True)
                    expr = BinaryOp(expr, "=", right)
                # 检查是否是对象字面量 ={...
                elif self._check(TokenType.LBRACE):
                    self._advance()  # 消耗 {
                    right = self._parse_object_literal(strict=True)
                    expr = BinaryOp(expr, "=", right)
                # 检查是否是表格字面量 =|...
                elif self._check(TokenType.PIPE):
                    self._advance()  # 消耗 |
                    right = self._parse_table_literal(strict=True)
                    expr = BinaryOp(expr, "=", right)
                else:
                    right = self._parse_additive_expr()
                    expr = BinaryOp(expr, "=", right)
            elif self._match(TokenType.COLON):
                if self._check(TokenType.IDENTIFIER):
                    expr = self._parse_meta_access(expr)
                # 检查是否是对象字面量 :{...
                elif self._check(TokenType.LBRACE):
                    self._advance()  # 消耗 {
                    right = self._parse_object_literal(strict=False)
                    expr = BinaryOp(expr, ":", right)
                # 检查是否是表格字面量 :|...
                elif self._check(TokenType.PIPE):
                    self._advance()  # 消耗 |
                    right = self._parse_table_literal(strict=False)
                    expr = BinaryOp(expr, ":", right)
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

    def _parse_binary_after_property_chain(self, expr: Expression) -> Expression:
        """解析属性链后的二元操作符"""
        # 辅助函数：检查表达式是否是 ::type 访问
        def is_type_access(e: Expression) -> bool:
            if isinstance(e, MetaAccess) and e.meta_name == "type":
                return True
            if isinstance(e, PropertyAccess):
                return is_type_access(e.object)
            return False

        while True:
            if self._match(TokenType.EQ):
                right = self._parse_or_expr()
                # 特殊处理：如果右边是标识符，且左边不是数字比较，则转换为字符串字面量
                if isinstance(right, Identifier):
                    right = StringLiteral(right.name)
                expr = BinaryOp(expr, "=", right)
            elif self._match(TokenType.COLON):
                if self._check(TokenType.IDENTIFIER):
                    expr = self._parse_meta_access(expr)
                else:
                    right = self._parse_or_expr()
                    expr = BinaryOp(expr, ":", right)
            elif self._match(TokenType.NE):
                right = self._parse_or_expr()
                # 特殊处理：如果右边是标识符，则转换为字符串字面量
                if isinstance(right, Identifier):
                    right = StringLiteral(right.name)
                expr = BinaryOp(expr, "!=", right)
            elif self._match(TokenType.GT):
                right = self._parse_or_expr()
                expr = BinaryOp(expr, ">", right)
            elif self._match(TokenType.GE):
                right = self._parse_or_expr()
                expr = BinaryOp(expr, ">=", right)
            elif self._match(TokenType.LT):
                right = self._parse_or_expr()
                expr = BinaryOp(expr, "<", right)
            elif self._match(TokenType.LE):
                right = self._parse_or_expr()
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
            elif self._match(TokenType.IS):
                # Schema 验证：is SchemaName
                expr = self._parse_schema_check(expr)
            else:
                break
        return expr
    
    def _parse_schema_check(self, expr: Expression) -> Expression:
        """解析 Schema 检查：is SchemaName"""
        if not self._match(TokenType.IDENTIFIER):
            raise ParseError(f"Expected schema name after 'is'")
        schema_name = self._previous().value
        
        # 检查是否有 which 子句
        base = None
        if self._match(TokenType.WHICH):
            base = self._parse_or_expr()
        
        return SchemaExpression(schema_name, base)
    
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
            
            # 存在性检查标记 ? 或 ?:
            exists_check = False
            optional = False
            if self._match(TokenType.QUESTION):
                exists_check = True
                # 检查是否是 ?:（可选标记）
                prev_token = self._previous()
                if prev_token.value == '?:':
                    optional = True
                    # ?: 已经包含了 :，所以不需要再匹配 COLON
                    # 检查后面是否有值
                    if self._check(TokenType.RBRACE) or self._check(TokenType.COMMA):
                        # 只有 ?: 没有值，创建 ExistsCheck
                        value = ExistsCheck(Identifier(key), optional=True)
                        properties.append(ObjectProperty(key, value, ":", optional=True))
                        if not self._check(TokenType.RBRACE):
                            self._match(TokenType.COMMA)
                        continue
                    else:
                        # 有值，解析属性值
                        value = self._parse_object_value()
                        properties.append(ObjectProperty(key, value, ":", optional=True))
                        if not self._check(TokenType.RBRACE):
                            self._match(TokenType.COMMA)
                        continue
            
            # 如果是存在性检查（后面没有 : 或 = 操作符）
            if exists_check and not self._check(TokenType.COLON) and not self._check(TokenType.EQ):
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
            properties.append(ObjectProperty(key, value, operator, optional=optional))
            
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
        
        # 处理 is Schema 语法
        if self._check(TokenType.IS):
            # 这里不应该直接遇到 IS，它应该在 _parse_property_chain 中处理
            # 但如果遇到了，尝试解析 Schema 表达式
            self._advance()  # 消耗 is
            if self._match(TokenType.IDENTIFIER):
                schema_name = self._previous().value
                return SchemaExpression(schema_name, None)
            else:
                raise ParseError("Expected schema name after 'is'")
        
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
        """解析表格字面量
        
        格式：
            | header1 | header2 |
            | value1  | value2  |
            
        支持选项：
            | header1 | header2 | sort by header1 desc
            | value1  | value2  |
        
        注意：调用此方法时，第一个 | 已经被消耗
        """
        headers = []
        rows = []
        sort_by = None
        sort_desc = False
        skip = 0
        row_header = False
        transpose = False
        
        # 解析表头行：| orderId | status |
        # 当前 token 应该是第一个表头（如 orderId）或 |
        while not self._is_at_end():
            # 跳过开头的 |
            if self._check(TokenType.PIPE):
                self._advance()
                continue
            
            # 检查是否是选项（sort by, skip, row header, transpose）
            if self._check(TokenType.IDENTIFIER):
                option_name = self._peek().value.lower()
                option_parsed = False
                
                # sort by column [asc|desc]
                if option_name == 'sort':
                    self._advance()  # 消耗 sort
                    if self._match(TokenType.IDENTIFIER) and self._previous().value.lower() == 'by':
                        if self._match(TokenType.IDENTIFIER):
                            sort_by = self._previous().value
                            # 检查是否有 asc/desc
                            if self._check(TokenType.IDENTIFIER):
                                order = self._peek().value.lower()
                                if order in ('asc', 'desc'):
                                    self._advance()
                                    sort_desc = (order == 'desc')
                            option_parsed = True
                
                # skip N
                elif option_name == 'skip':
                    self._advance()  # 消耗 skip
                    if self._match(TokenType.NUMBER):
                        skip = int(self._previous().value)
                        option_parsed = True
                
                # row header
                elif option_name == 'row':
                    self._advance()  # 消耗 row
                    if self._match(TokenType.IDENTIFIER) and self._previous().value.lower() == 'header':
                        row_header = True
                        option_parsed = True
                
                # transpose
                elif option_name == 'transpose':
                    self._advance()  # 消耗 transpose
                    transpose = True
                    option_parsed = True
                
                # 如果解析了选项，继续检查是否还有其他选项
                if option_parsed:
                    # 跳过一个 |（表头结束符）
                    if self._check(TokenType.PIPE):
                        self._advance()
                    # 如果接下来是标识符，检查是否是另一个选项
                    if self._check(TokenType.IDENTIFIER):
                        # 检查是否是已知的选项关键字
                        next_name = self._peek().value.lower()
                        if next_name in ('sort', 'skip', 'row', 'transpose'):
                            continue
                        # 否则是数据行开始，结束表头解析
                        # 回退到上一个 |，让数据行解析循环处理
                        if self.pos > 0 and self.tokens[self.pos - 1].type == TokenType.PIPE:
                            self.pos -= 1
                        break
                    # 如果遇到 |（数据行开始）或者是行尾，结束表头解析
                    if self._check(TokenType.PIPE) or self._is_at_end():
                        break
                    # 否则也结束表头解析（开始数据行）
                    break
            
            # 收集表头名称（可能是多个 token）
            header_parts = []
            while not self._is_at_end() and not self._check(TokenType.PIPE):
                if self._match(TokenType.IDENTIFIER):
                    header_parts.append(self._previous().value)
                elif self._match(TokenType.STRING):
                    header_parts.append(self._previous().value)
                elif self._match(TokenType.NUMBER):
                    header_parts.append(self._previous().value)
                else:
                    self._advance()
            
            if header_parts:
                headers.append(''.join(str(p) for p in header_parts))
            
            # 如果接下来是 |，继续解析下一个表头
            if self._check(TokenType.PIPE):
                self._advance()  # 消耗 |
                # 如果接下来还是 | 或者是数据行开始（换行后的|），表头结束
                if self._check(TokenType.PIPE):
                    break
                # 否则继续解析下一个表头
                continue
            else:
                break
        
        # 解析数据行
        while not self._is_at_end():
            # 数据行必须以 | 开头
            if not self._check(TokenType.PIPE):
                break
            
            self._advance()  # 消耗行首的 |
            
            row = []
            
            # 解析每个单元格
            while not self._is_at_end():
                # 跳过 |
                if self._check(TokenType.PIPE):
                    self._advance()
                    # 如果接下来还是 | 或者是行尾，当前单元格结束
                    if self._check(TokenType.PIPE) or self._check(TokenType.EOF):
                        break
                    continue
                
                # 收集单元格值
                cell_parts = []
                cell_types = []
                while not self._is_at_end() and not self._check(TokenType.PIPE):
                    if self._match(TokenType.IDENTIFIER):
                        cell_parts.append(self._previous().value)
                        cell_types.append('id')
                    elif self._match(TokenType.STRING):
                        cell_parts.append(self._previous().value)
                        cell_types.append('str')
                    elif self._match(TokenType.NUMBER):
                        cell_parts.append(self._previous().value)
                        cell_types.append('num')
                    elif self._match(TokenType.MINUS):
                        cell_parts.append('-')
                        cell_types.append('minus')
                    elif self._match(TokenType.DOT):
                        cell_parts.append('.')
                        cell_types.append('dot')
                    else:
                        self._advance()
                
                if cell_parts:
                    # 如果只有一个数字，创建 NumberLiteral
                    if len(cell_parts) == 1 and cell_types[0] == 'num':
                        value_str = cell_parts[0]
                        try:
                            if '.' in value_str:
                                row.append(NumberLiteral(float(value_str)))
                            else:
                                row.append(NumberLiteral(int(value_str)))
                        except ValueError:
                            row.append(StringLiteral(value_str))
                    # 如果是数字和小数点的组合（如 100.00）
                    elif len(cell_parts) == 3 and cell_types == ['num', 'dot', 'num']:
                        merged = ''.join(str(p) for p in cell_parts)
                        try:
                            row.append(NumberLiteral(float(merged)))
                        except ValueError:
                            row.append(StringLiteral(merged))
                    else:
                        merged = ''.join(str(p) for p in cell_parts)
                        row.append(StringLiteral(merged))
            
            if row:
                rows.append(row)
        
        return TableExpression(headers, rows, strict, sort_by, sort_desc, skip, row_header, transpose)
    
    def _parse_table_cell(self) -> Expression:
        """解析表格单元格"""
        # 跳过空白和逗号
        while self._match(TokenType.COMMA):
            pass
        
        if self._check(TokenType.PIPE) or self._is_at_end():
            return None
        
        # 字符串
        if self._match(TokenType.STRING):
            return StringLiteral(self._previous().value)
        
        # 数字
        if self._match(TokenType.NUMBER):
            value_str = self._previous().value
            try:
                if '.' in value_str:
                    return NumberLiteral(float(value_str))
                else:
                    return NumberLiteral(int(value_str))
            except ValueError:
                return StringLiteral(value_str)
        
        # 标识符（作为字符串）
        if self._match(TokenType.IDENTIFIER):
            return StringLiteral(self._previous().value)
        
        # 其他 token，收集为字符串
        tokens = []
        while not self._check(TokenType.PIPE) and not self._is_at_end():
            if self._check(TokenType.COMMA):
                self._advance()
                continue
            token = self._advance()
            tokens.append(token)
        
        if not tokens:
            return None
        
        value = ''.join(t.value for t in tokens).strip()
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

    def _is_array_literal_start(self) -> bool:
        """检查是否是数组字面量的开始"""
        # 假设当前位置是 [ 后面，所以初始 depth 为 1
        # 向前看，如果找到 , 或者多个元素，则是数组字面量
        pos = self.pos
        depth = 1  # 已经在 [ 里面
        element_count = 0

        while pos < len(self.tokens):
            token = self.tokens[pos]

            if token.type == TokenType.LBRACKET:
                depth += 1
            elif token.type == TokenType.RBRACKET:
                depth -= 1
                if depth == 0:
                    # 找到了匹配的 ]
                    # 如果只有一个元素，可能是索引访问；多个元素则是数组字面量
                    return element_count > 1
            elif token.type == TokenType.COMMA and depth == 1:
                # 在顶层找到逗号，说明是数组字面量
                return True
            elif token.type in (TokenType.NUMBER, TokenType.STRING, TokenType.IDENTIFIER,
                                TokenType.TRUE, TokenType.FALSE, TokenType.NULL,
                                TokenType.LBRACE, TokenType.STAR, TokenType.DOUBLE_STAR, TokenType.TRIPLE_STAR) and depth == 1:
                # 在顶层找到元素
                element_count += 1
            elif token.type == TokenType.EOF:
                return False

            pos += 1

        return False

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
