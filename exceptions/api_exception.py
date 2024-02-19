# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2023-07-07 10:14
# @Author : 毛鹏
from exceptions import PytestAutoTestError


class CacheIsNone(PytestAutoTestError):
    pass


class SendMessageError(PytestAutoTestError):
    pass


class ValueTypeError(PytestAutoTestError):
    pass


class TestEnvironmentNotObtainedError(PytestAutoTestError):
    pass


class AssertionFailure(PytestAutoTestError):
    pass


class ResponseError(PytestAutoTestError):
    pass


class AfterHandleError(PytestAutoTestError):
    pass


class LoginError(PytestAutoTestError):
    pass


class CaseParameterError(PytestAutoTestError):
    pass
