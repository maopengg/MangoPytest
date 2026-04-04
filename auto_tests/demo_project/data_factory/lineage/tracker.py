# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据血缘追踪器
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
数据血缘追踪器模块

提供高级API来记录和管理数据血缘关系：
- 记录数据创建
- 记录数据依赖
- 记录API调用
- 记录数据库操作
- 记录测试用例执行
"""

from contextlib import contextmanager
from datetime import datetime
from typing import Dict, List, Optional, Any

from .node import (
    DataLineageNode,
    LineageEdge,
    LineageNodeType,
    LineageRelation,
)
from .graph import DataLineageGraph


class DataLineageTracker:
    """
    数据血缘追踪器
    
    提供简洁的API来记录测试过程中的数据血缘关系。
    支持上下文管理器，自动追踪数据生命周期。
    
    Attributes:
        graph: 血缘图实例
        current_context: 当前上下文信息
        enabled: 是否启用追踪
    """

    def __init__(self, enabled: bool = True):
        self.graph = DataLineageGraph()
        self.current_context: Dict[str, Any] = {}
        self.enabled = enabled
        self._operation_stack: List[str] = []

    def record_creation(
            self,
            entity_type: str,
            entity_id: str,
            source: str = "",
            metadata: Optional[Dict[str, Any]] = None,
            node_type: LineageNodeType = LineageNodeType.ENTITY
    ) -> str:
        """
        记录数据创建
        
        Args:
            entity_type: 实体类型
            entity_id: 实体ID
            source: 数据来源
            metadata: 元数据
            node_type: 节点类型
        
        Returns:
            str: 节点ID
        """
        if not self.enabled:
            return ""

        node = DataLineageNode.from_entity(
            entity_type=entity_type,
            entity_id=entity_id,
            source=source or self._get_current_source(),
            metadata=metadata,
            node_type=node_type
        )

        node_id = self.graph.add_node(node)

        # 如果有当前操作上下文，建立关联
        if self._operation_stack:
            parent_id = self._operation_stack[-1]
            self.record_dependency(
                from_entity=parent_id,
                to_entity=node_id,
                relation_type=LineageRelation.CREATES
            )

        return node_id

    def record_dependency(
            self,
            from_entity: str,
            to_entity: str,
            relation_type: LineageRelation = LineageRelation.DEPENDS_ON,
            metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        记录数据依赖关系
        
        Args:
            from_entity: 源实体（可以是node_id或entity_id）
            to_entity: 目标实体（可以是node_id或entity_id）
            relation_type: 关系类型
            metadata: 关系元数据
        
        Returns:
            str: 边ID
        """
        if not self.enabled:
            return ""

        # 解析实体ID
        source_id = self._resolve_node_id(from_entity)
        target_id = self._resolve_node_id(to_entity)

        if not source_id or not target_id:
            return ""

        edge = LineageEdge(
            source_id=source_id,
            target_id=target_id,
            relation=relation_type,
            metadata=metadata or {}
        )

        return self.graph.add_edge(edge)

    def record_api_call(
            self,
            api_name: str,
            method: str,
            endpoint: str,
            request_data: Optional[Dict] = None,
            response_data: Optional[Dict] = None,
            related_entities: Optional[List[str]] = None
    ) -> str:
        """
        记录API调用
        
        Args:
            api_name: API名称
            method: HTTP方法
            endpoint: 端点
            request_data: 请求数据
            response_data: 响应数据
            related_entities: 相关实体ID列表
        
        Returns:
            str: API调用节点ID
        """
        if not self.enabled:
            return ""

        node = DataLineageNode.from_api_call(
            api_name=api_name,
            method=method,
            endpoint=endpoint,
            request_data=request_data,
            response_data=response_data
        )

        node_id = self.graph.add_node(node)

        # 建立与相关实体的关系
        if related_entities:
            for entity_id in related_entities:
                target_id = self._resolve_node_id(entity_id)
                if target_id:
                    edge = LineageEdge(
                        source_id=node_id,
                        target_id=target_id,
                        relation=LineageRelation.TRIGGERS
                    )
                    self.graph.add_edge(edge)

        return node_id

    def record_database_operation(
            self,
            operation: str,
            table: str,
            record_id: str,
            sql: Optional[str] = None,
            related_entities: Optional[List[str]] = None
    ) -> str:
        """
        记录数据库操作
        
        Args:
            operation: 操作类型
            table: 表名
            record_id: 记录ID
            sql: SQL语句
            related_entities: 相关实体ID列表
        
        Returns:
            str: 数据库操作节点ID
        """
        if not self.enabled:
            return ""

        node = DataLineageNode.from_database_operation(
            operation=operation,
            table=table,
            record_id=record_id,
            sql=sql
        )

        node_id = self.graph.add_node(node)

        # 建立与相关实体的关系
        if related_entities:
            for entity_id in related_entities:
                target_id = self._resolve_node_id(entity_id)
                if target_id:
                    relation = LineageRelation.PRODUCES if operation == "INSERT" else LineageRelation.TRANSFORMS
                    edge = LineageEdge(
                        source_id=node_id,
                        target_id=target_id,
                        relation=relation
                    )
                    self.graph.add_edge(edge)

        return node_id

    def record_test_case(
            self,
            test_name: str,
            test_file: str,
            test_class: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        记录测试用例执行
        
        Args:
            test_name: 测试名称
            test_file: 测试文件
            test_class: 测试类
            metadata: 元数据
        
        Returns:
            str: 测试用例节点ID
        """
        if not self.enabled:
            return ""

        node = DataLineageNode(
            node_type=LineageNodeType.TEST_CASE,
            entity_type="test_case",
            entity_id=test_name,
            source=test_file,
            metadata={
                "test_name": test_name,
                "test_file": test_file,
                "test_class": test_class,
                "start_time": datetime.now().isoformat(),
                **(metadata or {})
            }
        )

        return self.graph.add_node(node)

    def record_scenario(
            self,
            scenario_name: str,
            scenario_class: str,
            metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        记录场景执行
        
        Args:
            scenario_name: 场景名称
            scenario_class: 场景类
            metadata: 元数据
        
        Returns:
            str: 场景节点ID
        """
        if not self.enabled:
            return ""

        node = DataLineageNode(
            node_type=LineageNodeType.SCENARIO,
            entity_type="scenario",
            entity_id=scenario_name,
            source=scenario_class,
            metadata={
                "scenario_name": scenario_name,
                "scenario_class": scenario_class,
                "start_time": datetime.now().isoformat(),
                **(metadata or {})
            }
        )

        return self.graph.add_node(node)

    @contextmanager
    def trace_operation(self, operation_name: str, metadata: Optional[Dict] = None):
        """
        操作追踪上下文管理器
        
        在上下文中执行的操作会被自动追踪
        
        Args:
            operation_name: 操作名称
            metadata: 操作元数据
        
        Yields:
            str: 操作节点ID
        
        Example:
            with tracker.trace_operation("create_order") as op_id:
                order = create_order()  # 内部操作会被自动关联
        """
        if not self.enabled:
            yield ""
            return

        # 创建操作节点
        node = DataLineageNode(
            node_type=LineageNodeType.BUILDER,
            entity_type="operation",
            entity_id=operation_name,
            metadata=metadata or {}
        )

        node_id = self.graph.add_node(node)
        self._operation_stack.append(node_id)

        try:
            yield node_id
        finally:
            if self._operation_stack:
                self._operation_stack.pop()

    def get_upstream(
            self,
            entity_id: str,
            max_depth: int = 10
    ) -> List[DataLineageNode]:
        """
        获取实体的上游依赖
        
        Args:
            entity_id: 实体ID
            max_depth: 最大深度
        
        Returns:
            List[DataLineageNode]: 上游节点列表
        """
        node_id = self._resolve_node_id(entity_id)
        if not node_id:
            return []

        return self.graph.get_upstream_nodes(node_id, max_depth)

    def get_downstream(
            self,
            entity_id: str,
            max_depth: int = 10
    ) -> List[DataLineageNode]:
        """
        获取实体的下游依赖
        
        Args:
            entity_id: 实体ID
            max_depth: 最大深度
        
        Returns:
            List[DataLineageNode]: 下游节点列表
        """
        node_id = self._resolve_node_id(entity_id)
        if not node_id:
            return []

        return self.graph.get_downstream_nodes(node_id, max_depth)

    def get_lineage_path(
            self,
            source_id: str,
            target_id: str
    ) -> Optional[Any]:
        """
        获取两个实体之间的血缘路径
        
        Args:
            source_id: 源实体ID
            target_id: 目标实体ID
        
        Returns:
            Optional[LineagePath]: 路径或None
        """
        source_node_id = self._resolve_node_id(source_id)
        target_node_id = self._resolve_node_id(target_id)

        if not source_node_id or not target_node_id:
            return None

        return self.graph.find_path(source_node_id, target_node_id)

    def get_impact_analysis(
            self,
            entity_id: str
    ) -> Dict[str, Any]:
        """
        获取实体的影响分析
        
        Args:
            entity_id: 实体ID
        
        Returns:
            Dict[str, Any]: 影响分析结果
        """
        node_id = self._resolve_node_id(entity_id)
        if not node_id:
            return {"error": f"Entity not found: {entity_id}"}

        upstream = self.get_upstream(entity_id)
        downstream = self.get_downstream(entity_id)

        node = self.graph.get_node(node_id)

        return {
            "entity": node.to_dict() if node else None,
            "upstream_count": len(upstream),
            "downstream_count": len(downstream),
            "upstream_entities": [
                {"type": n.entity_type, "id": n.entity_id}
                for n in upstream
            ],
            "downstream_entities": [
                {"type": n.entity_type, "id": n.entity_id}
                for n in downstream
            ],
            "impact_level": "high" if len(downstream) > 5 else "medium" if len(downstream) > 0 else "low"
        }

    def generate_report(self) -> Dict[str, Any]:
        """
        生成血缘追踪报告
        
        Returns:
            Dict[str, Any]: 报告数据
        """
        stats = self.graph.get_statistics()

        return {
            "summary": stats,
            "roots": [
                {"type": n.entity_type, "id": n.entity_id}
                for n in self.graph.get_roots()
            ],
            "leaves": [
                {"type": n.entity_type, "id": n.entity_id}
                for n in self.graph.get_leaves()
            ],
            "cycles": self.graph.detect_cycles(),
            "generated_at": datetime.now().isoformat(),
        }

    def export_to_dict(self) -> Dict[str, Any]:
        """
        导出为字典
        
        Returns:
            Dict[str, Any]: 完整血缘图数据
        """
        return self.graph.to_dict()

    def clear(self):
        """清空追踪数据"""
        self.graph.clear()
        self.current_context.clear()
        self._operation_stack.clear()

    def _resolve_node_id(self, entity_ref: str) -> Optional[str]:
        """
        解析实体引用为节点ID
        
        Args:
            entity_ref: 实体引用（node_id或entity_type:entity_id）
        
        Returns:
            Optional[str]: 节点ID或None
        """
        # 如果已经是节点ID
        if entity_ref in self.graph.nodes:
            return entity_ref

        # 尝试解析为 entity_type:entity_id 格式
        if ":" in entity_ref:
            parts = entity_ref.split(":", 1)
            if len(parts) == 2:
                node = self.graph.get_node_by_entity(parts[0], parts[1])
                if node:
                    return node.node_id

        return None

    def _get_current_source(self) -> str:
        """获取当前来源"""
        if self._operation_stack:
            node_id = self._operation_stack[-1]
            node = self.graph.get_node(node_id)
            if node:
                return f"{node.entity_type}:{node.entity_id}"
        return "unknown"


# 全局追踪器实例（单例模式）
_global_tracker: Optional[DataLineageTracker] = None


def get_global_tracker(enabled: bool = True) -> DataLineageTracker:
    """
    获取全局血缘追踪器
    
    Args:
        enabled: 是否启用追踪
    
    Returns:
        DataLineageTracker: 全局追踪器实例
    """
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = DataLineageTracker(enabled=enabled)
    return _global_tracker


def reset_global_tracker():
    """重置全局追踪器"""
    global _global_tracker
    _global_tracker = None
