# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2023-07-07 10:14
# @Author : 毛鹏
from exceptions.error_msg import *
from tools.log import log


class PytestAutoTestError(Exception):

    def __init__(self, code: int, msg: str, value: tuple = None, error: any = None):
        self.msg = msg.format(*value) if value else msg
        self.code = code
        if error:
            log.error(f'报错提示：{self.msg}， 报错内容：{error}')
        else:
            log.error(f'{self.msg}')

    def __str__(self):
        return f"[{self.code}] {self.msg}"


class UiError(PytestAutoTestError):
    pass


class ApiError(PytestAutoTestError):
    pass


class ToolsError(PytestAutoTestError):
    pass
