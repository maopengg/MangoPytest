# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 策略层 - 数据构造与持久化策略
# @Time   : 2026-04-01
# @Author : 毛鹏
"""
策略层（Strategy Layer）- L1

提供多种数据构造和持久化策略，支持不同场景下的性能与可靠性需求：
- APIStrategy: 调用REST/GraphQL接口（默认，最可靠）
- DBStrategy: 直接SQL插入（批量/性能测试）
- HybridStrategy: API头+DB明细（复杂对象）
- MockStrategy: 本地内存对象（单元测试）

使用示例：
    from auto_tests.bdd_api_mock.data_factory.strategies import APIStrategy, DBStrategy
    
    # API策略（默认）
    strategy = APIStrategy(api_client)
    user = strategy.create(UserEntity, username="test", password="123456")
    
    # DB策略（批量构造）
    strategy = DBStrategy(db_connection)
    users = strategy.batch_create(UserEntity, data_list)
"""

from .api_strategy import APIStrategy
from .db_strategy import DBStrategy
from .hybrid_strategy import HybridStrategy
from .mock_strategy import MockStrategy

__all__ = [
    # 具体策略
    "APIStrategy",
    "DBStrategy",
    "HybridStrategy",
    "MockStrategy",
]
