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


class StatusEnum(BaseEnum):
    """状态枚举"""
    SUCCESS = 1
    FAIL = 0

    @classmethod
    def obj(cls):
        return {0: "关闭&进行中&失败", 1: "启用&已完成&通过"}


class NoticeEnum(BaseEnum):
    """通知枚举"""
    MAIL = 0
    WECOM = 1
    NAILING = 2

    @classmethod
    def obj(cls):
        return {0: "邮箱", 1: "企微", 2: "钉钉-未测试"}


class ClientNameEnum(BaseEnum):
    """
    端名称
    """
    DRIVER = 'Mango Actuator'
    SERVER = 'Mango Server'
    WEB = 'mango-console'
    PLATFORM_CHINESE = '芒果自动化测试平台'
    PLATFORM_ENGLISH = 'MangoTestPlatform'

    @classmethod
    def obj(cls):
        return {'DRIVER': "Mango Actuator", 'SERVER': "Mango Server", 'WEB': "mango-console"}
