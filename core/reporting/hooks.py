# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: pytest 钩子集成
# @Time   : 2026-04-03
# @Author : 毛鹏

"""
pytest 钩子集成

自动收集测试信息并记录到 Allure 报告，包括：
- 测试标题和描述（从 docstring 提取）
- 功能模块和用户故事（从 marker 提取）
- 测试执行时间线
- 测试状态

使用示例：
    # 在 conftest.py 中导入以自动启用
    from pe.reporting.hooks import pytest_configure
    
    # 或者使用装饰器
    from pe.reporting.hooks import allure_feature, allure_story
    
    @allure_feature("用户管理")
    @allure_story("用户创建")
    def test_create_user():
        pass
"""

import pytest

import allure

from .adapter import AllureAdapter


class AllureHooksPlugin:
    """Allure pytest 钩子插件"""

    def __init__(self):
        self.current_test = None
        self.test_start_time = None

    def pytest_runtest_setup(self, item):
        """测试开始前"""
        self.current_test = item
        import time
        self.test_start_time = time.time()

        # 从测试函数的 docstring 提取信息
        if item.function.__doc__:
            doc = item.function.__doc__.strip()
            lines = doc.split('\n')

            # 第一行作为标题
            if lines:
                AllureAdapter.title(lines[0])

            # 其余行作为描述
            if len(lines) > 1:
                description = '\n'.join(lines[1:]).strip()
                AllureAdapter.description(description)

        # 从 pytest marker 提取 feature/story/severity/tag
        # 使用 allure.label 直接设置标签
        feature_marker = item.get_closest_marker('feature')
        if feature_marker:
            allure.label('feature', feature_marker.args[0])

        story_marker = item.get_closest_marker('story')
        if story_marker:
            allure.label('story', story_marker.args[0])

        # 提取 severity
        severity_marker = item.get_closest_marker('severity')
        if severity_marker:
            allure.severity(
                getattr(allure.severity_level, severity_marker.args[0].upper(), allure.severity_level.NORMAL))

        # 提取 tags
        tag_marker = item.get_closest_marker('tag')
        if tag_marker:
            for tag in tag_marker.args:
                allure.label('tag', tag)

    def pytest_runtest_teardown(self, item):
        """测试结束后"""
        # 可以在这里记录测试执行时间等额外信息
        if self.test_start_time:
            import time
            duration = time.time() - self.test_start_time
            AllureAdapter.attach_text(
                "测试执行时间",
                f"{duration:.3f} 秒"
            )

    def pytest_runtest_makereport(self, item, call):
        """生成测试报告时"""
        # 在测试失败时附加额外信息
        if call.when == "call" and call.excinfo is not None:
            # 附加异常信息
            exc_type = call.excinfo.type.__name__
            exc_value = str(call.excinfo.value)
            AllureAdapter.attach_text(
                "异常信息",
                f"类型: {exc_type}\n信息: {exc_value}"
            )


# 创建插件实例
allure_hooks_plugin = AllureHooksPlugin()


def pytest_configure(config):
    """pytest 配置钩子
    
    在 conftest.py 中导入此函数以自动启用 Allure 钩子
    """
    config.pluginmanager.register(allure_hooks_plugin)

    # 添加自定义 marker
    config.addinivalue_line(
        "markers", "feature(name): 标记功能模块 (Allure)"
    )
    config.addinivalue_line(
        "markers", "story(name): 标记用户故事 (Allure)"
    )
    config.addinivalue_line(
        "markers", "severity(level): 设置严重级别 blocker/critical/normal/minor/trivial (Allure)"
    )
    config.addinivalue_line(
        "markers", "tag(name): 添加标签 (Allure)"
    )


# ========== 便捷装饰器 ==========

def allure_feature(name: str):
    """标记功能模块
    
    使用示例：
        @allure_feature("用户管理")
        def test_create_user():
            pass
    """
    return pytest.mark.feature(name)


def allure_story(name: str):
    """标记用户故事
    
    使用示例：
        @allure_story("用户创建")
        def test_create_user():
            pass
    """
    return pytest.mark.story(name)


def allure_severity(level: str):
    """设置严重级别
    
    Args:
        level: blocker, critical, normal, minor, trivial
        
    使用示例：
        @allure_severity("critical")
        def test_critical_feature():
            pass
    """
    return pytest.mark.severity(level)


def allure_tag(*tags: str):
    """添加标签
    
    使用示例：
        @allure_tag("smoke", "regression")
        def test_example():
            pass
    """
    return pytest.mark.tag(*tags)


def allure_label(name: str, value: str):
    """添加自定义标签
    
    使用示例：
        @allure_label("component", "backend")
        def test_api():
            pass
    """
    return pytest.mark.label(name, value)
