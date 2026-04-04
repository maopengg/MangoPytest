# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据血缘分析器
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
数据血缘分析器模块

提供高级分析功能：
- 影响分析：修改某数据会影响哪些下游数据
- 溯源分析：数据从哪里来，经过哪些转换
- 质量分析：数据质量问题的传播路径
- 合规分析：敏感数据的流向
- 可视化导出：生成Graphviz/Mermaid格式

注意：枚举已从 enums.demo_enum 导入
"""

from collections import defaultdict
from typing import Dict, List, Optional, Any

from .node import DataLineageNode, LineageEdge, LineageRelation, LineagePath
from .graph import DataLineageGraph

# 从统一的枚举文件导入
from enums.demo_enum import ImpactLevel


class LineageAnalyzer:
    """
    血缘分析器
    
    提供对血缘图的深度分析能力，包括影响分析、溯源分析等。
    
    Attributes:
        graph: 血缘图实例
    """

    def __init__(self, graph: DataLineageGraph):
        self.graph = graph

    def analyze_impact(
            self,
            entity_type: str,
            entity_id: str,
            max_depth: int = 10
    ) -> Dict[str, Any]:
        """
        影响分析 - 分析修改某数据会影响哪些下游数据
        
        Args:
            entity_type: 实体类型
            entity_id: 实体ID
            max_depth: 最大分析深度
        
        Returns:
            Dict[str, Any]: 影响分析结果
        """
        node = self.graph.get_node_by_entity(entity_type, entity_id)
        if not node:
            return {"error": f"Entity not found: {entity_type}:{entity_id}"}

        # 获取所有下游节点
        downstream = self.graph.get_downstream_nodes(node.node_id, max_depth)

        # 按类型分组
        by_type = defaultdict(list)
        for n in downstream:
            by_type[n.entity_type].append({
                "id": n.entity_id,
                "source": n.source,
                "lifecycle": n.lifecycle
            })

        # 计算影响级别
        impact_level = self._calculate_impact_level(len(downstream), by_type)

        # 找出关键路径
        critical_paths = self._find_critical_paths(node.node_id, downstream)

        return {
            "entity": {
                "type": entity_type,
                "id": entity_id,
                "source": node.source
            },
            "impact_level": impact_level.name,
            "total_downstream": len(downstream),
            "downstream_by_type": dict(by_type),
            "critical_paths": critical_paths,
            "recommendation": self._generate_recommendation(impact_level, downstream)
        }

    def trace_lineage(
            self,
            entity_type: str,
            entity_id: str,
            direction: str = "both",
            max_depth: int = 10
    ) -> Dict[str, Any]:
        """
        血缘溯源 - 追溯数据的完整来源和去向
        
        Args:
            entity_type: 实体类型
            entity_id: 实体ID
            direction: 方向（upstream/downstream/both）
            max_depth: 最大深度
        
        Returns:
            Dict[str, Any]: 溯源结果
        """
        node = self.graph.get_node_by_entity(entity_type, entity_id)
        if not node:
            return {"error": f"Entity not found: {entity_type}:{entity_id}"}

        result = {
            "entity": node.to_dict(),
            "direction": direction,
            "max_depth": max_depth
        }

        if direction in ("upstream", "both"):
            upstream = self.graph.get_upstream_nodes(node.node_id, max_depth)
            result["upstream"] = {
                "count": len(upstream),
                "entities": [n.to_dict() for n in upstream],
                "root_sources": self._find_root_sources(node.node_id, upstream)
            }

        if direction in ("downstream", "both"):
            downstream = self.graph.get_downstream_nodes(node.node_id, max_depth)
            result["downstream"] = {
                "count": len(downstream),
                "entities": [n.to_dict() for n in downstream],
                "end_consumers": self._find_end_consumers(node.node_id, downstream)
            }

        return result

    def analyze_data_quality(
            self,
            entity_type: str,
            entity_id: str,
            quality_issues: List[str]
    ) -> Dict[str, Any]:
        """
        数据质量分析 - 分析质量问题的影响范围
        
        Args:
            entity_type: 实体类型
            entity_id: 实体ID
            quality_issues: 质量问题列表
        
        Returns:
            Dict[str, Any]: 质量分析结果
        """
        node = self.graph.get_node_by_entity(entity_type, entity_id)
        if not node:
            return {"error": f"Entity not found: {entity_type}:{entity_id}"}

        # 获取下游影响
        downstream = self.graph.get_downstream_nodes(node.node_id)

        # 分析传播路径
        propagation_paths = []
        for target in downstream:
            path = self.graph.find_path(node.node_id, target.node_id)
            if path:
                propagation_paths.append({
                    "target": f"{target.entity_type}:{target.entity_id}",
                    "path_length": len(path),
                    "nodes": [n.entity_type for n in path.nodes]
                })

        # 按路径长度排序
        propagation_paths.sort(key=lambda x: x["path_length"], reverse=True)

        return {
            "source_entity": f"{entity_type}:{entity_id}",
            "quality_issues": quality_issues,
            "affected_entities_count": len(downstream),
            "propagation_risk": "high" if len(downstream) > 10 else "medium" if len(downstream) > 3 else "low",
            "propagation_paths": propagation_paths[:10],  # 只显示前10条
            "recommendation": f"建议优先修复影响 {len(downstream)} 个下游实体的数据质量问题"
        }

    def analyze_compliance(
            self,
            sensitive_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        合规分析 - 分析敏感数据的流向
        
        Args:
            sensitive_types: 敏感数据类型列表
        
        Returns:
            Dict[str, Any]: 合规分析结果
        """
        if sensitive_types is None:
            sensitive_types = ["user", "payment", "personal_info"]

        findings = []

        for node in self.graph.nodes.values():
            if node.entity_type in sensitive_types:
                downstream = self.graph.get_downstream_nodes(node.node_id)

                # 检查是否有不合规的流向
                external_consumers = [
                    n for n in downstream
                    if n.source not in ("internal", "api", "database")
                ]

                if external_consumers:
                    findings.append({
                        "sensitive_entity": f"{node.entity_type}:{node.entity_id}",
                        "external_consumers": [
                            f"{n.entity_type}:{n.entity_id}"
                            for n in external_consumers
                        ],
                        "risk_level": "high" if len(external_consumers) > 3 else "medium"
                    })

        return {
            "sensitive_types_checked": sensitive_types,
            "total_findings": len(findings),
            "findings": findings,
            "compliance_status": "pass" if not findings else "review_required"
        }

    def find_orphaned_data(self) -> List[Dict[str, Any]]:
        """
        查找孤立数据 - 没有上游来源的数据
        
        Returns:
            List[Dict[str, Any]]: 孤立数据列表
        """
        orphaned = []

        for node in self.graph.nodes.values():
            # 检查是否有上游
            upstream = self.graph.get_upstream_nodes(node.node_id, max_depth=1)

            if not upstream and node.node_type.name == "ENTITY":
                orphaned.append({
                    "type": node.entity_type,
                    "id": node.entity_id,
                    "source": node.source,
                    "created_at": node.created_at.isoformat()
                })

        return orphaned

    def find_hotspots(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        查找热点数据 - 被大量依赖的数据
        
        Args:
            top_n: 返回前N个
        
        Returns:
            List[Dict[str, Any]]: 热点数据列表
        """
        hotspots = []

        for node in self.graph.nodes.values():
            downstream_count = len(
                self.graph.get_downstream_nodes(node.node_id, max_depth=1)
            )

            if downstream_count > 0:
                hotspots.append({
                    "type": node.entity_type,
                    "id": node.entity_id,
                    "downstream_count": downstream_count,
                    "centrality": "high" if downstream_count > 10 else "medium"
                })

        # 按下游数量排序
        hotspots.sort(key=lambda x: x["downstream_count"], reverse=True)

        return hotspots[:top_n]

    def generate_mermaid(self, highlight_entity: Optional[str] = None) -> str:
        """
        生成Mermaid流程图
        
        Args:
            highlight_entity: 高亮显示的实体
        
        Returns:
            str: Mermaid图表代码
        """
        lines = ["graph TD"]

        # 添加节点
        for node in self.graph.nodes.values():
            node_label = f"{node.entity_type}:{node.entity_id}"

            # 根据类型设置样式
            if node.node_type.name == "ENTITY":
                style = f'["{node_label}"]'
            elif node.node_type.name == "API_CALL":
                style = f'{{"{node_label}"}}'
            else:
                style = f'["{node_label}"]'

            # 高亮处理
            if highlight_entity and highlight_entity in node_label:
                lines.append(f"    {node.node_id}{style}")
                lines.append(f"    style {node.node_id} fill:#ff6b6b")
            else:
                lines.append(f"    {node.node_id}{style}")

        # 添加边
        for edge in self.graph.edges.values():
            relation_label = edge.relation.value
            lines.append(f"    {edge.source_id} -->|{relation_label}| {edge.target_id}")

        return "\n".join(lines)

    def generate_graphviz(self, highlight_entity: Optional[str] = None) -> str:
        """
        生成Graphviz DOT格式
        
        Args:
            highlight_entity: 高亮显示的实体
        
        Returns:
            str: DOT格式代码
        """
        lines = [
            "digraph DataLineage {",
            '    rankdir=TB;',
            '    node [shape=box, style=filled, fillcolor=lightblue];',
            '    edge [color=gray];',
            ""
        ]

        # 添加节点
        for node in self.graph.nodes.values():
            node_label = f"{node.entity_type}\\n{node.entity_id}"

            # 根据类型设置颜色
            if node.node_type.name == "ENTITY":
                fillcolor = "lightblue"
            elif node.node_type.name == "API_CALL":
                fillcolor = "lightgreen"
            elif node.node_type.name == "DATABASE":
                fillcolor = "lightyellow"
            else:
                fillcolor = "lightgray"

            # 高亮处理
            if highlight_entity and highlight_entity in f"{node.entity_type}:{node.entity_id}":
                fillcolor = "red"

            lines.append(f'    "{node.node_id}" [label="{node_label}", fillcolor={fillcolor}];')

        lines.append("")

        # 添加边
        for edge in self.graph.edges.values():
            lines.append(f'    "{edge.source_id}" -> "{edge.target_id}" [label="{edge.relation.value}"];')

        lines.append("}")

        return "\n".join(lines)

    def _calculate_impact_level(
            self,
            downstream_count: int,
            by_type: Dict[str, List]
    ) -> ImpactLevel:
        """计算影响级别"""
        if downstream_count == 0:
            return ImpactLevel.LOW
        elif downstream_count > 20 or "payment" in by_type or "order" in by_type:
            return ImpactLevel.CRITICAL
        elif downstream_count > 5:
            return ImpactLevel.HIGH
        else:
            return ImpactLevel.MEDIUM

    def _find_critical_paths(
            self,
            source_id: str,
            downstream_nodes: List[DataLineageNode]
    ) -> List[Dict[str, Any]]:
        """查找关键路径"""
        paths = []

        # 找出最长的路径
        for target in downstream_nodes:
            path = self.graph.find_path(source_id, target.node_id)
            if path and len(path) >= 3:  # 只显示长度>=3的路径
                paths.append({
                    "target": f"{target.entity_type}:{target.entity_id}",
                    "length": len(path),
                    "nodes": [f"{n.entity_type}:{n.entity_id}" for n in path.nodes]
                })

        # 按长度排序，返回前5条
        paths.sort(key=lambda x: x["length"], reverse=True)
        return paths[:5]

    def _find_root_sources(
            self,
            node_id: str,
            upstream_nodes: List[DataLineageNode]
    ) -> List[str]:
        """查找根来源"""
        roots = []

        for node in upstream_nodes:
            # 检查是否是根节点
            if not self.graph.get_upstream_nodes(node.node_id, max_depth=1):
                roots.append(f"{node.entity_type}:{node.entity_id}")

        return roots if roots else ["unknown"]

    def _find_end_consumers(
            self,
            node_id: str,
            downstream_nodes: List[DataLineageNode]
    ) -> List[str]:
        """查找最终消费者"""
        consumers = []

        for node in downstream_nodes:
            # 检查是否是叶子节点
            if not self.graph.get_downstream_nodes(node.node_id, max_depth=1):
                consumers.append(f"{node.entity_type}:{node.entity_id}")

        return consumers if consumers else ["none"]

    def _generate_recommendation(
            self,
            impact_level: ImpactLevel,
            downstream: List[DataLineageNode]
    ) -> str:
        """生成建议"""
        if impact_level == ImpactLevel.CRITICAL:
            return f"警告：此数据影响 {len(downstream)} 个下游实体，修改前必须进行充分测试"
        elif impact_level == ImpactLevel.HIGH:
            return f"注意：此数据影响 {len(downstream)} 个下游实体，建议评估影响后再修改"
        elif impact_level == ImpactLevel.MEDIUM:
            return f"提示：此数据影响 {len(downstream)} 个下游实体"
        else:
            return "此数据无下游依赖，可安全修改"

    def generate_full_report(self) -> Dict[str, Any]:
        """生成完整分析报告"""
        stats = self.graph.get_statistics()

        return {
            "summary": stats,
            "hotspots": self.find_hotspots(top_n=5),
            "orphaned_data": self.find_orphaned_data(),
            "cycles": self.graph.detect_cycles(),
            "compliance": self.analyze_compliance(),
            "roots": [
                {"type": n.entity_type, "id": n.entity_id}
                for n in self.graph.get_roots()
            ],
            "leaves": [
                {"type": n.entity_type, "id": n.entity_id}
                for n in self.graph.get_leaves()
            ]
        }
