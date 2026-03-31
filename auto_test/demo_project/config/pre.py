# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 预发布环境配置
# @Time   : 2026-03-31
# @Author : 毛鹏
from .settings import BaseSettings, DatabaseConfig, RedisConfig, APIConfig, LogConfig


class PreSettings(BaseSettings):
    """
    预发布环境配置
    用于上线前的最终验证
    """

    ENV: str = "pre"
    DEBUG: bool = False

    # 预发布环境数据库配置
    DATABASE = DatabaseConfig(
        host="pre-db.example.com",
        port=3306,
        username="pre_user",
        password="pre_password",
        database="pre_db"
    )

    # 预发布环境Redis配置
    REDIS = RedisConfig(
        host="pre-redis.example.com",
        port=6379,
        db=3
    )

    # 预发布环境API配置
    API = APIConfig(
        host="https://pre-api.example.com",
        timeout=30,
        retry_times=3,
        verify_ssl=True
    )

    # 预发布环境日志配置
    LOG = LogConfig(
        level="INFO",
        file_path="./logs/pre.log"
    )

    # 预发布环境测试数据配置
    TEST_DATA_CLEANUP = True

    # 预发布环境并发配置
    WORKERS: int = 8
    MAX_CONCURRENT: int = 20

    # 测试报告配置
    REPORT_DIR: str = "./reports/pre"
    SCREENSHOT_DIR: str = "./reports/pre/screenshots"


# 预发布环境配置实例
settings = PreSettings()
