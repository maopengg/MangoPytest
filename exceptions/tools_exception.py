# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2023-07-07 10:14
# @Author : 毛鹏
from exceptions import AutoTestError


class CacheIsNone(AutoTestError):
    def __init__(self, msg):
        self.code = 301
        self.msg = msg


class CacheIsEmptyError(AutoTestError):
    def __init__(self, msg):
        self.code = 302
        self.msg = msg


class JsonPathError(AutoTestError):

    def __init__(self, msg):
        self.code = 300
        self.msg = msg


class FileDoesNotEexistError(AutoTestError):

    def __init__(self, msg):
        self.code = 300
        self.msg = msg


class ValueTypeError(AutoTestError):

    def __init__(self, msg):
        self.code = 300
        self.msg = msg
