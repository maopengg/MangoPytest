"""
词法分析器 - 将 DAL 表达式字符串转换为 Token 序列

对应 Java: DAL-java 中的 TokenScanner 和相关类
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Iterator


class TokenType(Enum):
    """Token 类型枚举"""
    # 字面量
    NUMBER = auto()           # 123, 1.5, -10
    STRING = auto()           # 'hello', "world"
    IDENTIFIER = auto()       # name, orderId, _private
    REGEX = auto()            # /pattern/
    
    # 比较操作符
    EQ = auto()               # = (严格相等)
    COLON = auto()            # : (宽容匹配)
    NE = auto()               # !=
    GT = auto()               # >
    LT = auto()               # <
    GE = auto()               # >=
    LE = auto()               # <=
    
    # 逻辑操作符
    AND = auto()              # and, &&
    OR = auto()               # or, ||
    NOT = auto()              # not, !
    
    # 算术操作符
    PLUS = auto()             # +
    MINUS = auto()            # -
    MUL = auto()              # *
    DIV = auto()              # /
    
    # 关键字
    IS = auto()               # is
    WHICH = auto()            # which
    IN = auto()               # in
    NULL = auto()             # null
    TRUE = auto()             # true
    FALSE = auto()            # false
    
    # 字符串匹配操作符
    MATCH = auto()            # ~ (正则匹配)
    CONTAINS = auto()         # contains
    STARTS = auto()           # starts
    ENDS = auto()             # ends
    
    # 符号
    LBRACE = auto()           # {
    RBRACE = auto()           # }
    LBRACKET = auto()         # [
    RBRACKET = auto()         # ]
    LPAREN = auto()           # (
    RPAREN = auto()           # )
    PIPE = auto()             # | (表格用)
    DOT = auto()              # .
    COMMA = auto()            # ,
    QUESTION = auto()         # ? (字段存在)
    STAR = auto()             # * (任意值)
    DOUBLE_STAR = auto()      # ** (任意对象)
    TRIPLE_STAR = auto()      # *** (任意列表)
    COLON_COLON = auto()      # :: (元数据访问)
    BANG = auto()             # ! (非/不存在)
    
    # 特殊
    NEWLINE = auto()          # 换行
    EOF = auto()              # 结束


@dataclass
class Token:
    """Token 数据类"""
    type: TokenType
    value: str
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', {self.line}:{self.column})"


class Lexer:
    """
    DAL 词法分析器
    
    将 DAL 表达式字符串转换为 Token 序列
    
    Example:
        >>> lexer = Lexer("name = '张三'")
        >>> tokens = lexer.tokenize()
        >>> for token in tokens:
        ...     print(token)
        Token(IDENTIFIER, 'name', 1:1)
        Token(EQ, '=', 1:6)
        Token(STRING, '张三', 1:8)
        Token(EOF, '', 1:12)
    """
    
    # 关键字映射
    KEYWORDS = {
        'and': TokenType.AND,
        'or': TokenType.OR,
        'not': TokenType.NOT,
        'is': TokenType.IS,
        'which': TokenType.WHICH,
        'in': TokenType.IN,
        'null': TokenType.NULL,
        'true': TokenType.TRUE,
        'false': TokenType.FALSE,
        'contains': TokenType.CONTAINS,
        'starts': TokenType.STARTS,
        'ends': TokenType.ENDS,
    }
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def tokenize(self) -> List[Token]:
        """将源代码转换为 Token 列表"""
        while not self._is_at_end():
            self._scan_token()
        
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens
    
    def _is_at_end(self) -> bool:
        """检查是否到达源代码末尾"""
        return self.pos >= len(self.source)
    
    def _peek(self, offset: int = 0) -> str:
        """查看当前位置或偏移位置的字符"""
        pos = self.pos + offset
        if pos >= len(self.source):
            return '\0'
        return self.source[pos]
    
    def _advance(self) -> str:
        """前进一个字符并返回"""
        char = self._peek()
        self.pos += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char
    
    def _match(self, expected: str) -> bool:
        """匹配并消耗指定字符"""
        if self._is_at_end():
            return False
        if self.source[self.pos] != expected:
            return False
        self._advance()
        return True
    
    def _add_token(self, token_type: TokenType, value: str = None):
        """添加 Token"""
        if value is None:
            # 根据位置计算 value
            if self.pos > 0:
                value = self.source[self.pos - len(str(token_type)):self.pos]
            else:
                value = ""
        self.tokens.append(Token(token_type, value, self.line, self.column - len(value)))
    
    def _scan_token(self):
        """扫描单个 Token"""
        char = self._advance()
        
        # 跳过空白字符（除了换行）
        if char in ' \t\r':
            return
        
        # 换行
        if char == '\n':
            self._add_token(TokenType.NEWLINE, char)
            return
        
        # 单字符符号
        single_char_tokens = {
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '.': TokenType.DOT,
            ',': TokenType.COMMA,
        }
        
        if char in single_char_tokens:
            self._add_token(single_char_tokens[char], char)
            return
        
        # 双字符符号
        if char == '=':
            if self._match('='):
                # == 也当作 = 处理
                self._add_token(TokenType.EQ, '==')
            else:
                self._add_token(TokenType.EQ, '=')
            return
        
        if char == ':':
            if self._match(':'):
                self._add_token(TokenType.COLON_COLON, '::')
            else:
                self._add_token(TokenType.COLON, ':')
            return
        
        if char == '!':
            if self._match('='):
                self._add_token(TokenType.NE, '!=')
            else:
                self._add_token(TokenType.BANG, '!')
            return
        
        if char == '>':
            if self._match('='):
                self._add_token(TokenType.GE, '>=')
            else:
                self._add_token(TokenType.GT, '>')
            return
        
        if char == '<':
            if self._match('='):
                self._add_token(TokenType.LE, '<=')
            else:
                self._add_token(TokenType.LT, '<')
            return
        
        if char == '+':
            self._add_token(TokenType.PLUS, '+')
            return
        
        if char == '-':
            self._add_token(TokenType.MINUS, '-')
            return
        
        if char == '*':
            if self._match('*'):
                if self._match('*'):
                    self._add_token(TokenType.TRIPLE_STAR, '***')
                else:
                    self._add_token(TokenType.DOUBLE_STAR, '**')
            else:
                self._add_token(TokenType.STAR, '*')
            return
        
        if char == '/':
            # 检查是否是注释 //
            if self._peek() == '/':
                self._skip_comment()
            # 检查是否是正则表达式
            elif self._is_regex_start():
                self._scan_regex()
            else:
                self._add_token(TokenType.DIV, '/')
            return
        
        if char == '?':
            if self._match(':'):
                self._add_token(TokenType.QUESTION, '?:')
            else:
                self._add_token(TokenType.QUESTION, '?')
            return
        
        if char == '&':
            if self._match('&'):
                self._add_token(TokenType.AND, '&&')
            return
        
        if char == '|':
            if self._match('|'):
                self._add_token(TokenType.OR, '||')
            else:
                self._add_token(TokenType.PIPE, '|')
            return
        
        if char == '~':
            self._add_token(TokenType.MATCH, '~')
            return
        
        # 字符串
        if char in '"\'':
            self._scan_string(char)
            return
        
        # 数字
        if char.isdigit():
            self._scan_number(char)
            return
        
        # 标识符或关键字
        if char.isalpha() or char == '_':
            self._scan_identifier(char)
            return
        
        # 注释 // 或 #
        if char == '/' and self._peek() == '/':
            self._skip_comment()
            return
        
        if char == '#':
            self._skip_comment()
            return
        
        # 无法识别的字符
        raise SyntaxError(f"Unexpected character '{char}' at line {self.line}, column {self.column}")
    
    def _is_regex_start(self) -> bool:
        """检查当前位置是否是正则表达式开始"""
        # 简单启发式：如果前面是 = 或 : 或 ( 或 [ 或 { 或 , 或空格，则可能是正则
        if self.pos < 2:
            return True
        prev_char = self.source[self.pos - 2] if self.pos >= 2 else ' '
        return prev_char in '=:(\'", \t\n'
    
    def _scan_regex(self):
        """扫描正则表达式 /pattern/"""
        start_line = self.line
        start_column = self.column - 1
        pattern = ""
        
        while not self._is_at_end() and self._peek() != '/':
            char = self._advance()
            if char == '\\':
                # 转义字符
                if not self._is_at_end():
                    pattern += '\\' + self._advance()
            else:
                pattern += char
        
        if self._is_at_end():
            raise SyntaxError(f"Unterminated regex at line {start_line}, column {start_column}")
        
        self._advance()  # 消耗结尾的 /
        self._add_token(TokenType.REGEX, pattern)
    
    def _scan_string(self, quote: str):
        """扫描字符串"""
        start_line = self.line
        start_column = self.column - 1
        value = ""
        
        while not self._is_at_end() and self._peek() != quote:
            char = self._advance()
            if char == '\\':
                # 转义字符
                if self._is_at_end():
                    raise SyntaxError(f"Unterminated string at line {start_line}, column {start_column}")
                escape_char = self._advance()
                if escape_char == 'n':
                    value += '\n'
                elif escape_char == 't':
                    value += '\t'
                elif escape_char == '\\':
                    value += '\\'
                elif escape_char == quote:
                    value += quote
                else:
                    value += escape_char
            else:
                value += char
        
        if self._is_at_end():
            raise SyntaxError(f"Unterminated string at line {start_line}, column {start_column}")
        
        self._advance()  # 消耗结尾的引号
        self._add_token(TokenType.STRING, value)
    
    def _scan_number(self, first_char: str):
        """扫描数字（整数或浮点数）"""
        value = first_char
        
        while not self._is_at_end() and (self._peek().isdigit() or self._peek() == '.'):
            if self._peek() == '.':
                if '.' in value:
                    break  # 第二个小数点，停止
            value += self._advance()
        
        self._add_token(TokenType.NUMBER, value)
    
    def _scan_identifier(self, first_char: str):
        """扫描标识符或关键字"""
        value = first_char
        
        while not self._is_at_end() and (self._peek().isalnum() or self._peek() == '_'):
            value += self._advance()
        
        # 检查是否是关键字
        token_type = self.KEYWORDS.get(value.lower(), TokenType.IDENTIFIER)
        self._add_token(token_type, value)
    
    def _skip_comment(self):
        """跳过单行注释 //..."""
        while not self._is_at_end() and self._peek() != '\n':
            self._advance()
        # 消耗换行符（如果有）
        if not self._is_at_end() and self._peek() == '\n':
            self._advance()


def tokenize(source: str) -> List[Token]:
    """
    便捷函数：将源代码转换为 Token 列表
    
    Args:
        source: DAL 表达式字符串
        
    Returns:
        Token 列表
        
    Example:
        >>> tokens = tokenize("name = '张三'")
        >>> [t.type.name for t in tokens]
        ['IDENTIFIER', 'EQ', 'STRING', 'EOF']
    """
    lexer = Lexer(source)
    return lexer.tokenize()
