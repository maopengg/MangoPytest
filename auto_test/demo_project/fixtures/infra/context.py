# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 测试上下文fixtures
# @Time   : 2026-03-31
# @Author : 毛鹏
import pytest
from typing import Dict, Any, Generator


class TestContext:
    """
    测试上下文类
    用于在测试用例之间传递数据
    """
    
    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.token: str = None
        self.user: Dict[str, Any] = None
    
    def set(self, key: str, value: Any):
        """设置上下文数据"""
        self.data[key] = value
    
    def get(self, key: str, default=None) -> Any:
        """获取上下文数据"""
        return self.data.get(key, default)
    
    def clear(self):
        """清空上下文"""
        self.data.clear()
        self.token = None
        self.user = None


@pytest.fixture(scope="function")
def test_context() -> Generator[TestContext, None, None]:
    """
    测试上下文fixture
    每个测试函数独立的上下文
    """
    context = TestContext()
    yield context
    context.clear()


@pytest.fixture(scope="class")
def class_context() -> Generator[TestContext, None, None]:
    """
    类级别测试上下文fixture
    同一个测试类共享的上下文
    """
    context = TestContext()
    yield context
    context.clear()


@pytest.fixture(scope="module")
def module_context() -> Generator[TestContext, None, None]:
    """
    模块级别测试上下文fixture
    同一个模块共享的上下文
    """
    context = TestContext()
    yield context
    context.clear()
