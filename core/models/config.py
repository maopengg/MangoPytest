# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 配置相关数据模型
# @Time   : 2026-05-03
# @Author : 毛鹏
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from core.enums.demo_enum import CreateStrategy, Environment


@dataclass
class BaseConfig:
    """基础配置"""
    ENV: Environment = Environment.TEST
    DEFAULT_STRATEGY: CreateStrategy = CreateStrategy.API_ONLY
    AUTO_CLEANUP: bool = True
    CASCADE_CLEANUP: bool = False
    ENABLE_LINEAGE: bool = True
    HOST: str = "http://localhost:8003"
    TIMEOUT: int = 30
    DEBUG: bool = False
    VERBOSE: bool = False
    EXTRA: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DevConfig(BaseConfig):
    """开发环境配置"""
    ENV: Environment = Environment.DEV
    DEBUG: bool = True
    VERBOSE: bool = True
    HOST: str = "http://localhost:8003"
    DEFAULT_STRATEGY: CreateStrategy = CreateStrategy.MOCK


@dataclass
class TestConfig(BaseConfig):
    """测试环境配置"""
    ENV: Environment = Environment.TEST
    DEBUG: bool = True
    HOST: str = "http://43.142.161.61:8003/"
    DEFAULT_STRATEGY: CreateStrategy = CreateStrategy.API_ONLY


@dataclass
class PreConfig(BaseConfig):
    """预发环境配置"""
    ENV: Environment = Environment.PRE
    DEBUG: bool = False
    HOST: str = "http://43.142.161.61:8003/"
    DEFAULT_STRATEGY: CreateStrategy = CreateStrategy.API_ONLY


@dataclass
class ProdConfig(BaseConfig):
    """生产环境配置"""
    ENV: Environment = Environment.PROD
    DEBUG: bool = False
    HOST: str = "http://43.142.161.61:8003/"
    AUTO_CLEANUP: bool = False
    DEFAULT_STRATEGY: CreateStrategy = CreateStrategy.API_ONLY


@dataclass
class CIConfig(BaseConfig):
    """CI/CD环境配置"""
    ENV: Environment = Environment.CI
    DEBUG: bool = False
    VERBOSE: bool = True
    DEFAULT_STRATEGY: CreateStrategy = CreateStrategy.DB_ONLY
    AUTO_CLEANUP: bool = True
    CASCADE_CLEANUP: bool = True
    PARALLEL: bool = True
    MAX_WORKERS: int = 4


class Settings:
    """配置管理器（单例）"""

    _instance: Optional['Settings'] = None
    _config: Optional[BaseConfig] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """加载配置"""
        env = self._detect_environment()

        config_map = {
            Environment.DEV: DevConfig(),
            Environment.TEST: TestConfig(),
            Environment.PRE: PreConfig(),
            Environment.PROD: ProdConfig(),
            Environment.CI: CIConfig(),
        }
        self._config = config_map.get(env, TestConfig())

    def _detect_environment(self) -> Environment:
        """检测运行环境"""
        import os
        env_str = os.environ.get("ENV", "test").lower()

        if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
            return Environment.CI

        env_map = {
            "dev": Environment.DEV,
            "development": Environment.DEV,
            "test": Environment.TEST,
            "testing": Environment.TEST,
            "pre": Environment.PRE,
            "staging": Environment.PRE,
            "prod": Environment.PROD,
            "production": Environment.PROD,
            "ci": Environment.CI,
        }
        return env_map.get(env_str, Environment.TEST)

    @property
    def config(self) -> BaseConfig:
        """获取当前配置"""
        return self._config

    def reload(self):
        """重新加载配置"""
        self._load_config()

    def update(self, **kwargs):
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)

    @property
    def ENV(self) -> Environment:
        return self._config.ENV

    @property
    def DEFAULT_STRATEGY(self) -> CreateStrategy:
        return self._config.DEFAULT_STRATEGY

    @property
    def AUTO_CLEANUP(self) -> bool:
        return self._config.AUTO_CLEANUP

    @property
    def CASCADE_CLEANUP(self) -> bool:
        return self._config.CASCADE_CLEANUP

    @property
    def ENABLE_LINEAGE(self) -> bool:
        return self._config.ENABLE_LINEAGE

    @property
    def HOST(self) -> str:
        return self._config.HOST

    @property
    def DEBUG(self) -> bool:
        return self._config.DEBUG


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings
