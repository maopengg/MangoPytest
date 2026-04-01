# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据血缘节点定义
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
数据血缘节点模块

定义血缘追踪中的核心数据结构：
- LineageNodeType: 节点类型枚举
- LineageRelation: 关系类型枚举  
- DataLineageNode: 血缘节点（实体）
- LineageEdge: 血缘边（关系）
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import uuid


class LineageNodeType(Enum):
    """血缘节点类型"""
    ENTITY = auto()      # 业务实体（User, Order等）
    API_CALL = auto()    # API调用
    DATABASE = auto()    # 数据库操作
    FILE = auto()        # 文件操作
    EVENT = auto()       # 事件/消息
    TEST_CASE = auto()   # 测试用例
    SCENARIO = auto()    # 测试场景
    BUILDER = auto()     # 构造器


class LineageRelation(Enum):
    """血缘关系类型"""
    CREATES = "creates"           # 创建
    DEPENDS_ON = "depends_on"     # 依赖
    REFERENCES = "references"     # 引用
    TRIGGERS = "triggers"         # 触发
    CONTAINS = "contains"         # 包含
    TRANSFORMS = "transforms"     # 转换
    PRODUCES = "produces"         # 产生
    CONSUMES = "consumes"         # 消费


@dataclass
class LineageEdge:
    """
    血缘边 - 表示两个节点之间的关系
    
    Attributes:
        source_id: 源节点ID
        target_id: 目标节点ID
        relation: 关系类型
        metadata: 关系元数据
        timestamp: 关系建立时间
    """
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
    """
    血缘节点 - 表示数据血缘图中的一个实体
    
    Attributes:
        node_id: 节点唯一标识
        node_type: 节点类型
        entity_type: 实体类型（如"user", "order"）
        entity_id: 实体ID
        source: 数据来源（如"api_call", "db_insert"）
        metadata: 节点元数据
        created_at: 创建时间
        updated_at: 更新时间
        lifecycle: 生命周期状态
    """
    node_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    node_type: LineageNodeType = LineageNodeType.ENTITY
    entity_type: str = ""
    entity_id: str = ""
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    lifecycle: str = "active"  # active, archived, deleted
    
    # 关联的边（入边和出边）
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
        """
        从实体创建血缘节点
        
        Args:
            entity_type: 实体类型
            entity_id: 实体ID
            source: 数据来源
            metadata: 元数据
            node_type: 节点类型
        
        Returns:
            DataLineageNode: 血缘节点
        """
        return cls(
            node_type=node_type,
            entity_type=entity_type,
            entity_id=entity_id,
            source=source,
            metadata=metadata or {},
        )
    
    @classmethod
    def from_api_call(
        cls,
        api_name: str,
        method: str,
        endpoint: str,
        request_data: Optional[Dict] = None,
        response_data: Optional[Dict] = None
    ) -> "DataLineageNode":
        """
        从API调用创建血缘节点
        
        Args:
            api_name: API名称
            method: HTTP方法
            endpoint: 端点
            request_data: 请求数据
            response_data: 响应数据
        
        Returns:
            DataLineageNode: 血缘节点
        """
        return cls(
            node_type=LineageNodeType.API_CALL,
            entity_type="api_call",
            entity_id=f"{method}_{endpoint}",
            source="api",
            metadata={
                "api_name": api_name,
                "method": method,
                "endpoint": endpoint,
                "request": request_data,
                "response": response_data,
            },
        )
    
    @classmethod
    def from_database_operation(
        cls,
        operation: str,
        table: str,
        record_id: str,
        sql: Optional[str] = None
    ) -> "DataLineageNode":
        """
        从数据库操作创建血缘节点
        
        Args:
            operation: 操作类型（INSERT/UPDATE/DELETE）
            table: 表名
            record_id: 记录ID
            sql: SQL语句
        
        Returns:
            DataLineageNode: 血缘节点
        """
        return cls(
            node_type=LineageNodeType.DATABASE,
            entity_type=f"db_{table}",
            entity_id=record_id,
            source="database",
            metadata={
                "operation": operation,
                "table": table,
                "sql": sql,
            },
        )


@dataclass
class LineagePath:
    """
    血缘路径 - 表示从一个节点到另一个节点的完整路径
    
    Attributes:
        nodes: 路径上的节点列表
        edges: 路径上的边列表
        path_type: 路径类型（upstream/downstream）
    """
    nodes: List[DataLineageNode] = field(default_factory=list)
    edges: List[LineageEdge] = field(default_factory=list)
    path_type: str = "unknown"  # upstream, downstream
    
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
