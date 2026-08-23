# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: SQL 自动化占位项目（尚未提供 pytest Case）
# @Time   : 2025-01-09 11:15
# @Author : 毛鹏

from core.enums.tools_enum import AutoTestTypeEnum, EnvironmentEnum

PROJECT_NAME = "sql"
PROJECT_TYPE = AutoTestTypeEnum.OTHER
DEFAULT_ENV = EnvironmentEnum.TEST
PROJECT_DISPLAY_NAME = "SQL 自动化"

NOTICE_CHANNEL = "email"
NOTICE_EMAIL_SEND_LIST = []
NOTICE_WECHAT_WEBHOOK = ""
NOTICE_FEISHU_WEBHOOK = ""
