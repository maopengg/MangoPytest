# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2026-03-31 16:30
# @Author : 毛鹏
import pytest

from auto_test.test_demo.data_factory import ApprovalDataFactory


@pytest.fixture(scope="function")
def data_factory(api_client, db_session):
    """数据工厂fixture，每个测试函数独立"""
    return ApprovalDataFactory(api_client, db_session)


# --- 分层数据fixture，按需使用 ---
@pytest.fixture(scope="function")
def d_data(data_factory):
    """仅提供D模块数据"""
    d_id = data_factory.create_module_d_data()
    return {"d_id": d_id}


@pytest.fixture(scope="function")
def c_data(data_factory, d_data):
    """提供C模块数据，自动依赖D"""
    c_id = data_factory.create_module_c_data(depends_on_d=True, d_overrides={"id": d_data["d_id"]})
    return {"c_id": c_id, "d_id": d_data["d_id"]}


@pytest.fixture(scope="function")
def b_data(data_factory, c_data):
    """提供B模块数据，自动依赖C"""
    b_id = data_factory.create_module_b_data(depends_on_c=True, c_overrides={"id": c_data["c_id"]})
    return {"b_id": b_id, "c_id": c_data["c_id"]}


@pytest.fixture(scope="function")
def a_full_chain_data(data_factory):
    """直接提供完整的A依赖链数据（最常用）"""
    b_id = data_factory.create_module_b_data()  # 内部自动建C和D
    a_data = data_factory.create_module_a_data(b_id=b_id)
    return a_data  # 包含a_id, b_id, c_id, d_id
