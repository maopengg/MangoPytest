# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据血缘相关模型
# @Time   : 2026-05-03
# @Author : 毛鹏
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any

from core.enums.demo_enum import LineageNodeType, LineageRelation


@dataclass
class LineageEdge:
    """血缘边 - 表示两个节点之间的关系"""
    source_id: str
    target_id: str
    relation: LineageRelation
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    edge_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "edge_id": self.edge_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation": self.relation.value,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class DataLineageNode:
    """血缘节点 - 表示数据血缘图中的一个实体"""
    node_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    node_type: LineageNodeType = LineageNodeType.ENTITY
    entity_type: str = ""
    entity_id: str = ""
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    lifecycle: str = "active"
    incoming_edges: List[str] = field(default_factory=list)
    outgoing_edges: List[str] = field(default_factory=list)

    def __post_init__(self):
        """初始化后处理"""
        if not self.entity_id and self.metadata.get("id"):
            self.entity_id = str(self.metadata.get("id"))

    def add_incoming_edge(self, edge_id: str):
        """添加入边"""
        if edge_id not in self.incoming_edges:
            self.incoming_edges.append(edge_id)
            self.updated_at = datetime.now()

    def add_outgoing_edge(self, edge_id: str):
        """添加出边"""
        if edge_id not in self.outgoing_edges:
            self.outgoing_edges.append(edge_id)
            self.updated_at = datetime.now()

    def get_full_id(self) -> str:
        """获取完整标识"""
        return f"{self.entity_type}:{self.entity_id}"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.name,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "source": self.source,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "lifecycle": self.lifecycle,
            "incoming_edges": self.incoming_edges,
            "outgoing_edges": self.outgoing_edges,
        }

    @classmethod
    def from_entity(
            cls,
            entity_type: str,
            entity_id: str,
            source: str = "",
            metadata: Optional[Dict[str, Any]] = None,
            node_type: LineageNodeType = LineageNodeType.ENTITY
    ) -> "DataLineageNode":
        """从实体创建血缘节点"""
        return cls(
            node_type=node_type,
            entity_type=entity_type,
            entity_id=entity_id,
            source=source,
            metadata=metadata or {},
        )


@dataclass
class LineagePath:
    """血缘路径 - 表示从一个节点到另一个节点的完整路径"""
    nodes: List[DataLineageNode] = field(default_factory=list)
    edges: List[LineageEdge] = field(default_factory=list)
    path_type: str = "unknown"

    def __len__(self) -> int:
        """路径长度（边数）"""
        return len(self.edges)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "path_type": self.path_type,
            "length": len(self),
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
        }
