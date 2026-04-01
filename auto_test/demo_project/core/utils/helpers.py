# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Core Helpers - 辅助函数
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
Core Helpers 模块

提供通用的辅助函数
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime


def generate_id(prefix: str = "") -> str:
    """
    生成唯一标识
    
    @param prefix: 前缀
    @return: 唯一标识
    
    使用示例：
        id = generate_id("user")  # "user_a1b2c3d4"
    """
    suffix = uuid.uuid4().hex[:8]
    if prefix:
        return f"{prefix}_{suffix}"
    return suffix


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    合并多个字典
    
    @param dicts: 要合并的字典
    @return: 合并后的字典
    
    使用示例：
        result = merge_dicts(
            {"a": 1},
            {"b": 2},
            {"c": 3}
        )
        # result: {"a": 1, "b": 2, "c": 3}
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def filter_dict(
    data: Dict[str, Any],
    include: Optional[list] = None,
    exclude: Optional[list] = None
) -> Dict[str, Any]:
    """
    过滤字典
    
    @param data: 原始字典
    @param include: 包含的键列表
    @param exclude: 排除的键列表
    @return: 过滤后的字典
    
    使用示例：
        data = {"a": 1, "b": 2, "c": 3}
        
        # 只保留指定键
        result = filter_dict(data, include=["a", "b"])
        # result: {"a": 1, "b": 2}
        
        # 排除指定键
        result = filter_dict(data, exclude=["b"])
        # result: {"a": 1, "c": 3}
    """
    if include:
        return {k: v for k, v in data.items() if k in include}
    
    if exclude:
        return {k: v for k, v in data.items() if k not in exclude}
    
    return data.copy()


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化日期时间
    
    @param dt: 日期时间
    @param fmt: 格式
    @return: 格式化后的字符串
    """
    return dt.strftime(fmt)


def parse_datetime(s: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    解析日期时间
    
    @param s: 日期时间字符串
    @param fmt: 格式
    @return: 日期时间对象
    """
    return datetime.strptime(s, fmt)


def truncate_string(s: str, max_length: int, suffix: str = "...") -> str:
    """
    截断字符串
    
    @param s: 原始字符串
    @param max_length: 最大长度
    @param suffix: 后缀
    @return: 截断后的字符串
    """
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix


def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    安全获取字典值
    
    @param data: 字典
    @param key: 键
    @param default: 默认值
    @return: 值或默认值
    """
    return data.get(key, default)


__all__ = [
    "generate_id",
    "merge_dicts",
    "filter_dict",
    "format_datetime",
    "parse_datetime",
    "truncate_string",
    "safe_get",
]
