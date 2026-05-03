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

from pydantic import Field

from core.base.config import BaseConfig


class BddUIMockConfig(BaseConfig):
    """
    MockUI 测试基础配置类
    """

    # 项目标识
    PROJECT_NAME: str = Field(default="MockUI 自动化测试", description="项目名称")

    # UI 测试配置
    BROWSER: str = Field(default="chrome", description="浏览器类型")
    HEADLESS: bool = Field(default=False, description="是否无头模式")
    IMPLICIT_WAIT: int = Field(default=10, description="隐式等待时间(秒)")
    PAGE_LOAD_TIMEOUT: int = Field(default=30, description="页面加载超时(秒)")
    SCRIPT_TIMEOUT: int = Field(default=10, description="脚本执行超时(秒)")

    # 窗口配置
    WINDOW_WIDTH: int = Field(default=1920, description="窗口宽度")
    WINDOW_HEIGHT: int = Field(default=1080, description="窗口高度")

    # Allure 报告配置
    ALLURE_REPORT_DIR: str = Field(default="reports/ui_mock/allure", description="Allure报告目录")
    ALLURE_HISTORY_DIR: str = Field(default="reports/ui_mock/history", description="Allure历史记录目录")

    # 日志配置
    LOG_DIR: str = Field(default="logs/ui_mock", description="日志目录")
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")

    # 截图配置
    SCREENSHOT_DIR: str = Field(default="reports/ui_mock/screenshots", description="截图目录")

    class Config:
        env_file_encoding = "utf-8"
        extra = "allow"


class DevConfig(BddUIMockConfig):
    """
    开发环境配置
    """

    ENV: str = "dev"
    BASE_URL: str = Field(default="http://localhost:8003", description="开发环境地址")

    # 开发环境使用有头模式便于调试
    HEADLESS: bool = Field(default=False, description="开发环境无头模式")
    LOG_LEVEL: str = Field(default="DEBUG", description="开发环境日志级别")

    class Config:
        env_file = ".env.dev"
        env_file_encoding = "utf-8"


class ProdConfig(BddUIMockConfig):
    """
    生产环境配置
    """

    ENV: str = "prod"
    BASE_URL: str = Field(default="http://43.142.161.61:8003", description="生产环境地址")

    # 生产环境配置
    HEADLESS: bool = Field(default=True, description="生产环境无头模式")
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")

    class Config:
        env_file = ".env.prod"
        env_file_encoding = "utf-8"


class TestConfig(ProdConfig):
    """
    测试环境配置
    """
    ENV: str = "test"

    class Config:
        env_file = ".env.test"
        env_file_encoding = "utf-8"


class PreConfig(ProdConfig):
    """
    预发布环境配置
    """
    ENV: str = "pre"

    class Config:
        env_file = ".env.pre"
        env_file_encoding = "utf-8"
