# -*- coding: utf-8 -*-
"""
占位符替换工具

支持多种占位符格式：
- ${{alias.attr}} - 双括号格式
- @alias.attr - 简洁格式
- {{attr}} - 当前实体简写格式
"""

import json
import re
from typing import Any, Dict, Optional


class PlaceholderReplacer:
    """占位符替换器
    
    支持递归替换字符串、字典、列表中的占位符。
    """
    
    # 支持的占位符格式
    PATTERNS = {
        'double_brace': r'\$\{\{(\w+)\.(\w+)\}\}',  # ${{alias.attr}}
        'at_sign': r'@(\w+)\.(\w+)',                 # @alias.attr
        'single_brace': r'\{\{(\w+)\}\}',           # {{attr}}
    }
    
    def __init__(self, context: Dict[str, Any]):
        """
        @param context: 占位符到值的映射字典
        """
        self.context = context
    
    def replace(self, obj: Any) -> Any:
        """递归替换对象中的占位符
        
        @param obj: 可能包含占位符的对象（str, dict, list）
        @return: 替换后的对象
        """
        if isinstance(obj, str):
            return self._replace_string(obj)
        elif isinstance(obj, dict):
            return {k: self.replace(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.replace(item) for item in obj]
        else:
            return obj
    
    def _replace_string(self, s: str) -> Any:
        """替换字符串中的占位符
        
        如果整个字符串是一个占位符，返回原始值（保持类型）。
        否则进行字符串替换。
        
        @param s: 输入字符串
        @return: 替换后的值或字符串
        """
        # 检查是否是纯占位符（整个字符串就是一个占位符）
        for pattern_name, pattern in self.PATTERNS.items():
            match = re.match(f'^\\s*{pattern}\\s*$', s)
            if match:
                if pattern_name == 'single_brace':
                    # {{attr}} 格式
                    attr = match.group(1)
                    key = f"{{{{{attr}}}}}"
                else:
                    # ${{alias.attr}} 或 @alias.attr 格式
                    alias, attr = match.groups()
                    key = f"{alias}.{attr}"
                
                if key in self.context:
                    return self.context[key]
                raise ValueError(f"占位符 '{s}' 未找到对应值")
        
        # 非纯占位符，进行字符串替换
        result = s
        for pattern_name, pattern in self.PATTERNS.items():
            if pattern_name == 'single_brace':
                # {{attr}}
                def replacer(m):
                    attr = m.group(1)
                    key = f"{{{{{attr}}}}}"
                    return str(self.context.get(key, m.group(0)))
            else:
                # ${{alias.attr}} 或 @alias.attr
                def replacer(m):
                    alias, attr = m.groups()
                    key = f"{alias}.{attr}"
                    return str(self.context.get(key, m.group(0)))
            
            result = re.sub(pattern, replacer, result)
        
        return result
    
    @classmethod
    def from_docstring(cls, docstring: str, entity_context) -> "PlaceholderReplacer":
        """从 docstring 和实体上下文创建替换器
        
        @param docstring: 包含占位符的字符串
        @param entity_context: EntityContext 实例
        @return: PlaceholderReplacer 实例
        """
        context = entity_context.build_placeholder_context(docstring)
        return cls(context)


def replace_placeholders(obj: Any, context: Dict[str, Any]) -> Any:
    """便捷函数：替换对象中的占位符
    
    @param obj: 可能包含占位符的对象
    @param context: 占位符到值的映射
    @return: 替换后的对象
    
    示例:
        >>> context = {"user.id": 123, "product.id": 456}
        >>> replace_placeholders("${{user.id}}", context)
        123
        >>> replace_placeholders({"user_id": "${{user.id}}"}, context)
        {"user_id": 123}
    """
    replacer = PlaceholderReplacer(context)
    return replacer.replace(obj)


def parse_json_with_placeholders(docstring: str, entity_context) -> Any:
    """解析包含占位符的 JSON 字符串
    
    @param docstring: JSON 字符串，可能包含占位符
    @param entity_context: EntityContext 实例
    @return: 解析后的 Python 对象
    @raises json.JSONDecodeError: 如果 JSON 格式错误
    
    示例:
        >>> docstring = '{"user_id": ${{user.id}}, "name": "test"}'
        >>> parse_json_with_placeholders(docstring, context)
        {"user_id": 123, "name": "test"}
    """
    if not docstring or not docstring.strip():
        return {}
    
    # 先替换占位符
    replacer = PlaceholderReplacer.from_docstring(docstring, entity_context)
    replaced = replacer.replace(docstring)
    
    # 再解析 JSON
    return json.loads(replaced)
