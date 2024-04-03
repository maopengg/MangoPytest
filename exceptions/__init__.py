# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-07-07 10:14
# @Author : 毛鹏
from tools.logging_tool import logger


class PytestAutoTestError(Exception):

    def __init__(self, code: int, msg: str, value: tuple = None, error: any = None):
        if value:
            msg = msg.format(*value)
        if error:
            logger.error(error)
        else:
            logger.error(msg)
        self.code = code
        self.msg = msg
