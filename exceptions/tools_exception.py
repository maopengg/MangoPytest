# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2023-07-07 10:14
# @Author : 毛鹏
from exceptions import PytestAutoTestError


class CacheIsNone(PytestAutoTestError):
    pass


class CacheIsEmptyError(PytestAutoTestError):
    pass


class JsonPathError(PytestAutoTestError):
    pass


class FileDoesNotEexistError(PytestAutoTestError):
    pass


class ValueTypeError(PytestAutoTestError):
    pass

class MysqlConnectionError(PytestAutoTestError):
    pass


class MysqlQueryError(PytestAutoTestError):
    pass
