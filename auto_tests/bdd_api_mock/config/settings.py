# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: BDD API Mock 配置类 - 支持多环境
# @Time   : 2026-04-25
# @Author : 毛鹏

"""
BDD API Mock 多环境配置

继承自 core.base.BaseConfig，支持以下环境：
- dev: 开发环境 (localhost)
- prod: 生产环境 (43.142.161.61)
- test/pre: 使用 prod 配置
"""

from pydantic import Field
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

from core.base import BaseConfig


class BddApiMockConfig(BaseConfig):
    """
    BDD API Mock 基础配置类
    
    所有环境配置类的基类，定义通用配置项
    """
    
    # 项目标识
    PROJECT_NAME: str = Field(default="BDD API Mock 自动化测试", description="项目名称")
    
    # API Mock 特有配置
    MOCK_API_PREFIX: str = Field(default="/api", description="API前缀")
    MOCK_TIMEOUT: int = Field(default=30, description="请求超时时间(秒)")
    MOCK_RETRY_TIMES: int = Field(default=3, description="请求重试次数")
    
    # 测试账号配置
    TEST_USERNAME: str = Field(default="testuser", description="测试用户名")
    TEST_PASSWORD: str = Field(default="482c811da5d5b4bc6d497ffa98491e38", description="测试密码(MD5)")
    
    # Allure 报告配置
    ALLURE_REPORT_DIR: str = Field(default="reports/bdd_api_mock/allure", description="Allure报告目录")
    ALLURE_HISTORY_DIR: str = Field(default="reports/bdd_api_mock/history", description="Allure历史记录目录")
    
    # 日志配置
    LOG_DIR: str = Field(default="logs/bdd_api_mock", description="日志目录")
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    
    # SQLAlchemy 相关（延迟初始化）
    _engine = None
    _SessionLocal = None
    _Base = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 初始化 SQLAlchemy
        self._init_db()
    
    def _init_db(self):
        """初始化数据库连接"""
        # 创建引擎
        self._engine = create_engine(
            self.DB_URL,
            poolclass=StaticPool,
            pool_pre_ping=True,
            echo=False,
        )
        
        # 创建会话工厂
        self._SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine
        )
        
        # 声明基类
        self._Base = declarative_base()
    
    @property
    def engine(self):
        """SQLAlchemy 引擎"""
        return self._engine
    
    @property
    def SessionLocal(self):
        """会话工厂"""
        return self._SessionLocal
    
    @property
    def Base(self):
        """声明基类"""
        return self._Base
    
    def get_db_session(self):
        """获取数据库会话"""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()
    
    class Config:
        env_file_encoding = "utf-8"
        extra = "allow"


class DevConfig(BddApiMockConfig):
    """
    开发环境配置
    
    用于本地开发调试
    """
    
    ENV: str = "dev"
    BASE_URL: str = Field(default="http://localhost:8003", description="开发环境API地址")
    
    # 开发环境数据库
    DB_HOST: str = Field(default="localhost", description="开发数据库主机")
    DB_PORT: int = Field(default=3306, description="开发数据库端口")
    DB_USER: str = Field(default="root", description="数据库用户名")
    DB_PASSWORD: str = Field(default="", description="数据库密码")
    DB_NAME: str = Field(default="mango_mock_dev", description="开发数据库名")
    
    # 开发环境日志级别
    LOG_LEVEL: str = Field(default="DEBUG", description="开发环境日志级别")
    
    # 开发环境重试次数
    MOCK_RETRY_TIMES: int = Field(default=1, description="开发环境重试次数")
    
    class Config:
        env_file = ".env.dev"
        env_file_encoding = "utf-8"


class ProdConfig(BddApiMockConfig):
    """
    生产环境配置（也用于 test/pre 环境）
    
    用于测试和生产环境
    """
    
    ENV: str = "prod"
    BASE_URL: str = Field(default="http://43.142.161.61:8003", description="生产环境API地址")
    
    # 数据库配置
    DB_HOST: str = Field(default="43.142.161.61", description="数据库主机")
    DB_PORT: int = Field(default=3306, description="数据库端口")
    DB_USER: str = Field(default="root", description="数据库用户名")
    DB_PASSWORD: str = Field(default="mP123456&", description="数据库密码")
    DB_NAME: str = Field(default="mango_mock", description="数据库名")
    
    # 日志级别
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    
    # 超时和重试
    MOCK_TIMEOUT: int = Field(default=30, description="超时时间")
    MOCK_RETRY_TIMES: int = Field(default=3, description="重试次数")
    
    class Config:
        env_file = ".env.prod"
        env_file_encoding = "utf-8"


class TestConfig(ProdConfig):
    """
    测试环境配置
    
    继承自 ProdConfig，使用相同的配置
    """
    ENV: str = "test"
    
    class Config:
        env_file = ".env.test"
        env_file_encoding = "utf-8"


class PreConfig(ProdConfig):
    """
    预发布环境配置
    
    继承自 ProdConfig，使用相同的配置
    """
    ENV: str = "pre"
    
    class Config:
        env_file = ".env.pre"
        env_file_encoding = "utf-8"
