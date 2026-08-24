# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: MockUI 测试配置类
# @Time   : 2026-04-25
# @Author : 毛鹏

"""
MockUI 测试配置

支持以下环境：
- dev: 开发环境
- prod: 生产环境
- test/pre: 使用 prod 配置
"""

from pathlib import Path

from pydantic import ConfigDict, Field

from core.ui.config import UIRuntimeConfig
from core.utils.artifacts import artifact_path

CONFIG_DIR = Path(__file__).resolve().parent


class MockUIConfig(UIRuntimeConfig):
    """
    MockUI 测试基础配置类
    """

    # 项目标识
    PROJECT_NAME: str = Field(default="MockUI 自动化测试", description="项目名称")
    ELEMENT_PROJECT: str = "mock_ui"
    ELEMENT_PRODUCT: str = Field(default="MockUI服务", description="元素产品名称")

    # UI 测试配置
    BROWSER: str = Field(default="chrome", description="浏览器类型")
    ARTIFACT_DIR: str = Field(
        default=artifact_path("reports", "simple_ui", "artifacts"),
        description="单条用例运行产物目录",
    )

    # simple_ui 使用较大的桌面窗口
    WINDOW_WIDTH: int = Field(default=1920, description="窗口宽度")
    WINDOW_HEIGHT: int = Field(default=1080, description="窗口高度")

    # Allure 报告配置
    ALLURE_REPORT_DIR: str = Field(default=artifact_path("reports", "simple_ui", "allure"), description="Allure报告目录")
    ALLURE_HISTORY_DIR: str = Field(default=artifact_path("reports", "simple_ui", "history"), description="Allure历史记录目录")

    # 日志配置
    LOG_DIR: str = Field(default=artifact_path("temp", "logs", "simple_ui"), description="日志目录")
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")

    # 截图配置
    SCREENSHOT_DIR: str = Field(default=artifact_path("screenshots", "simple_ui"), description="截图目录")

    model_config = ConfigDict(env_file_encoding="utf-8", extra="allow")


class DevConfig(MockUIConfig):
    """
    开发环境配置
    """

    ENV: str = "dev"
    BASE_URL: str = Field(default="http://localhost:8003", description="开发环境地址")

    # 开发环境使用有头模式便于调试
    HEADLESS: bool = Field(default=False, description="开发环境无头模式")
    LOG_LEVEL: str = Field(default="DEBUG", description="开发环境日志级别")

    model_config = ConfigDict(
        env_file=CONFIG_DIR / ".env.dev", env_file_encoding="utf-8", extra="allow"
    )


class _RemoteConfig(MockUIConfig):
    BASE_URL: str = Field(default="http://43.142.161.61:8003", description="生产环境地址")
    HEADLESS: bool = Field(default=True, description="生产环境无头模式")
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")


class ProdConfig(_RemoteConfig):
    """生产环境配置。"""

    ENV: str = "prod"

    model_config = ConfigDict(
        env_file=CONFIG_DIR / ".env.prod", env_file_encoding="utf-8", extra="allow"
    )


class TestConfig(_RemoteConfig):
    """
    测试环境配置
    """
    ENV: str = "test"

    model_config = ConfigDict(
        env_file=CONFIG_DIR / ".env.test", env_file_encoding="utf-8", extra="allow"
    )


class PreConfig(_RemoteConfig):
    """
    预发布环境配置
    """
    ENV: str = "pre"

    model_config = ConfigDict(
        env_file=CONFIG_DIR / ".env.pre", env_file_encoding="utf-8", extra="allow"
    )
