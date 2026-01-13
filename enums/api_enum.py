# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-01-17 11:14
# @Author : 毛鹏
from enums import BaseEnum


class MethodEnum(BaseEnum):
    """方法枚举"""
    GET = 0
    POST = 1
    PUT = 2
    DELETE = 3
    OPTIONS = 4
    DEAD = 5
    PATCH = 6

    @classmethod
    def obj(cls):
        return {0: "GET", 1: "POST", 2: "PUT", 3: "DELETE", 4: "OPTIONS", 5: "DEAD", 6: "PATCH"}


class ClientEnum(BaseEnum):
    """设备类型"""
    WEB = 0
    APP = 1
    MINI = 2

    @classmethod
    def obj(cls):
        return {0: "WEB", 1: "APP", 2: "MINI"}

