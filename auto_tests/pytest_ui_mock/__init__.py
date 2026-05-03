# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2026-03-03 14:07
# @Author : 毛鹏
from core.enums.tools_enum import AutoTestTypeEnum, EnvironmentEnum

PROJECT_NAME = "pytest_ui_mock"
PROJECT_TYPE = AutoTestTypeEnum.UI
DEFAULT_ENV = EnvironmentEnum.PROD
PROJECT_DISPLAY_NAME = "MockUI服务"

NOTICE_CHANNEL = "email"
NOTICE_EMAIL_SEND_LIST = ["729164035@qq.com"]
NOTICE_WECHAT_WEBHOOK = ""
NOTICE_FEISHU_WEBHOOK = ""
