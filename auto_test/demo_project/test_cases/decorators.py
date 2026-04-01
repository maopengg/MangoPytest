# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: @case_data 装饰器 - 场景变体自动展开
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
@case_data 装饰器模块

提供 pytest 装饰器：@case_data
- 自动展开场景变体为多个测试用例
- 支持单变体、多变体组合
- 自动注入 test_context

使用示例：
    # 单变体测试
    @case_data(scenario=LoginScenario.variant(actor="admin", credential="correct"))
    def test_login_success(self, test_context):
        result = test_context.get("result")
        assert result["success"] is True
    
    # 多变体批量测试（自动生成12条用例）
    @case_data(scenario=LoginScenario.all_variants())
    def test_login_all_combinations(self, test_context):
        result = test_context.get("result")
        expected = result["expected"]
        assert result["success"] == expected["success"]
"""

import pytest
from typing import Any, Dict, List, Optional, Callable, Union
from functools import wraps
import inspect

# 导入项目模块
try:
    from auto_test.demo_project.data_factory.scenarios.base_scenario import BaseScenario
    from auto_test.demo_project.fixtures.infra.context import TestContext
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from data_factory.scenarios.base_scenario import BaseScenario
    from fixtures.infra.context import TestContext


def case_data(
    scenario: Optional[BaseScenario] = None,
    variants: Optional[List[Dict[str, Any]]] = None,
    data: Optional[List[Dict[str, Any]]] = None,
    **kwargs
):
    """
    @case_data 装饰器 - 场景变体自动展开
    
    将场景变体自动展开为多个测试用例，支持以下模式：
    
    模式1：单变体测试
        @case_data(scenario=LoginScenario.variant(actor="admin"))
        def test_login(self, test_context):
            pass
    
    模式2：多变体批量测试
        @case_data(scenario=LoginScenario.all_variants())
        def test_login_all(self, test_context):
            pass
    
    模式3：自定义数据
        @case_data(data=[{"user": "admin"}, {"user": "normal"}])
        def test_users(self, test_context):
            pass
    
    @param scenario: 场景实例或变体列表
    @param variants: 变体列表（替代 scenario）
    @param data: 自定义测试数据
    @param kwargs: 其他参数
    @return: 装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        # 获取测试数据列表
        test_data_list = _get_test_data(scenario, variants, data)
        
        # 使用 pytest.mark.parametrize 展开测试
        if test_data_list:
            # 为每个变体生成测试参数
            parametrize_data = []
            test_ids = []
            
            for i, test_data in enumerate(test_data_list):
                # 生成测试ID
                test_id = _generate_test_id(func.__name__, test_data, i)
                test_ids.append(test_id)
                
                # 准备测试数据
                param_data = {
                    "_case_data": test_data,
                    "_case_index": i,
                    "_case_id": test_id,
                }
                parametrize_data.append(pytest.param(param_data, id=test_id))
            
            # 应用 parametrize
            func = pytest.mark.parametrize(
                "_case_data_wrapper",
                parametrize_data
            )(func)
        
        # 包装函数以注入 test_context
        @wraps(func)
        def wrapper(*args, **func_kwargs):
            # 获取 _case_data_wrapper 参数
            case_wrapper = func_kwargs.pop("_case_data_wrapper", None)
            
            # 创建或获取 test_context
            test_ctx = _get_or_create_test_context(func_kwargs)
            
            # 注入测试数据到 test_context
            if case_wrapper:
                test_data = case_wrapper.get("_case_data", {})
                test_ctx.set("_case_data", test_data)
                test_ctx.set("_case_index", case_wrapper.get("_case_index", 0))
                test_ctx.set("_case_id", case_wrapper.get("_case_id", ""))
                
                # 如果是场景变体，执行场景并存储结果
                if isinstance(test_data, dict) and "scenario_class" in test_data:
                    _execute_scenario(test_ctx, test_data)
                else:
                    # 普通数据，直接存储
                    for key, value in test_data.items():
                        test_ctx.set(key, value)
            
            # 确保 test_context 在 kwargs 中
            if "test_context" not in func_kwargs:
                func_kwargs["test_context"] = test_ctx
            
            # 调用原始函数
            return func(*args, **func_kwargs)
        
        # 复制 pytest 标记
        wrapper.pytestmark = getattr(func, "pytestmark", [])
        
        return wrapper
    
    return decorator


