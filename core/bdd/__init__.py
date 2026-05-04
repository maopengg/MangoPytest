# -*- coding: utf-8 -*-
"""
BDD 测试框架核心模块

提供通用的 BDD 测试工具，支持多项目：
- EntityContext: 实体上下文管理
- PlaceholderReplacer: 占位符替换
- 通用步骤定义 (data_steps, api_steps, assertion_steps)

快速开始:
    1. 在项目 conftest.py 中导入
    2. 提供必要的 fixtures: entity_factory_map, db_session, api_client
    3. 编写 Feature 文件使用新语法

详见 README.md
"""

from .context import EntityContext, entity_context
from .placeholder import (
    PlaceholderReplacer,
    replace_placeholders,
    parse_json_with_placeholders,
)

__all__ = [
    # 上下文管理
    "EntityContext",
    "entity_context",
    # 占位符替换
    "PlaceholderReplacer",
    "replace_placeholders",
    "parse_json_with_placeholders",
]

__version__ = "1.0.0"
