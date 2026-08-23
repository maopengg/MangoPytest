"""Mango Mock 的多协议 API 自动化演示项目。"""

from core.enums.tools_enum import AutoTestTypeEnum, EnvironmentEnum

PROJECT_NAME = "pytest_api"
PROJECT_TYPE = AutoTestTypeEnum.API
DEFAULT_ENV = EnvironmentEnum.TEST
PROJECT_DISPLAY_NAME = "pytest_api"

NOTICE_CHANNEL = "email"
NOTICE_EMAIL_SEND_LIST = []
NOTICE_WECHAT_WEBHOOK = ""
NOTICE_FEISHU_WEBHOOK = ""
