# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据血缘追踪模块
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
数据血缘追踪模块

目录结构：
    lineage/
    ├── __init__.py          # 导出所有血缘追踪组件
    ├── node.py              # 血缘节点定义
    ├── graph.py             # 血缘图管理
    ├── tracker.py           # 血缘追踪器
    └── analyzer.py          # 血缘分析器

使用示例：
    from auto_tests.bdd_api_mock.data_factory.lineage import (
        DataLineageTracker,
        LineageAnalyzer,
        LineageNodeType,
    )
    
    # 创建追踪器
    tracker = DataLineageTracker()
    
    # 记录数据创建
    tracker.record_creation(
        entity_type="user",
        entity_id="user_123",
        source="api_call",
        metadata={"username": "test_user"}
    )
    
    # 记录数据依赖
    tracker.record_dependency(
        from_entity="user_123",
        to_entity="order_456",
        relation_type="creates"
    )
"""

from .analyzer import LineageAnalyzer
from .graph import DataLineageGraph
from .tracker import DataLineageTracker

__all__ = [
    # 图管理
    "DataLineageGraph",
    # 追踪器
    "DataLineageTracker",
    # 分析器
    "LineageAnalyzer",
]
