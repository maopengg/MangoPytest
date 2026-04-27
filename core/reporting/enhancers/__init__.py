# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Allure 增强器 - PE 特色功能
# @Time   : 2026-04-03
# @Author : 毛鹏

"""
Allure 增强器模块

提供 MangoPytest 框架特色功能的 Allure 可视化：
- 数据血缘图可视化
- 变体矩阵展示
- 状态流转图
- 事件流展示
- 性能指标嵌入
"""

from .lineage import LineageEnhancer
from .matrix import MatrixEnhancer
from .state_machine import StateMachineEnhancer

__all__ = [
    "LineageEnhancer",
    "MatrixEnhancer",
    "StateMachineEnhancer",
]
