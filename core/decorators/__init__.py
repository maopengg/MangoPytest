# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 装饰器模块 - 所有项目装饰器集中管理
# @Time   : 2026-04-04
# @Author : 毛鹏
"""
统一装饰器模块

集中管理所有装饰器，包括：
- API测试装饰器
- UI测试装饰器
- 其他测试装饰器
- 工具装饰器

使用方式：
    from core.decorators.ui import case_data, request_data, timer
"""

# API测试装饰器
from .api import (
    case_data as api_case_data,
    request_data,
    timer,
    log_decorator,
    CleanupContext,
    api_allure_logger,
    _log_api_response_to_allure,
)
# 其他测试装饰器
from .other import (
    case_data as other_case_data,
)
# UI测试装饰器
from .ui import (
    case_data as ui_case_data,
)
# 工具装饰器（从 core.utils.decorators 迁移）
from .utils import (
    retry,
    singleton,
    deprecated,
    timeit,
    memoize,
    throttle,
    validate_input,
    log_execution,
    async_task,
    cache_result,
)

# 便捷别名
api_case_data = api_case_data
ui_case_data = ui_case_data
other_case_data = other_case_data

__all__ = [
    # API测试装饰器
    'api_case_data',
    'request_data',
    'timer',
    'log_decorator',
    'CleanupContext',
    'api_allure_logger',
    '_log_api_response_to_allure',
    # UI测试装饰器
    'ui_case_data',
    # 其他测试装饰器
    'other_case_data',
    # 工具装饰器
    'retry',
    'singleton',
    'deprecated',
    'timeit',
    'memoize',
    'throttle',
    'validate_input',
    'log_execution',
    'async_task',
    'cache_result',
]
