# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2026-05-03
# @Author : 毛鹏
"""bdd_ui_mock — BDD 范式 UI 自动化测试"""
from core.enums.tools_enum import AutoTestTypeEnum, EnvironmentEnum

PROJECT_NAME = "bdd_ui_mock"
PROJECT_TYPE = AutoTestTypeEnum.UI
DEFAULT_ENV = EnvironmentEnum.PRO
PROJECT_DISPLAY_NAME = "MockUI服务"

NOTICE_CHANNEL = "email"
NOTICE_EMAIL_SEND_LIST = ["729164035@qq.com"]
NOTICE_WECHAT_WEBHOOK = ""
NOTICE_FEISHU_WEBHOOK = ""
