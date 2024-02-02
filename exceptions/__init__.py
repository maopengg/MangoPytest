# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-07-07 10:14
# @Author : 毛鹏
from tools.logging_tool.log_control import ERROR


class PytestAutoTestError(Exception):

    def __init__(self, code: int, msg: str, value: tuple = None, error: any = None):
        if value:
            msg = msg.format(*value)
        if error:
            ERROR.logger.error(error)
        self.code = code
        self.msg = msg
