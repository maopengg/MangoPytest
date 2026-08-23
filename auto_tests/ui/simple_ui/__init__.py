# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 轻量 UI 自动化 Demo
# @Time   : 2026-03-03 14:07
# @Author : 毛鹏

from core.enums.tools_enum import AutoTestTypeEnum, EnvironmentEnum

PROJECT_NAME = "simple_ui"
PROJECT_TYPE = AutoTestTypeEnum.UI
DEFAULT_ENV = EnvironmentEnum.TEST
PROJECT_DISPLAY_NAME = "MockUI服务"

NOTICE_CHANNEL = "email"
NOTICE_EMAIL_SEND_LIST = []
NOTICE_WECHAT_WEBHOOK = ""
NOTICE_FEISHU_WEBHOOK = ""
