# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2023-07-04 13:42
# @Author : 毛鹏
from enums import BaseEnum


class NotificationType(BaseEnum):
    """ 自动化通知方式 """
    EMAIL = 0
    WECHAT = 1


class RequestType(BaseEnum):
    """
    request请求发送，请求参数的数据类型
    """
    JSON = "JSON"
    PARAMS = "PARAMS"
    DATA = "DATA"
    FILE = 'FILE'
    EXPORT = "EXPORT"
    NONE = "NONE"


class AssEnum(BaseEnum):
    response = 0
    sql = 1


class AfterHandleEnum(BaseEnum):
    sql = 1
