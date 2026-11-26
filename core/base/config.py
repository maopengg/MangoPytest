# -*- coding: utf-8 -*-
"""
基础配置类 - Core Base 模块

所有子项目的配置类都应该继承此类
"""

from pathlib import Path

from pydantic import Field, ConfigDict, field_validator, model_validator
from pydantic_settings import BaseSettings

from core.runtime import runtime_path

OUTPUT_DIRECTORY_FIELDS = (
    "LOG_DIR", "ALLURE_REPORT_DIR", "ALLURE_HISTORY_DIR", "ARTIFACT_DIR", "SCREENSHOT_DIR",
)


class BaseConfig(BaseSettings):
    """基础配置类

    所有子项目的配置类都应该继承此类，提供：
    - 环境标识
    - API 基础 URL
    - 数据库配置
    - 连接池配置

    使用示例：
        from core.base import BaseConfig

        class MyConfig(BaseConfig):
            BASE_URL: str = "http://my-api.com"
            DB_NAME: str = "my_db"
    """

    # Pydantic V2 配置
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    @field_validator(*OUTPUT_DIRECTORY_FIELDS, mode="before", check_fields=False)
    @classmethod
    def resolve_output_directory(cls, value):
        if not isinstance(value, str) or not value.strip():
            return value
        directory = Path(value).expanduser()
        if directory.is_absolute():
            return str(directory)
        parts = directory.parts
        if parts and parts[0] in {"artifacts", "runtime"}:
            parts = parts[1:]
        if parts[:2] in {("temp", "logs"), ("temp", "cache")}:
            parts = parts[1:]
        return runtime_path(*parts)

    @model_validator(mode="after")
    def resolve_extra_output_directories(self):
        # 部分旧 .env 中的输出字段尚未在对应项目模型中声明。
        extra = self.model_extra or {}
        for name in OUTPUT_DIRECTORY_FIELDS:
            if name in extra:
                extra[name] = self.resolve_output_directory(extra[name])
        return self

    # 环境标识
    ENV: str = Field(default="test", description="环境标识")

    # API 基础 URL
    BASE_URL: str = Field(default="http://localhost:8000", description="API 基础 URL")

    # 数据库配置
    DB_HOST: str = Field(default="localhost", description="数据库主机")
    DB_PORT: int = Field(default=3306, description="数据库端口")
    DB_USER: str = Field(default="root", description="数据库用户名")
    DB_PASSWORD: str = Field(default="", description="数据库密码")
    DB_NAME: str = Field(default="test", description="数据库名称")

    # 连接池配置
    DB_POOL_SIZE: int = Field(default=5, description="连接池大小")
    DB_MAX_OVERFLOW: int = Field(default=10, description="最大溢出连接数")
    DB_POOL_TIMEOUT: int = Field(default=30, description="连接池超时时间")
    DB_POOL_RECYCLE: int = Field(default=3600, description="连接回收时间")

    @property
    def DB_URL(self) -> str:
        """生成数据库连接 URL

        Returns:
            MySQL 连接 URL，格式：mysql+pymysql://user:pass@host:port/db?charset=utf8mb4
        """
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?charset=utf8mb4"
        )
