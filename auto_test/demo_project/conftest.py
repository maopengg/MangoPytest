# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: pytest配置文件 - 新架构
# @Time   : 2026-03-31
# @Author : 毛鹏


# 项目级别的pytest配置
def pytest_configure(config):
    """pytest配置钩子"""
    # 添加自定义标记
    config.addinivalue_line(
        "markers", "approval_flow: 标记审批流相关测试"
    )
    config.addinivalue_line(
        "markers", "entity_test: 标记实体相关测试"
    )
    config.addinivalue_line(
        "markers", "scenario_test: 标记场景相关测试"
    )


def pytest_collection_modifyitems(config, items):
    """测试收集完成后的钩子"""
    # 可以在这里对测试项进行排序或过滤
    pass
