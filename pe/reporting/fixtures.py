# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Allure pytest fixtures
# @Time   : 2026-04-03
# @Author : 毛鹏

"""
Allure pytest fixtures

提供与 pytest 集成的 fixtures：
- allure_context: 自动记录 Context 操作到 Allure
- allure_lineage: 自动记录血缘信息到 Allure
- allure_variant: 自动记录变体信息到 Allure

使用示例：
    def test_example(allure_context):
        user = allure_context.create(UserEntity, username="test")
        assert user is not None
"""

import pytest
from typing import Optional, Any
from datetime import datetime

try:
    import allure

    HAS_ALLURE = True
except ImportError:
    HAS_ALLURE = False

from .adapter import AllureAdapter
from .enhancers import LineageEnhancer, MatrixEnhancer


class ContextAllureRecorder:
    """Context 操作 Allure 记录器"""

    def __init__(self, test_context):
        self.test_context = test_context
        self.operations = []

    def record_create(self, entity_class, entity, **kwargs):
        """记录创建操作"""
        entity_type = entity_class.__name__
        entity_id = getattr(entity, "id", "unknown")

        op = {
            "type": "create",
            "entity_type": entity_type,
            "entity_id": entity_id,
            "timestamp": datetime.now().isoformat(),
            "data": kwargs,
        }
        self.operations.append(op)

        with AllureAdapter.step(f"创建 {entity_type} (ID: {entity_id})"):
            AllureAdapter.attach_json(
                f"{entity_type}_{entity_id}",
                {"entity_type": entity_type, "entity_id": entity_id, **kwargs},
            )

    def record_use(self, entity_class, entity, **filters):
        """记录复用操作"""
        entity_type = entity_class.__name__
        entity_id = getattr(entity, "id", "unknown") if entity else "not_found"

        op = {
            "type": "use",
            "entity_type": entity_type,
            "entity_id": entity_id,
            "timestamp": datetime.now().isoformat(),
            "filters": filters,
        }
        self.operations.append(op)

        with AllureAdapter.step(f"复用 {entity_type} (ID: {entity_id})"):
            AllureAdapter.attach_json(
                f"use_{entity_type}_{entity_id}",
                {
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "filters": filters,
                },
            )

    def record_action(self, action_name: str, result: Any):
        """记录业务动作"""
        op = {
            "type": "action",
            "action_name": action_name,
            "timestamp": datetime.now().isoformat(),
            "result": str(result),
        }
        self.operations.append(op)

        with AllureAdapter.step(f"执行动作: {action_name}"):
            AllureAdapter.attach_text(f"action_{action_name}", f"结果: {result}")

    def attach_summary(self):
        """附加操作摘要"""
        summary = {
            "total_operations": len(self.operations),
            "create_count": len(
                [op for op in self.operations if op["type"] == "create"]
            ),
            "use_count": len([op for op in self.operations if op["type"] == "use"]),
            "action_count": len(
                [op for op in self.operations if op["type"] == "action"]
            ),
            "operations": self.operations,
        }
        AllureAdapter.attach_json("Context 操作摘要", summary)


@pytest.fixture(scope="function")
def allure_context(test_context):
    """
    Allure 集成的 Context fixture

    自动将 Context 操作记录到 Allure 报告

    使用示例：
        def test_example(allure_context):
            user = allure_context.create(UserEntity, username="test")
            assert user is not None
    """
    if not HAS_ALLURE:
        yield test_context
        return

    # 创建记录器
    recorder = ContextAllureRecorder(test_context)

    # 包装 Context 的关键方法
    original_create = test_context.create
    original_use = test_context.use
    original_action = test_context.action

    def wrapped_create(entity_class, **kwargs):
        entity = original_create(entity_class, **kwargs)
        recorder.record_create(entity_class, entity, **kwargs)
        return entity

    def wrapped_use(entity_class, **filters):
        entity = original_use(entity_class, **filters)
        recorder.record_use(entity_class, entity, **filters)
        return entity

    def wrapped_action(action_func, *args, **kwargs):
        result = original_action(action_func, *args, **kwargs)
        action_name = getattr(action_func, "__name__", "unknown")
        recorder.record_action(action_name, result)
        return result

    # 替换方法
    test_context.create = wrapped_create
    test_context.use = wrapped_use
    test_context.action = wrapped_action

    yield test_context

    # 测试结束后附加摘要
    recorder.attach_summary()

    # 恢复原始方法
    test_context.create = original_create
    test_context.use = original_use
    test_context.action = original_action


@pytest.fixture(scope="function")
def allure_lineage(test_context):
    """
    Allure 集成的血缘追踪 fixture

    自动将数据血缘信息附加到 Allure 报告

    使用示例：
        def test_example(allure_context, allure_lineage):
            user = allure_context.create(UserEntity, username="test")
            # 血缘信息自动附加到报告
    """
    yield

    # 测试结束后附加血缘信息
    if (
        HAS_ALLURE
        and hasattr(test_context, "_lineage_tracker")
        and test_context._lineage_tracker
    ):
        tracker = test_context._lineage_tracker
        LineageEnhancer.attach_lineage_graph(tracker)
        LineageEnhancer.attach_lineage_analysis(tracker)


@pytest.fixture(scope="function")
def allure_variant(request):
    """
    Allure 集成的变体矩阵 fixture

    自动将变体信息附加到 Allure 报告

    使用示例：
        @pytest.mark.parametrize("variant", variants)
        def test_example(allure_variant, variant):
            # 变体信息自动附加到报告
            pass
    """
    if HAS_ALLURE:
        # 从 request 中获取变体信息
        if hasattr(request, "param"):
            variant_data = request.param
            variant_name = getattr(variant_data, "name", "unknown")
            MatrixEnhancer.attach_variant_info(
                variant_name, variant_data.data if hasattr(variant_data, "data") else {}
            )

    yield
