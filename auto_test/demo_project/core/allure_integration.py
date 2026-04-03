# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: Allure 集成 - 将架构功能可视化到报告
# @Time   : 2026-04-03
# @Author : 毛鹏

"""
Allure 集成模块

将以下功能可视化到 Allure 报告：
1. Context 操作（create/use/action/expect/event）
2. 数据血缘追踪（lineage graph）
3. 场景变体信息（variant matrix）
4. 状态机流转（state transitions）
5. 构造器依赖链（builder dependencies）
"""

import json
from typing import Any, Dict, Optional, List
from datetime import datetime

try:
    import allure
    HAS_ALLURE = True
except ImportError:
    HAS_ALLURE = False


class AllureHelper:
    """Allure 辅助类 - 简化集成"""

    @staticmethod
    def feature(name: str):
        """标记功能模块"""
        if HAS_ALLURE:
            allure.feature(name)

    @staticmethod
    def story(name: str):
        """标记用户故事"""
        if HAS_ALLURE:
            allure.story(name)

    @staticmethod
    def title(name: str):
        """设置测试标题"""
        if HAS_ALLURE:
            allure.title(name)

    @staticmethod
    def description(text: str):
        """设置测试描述"""
        if HAS_ALLURE:
            allure.description(text)

    @staticmethod
    def step(name: str, *args, **kwargs):
        """记录测试步骤"""
        if HAS_ALLURE:
            return allure.step(name)
        else:
            # 返回空上下文管理器
            class NullContext:
                def __enter__(self):
                    return self
                def __exit__(self, *args):
                    pass
            return NullContext()

    @staticmethod
    def attach_json(name: str, data: Dict[str, Any]):
        """附加 JSON 数据"""
        if HAS_ALLURE:
            allure.attach(
                json.dumps(data, ensure_ascii=False, indent=2),
                name=name,
                attachment_type=allure.attachment_type.JSON
            )

    @staticmethod
    def attach_text(name: str, text: str):
        """附加文本数据"""
        if HAS_ALLURE:
            allure.attach(text, name=name, attachment_type=allure.attachment_type.TEXT)

    @staticmethod
    def attach_html(name: str, html: str):
        """附加 HTML 数据"""
        if HAS_ALLURE:
            allure.attach(html, name=name, attachment_type=allure.attachment_type.HTML)


