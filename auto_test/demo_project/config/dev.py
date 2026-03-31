# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 开发环境配置
# @Time   : 2026-03-31
# @Author : 毛鹏
from .settings import BaseSettings, DatabaseConfig, RedisConfig, APIConfig, LogConfig


class DevSettings(BaseSettings):
    """
    开发环境配置
    用于本地开发和调试
    """

    ENV: str = "dev"
    DEBUG: bool = True

    # 开发环境数据库配置
    DATABASE = DatabaseConfig(
        host="localhost",
        port=3306,
        username="dev_user",
        password="dev_password",
        database="dev_db"
    )

    # 开发环境Redis配置
    REDIS = RedisConfig(
        host="localhost",
        port=6379,
        db=1
    )

    # 开发环境API配置
    API = APIConfig(
        host="http://localhost:8003",
        timeout=30,
        retry_times=1  # 开发环境减少重试次数
    )

    # 开发环境日志配置
    LOG = LogConfig(
        level="DEBUG",
        file_path="./logs/dev.log"
    )

    # 开发环境测试数据配置
    TEST_DATA_CLEANUP = False  # 开发环境不自动清理数据，方便调试


# 开发环境配置实例
settings = DevSettings()