def _get_test_data(
    scenario: Optional[Any],
    variants: Optional[List[Dict[str, Any]]],
    data: Optional[List[Dict[str, Any]]]
) -> List[Dict[str, Any]]:
    """
    获取测试数据列表
    
    @param scenario: 场景实例或变体列表
    @param variants: 变体列表
    @param data: 自定义数据
    @return: 测试数据列表
    """
    # 优先使用 data
    if data:
        return data
    
    # 使用 variants
    if variants:
        return variants
    
    # 使用 scenario
    if scenario:
        # 如果是列表（all_variants 返回的）
        if isinstance(scenario, list):
            return [
                {
                    "variant": variant,
                    "variant_data": variant.values if hasattr(variant, 'values') else variant,
                }
                for variant in scenario
            ]
        
        # 如果是单个变体（variant 返回的）
        if isinstance(scenario, dict):
            return [{"variant": scenario, "variant_data": scenario}]
        
        # 如果是 BaseScenario 实例
        if isinstance(scenario, BaseScenario):
            return [{"scenario_instance": scenario}]
    
    # 默认返回空列表
    return []


def _generate_test_id(func_name: str, test_data: Dict[str, Any], index: int) -> str:
    """
    生成测试ID
    
    @param func_name: 函数名
    @param test_data: 测试数据
    @param index: 索引
    @return: 测试ID
    """
    # 尝试从变体数据生成ID
    if "variant_data" in test_data:
        variant_data = test_data["variant_data"]
        if isinstance(variant_data, dict):
            parts = [f"{k}={v}" for k, v in variant_data.items() if not isinstance(v, (dict, list))]
            if parts:
                return f"{func_name}[{'_'.join(parts)}]"
    
    # 默认使用索引
    return f"{func_name}[{index}]"


def _get_or_create_test_context(func_kwargs: Dict[str, Any]) -> TestContext:
    """
    获取或创建 test_context
    
    @param func_kwargs: 函数关键字参数
    @return: TestContext 实例
    """
    if "test_context" in func_kwargs:
        ctx = func_kwargs["test_context"]
        if isinstance(ctx, TestContext):
            return ctx
    
    # 创建新的 TestContext
    return TestContext(auto_cleanup=True)


def _execute_scenario(test_ctx: TestContext, test_data: Dict[str, Any]):
    """
    执行场景并存储结果
    
    @param test_ctx: 测试上下文
    @param test_data: 测试数据
    """
    scenario_class = test_data.get("scenario_class")
    variant = test_data.get("variant")
    variant_data = test_data.get("variant_data", {})
    
    if scenario_class and issubclass(scenario_class, BaseScenario):
        # 创建场景实例
        scenario = scenario_class()
        
        # 设置变体
        if variant:
            scenario.set_variant(str(variant), variant_data)
        
        # 执行场景
        result = scenario.execute()
        
        # 存储结果
        test_ctx.set("result", {
            "success": result.success,
            "data": result.data,
            "entities": result.entities,
            "expected": result.expected,
            "actual": result.actual,
        })
        
        # 存储实体
        for name, entity in result.entities.items():
            test_ctx.set(name, entity)


# 辅助函数

def scenario_variant(scenario_class: type, **selections) -> Dict[str, Any]:
    """
    获取场景变体（辅助函数）
    
    @param scenario_class: 场景类
    @param selections: 变体选择
    @return: 测试数据字典
    """
    variant_data = scenario_class.variant(**selections)
    return {
        "scenario_class": scenario_class,
        "variant": variant_data,
        "variant_data": variant_data,
    }


def scenario_all_variants(scenario_class: type) -> List[Dict[str, Any]]:
    """
    获取场景所有变体（辅助函数）
    
    @param scenario_class: 场景类
    @return: 测试数据列表
    """
    variants = scenario_class.all_variants()
    return [
        {
            "scenario_class": scenario_class,
            "variant": variant,
            "variant_data": variant.values if hasattr(variant, 'values') else variant,
        }
        for variant in variants
    ]


# 导出
__all__ = [
    "case_data",
    "scenario_variant",
    "scenario_all_variants",
]
