# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Scenario Fixtures - 场景 fixtures
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
Scenario Fixtures 模块

提供预配置的场景 fixtures
"""

from .approval_fixtures import (
    full_approval_scenario,
    full_approval_result,
)

__all__ = [
    "full_approval_scenario",
    "full_approval_result",
]
