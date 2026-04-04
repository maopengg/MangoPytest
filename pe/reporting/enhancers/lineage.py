# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 血缘图可视化增强器
# @Time   : 2026-04-03
# @Author : 毛鹏

"""
数据血缘图可视化增强器

将数据血缘信息可视化到 Allure 报告，包括：
- 血缘图数据（节点和边）
- 血缘分析统计
- 实体关系可视化

使用示例：
    from pe.reporting.enhancers import LineageEnhancer
    
    # 在测试结束时附加血缘信息
    LineageEnhancer.attach_lineage_graph(tracker)
    LineageEnhancer.attach_lineage_analysis(tracker)
"""

from typing import Any, Dict, Optional, TYPE_CHECKING

from ..adapter import AllureAdapter

if TYPE_CHECKING:
    from auto_test.demo_project.data_factory.lineage.tracker import DataLineageTracker


class LineageEnhancer:
    """血缘图可视化增强器"""

    @staticmethod
    def attach_lineage_graph(tracker: "DataLineageTracker"):
        """附加血缘图数据
        
        Args:
            tracker: 数据血缘追踪器
        """
        if not tracker or not hasattr(tracker, 'graph'):
            return

        graph = tracker.graph
        
        # 构建图数据
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
        """附加血缘分析
        
        Args:
            tracker: 数据血缘追踪器
        """
        if not tracker or not hasattr(tracker, 'analyzer'):
            return

        analyzer = tracker.analyzer
        
        # 收集分析数据
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
        """附加血缘摘要（简化版）
        
        Args:
            tracker: 数据血缘追踪器
        """
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
