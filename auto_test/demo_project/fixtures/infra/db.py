# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据库fixtures
# @Time   : 2026-03-31
# @Author : 毛鹏
import pytest
from typing import Generator


@pytest.fixture(scope="session")
def db_session():
    """
    数据库会话fixture
    用于数据库操作
    """
    # 这里可以根据实际需要连接真实数据库
    # 当前mock_api使用内存数据，此fixture主要用于兼容性
    yield None


@pytest.fixture(scope="function")
def db_transaction():
    """
    数据库事务fixture
    每个测试函数在独立的事务中执行，结束后回滚
    """
    # 对于mock_api，我们使用数据清理代替事务回滚
    yield None


@pytest.fixture(scope="function")
def clean_db_state():
    """
    清理数据库状态fixture
    测试前清理数据，确保测试环境干净
    """
    from auto_test.demo_project.data_factory import data_factory
    
    # 测试前清理
    data_factory.cleanup_all()
    yield
    # 测试后清理
    data_factory.cleanup_all()
