# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 系统接口测试用例 - /health, /info
# @Time   : 2026-03-31
# @Author : 毛鹏
import allure

from auto_test.demo_project.data_factory.builders.system import SystemBuilder
from auto_test.demo_project.test_cases.base import UnitTest, IntegrationTest


@allure.feature("系统管理")
@allure.story("健康检查")
class TestHealthCheck(UnitTest):
    """健康检查接口测试"""

    @allure.title("健康检查-正常")
    def test_health_check_success(self, test_token):
        """测试健康检查接口"""
        system_builder = SystemBuilder(token=test_token)
        result = system_builder.health_check()

        assert result is not None
        assert result.get("status") == "healthy"
        assert "timestamp" in result

    @allure.title("健康检查-使用fixture")
    def test_health_check_with_fixture(self, server_health):
        """测试使用fixture的健康检查"""
        assert server_health is not None
        assert server_health.get("status") == "healthy"
        assert "timestamp" in server_health

    @allure.title("健康检查-多次调用")
    def test_health_check_multiple_calls(self, test_token):
        """测试多次调用健康检查"""
        system_builder = SystemBuilder(token=test_token)

        # 多次调用应该都返回正常
        for _ in range(5):
            result = system_builder.health_check()
            assert result is not None
            assert result.get("status") == "healthy"


@allure.feature("系统管理")
@allure.story("服务器信息")
class TestServerInfo(UnitTest):
    """服务器信息接口测试"""

    @allure.title("获取服务器信息")
    def test_get_server_info(self, test_token):
        """测试获取服务器信息接口"""
        system_builder = SystemBuilder(token=test_token)
        result = system_builder.get_server_info()

        assert result is not None
        assert result.get("app_name") == "Mock API Service"
        assert result.get("version") == "2.0.0"
        assert result.get("framework") == "FastAPI"
        assert "python_version" in result

    @allure.title("获取服务器信息-使用fixture")
    def test_get_server_info_with_fixture(self, server_info):
        """测试使用fixture获取服务器信息"""
        assert server_info is not None
        assert server_info.get("app_name") == "Mock API Service"
        assert server_info.get("version") == "2.0.0"
        assert server_info.get("framework") == "FastAPI"

    @allure.title("获取服务器信息-字段完整性")
    def test_server_info_fields(self, test_token):
        """测试服务器信息字段完整性"""
        system_builder = SystemBuilder(token=test_token)
        result = system_builder.get_server_info()

        # 验证所有必需字段
        required_fields = ["app_name", "version", "framework", "python_version"]
        for field in required_fields:
            assert field in result
            assert result[field] is not None


@allure.feature("系统管理")
@allure.story("综合系统测试")
class TestSystemIntegration(IntegrationTest):
    """系统接口综合测试"""

    @allure.title("系统接口-完整流程")
    def test_system_full_flow(self, test_token):
        """测试系统接口完整流程"""
        system_builder = SystemBuilder(token=test_token)

        # 1. 检查健康状态
        health = system_builder.health_check()
        assert health is not None
        assert health.get("status") == "healthy"

        # 2. 获取服务器信息
        info = system_builder.get_server_info()
        assert info is not None
        assert info.get("app_name") == "Mock API Service"

        # 3. 再次检查健康状态
        health2 = system_builder.health_check()
        assert health2 is not None
        assert health2.get("status") == "healthy"

    @allure.title("系统接口-使用数据工厂builder")
    def test_system_with_builder(self, test_token):
        """测试使用数据工厂builder访问系统接口"""
        # 直接使用数据工厂创建builder
        system_builder = SystemBuilder(token=test_token)

        # 验证builder可以正常工作
        health = system_builder.health_check()
        info = system_builder.get_server_info()

        assert health is not None
        assert info is not None
        assert health.get("status") == "healthy"
        assert info.get("app_name") == "Mock API Service"

    @allure.title("系统接口-并发调用")
    def test_system_concurrent_calls(self, test_token):
        """测试系统接口并发调用"""
        import concurrent.futures

        system_builder = SystemBuilder(token=test_token)

        def check_health():
            return system_builder.health_check()

        def get_info():
            return system_builder.get_server_info()

        # 并发调用
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for _ in range(5):
                futures.append(executor.submit(check_health))
                futures.append(executor.submit(get_info))

            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # 验证所有调用都成功
        assert len(results) == 10
        for result in results:
            assert result is not None
