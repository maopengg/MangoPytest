# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Allure 报告适配器和增强器
# @Time   : 2026-05-03
# @Author : 毛鹏
"""
Allure 报告适配器和增强器

提供：
- Allure 基础适配器：步骤、附件、标签管理
- 血缘增强器：数据血缘可视化
- 矩阵增强器：变体矩阵展示
- 状态机增强器：状态流转图

使用示例：
    from core.testing import AllureAdapter
    
    # 记录步骤
    with AllureAdapter.step("创建用户"):
        user = create_user()
    
    # 附加数据
    AllureAdapter.attach_json("用户信息", user.to_dict())
"""

import json
from functools import wraps
from typing import Any, Dict, Optional, Callable, TYPE_CHECKING

import allure
from allure_commons.types import AttachmentType

if TYPE_CHECKING:
    from auto_tests.pytest_api_mock.data_factory.lineage.tracker import DataLineageTracker
    from auto_tests.pytest_api_mock.data_factory.state_machine.state_machine import StateMachine


class AllureAdapter:
    """Allure 适配器 - 核心功能封装"""

    # ========== 标签管理 ==========

    @staticmethod
    def feature(name: str):
        """标记功能模块"""
        allure.feature(name)

    @staticmethod
    def story(name: str):
        """标记用户故事"""
        allure.story(name)

    @staticmethod
    def title(name: str):
        """设置测试标题"""
        allure.title(name)

    @staticmethod
    def description(text: str):
        """设置测试描述"""
        allure.description(text)

    @staticmethod
    def severity(level: str):
        """设置严重级别

        Args:
            level: blocker, critical, normal, minor, trivial
        """
        allure.severity(getattr(allure.severity_level, level.upper(), allure.severity_level.NORMAL))

    @staticmethod
    def tag(*tags: str):
        """添加标签"""
        for tag in tags:
            allure.tag(tag)

    @staticmethod
    def label(name: str, value: str):
        """添加自定义标签"""
        allure.label(name, value)

    # ========== 步骤管理 ==========

    @staticmethod
    def step(name: str):
        """记录测试步骤

        使用示例：
            with AllureAdapter.step("创建用户"):
                user = UserEntity(username="test")
        """
        return allure.step(name)

    @staticmethod
    def nested_step(name: str):
        """创建嵌套步骤（用于动态步骤）"""
        return allure.step(name)

    # ========== 附件管理 ==========

    @staticmethod
    def attach_json(name: str, data: Dict[str, Any]):
        """附加 JSON 数据"""
        allure.attach(
            json.dumps(data, ensure_ascii=False, indent=2, default=str),
            name=name,
            attachment_type=AttachmentType.JSON
        )

    @staticmethod
    def attach_text(name: str, text: str):
        """附加文本数据"""
        allure.attach(text, name=name, attachment_type=AttachmentType.TEXT)

    @staticmethod
    def attach_html(name: str, html: str):
        """附加 HTML 数据"""
        allure.attach(html, name=name, attachment_type=AttachmentType.HTML)

    @staticmethod
    def attach_image(name: str, image_bytes: bytes):
        """附加图片数据"""
        allure.attach(image_bytes, name=name, attachment_type=AttachmentType.PNG)

    @staticmethod
    def attach_file(filepath: str, name: Optional[str] = None):
        """附加文件"""
        allure.attach.file(filepath, name=name or filepath)

    @staticmethod
    def attach_bytes(name: str, data: bytes, mime_type: str = "application/octet-stream"):
        """附加二进制数据"""
        allure.attach(data, name=name, attachment_type=mime_type)

    # ========== 装饰器 ==========

    @staticmethod
    def step_decorator(name: str):
        """步骤装饰器
        
        使用示例：
            @AllureAdapter.step_decorator("创建用户")
            def create_user():
                return UserEntity()
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                step_name = name.format(*args, **kwargs)
                with AllureAdapter.step(step_name):
                    return func(*args, **kwargs)

            return wrapper

        return decorator


# ========== 增强器 ==========

class LineageEnhancer:
    """血缘图可视化增强器"""

    @staticmethod
    def attach_lineage_graph(tracker: "DataLineageTracker"):
        """附加血缘图数据"""
        if not tracker or not hasattr(tracker, 'graph'):
            return

        graph = tracker.graph

        graph_data = {
            "nodes": [
                {
                    "id": node.id,
                    "type": node.entity_type,
                    "source": node.source,
                    "created_at": node.created_at.isoformat() if node.created_at else None
                }
                for node in graph.nodes.values()
            ],
            "edges": [
                {
                    "from": edge.from_node_id,
                    "to": edge.to_node_id,
                    "relation": edge.relation
                }
                for edge in graph.edges
            ],
            "metadata": {
                "total_nodes": len(graph.nodes),
                "total_edges": len(graph.edges)
            }
        }

        with AllureAdapter.step("数据血缘图"):
            AllureAdapter.attach_json("血缘图数据", graph_data)

    @staticmethod
    def attach_lineage_analysis(tracker: "DataLineageTracker"):
        """附加血缘分析"""
        if not tracker or not hasattr(tracker, 'analyzer'):
            return

        analyzer = tracker.analyzer

        analysis = {
            "total_nodes": len(analyzer.graph.nodes),
            "total_edges": len(analyzer.graph.edges),
            "entity_types": list(set(
                node.entity_type
                for node in analyzer.graph.nodes.values()
            )),
            "sources": list(set(
                node.source
                for node in analyzer.graph.nodes.values()
            )),
            "dependency_chains": analyzer.find_all_chains() if hasattr(analyzer, 'find_all_chains') else []
        }

        with AllureAdapter.step("血缘分析"):
            AllureAdapter.attach_json("血缘分析数据", analysis)

    @staticmethod
    def attach_lineage_summary(tracker: "DataLineageTracker"):
        """附加血缘摘要（简化版）"""
        if not tracker or not hasattr(tracker, 'graph'):
            return

        summary = {
            "实体数量": len(tracker.graph.nodes),
            "依赖关系": len(tracker.graph.edges),
            "实体类型": list(set(
                node.entity_type
                for node in tracker.graph.nodes.values()
            ))
        }

        AllureAdapter.attach_json("血缘摘要", summary)


class MatrixEnhancer:
    """变体矩阵展示增强器"""

    @staticmethod
    def attach_variant_info(variant_name: str, variant_data: Dict[str, Any]):
        """附加变体信息"""
        AllureAdapter.title(f"变体: {variant_name}")

        with AllureAdapter.step(f"变体参数: {variant_name}"):
            AllureAdapter.attach_json("变体参数", variant_data)

    @staticmethod
    def attach_variant_matrix(matrix):
        """附加变体矩阵"""
        if not hasattr(matrix, 'dimensions'):
            return

        matrix_data = {
            "dimensions": [
                {
                    "name": dim.name,
                    "variants": [
                        {
                            "name": v.name,
                            "data": v.data,
                            "order": v.order
                        }
                        for v in dim.variants
                    ]
                }
                for dim in matrix.dimensions
            ],
            "total_combinations": len(matrix.generate()) if hasattr(matrix, 'generate') else 0
        }

        with AllureAdapter.step("变体矩阵"):
            AllureAdapter.attach_json("变体矩阵数据", matrix_data)

    @staticmethod
    def attach_variant_summary(matrix):
        """附加变体摘要（简化版）"""
        if not hasattr(matrix, 'dimensions'):
            return

        summary = {
            "维度数": len(matrix.dimensions),
            "总组合数": len(matrix.generate()) if hasattr(matrix, 'generate') else 0,
            "维度详情": [
                {
                    "名称": dim.name,
                    "变体数": len(dim.variants)
                }
                for dim in matrix.dimensions
            ]
        }

        AllureAdapter.attach_json("变体摘要", summary)


class StateMachineEnhancer:
    """状态流转图增强器"""

    @staticmethod
    def attach_state_transitions(state_machine: "StateMachine"):
        """附加状态转换历史"""
        if not hasattr(state_machine, 'history'):
            return

        transitions = [
            {
                "from_state": t.from_state,
                "to_state": t.to_state,
                "timestamp": t.timestamp.isoformat() if hasattr(t, 'timestamp') and t.timestamp else None,
                "trigger": getattr(t, 'trigger', None),
                "success": getattr(t, 'success', True)
            }
            for t in state_machine.history
        ]

        data = {
            "current_state": state_machine.current_state,
            "transitions": transitions,
            "total_transitions": len(transitions)
        }

        with AllureAdapter.step("状态转换历史"):
            AllureAdapter.attach_json("状态流转", data)

    @staticmethod
    def attach_state_summary(state_machine: "StateMachine"):
        """附加状态摘要"""
        if not hasattr(state_machine, 'history'):
            return

        state_visits: Dict[str, int] = {}
        for t in state_machine.history:
            state_visits[t.to_state] = state_visits.get(t.to_state, 0) + 1

        summary = {
            "当前状态": state_machine.current_state,
            "总转换次数": len(state_machine.history),
            "状态访问统计": state_visits,
            "访问过的状态": list(state_visits.keys())
        }

        AllureAdapter.attach_json("状态摘要", summary)


# 便捷函数
step = AllureAdapter.step
attach_json = AllureAdapter.attach_json
attach_text = AllureAdapter.attach_text
attach_html = AllureAdapter.attach_html
attach_image = AllureAdapter.attach_image
attach_file = AllureAdapter.attach_file

feature = AllureAdapter.feature
story = AllureAdapter.story
title = AllureAdapter.title
description = AllureAdapter.description
severity = AllureAdapter.severity
tag = AllureAdapter.tag
label = AllureAdapter.label
