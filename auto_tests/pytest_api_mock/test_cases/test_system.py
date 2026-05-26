# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 系统接口测试用例 - /health, /info
# @Time   : 2026-03-31
# @Author : 毛鹏
import allure
import pytest

from auto_tests.pytest_api_mock.data_factory.builders.system import SystemBuilder
from auto_tests.pytest_api_mock.api_manager import pytest_api_mock
from core.base.layering_base import UnitTest, IntegrationTest
from core.exceptions import ApiError

@allure.epic('演示-pytest_api_mock')
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

    @allure.title("健康检查-缺少自定义头")
    def test_health_check_missing_custom_header(self, test_token):
        """覆盖 TC-SYS-0002。"""
        pytest_api_mock.set_token(test_token)
        with pytest.raises(ApiError) as exc_info:
            pytest_api_mock.system.health_check(with_custom_headers=False)

        assert exc_info.value.code == 403

    @allure.title("健康检查-自定义密钥错误")
    def test_health_check_invalid_custom_key(self, test_token):
        """覆盖 TC-SYS-0003。"""
        pytest_api_mock.set_token(test_token)
        with pytest.raises(ApiError) as exc_info:
            pytest_api_mock.system.health_check(
                headers={
                    "X-Custom-Key": "wrong_key",
                    "X-Request-Source": "pytest_api_mock",
                },
                with_custom_headers=False,
            )

        assert exc_info.value.code == 403


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

    @allure.title("服务器信息-缺少自定义头")
    def test_server_info_missing_custom_header(self, test_token):
        """覆盖 TC-SYS-0007。"""
        pytest_api_mock.set_token(test_token)
        with pytest.raises(ApiError) as exc_info:
            pytest_api_mock.system.get_server_info(with_custom_headers=False)

        assert exc_info.value.code == 403


@allure.feature("系统管理")
@allure.story("初始化和首页")
class TestStartupAndHome(UnitTest):
    """初始化数据和首页接口测试"""

    @allure.title("初始化数据成功")
    def test_startup_success(self):
        """覆盖 TC-SYS-0005。"""
        result = pytest_api_mock.system.startup()

        assert result.get("code") == 200
        assert "message" in result.get("data", {})

    @allure.title("访问首页成功")
    def test_home_success(self):
        """覆盖 TC-SYS-0006。"""
        response = pytest_api_mock.system.home()

        assert response.status_code == 200
        assert "芒果mock服务" in str(response.data)

    @allure.title("重复初始化数据")
    def test_startup_repeat(self):
        """覆盖 TC-SYS-0008。"""
        first = pytest_api_mock.system.startup()
        second = pytest_api_mock.system.startup()

        assert first.get("code") == 200
        assert second.get("code") == 200


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
