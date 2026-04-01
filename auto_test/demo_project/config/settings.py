# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 配置管理 - 策略配置化
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
配置管理模块

支持：
- 策略配置化（DEFAULT_STRATEGY）
- 清理配置（AUTO_CLEANUP, CASCADE_CLEANUP）
- 环境自动检测
- CI/CD 环境配置
"""

import os
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


class CreateStrategy(Enum):
    """数据创建策略"""
    API_ONLY = "api"           # 仅API调用
    DB_ONLY = "db"             # 仅数据库操作
    HYBRID = "hybrid"          # API+DB混合
    MOCK = "mock"              # Mock数据


class Environment(Enum):
    """运行环境"""
    DEV = "dev"
    TEST = "test"
    PRE = "pre"
    PROD = "prod"
    CI = "ci"


@dataclass
class BaseConfig:
    """基础配置"""
    
    # 环境
    ENV: Environment = Environment.TEST
    
    # 策略配置
    DEFAULT_STRATEGY: CreateStrategy = CreateStrategy.API_ONLY
    
    # 清理配置
    AUTO_CLEANUP: bool = True
    CASCADE_CLEANUP: bool = False
    
    # 血缘追踪
    ENABLE_LINEAGE: bool = True
    
    # API配置
    HOST: str = "http://localhost:8003"
    TIMEOUT: int = 30
    
    # 调试配置
    DEBUG: bool = False
    VERBOSE: bool = False
    
    # 扩展配置
    EXTRA: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DevConfig(BaseConfig):
    """开发环境配置"""
    ENV: Environment = Environment.DEV
    DEBUG: bool = True
    VERBOSE: bool = True
    DEFAULT_STRATEGY: CreateStrategy = CreateStrategy.MOCK


@dataclass
class TestConfig(BaseConfig):
    """测试环境配置"""
    ENV: Environment = Environment.TEST
    DEBUG: bool = True
    DEFAULT_STRATEGY: CreateStrategy = CreateStrategy.API_ONLY


@dataclass
class PreConfig(BaseConfig):
    """预发环境配置"""
    ENV: Environment = Environment.PRE
    DEBUG: bool = False
    DEFAULT_STRATEGY: CreateStrategy = CreateStrategy.API_ONLY


@dataclass
class ProdConfig(BaseConfig):
    """生产环境配置"""
    ENV: Environment = Environment.PROD
    DEBUG: bool = False
    AUTO_CLEANUP: bool = False  # 生产环境不自动清理
    DEFAULT_STRATEGY: CreateStrategy = CreateStrategy.API_ONLY


@dataclass
class CIConfig(BaseConfig):
    """CI/CD环境配置"""
    ENV: Environment = Environment.CI
    DEBUG: bool = False
    VERBOSE: bool = True
    
    # CI环境优化：使用DB策略加速
    DEFAULT_STRATEGY: CreateStrategy = CreateStrategy.DB_ONLY
    
    # 强制清理
    AUTO_CLEANUP: bool = True
    CASCADE_CLEANUP: bool = True
    
    # 并行执行
    PARALLEL: bool = True
    MAX_WORKERS: int = 4


class Settings:
    """配置管理器"""
    
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
        # 从环境变量读取
        env_str = os.environ.get("ENV", "test").lower()
        
        # CI环境检测
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
    
    # 便捷访问
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
