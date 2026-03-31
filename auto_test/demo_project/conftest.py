# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: pytest配置文件
# @Time   : 2026-03-31
# @Author : 毛鹏
import pytest
from typing import Dict, Any
from .data_factory.module_factory import ModuleDataFactory


@pytest.fixture(scope="function")
def data_factory():
    """数据工厂fixture - 每个测试函数一个实例"""
    return ModuleDataFactory()


@pytest.fixture(scope="function")
def module_d_data(data_factory):
    """D模块测试数据fixture"""
    data = data_factory.prepare_test_data("module_d")
    yield data
    data_factory.cleanup_test_data("module_d")


@pytest.fixture(scope="function") 
def module_c_data(data_factory):
    """C模块测试数据fixture（自动包含D模块数据）"""
    data = data_factory.prepare_test_data("module_c")
    yield data
    data_factory.cleanup_test_data("module_c")


@pytest.fixture(scope="function")
def module_b_data(data_factory):
    """B模块测试数据fixture（自动包含C、D模块数据）"""
    data = data_factory.prepare_test_data("module_b")
    yield data
    data_factory.cleanup_test_data("module_b")


@pytest.fixture(scope="function")
def module_a_data(data_factory):
    """A模块测试数据fixture（自动包含B、C、D模块数据）"""
    data = data_factory.prepare_test_data("module_a")
    yield data
    data_factory.cleanup_test_data("module_a")


@pytest.fixture(scope="function")
def approval_flow_data(data_factory):
    """完整的审批流数据fixture（包含所有模块数据）"""
    # 创建完整的审批流数据链
    data = data_factory.prepare_test_data("module_a")
    yield data
    data_factory.cleanup_test_data("module_a")


# 参数化fixture，支持不同场景的测试数据
@pytest.fixture(scope="function", params=["small", "medium", "large"])
def approval_flow_with_size(data_factory, request):
    """不同规模的审批流数据"""
    size = request.param
    
    if size == "small":
        custom_data = {"flow_name": "小型审批流", "description": "小型测试审批流"}
    elif size == "medium":
        custom_data = {"flow_name": "中型审批流", "description": "中型测试审批流"}
    else:
        custom_data = {"flow_name": "大型审批流", "description": "大型测试审批流"}
    
    data = data_factory.prepare_test_data("module_a", **custom_data)
    yield data
    data_factory.cleanup_test_data("module_a")