class ContextAllureAdapter:
    """Context 与 Allure 的适配器"""

    def __init__(self, context):
        self.context = context
        self.operations: List[Dict] = []

    def record_create(self, entity_type: str, entity_id: str, **kwargs):
        """记录创建操作"""
        op = {
            "type": "create",
            "entity_type": entity_type,
            "entity_id": entity_id,
            "timestamp": datetime.now().isoformat(),
            "data": kwargs
        }
        self.operations.append(op)

        with AllureHelper.step(f"创建 {entity_type} (ID: {entity_id})"):
            AllureHelper.attach_json(
                f"{entity_type}_{entity_id}",
                {"entity_type": entity_type, "entity_id": entity_id, **kwargs}
            )

    def record_use(self, entity_type: str, entity_id: str, **filters):
        """记录复用操作"""
        op = {
            "type": "use",
            "entity_type": entity_type,
            "entity_id": entity_id,
            "timestamp": datetime.now().isoformat(),
            "filters": filters
        }
        self.operations.append(op)

        with AllureHelper.step(f"复用 {entity_type} (ID: {entity_id})"):
            AllureHelper.attach_json(
                f"use_{entity_type}_{entity_id}",
                {"entity_type": entity_type, "entity_id": entity_id, "filters": filters}
            )

    def record_action(self, action_name: str, target_entity: str, result: Any):
        """记录业务动作"""
        op = {
            "type": "action",
            "action_name": action_name,
            "target_entity": target_entity,
            "timestamp": datetime.now().isoformat(),
            "result": str(result)
        }
        self.operations.append(op)

        with AllureHelper.step(f"执行动作: {action_name}"):
            AllureHelper.attach_text(
                f"action_{action_name}",
                f"目标实体: {target_entity}\n结果: {result}"
            )

    def record_expect(self, condition: str, result: bool):
        """记录预期验证"""
        op = {
            "type": "expect",
            "condition": condition,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        self.operations.append(op)

        status = "✅ 通过" if result else "❌ 失败"
        with AllureHelper.step(f"验证预期: {condition} {status}"):
            pass

    def record_event(self, event_name: str, priority: str, fired: bool):
        """记录事件触发"""
        op = {
            "type": "event",
            "event_name": event_name,
            "priority": priority,
            "fired": fired,
            "timestamp": datetime.now().isoformat()
        }
        self.operations.append(op)

        status = "✅ 已触发" if fired else "❌ 未触发"
        with AllureHelper.step(f"事件: {event_name} ({priority}) {status}"):
            pass

    def attach_summary(self):
        """附加操作摘要"""
        summary = {
            "total_operations": len(self.operations),
            "create_count": len([op for op in self.operations if op["type"] == "create"]),
            "use_count": len([op for op in self.operations if op["type"] == "use"]),
            "action_count": len([op for op in self.operations if op["type"] == "action"]),
            "expect_count": len([op for op in self.operations if op["type"] == "expect"]),
            "event_count": len([op for op in self.operations if op["type"] == "event"]),
            "operations": self.operations
        }
        AllureHelper.attach_json("Context 操作摘要", summary)


class LineageAllureAdapter:
    """血缘追踪与 Allure 的适配器"""

    @staticmethod
    def attach_lineage_graph(tracker):
        """附加血缘图"""
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
            ]
        }

        AllureHelper.attach_json("数据血缘图", graph_data)

    @staticmethod
    def attach_lineage_analysis(tracker):
        """附加血缘分析"""
        if not tracker or not hasattr(tracker, 'analyzer'):
            return

        analyzer = tracker.analyzer
        analysis = {
            "total_nodes": len(analyzer.graph.nodes),
            "total_edges": len(analyzer.graph.edges),
            "entity_types": list(set(node.entity_type for node in analyzer.graph.nodes.values())),
            "sources": list(set(node.source for node in analyzer.graph.nodes.values()))
        }

        AllureHelper.attach_json("血缘分析", analysis)


class VariantAllureAdapter:
    """变体矩阵与 Allure 的适配器"""

    @staticmethod
    def attach_variant_info(variant_name: str, variant_data: Dict[str, Any]):
        """附加变体信息"""
        AllureHelper.title(f"变体: {variant_name}")
        AllureHelper.attach_json("变体参数", variant_data)

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

        AllureHelper.attach_json("变体矩阵", matrix_data)


class StateMachineAllureAdapter:
    """状态机与 Allure 的适配器"""

    @staticmethod
    def attach_state_transitions(state_machine):
        """附加状态转换历史"""
        if not hasattr(state_machine, 'history'):
            return

        transitions = [
            {
                "from_state": t.from_state,
                "to_state": t.to_state,
                "timestamp": t.timestamp.isoformat() if hasattr(t, 'timestamp') else None,
                "trigger": getattr(t, 'trigger', None)
            }
            for t in state_machine.history
        ]

        AllureHelper.attach_json("状态转换历史", {
            "current_state": state_machine.current_state,
            "transitions": transitions
        })


class BuilderAllureAdapter:
    """构造器与 Allure 的适配器"""

    @staticmethod
    def attach_builder_dependencies(builder):
        """附加构造器依赖链"""
        if not hasattr(builder, 'dependencies'):
            return

        deps = {
            "builder_name": builder.__class__.__name__,
            "dependencies": builder.dependencies if isinstance(builder.dependencies, list) else [],
            "created_entities": getattr(builder, 'created_entities', [])
        }

        AllureHelper.attach_json("构造器依赖链", deps)


# 便捷函数
def allure_step(name: str):
    """便捷步骤记录"""
    return AllureHelper.step(name)


def allure_attach_json(name: str, data: Dict[str, Any]):
    """便捷 JSON 附加"""
    AllureHelper.attach_json(name, data)


def allure_attach_text(name: str, text: str):
    """便捷文本附加"""
    AllureHelper.attach_text(name, text)
