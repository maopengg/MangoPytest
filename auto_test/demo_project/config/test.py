# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 测试环境配置
# @Time   : 2026-03-31
# @Author : 毛鹏
from .settings import BaseSettings, DatabaseConfig, RedisConfig, APIConfig, LogConfig


class TestSettings(BaseSettings):
    """
    测试环境配置
    用于自动化测试执行
    """

    ENV: str = "test"
    DEBUG: bool = False

    # 测试环境数据库配置
    DATABASE = DatabaseConfig(
        host="test-db.example.com",
        port=3306,
        username="test_user",
        password="test_password",
        database="test_db"
    )

    # 测试环境Redis配置
    REDIS = RedisConfig(
        host="test-redis.example.com",
        port=6379,
        db=2
    )

    # 测试环境API配置
    API = APIConfig(
        host="http://test-api.example.com",
        timeout=30,
        retry_times=3
    )

    # 测试环境日志配置
    LOG = LogConfig(
        level="INFO",
        file_path="./logs/test.log"
    )

    # 测试环境测试数据配置
    TEST_DATA_CLEANUP = True  # 测试环境自动清理数据

    # 测试报告配置
    REPORT_DIR: str = "./reports/test"
    SCREENSHOT_DIR: str = "./reports/test/screenshots"


# 测试环境配置实例
settings = TestSettings()
