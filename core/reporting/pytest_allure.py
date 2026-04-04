# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Allure 集成 pytest 钩子
# @Time   : 2026-04-03
# @Author : 毛鹏

"""
Allure 集成 pytest 钩子

自动将以下信息记录到 Allure 报告：
1. 测试用例的 feature/story/title
2. Context 操作（create/use/action/expect/event）
3. 数据血缘追踪
4. 场景变体信息
5. 状态机流转

使用示例：
    # 在 conftest.py 中导入
    from pe.reporting.pytest_allure import (
        allure_context,
        allure_lineage,
        allure_variant,
        allure_feature,
        allure_story,
    )
    
    # 在测试中使用
    def test_example(allure_context):
        user = allure_context.create(UserEntity, username="test")
        assert user is not None
"""

from typing import Optional

import pytest

import allure

from .allure_integration import (
    AllureHelper,
    ContextAllureAdapter,
    LineageAllureAdapter,
    VariantAllureAdapter,
)


class AllureIntegrationPlugin:
    """Allure 集成插件"""

    def __init__(self):
        self.context_adapter: Optional[ContextAllureAdapter] = None
        self.current_test = None

    def pytest_runtest_setup(self, item):
        """测试开始前"""
        self.current_test = item

        # 从测试函数的 docstring 提取信息
        if item.function.__doc__:
            doc = item.function.__doc__.strip()
            lines = doc.split('\n')

            # 第一行作为标题
            if lines:
                AllureHelper.title(lines[0])

            # 其余行作为描述
            if len(lines) > 1:
                description = '\n'.join(lines[1:]).strip()
                AllureHelper.description(description)

        # 从 pytest marker 提取 feature/story
        feature_marker = item.get_closest_marker('feature')
        if feature_marker:
            AllureHelper.feature(feature_marker.args[0])

        story_marker = item.get_closest_marker('story')
        if story_marker:
            AllureHelper.story(story_marker.args[0])

    def pytest_runtest_teardown(self, item):
        """测试结束后"""
        if not self.context_adapter:
            return

        # 附加 Context 操作摘要
        self.context_adapter.attach_summary()
        self.context_adapter = None


# 创建插件实例
allure_plugin = AllureIntegrationPlugin()


def pytest_configure(config):
    """pytest 配置钩子"""
    config.pluginmanager.register(allure_plugin)

    # 添加自定义 marker
    config.addinivalue_line(
        "markers", "feature(name): 标记功能模块"
    )
    config.addinivalue_line(
        "markers", "story(name): 标记用户故事"
    )


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
    # 创建适配器
    adapter = ContextAllureAdapter(test_context)
    allure_plugin.context_adapter = adapter

    # 包装 Context 的关键方法
    original_create = test_context.create
    original_use = test_context.use
    original_action = test_context.action
    original_expect = test_context.expect
    original_fire_event = test_context.fire_event

    def wrapped_create(entity_class, **kwargs):
        entity = original_create(entity_class, **kwargs)
        entity_id = getattr(entity, 'id', 'unknown')
        adapter.record_create(entity_class.__name__, entity_id, **kwargs)
        return entity

    def wrapped_use(entity_class, **filters):
        entity = original_use(entity_class, **filters)
        if entity:
            entity_id = getattr(entity, 'id', 'unknown')
            adapter.record_use(entity_class.__name__, entity_id, **filters)
        return entity

    def wrapped_action(action_func, *args, **kwargs):
        result = original_action(action_func, *args, **kwargs)
        action_name = getattr(action_func, '__name__', 'unknown')
        target_entity = getattr(action_func, '__self__', 'unknown')
        adapter.record_action(action_name, str(target_entity), result)
        return result

    def wrapped_expect(value):
        expectation = original_expect(value)
        # 记录预期验证
        adapter.record_expect(f"expect({value})", True)
        return expectation

    def wrapped_fire_event(event_name, priority="normal"):
        result = original_fire_event(event_name, priority)
        fired = test_context.event(event_name).was_fired()
        adapter.record_event(event_name, priority, fired)
        return result

    # 替换方法
    test_context.create = wrapped_create
    test_context.use = wrapped_use
    test_context.action = wrapped_action
    test_context.expect = wrapped_expect
    test_context.fire_event = wrapped_fire_event

    yield test_context

    # 恢复原始方法
    test_context.create = original_create
    test_context.use = original_use
    test_context.action = original_action
    test_context.expect = original_expect
    test_context.fire_event = original_fire_event


@pytest.fixture(scope="function")
def allure_lineage(test_context):
    """
    Allure 集成的血缘追踪 fixture

    自动将数据血缘信息附加到 Allure 报告
    """
    yield

    # 测试结束后附加血缘信息
    if hasattr(test_context, '_lineage_tracker') and test_context._lineage_tracker:
        tracker = test_context._lineage_tracker
        LineageAllureAdapter.attach_lineage_graph(tracker)
        LineageAllureAdapter.attach_lineage_analysis(tracker)


@pytest.fixture(scope="function")
def allure_variant(request):
    """
    Allure 集成的变体矩阵 fixture

    自动将变体信息附加到 Allure 报告
    """
    # 从 request 中获取变体信息
    if hasattr(request, 'param'):
        variant_data = request.param
        variant_name = getattr(variant_data, 'name', 'unknown')
        VariantAllureAdapter.attach_variant_info(variant_name,
                                                 variant_data.data if hasattr(variant_data, 'data') else {})

    yield


# 便捷装饰器
def allure_feature(name: str):
    """标记功能模块"""
    return pytest.mark.feature(name)


def allure_story(name: str):
    """标记用户故事"""
    return pytest.mark.story(name)
