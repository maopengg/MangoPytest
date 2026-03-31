# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 生产环境配置
# @Time   : 2026-03-31
# @Author : 毛鹏
from .settings import BaseSettings, DatabaseConfig, RedisConfig, APIConfig, LogConfig


class ProdSettings(BaseSettings):
    """
    生产环境配置
    用于正式环境监控和回归测试
    """

    ENV: str = "prod"
    DEBUG: bool = False

    # 生产环境数据库配置（只读或特定测试库）
    DATABASE = DatabaseConfig(
        host="prod-db.example.com",
        port=3306,
        username="prod_test_user",  # 生产环境使用专门的测试账号
        password="prod_test_password",
        database="prod_test_db"  # 生产环境使用独立的测试数据库
    )

    # 生产环境Redis配置
    REDIS = RedisConfig(
        host="prod-redis.example.com",
        port=6379,
        db=0
    )

    # 生产环境API配置
    API = APIConfig(
        host="https://api.example.com",
        timeout=60,  # 生产环境超时时间更长
        retry_times=5,  # 生产环境重试次数更多
        verify_ssl=True
    )

    # 生产环境日志配置
    LOG = LogConfig(
        level="WARNING",  # 生产环境只记录警告及以上级别
        file_path="./logs/prod.log"
    )

    # 生产环境测试数据配置
    TEST_DATA_CLEANUP = True  # 生产环境必须清理测试数据
    TEST_DATA_PREFIX: str = "auto_test_"  # 生产环境使用特殊前缀

    # 生产环境并发配置
    WORKERS: int = 16
    MAX_CONCURRENT: int = 50

    # 测试报告配置
    REPORT_DIR: str = "./reports/prod"
    SCREENSHOT_DIR: str = "./reports/prod/screenshots"

    # 生产环境安全配置
    ENABLE_DATA_MASKING: bool = True  # 启用数据脱敏
    STRICT_MODE: bool = True  # 严格模式


# 生产环境配置实例
settings = ProdSettings()
