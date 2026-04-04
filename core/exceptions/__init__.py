# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 异常模块 - 统一异常管理
# @Time   : 2023-07-07 10:14
# @Author : 毛鹏
"""
统一异常模块

提供项目级别的统一异常类：
- PytestAutoTestError: 基础异常类
- UiError: UI测试异常
- ApiError: API测试异常
- ToolsError: 工具类异常

使用方式：
    from core.exceptions import ApiError, ERROR_MSG_0001
    raise ApiError(*ERROR_MSG_0001)
"""
from core.exceptions.error_msg import *

class PytestAutoTestError(Exception):
    """基础异常类"""

    def __init__(self, code: int, msg: str, value: tuple = None, error: any = None):
        self.msg = msg.format(*value) if value else msg
        self.code = code
        from core.utils import log
        if error:
            log.error(f'报错提示：{self.msg}， 报错内容：{error}')
        else:
            log.error(f'{self.msg}')

    def __str__(self):
        return f"[{self.code}] {self.msg}"


class UiError(PytestAutoTestError):
    """UI测试异常"""
    pass


class ApiError(PytestAutoTestError):
    """API测试异常"""
    pass


class ToolsError(PytestAutoTestError):
    """工具类异常"""
    pass


class ValidationError(PytestAutoTestError):
    """数据验证异常"""
    pass


class ConfigError(PytestAutoTestError):
    """配置异常"""
    pass


class DataError(PytestAutoTestError):
    """数据异常"""
    pass

