# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: API客户端fixtures - 新架构
# @Time   : 2026-03-31
# @Author : 毛鹏
import pytest

from auto_tests.demo_project.api_manager import demo_project


@pytest.fixture(scope="session")
def api_client():
    """
    API客户端fixture
    提供统一的API访问入口
    """
    return demo_project


@pytest.fixture(scope="session")
def authenticated_client(api_client):
    """
    已认证的API客户端fixture
    自动登录并返回带token的客户端
    """
    from auto_tests.demo_project.api_manager import demo_project


    result = demo_project.auth.api_login(username="testuser", password="password123")

    if result.get("code") != 200:
        pytest.skip(f"无法获取认证token，跳过测试: {result.get('message')}")

    # 设置token到全局
    token = result["data"]["token"]
    api_client.token = token
    demo_project.token = token
    # 设置全局 token，所有 API 请求会自动添加 Authorization header
    from auto_tests.demo_project.api_manager import DemoProjectBaseAPI
    DemoProjectBaseAPI.set_token(token)
    return api_client


@pytest.fixture(scope="function")
def api_client_with_cleanup():
    """
    带清理功能的API客户端fixture
    每个测试函数结束后清理创建的数据
    """
    created_builders = []

    yield demo_project

    # 测试结束后清理所有builder创建的数据
    for builder in reversed(created_builders):
        if hasattr(builder, "cleanup"):
            builder.cleanup()
