# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2023-07-07 10:14
# @Author : 毛鹏


class MyBaseFailure(Exception):
    pass


class CacheIsNone(Exception):
    def __init__(self, msg):
        self.code = 301
        self.msg = msg


class SendMessageError(Exception):
    def __init__(self, msg):
        self.code = 301
        self.msg = msg


class ValueTypeError(Exception):
    def __init__(self, msg):
        self.code = 301
        self.msg = msg


class ValueNotFoundError(MyBaseFailure):
    pass


class AssertionFailure(AssertionError):
    def __init__(self, msg):
        self.code = 301
        self.msg = msg
