# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2023-07-04 13:42
# @Author : 毛鹏
from enum import Enum


class ProjectEnum(Enum):
    CDXP = 'cdxp'
    AIGC = 'aigc'


class NotificationType(Enum):
    """ 自动化通知方式 """
    EMAIL = 0
    WECHAT = 1


class RequestType(Enum):
    """
    request请求发送，请求参数的数据类型
    """
    JSON = "JSON"
    PARAMS = "PARAMS"
    DATA = "DATA"
    FILE = 'FILE'
    EXPORT = "EXPORT"
    NONE = "NONE"
