"""
DAL 核心模块

包含词法分析、语法分析、运行时等核心组件。
"""

from .lexer import Lexer, Token, TokenType
from .parser import Parser
from .ast_nodes import *
from .runtime import DALRuntime, RuntimeContext, EvaluationResult
from .operators import Operators

__all__ = [
    'Lexer',
    'Token',
    'TokenType',
    'Parser',
    'DALRuntime',
    'RuntimeContext',
    'EvaluationResult',
    'Operators',
    # AST nodes
    'ASTNode',
    'Expression',
    'Literal',
    'Identifier',
    'PropertyAccess',
    'IndexAccess',
    'BinaryOp',
    'UnaryOp',
    'ObjectLiteral',
    'ArrayLiteral',
    'TableExpression',
    'SchemaExpression',
    'ExistsCheck',
]
