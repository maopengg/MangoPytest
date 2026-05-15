# -*- coding: utf-8 -*-
"""
数据血缘追踪模块 - BDD 版本

提供测试过程中的数据血缘追踪功能，支持 Allure 报告集成。

主要功能：
    1. 记录数据创建 - 追踪谁创建了哪条数据
    2. 记录数据依赖 - 追踪数据之间的关系
    3. 生成清理顺序 - 按依赖关系确定数据清理顺序
    4. Allure 集成 - 自动附加血缘报告到 Allure

使用示例：
    # 方式1：使用上下文管理器
    from auto_tests.bdd_api_mock.data_factory.lineage import get_tracker
    
    tracker = get_tracker()
    with tracker.track_test("test_order_workflow"):
        user = UserSpec()
        tracker.record_creation("user", user.id, metadata={"username": user.username})
        
        order = OrderSpec(user_id=user.id)
        tracker.record_creation("order", order.id, parent_entity=f"user:{user.id}")
    
    # 方式2：手动记录
    tracker.record_creation(
        entity_type="user",
        entity_id=user.id,
        source="factory",
        metadata={"username": user.username}
    )
    
    # 获取清理顺序
    cleanup_order = tracker.get_cleanup_order()
    
    # 生成 Mermaid 图
    mermaid = tracker.generate_mermaid_graph()
"""

from .tracker import DataLineageTracker, get_tracker, reset_tracker
from .graph import DataLineageGraph, Edge

__all__ = [
    # 追踪器
    "DataLineageTracker",
    "get_tracker",
    "reset_tracker",
    # 图管理
    "DataLineageGraph",
    "Edge",
]

# 版本信息
__version__ = "1.0.0"
