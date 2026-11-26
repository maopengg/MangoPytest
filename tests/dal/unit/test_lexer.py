"""
词法分析器单元测试

对应 Java: DAL-java/src/test/resources/features/dal/const/*.feature
"""
import pytest
from core.dal.core.lexer import Lexer, TokenType, tokenize


class TestNumberToken:
    """数字 Token 测试"""
    
    def test_integer(self):
        tokens = tokenize("123")
        assert len(tokens) == 2  # NUMBER + EOF
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == "123"
    
    def test_float(self):
        tokens = tokenize("1.5")
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == "1.5"
    
    def test_negative_number(self):
        tokens = tokenize("-10")
        assert tokens[0].type == TokenType.MINUS
        assert tokens[1].type == TokenType.NUMBER
        assert tokens[1].value == "10"


class TestStringToken:
    """字符串 Token 测试"""
    
    def test_double_quoted_string(self):
        tokens = tokenize('"hello"')
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello"
    
    def test_single_quoted_string(self):
        tokens = tokenize("'hello'")
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello"
    
    def test_string_with_spaces(self):
        tokens = tokenize('"hello world"')
        assert tokens[0].value == "hello world"
    
    def test_string_with_escape(self):
        tokens = tokenize('"hello\\nworld"')
        assert tokens[0].value == "hello\nworld"


class TestOperatorToken:
    """操作符 Token 测试"""
    
    def test_equal(self):
        tokens = tokenize("=")
        assert tokens[0].type == TokenType.EQ
    
    def test_colon(self):
        tokens = tokenize(":")
        assert tokens[0].type == TokenType.COLON
    
    def test_not_equal(self):
        tokens = tokenize("!=")
        assert tokens[0].type == TokenType.NE
    
    def test_greater_than(self):
        tokens = tokenize(">")
        assert tokens[0].type == TokenType.GT
    
    def test_less_than(self):
        tokens = tokenize("<")
        assert tokens[0].type == TokenType.LT
    
    def test_greater_equal(self):
        tokens = tokenize(">=")
        assert tokens[0].type == TokenType.GE
    
    def test_less_equal(self):
        tokens = tokenize("<=")
        assert tokens[0].type == TokenType.LE


class TestLogicalToken:
    """逻辑操作符 Token 测试"""
    
    def test_and(self):
        tokens = tokenize("and")
        assert tokens[0].type == TokenType.AND
    
    def test_or(self):
        tokens = tokenize("or")
        assert tokens[0].type == TokenType.OR
    
    def test_not(self):
        tokens = tokenize("not")
        assert tokens[0].type == TokenType.NOT
    
    def test_and_symbol(self):
        tokens = tokenize("&&")
        assert tokens[0].type == TokenType.AND
    
    def test_or_symbol(self):
        tokens = tokenize("||")
        assert tokens[0].type == TokenType.OR


class TestKeywordToken:
    """关键字 Token 测试"""
    
    def test_null(self):
        tokens = tokenize("null")
        assert tokens[0].type == TokenType.NULL
    
    def test_true(self):
        tokens = tokenize("true")
        assert tokens[0].type == TokenType.TRUE
    
    def test_false(self):
        tokens = tokenize("false")
        assert tokens[0].type == TokenType.FALSE
    
    def test_is(self):
        tokens = tokenize("is")
        assert tokens[0].type == TokenType.IS
    
    def test_which(self):
        tokens = tokenize("which")
        assert tokens[0].type == TokenType.WHICH


class TestSymbolToken:
    """符号 Token 测试"""
    
    def test_brace(self):
        tokens = tokenize("{ }")
        assert tokens[0].type == TokenType.LBRACE
        assert tokens[1].type == TokenType.RBRACE
    
    def test_bracket(self):
        tokens = tokenize("[ ]")
        assert tokens[0].type == TokenType.LBRACKET
        assert tokens[1].type == TokenType.RBRACKET
    
    def test_paren(self):
        tokens = tokenize("( )")
        assert tokens[0].type == TokenType.LPAREN
        assert tokens[1].type == TokenType.RPAREN
    
    def test_dot(self):
        tokens = tokenize(".")
        assert tokens[0].type == TokenType.DOT
    
    def test_comma(self):
        tokens = tokenize(",")
        assert tokens[0].type == TokenType.COMMA
    
    def test_question(self):
        tokens = tokenize("?")
        assert tokens[0].type == TokenType.QUESTION


class TestIdentifierToken:
    """标识符 Token 测试"""
    
    def test_simple_identifier(self):
        tokens = tokenize("name")
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "name"
    
    def test_identifier_with_underscore(self):
        tokens = tokenize("_private")
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "_private"
    
    def test_identifier_with_number(self):
        tokens = tokenize("name123")
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "name123"


class TestComplexExpression:
    """复杂表达式测试"""
    
    def test_simple_equality(self):
        tokens = tokenize("name = '张三'")
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[1].type == TokenType.EQ
        assert tokens[2].type == TokenType.STRING
    
    def test_comparison_with_and(self):
        tokens = tokenize("age > 18 and age < 60")
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[1].type == TokenType.GT
        assert tokens[2].type == TokenType.NUMBER
        assert tokens[3].type == TokenType.AND
        assert tokens[4].type == TokenType.IDENTIFIER
    
    def test_object_literal(self):
        tokens = tokenize("{ name: '张三', age: 25 }")
        assert tokens[0].type == TokenType.LBRACE
        assert tokens[1].type == TokenType.IDENTIFIER
        assert tokens[2].type == TokenType.COLON
        assert tokens[3].type == TokenType.STRING


class TestComment:
    """注释测试"""
    
    def test_single_line_comment(self):
        tokens = tokenize("// this is a comment\nname")
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "name"


class TestRegex:
    """正则表达式测试"""
    
    def test_simple_regex(self):
        tokens = tokenize("/hello/")
        assert tokens[0].type == TokenType.REGEX
        assert tokens[0].value == "hello"
    
    def test_regex_with_pattern(self):
        tokens = tokenize("/^[a-z]+$/")
        assert tokens[0].type == TokenType.REGEX
        assert tokens[0].value == "^[a-z]+$"


class TestWildcard:
    """通配符测试"""
    
    def test_star(self):
        tokens = tokenize("*")
        assert tokens[0].type == TokenType.STAR
    
    def test_double_star(self):
        tokens = tokenize("**")
        assert tokens[0].type == TokenType.DOUBLE_STAR
    
    def test_triple_star(self):
        tokens = tokenize("***")
        assert tokens[0].type == TokenType.TRIPLE_STAR


class TestError:
    """错误处理测试"""
    
    def test_unexpected_character(self):
        with pytest.raises(SyntaxError):
            tokenize("@")
    
    def test_unterminated_string(self):
        with pytest.raises(SyntaxError):
            tokenize('"hello')
