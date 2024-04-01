# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2023-07-04 13:42
# @Author : 毛鹏

from enums import BaseEnum


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
    PLATFORM_CHINESE = '自动化测试'
    PLATFORM_ENGLISH = 'AutoTest'


class AutoTestTypeEnum(BaseEnum):
    """自动测试类型"""
    UI = 0
    API = 1
    PERF = 2

    @classmethod
    def obj(cls):
        return {0: "界面", 1: "接口", 2: "性能"}


class EnvironmentEnum(BaseEnum):
    """测试环境枚举"""
    DEV = 0
    TEST = 1
    PRE = 2
    UAT = 3
    SIM = 4
    PRO = 5

    @classmethod
    def obj(cls):
        return {0: "开发环境", 1: "测试环境", 2: "预发环境", 3: "验收环境", 4: "仿真环境", 5: "生产环境", }


class NotificationType(BaseEnum):
    """通知枚举"""
    MAIL = 0
    WECOM = 1
    NAILING = 2

    @classmethod
    def obj(cls):
        return {0: "邮箱", 1: "企微", 2: "钉钉-未测试"}


class AssEnum(BaseEnum):
    response = 0
    sql = 1

    @classmethod
    def obj(cls):
        return {0: "响应", 1: 'sql'}


class StatusEnum(BaseEnum):
    """状态枚举"""
    SUCCESS = 1
    FAIL = 0

    @classmethod
    def obj(cls):
        return {0: "关闭&进行中&失败", 1: "启用&已完成&通过"}


class ClientEnum(BaseEnum):
    """设备类型"""
    WEB = 0
    Android = 1
    MINI = 2

    @classmethod
    def obj(cls):
        return {0: "WEB", 1: "安卓", 2: "MINI"}
