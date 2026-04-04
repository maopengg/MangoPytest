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

注意：枚举和模型已从 enums.demo_enum 和 models.demo_model 导入
"""

from core.enums.demo_enum import Environment, CreateStrategy
# 从统一的模型文件导入
from core.models.demo_model import (
    Settings, get_settings,
    BaseConfig, DevConfig, TestConfig, PreConfig, ProdConfig, CIConfig
)

# 保持向后兼容的导出
__all__ = [
    'Settings', 'get_settings', 'settings',
    'BaseConfig', 'DevConfig', 'TestConfig', 'PreConfig', 'ProdConfig', 'CIConfig',
    'Environment', 'CreateStrategy'
]

# 全局配置实例（从模型文件导入）
settings = get_settings()
