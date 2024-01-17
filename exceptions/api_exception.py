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


class SendMessageError(AutoTestError):
    def __init__(self, msg):
        self.code = 301
        self.msg = msg


class ValueTypeError(AutoTestError):
    def __init__(self, msg):
        self.code = 301
        self.msg = msg


class TestEnvironmentNotObtainedError(AutoTestError):
    def __init__(self, msg):
        self.code = 301
        self.msg = msg


class AssertionFailure(AutoTestError):
    def __init__(self, msg):
        self.code = 301
        self.msg = msg


class ResponseError(AutoTestError):
    def __init__(self, msg):
        self.code = 301
        self.msg = msg


class AfterHandleError(AutoTestError):
    def __init__(self, msg):
        self.code = 301
        self.msg = msg


class LoginError(AutoTestError):
    def __init__(self, msg):
        self.code = 301
        self.msg = msg
