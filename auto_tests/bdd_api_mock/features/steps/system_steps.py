# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 系统管理模块 BDD 步骤定义
# @Time   : 2026-04-17
# @Author : 毛鹏
"""
系统管理模块步骤定义
"""

import pytest
from pytest_bdd import given, when, then, parsers
from pytest_bdd.parsers import parse

from auto_tests.bdd_api_mock.data_factory.builders.system import SystemBuilder


# ==================== When 步骤 ====================


@when("用户执行健康检查", target_fixture="health_result")
def user_health_check(authenticated_user):
    """用户执行健康检查"""
    token = authenticated_user["token"]
    system_builder = SystemBuilder(token=token)
    result = system_builder.health_check()
    return result


@when(
    parsers.parse("用户连续执行 {count:d} 次健康检查"), target_fixture="health_results"
)
def user_multiple_health_checks(authenticated_user, count):
    """用户连续执行多次健康检查"""
    token = authenticated_user["token"]
    system_builder = SystemBuilder(token=token)
    results = []

    for _ in range(count):
        result = system_builder.health_check()
        results.append(result)

    return results


@when("用户获取服务器信息", target_fixture="server_info")
def user_get_server_info(authenticated_user):
    """用户获取服务器信息"""
    token = authenticated_user["token"]
    system_builder = SystemBuilder(token=token)
    result = system_builder.get_server_info()
    return result


# ==================== Then 步骤 ====================


@then("健康检查应该成功")
def verify_health_check_success(health_result):
    """验证健康检查成功"""
    assert health_result is not None
    assert health_result.get("status") == "healthy"


@then(parsers.parse('系统状态应该是 "{status}"'))
def verify_system_status(health_result, status):
    """验证系统状态"""
    assert health_result.get("status") == status


@then("返回结果应该包含时间戳")
def verify_health_check_has_timestamp(health_result):
    """验证健康检查结果包含时间戳"""
    assert "timestamp" in health_result


@then("所有健康检查都应该成功")
def verify_all_health_checks_success(health_results):
    """验证所有健康检查都成功"""
    for result in health_results:
        assert result is not None
        assert result.get("status") == "healthy"


@then(parsers.parse('每次检查的系统状态都应该是 "{status}"'))
def verify_all_health_check_status(health_results, status):
    """验证每次检查的系统状态"""
    for result in health_results:
        assert result.get("status") == status


@then("应该成功返回服务器信息")
def verify_server_info_returned(server_info):
    """验证成功返回服务器信息"""
    assert server_info is not None


@then(parsers.parse('服务器信息应该包含应用名称 "{app_name}"'))
def verify_server_info_app_name(server_info, app_name):
    """验证服务器信息包含应用名称"""
    assert server_info.get("app_name") == app_name


@then(parsers.parse('服务器信息应该包含版本 "{version}"'))
def verify_server_info_version(server_info, version):
    """验证服务器信息包含版本"""
    assert server_info.get("version") == version


@then(parsers.parse('服务器信息应该包含框架 "{framework}"'))
def verify_server_info_framework(server_info, framework):
    """验证服务器信息包含框架"""
    assert server_info.get("framework") == framework


@then("服务器信息应该包含Python版本")
def verify_server_info_python_version(server_info):
    """验证服务器信息包含Python版本"""
    assert "python_version" in server_info
    assert server_info.get("python_version") is not None


@then("服务器信息应该包含以下字段:", target_fixture="required_fields")
def verify_server_info_has_fields(server_info, table):
    """验证服务器信息包含指定字段"""
    fields = [row["field"] for row in table]
    for field in fields:
        assert field in server_info
    return fields


@then("所有字段都应该有值")
def verify_all_fields_have_values(server_info, required_fields):
    """验证所有字段都有值"""
    for field in required_fields:
        assert server_info.get(field) is not None


@then("应用应该正常运行")
def verify_app_running_normally(health_result, server_info):
    """验证应用正常运行"""
    assert health_result.get("status") == "healthy"
    assert server_info.get("app_name") == "Mock API Service"
