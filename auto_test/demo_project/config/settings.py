# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 配置基类 - 基础配置定义
# @Time   : 2026-03-31
# @Author : 毛鹏
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class DatabaseConfig:
    """数据库配置"""
    host: str = "localhost"
    port: int = 3306
    username: str = "root"
    password: str = ""
    database: str = "test_db"
    charset: str = "utf8mb4"


@dataclass
class RedisConfig:
    """Redis配置"""
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    db: int = 0


@dataclass
class APIConfig:
    """API配置"""
    host: str = "http://localhost:8000"
    timeout: int = 30
    retry_times: int = 3
    verify_ssl: bool = False


@dataclass
class LogConfig:
    """日志配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_bytes: int = 10485760  # 10MB
    backup_count: int = 5


class BaseSettings:
    """
    配置基类
    所有环境配置的父类，定义通用配置项
    """

    # 环境名称
    ENV: str = "base"

    # 调试模式
    DEBUG: bool = False

    # 数据库配置
    DATABASE: DatabaseConfig = field(default_factory=DatabaseConfig)

    # Redis配置
    REDIS: RedisConfig = field(default_factory=RedisConfig)

    # API配置
    API: APIConfig = field(default_factory=APIConfig)

    # 日志配置
    LOG: LogConfig = field(default_factory=LogConfig)

    # 测试数据配置
    TEST_DATA_CLEANUP: bool = True  # 测试后是否清理数据
    TEST_DATA_PREFIX: str = "test_"  # 测试数据前缀

    # 并发配置
    WORKERS: int = 4
    MAX_CONCURRENT: int = 10

    # 报告配置
    REPORT_DIR: str = "./reports"
    SCREENSHOT_DIR: str = "./reports/screenshots"

    @classmethod
    def get_settings(cls):
        """获取配置实例"""
        return cls()

    def to_dict(self) -> dict:
        """将配置转换为字典"""
        result = {}
        for key in dir(self):
            if not key.startswith("_") and not callable(getattr(self, key)):
                value = getattr(self, key)
                if hasattr(value, "__dataclass_fields__"):
                    result[key] = {
                        k: v for k, v in value.__dict__.items()
                        if not k.startswith("_")
                    }
                else:
                    result[key] = value
        return result
