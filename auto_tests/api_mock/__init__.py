# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: API Mock 测试模块 - 不依赖Excel配置
# @Time   : 2026-01-18
# @Author : 毛鹏

"""
API Mock 自动化测试模块

使用方式:
    # 导入配置
    from auto_tests.api_mock import settings, get_config

    # 使用当前环境配置
    print(settings.BASE_URL)
    print(settings.TEST_USERNAME)

    # 切换到其他环境
    dev_config = get_config("dev")
    print(dev_config.BASE_URL)

环境切换:
    通过环境变量 ENV 切换环境:
    - dev: 开发环境
    - test: 测试环境（默认）
    - pre: 预发布环境
    - prod: 生产环境

    示例:
        import os
        os.environ["ENV"] = "dev"
        from auto_tests.api_mock import settings  # 现在加载的是 dev 环境配置
"""

from core.enums.tools_enum import AutoTestTypeEnum, EnvironmentEnum

PROJECT_NAME = "api_mock"
PROJECT_TYPE = AutoTestTypeEnum.API
DEFAULT_ENV = EnvironmentEnum.PROD
PROJECT_DISPLAY_NAME = "MockAPI服务"

NOTICE_CHANNEL = "email"
NOTICE_EMAIL_SEND_LIST = ["729164035@qq.com"]
NOTICE_WECHAT_WEBHOOK = ""
NOTICE_FEISHU_WEBHOOK = ""

# 导入配置系统（同时提供向后兼容的 BASE_URL 和 user_info）
from .config import (
    ApiMockConfig,
    DevConfig,
    TestConfig,
    PreConfig,
    ProdConfig,
    get_config,
    settings,
)

# 向后兼容：从配置中导出 BASE_URL 和 user_info
BASE_URL: str = settings.BASE_URL
user_info: dict = {
    "username": settings.TEST_USERNAME,
    "password": settings.TEST_PASSWORD
}

__all__ = [
    # 项目配置常量
    "PROJECT_NAME",
    "PROJECT_TYPE",
    "DEFAULT_ENV",
    "PROJECT_DISPLAY_NAME",
    # 向后兼容的导出
    "user_info",
    "BASE_URL",
    # 配置类导出
    "ApiMockConfig",
    "DevConfig",
    "TestConfig",
    "PreConfig",
    "ProdConfig",
    "get_config",
    "settings",
]
