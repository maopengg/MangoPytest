# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-07-07 10:14
# @Author : 毛鹏
from tools.log_collector import log


class PytestAutoTestError(Exception):

    def __init__(self, code: int, msg: str, value: tuple = None, error: any = None, is_log: bool = True):
        if value:
            msg = msg.format(*value)
        if error and is_log:
            log.error(f'报错提示：{msg}， 报错内容：{error}')
        else:
            log.error(f'报错提示：{msg}')
        self.code = code
        self.msg = msg
