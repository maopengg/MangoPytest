# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: API客户端fixtures
# @Time   : 2026-03-31
# @Author : 毛鹏
import pytest
from typing import Generator

from auto_test.demo_project.api_manager import demo_project
from auto_test.demo_project.data_factory import data_factory


@pytest.fixture(scope="session")
def api_client():
    """
    API客户端fixture
    提供统一的API访问入口
    """
    return demo_project


@pytest.fixture(scope="session")
def authenticated_client():
    """
    已认证的API客户端fixture
    自动登录并返回带token的客户端
    """
    # 先登录获取token
    token = data_factory.login()
    if not token:
        pytest.skip("无法获取认证token，跳过测试")
    
    return demo_project


@pytest.fixture(scope="function")
def api_client_with_cleanup():
    """
    带清理功能的API客户端fixture
    每个测试函数结束后清理创建的数据
    """
    yield demo_project
    # 测试结束后清理数据
    data_factory.cleanup_all()
