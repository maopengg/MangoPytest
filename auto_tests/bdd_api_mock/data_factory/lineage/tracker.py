# -*- coding: utf-8 -*-
"""
数据血缘追踪器 - BDD 版本（支持 Allure）

提供简洁的 API 来记录测试过程中的数据血缘关系，
并自动集成 Allure 报告，展示数据创建链路。
"""

from contextlib import contextmanager
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field

from .graph import DataLineageGraph

# 可选的 Allure 支持
try:
    import allure
    from allure_commons.types import AttachmentType
    ALLURE_AVAILABLE = True
except ImportError:
    ALLURE_AVAILABLE = False
    allure = None


@dataclass
class LineageNode:
    """血缘节点"""
    node_id: str
    entity_type: str
    entity_id: Any
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    dependencies: Set[str] = field(default_factory=set)


class DataLineageTracker:
    """
    数据血缘追踪器
    
    提供简洁的 API 来记录测试过程中的数据血缘关系，
    支持 Allure 报告集成。
    
    Attributes:
        graph: 血缘图实例
        enabled: 是否启用追踪
        _current_test: 当前测试名称
    """

    def __init__(self, enabled: bool = True, test_name: str = ""):
        self.graph = DataLineageGraph()
        self.enabled = enabled
        self._current_test = test_name
        self._created_entities: List[Dict[str, Any]] = []
        self._node_map: Dict[str, LineageNode] = {}

    def record_creation(
        self,
        entity_type: str,
        entity_id: Any,
        source: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        parent_entity: Optional[str] = None
    ) -> str:
        """
        记录数据创建
        
        Args:
            entity_type: 实体类型（如 "user", "order"）
            entity_id: 实体ID
            source: 数据来源（如 "api_call", "factory"）
            metadata: 元数据（如 {"username": "test"}）
            parent_entity: 父实体 node_id（用于建立依赖关系）
        
        Returns:
            str: 节点ID
        """
        if not self.enabled:
            return ""

        node_id = f"{entity_type}:{entity_id}"
        
        node = LineageNode(
            node_id=node_id,
            entity_type=entity_type,
            entity_id=entity_id,
            source=source or "factory",
            metadata=metadata or {}
        )

        # 如果有父实体，建立依赖关系
        if parent_entity and parent_entity in self._node_map:
            node.dependencies.add(parent_entity)
            self._node_map[parent_entity].dependencies.add(node_id)

        self._node_map[node_id] = node
        self.graph.add_node(node)

        # 记录创建历史
        self._created_entities.append({
            "node_id": node_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "source": source,
            "metadata": metadata
        })

        # Allure 记录
        if ALLURE_AVAILABLE:
            self._allure_record_creation(node)

        return node_id

    def record_dependency(
        self,
        from_entity: str,
        to_entity: str,
        relation_type: str = "creates"
    ) -> None:
        """
        记录数据依赖关系
        
        Args:
            from_entity: 源实体 node_id
            to_entity: 目标实体 node_id
            relation_type: 关系类型（如 "creates", "depends_on"）
        """
        if not self.enabled:
            return

        if from_entity in self._node_map and to_entity in self._node_map:
            self._node_map[from_entity].dependencies.add(to_entity)
            self._node_map[to_entity].dependencies.add(from_entity)
            self.graph.add_edge(from_entity, to_entity, relation_type)

    def get_created_entities(self) -> List[Dict[str, Any]]:
        """获取所有创建的实体列表"""
        return self._created_entities.copy()

    def get_entity_lineage(self, entity_type: str, entity_id: Any) -> Optional[LineageNode]:
        """获取实体的血缘信息"""
        node_id = f"{entity_type}:{entity_id}"
        return self._node_map.get(node_id)

    def get_cleanup_order(self) -> List[Dict[str, Any]]:
        """
        获取数据清理顺序（按依赖关系逆序）
        
        Returns:
            List[Dict]: 按清理顺序排列的实体列表
        """
        if not self._created_entities:
            return []
        
        # 使用图的拓扑排序获取清理顺序
        node_ids = [e["node_id"] for e in self._created_entities]
        cleanup_order = self.graph.get_reverse_topological_order(node_ids)
        
        result = []
        for node_id in cleanup_order:
            if node_id in self._node_map:
                node = self._node_map[node_id]
                result.append({
                    "entity_type": node.entity_type,
                    "entity_id": node.entity_id,
                    "node_id": node_id
                })
        
        return result

    def generate_mermaid_graph(self) -> str:
        """
        生成 Mermaid 格式的血缘图
        
        Returns:
            str: Mermaid 图表代码
        """
        lines = ["graph TD"]
        
        # 添加节点
        for node_id, node in self._node_map.items():
            safe_id = node_id.replace(":", "_")
            label = f"{node.entity_type}:{node.entity_id}"
            lines.append(f"    {safe_id}[{label}]")
        
        # 添加边
        for node_id, node in self._node_map.items():
            safe_id = node_id.replace(":", "_")
            for dep_id in node.dependencies:
                if dep_id in self._node_map:
                    safe_dep_id = dep_id.replace(":", "_")
                    lines.append(f"    {safe_id} --> {safe_dep_id}")
        
        return "\n".join(lines)

    def attach_to_allure(self) -> None:
        """
        将血缘追踪结果附加到 Allure 报告
        """
        if not ALLURE_AVAILABLE or not allure:
            return

        # 1. 添加数据创建统计
        entity_count = {}
        for entity in self._created_entities:
            etype = entity["entity_type"]
            entity_count[etype] = entity_count.get(etype, 0) + 1
        
        stats = "## 数据创建统计\n\n"
        for etype, count in sorted(entity_count.items()):
            stats += f"- **{etype}**: {count} 条\n"
        stats += f"\n**总计**: {len(self._created_entities)} 条数据\n"
        
        allure.attach(stats, "数据血缘统计", AttachmentType.MARKDOWN)

        # 2. 添加详细列表
        details = "## 数据创建详情\n\n"
        details += "| 实体类型 | 实体ID | 来源 | 元数据 |\n"
        details += "|---------|--------|------|--------|\n"
        
        for entity in self._created_entities:
            metadata_str = str(entity.get("metadata", {}))[:50]
            details += f"| {entity['entity_type']} | {entity['entity_id']} | {entity.get('source', '-')} | {metadata_str} |\n"
        
        allure.attach(details, "数据创建详情", AttachmentType.MARKDOWN)

        # 3. 添加 Mermaid 血缘图
        mermaid = self.generate_mermaid_graph()
        if len(self._node_map) > 1:
            allure.attach(
                f"## 数据血缘关系图\n\n```mermaid\n{mermaid}\n```",
                "血缘关系图",
                AttachmentType.MARKDOWN
            )

        # 4. 添加清理顺序
        cleanup_order = self.get_cleanup_order()
        if cleanup_order:
            cleanup = "## 建议的数据清理顺序（按依赖逆序）\n\n"
            for i, item in enumerate(cleanup_order, 1):
                cleanup += f"{i}. {item['entity_type']} (ID: {item['entity_id']})\n"
            allure.attach(cleanup, "数据清理顺序", AttachmentType.MARKDOWN)

    def _allure_record_creation(self, node: LineageNode) -> None:
        """内部方法：记录到 Allure"""
        if not ALLURE_AVAILABLE or not allure:
            return
        
        # 添加步骤描述
        step_title = f"创建 {node.entity_type}: {node.entity_id}"
        with allure.step(step_title):
            if node.metadata:
                allure.attach(
                    str(node.metadata),
                    "实体数据",
                    AttachmentType.JSON
                )

    @contextmanager
    def track_test(self, test_name: str):
        """
        上下文管理器：追踪整个测试的数据血缘
        
        使用示例:
            with tracker.track_test("test_order_workflow"):
                # 测试代码
                user = UserSpec()
                order = OrderSpec(user_id=user.id)
        """
        self._current_test = test_name
        self._created_entities.clear()
        self._node_map.clear()
        self.graph.clear()
        
        try:
            yield self
        finally:
            # 测试结束时附加报告
            self.attach_to_allure()


# 全局追踪器实例（单例模式）
_global_tracker: Optional[DataLineageTracker] = None


def get_tracker(enabled: bool = True) -> DataLineageTracker:
    """获取全局血缘追踪器实例"""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = DataLineageTracker(enabled=enabled)
    return _global_tracker


def reset_tracker() -> None:
    """重置全局追踪器"""
    global _global_tracker
    _global_tracker = None
