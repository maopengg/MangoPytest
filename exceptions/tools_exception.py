# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2023-07-07 10:14
# @Author : 毛鹏
from exceptions import PytestAutoTestError


class CacheIsNone(PytestAutoTestError):
    pass


class TestProjectError(PytestAutoTestError):
    pass


class CacheIsEmptyError(PytestAutoTestError):
    pass


class GetProjectDataError(PytestAutoTestError):
    pass


class DataFrameQueryNullError(PytestAutoTestError):
    pass


class DataFrameQueryManyError(PytestAutoTestError):
    pass


class JsonPathError(PytestAutoTestError):
    pass


class JsonSerializationError(PytestAutoTestError):
    pass


class FileDoesNotEexistError(PytestAutoTestError):
    pass


class ValueTypeError(PytestAutoTestError):
    pass


class MysqlConnectionError(PytestAutoTestError):
    pass


class MysqlQueryError(PytestAutoTestError):
    pass
