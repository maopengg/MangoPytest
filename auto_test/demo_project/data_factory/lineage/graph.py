# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 数据血缘图管理
# @Time   : 2026-04-01
# @Author : 毛鹏

"""
数据血缘图模块

管理血缘节点和边的图结构，提供：
- 节点和边的增删改查
- 上游/下游追溯
- 路径查找
- 循环检测
"""

from typing import Dict, List, Optional, Set, Any
from collections import defaultdict, deque

try:
    from .node import DataLineageNode, LineageEdge, LineageRelation, LineagePath
except ImportError:
    from node import DataLineageNode, LineageEdge, LineageRelation, LineagePath


class DataLineageGraph:
    """
    数据血缘图
    
    使用邻接表存储节点和边的关系，支持高效的上游/下游追溯。
    
    Attributes:
        nodes: 节点字典 {node_id: DataLineageNode}
        edges: 边字典 {edge_id: LineageEdge}
        entity_index: 实体索引 {(entity_type, entity_id): node_id}
    """
    
    def __init__(self):
        self.nodes: Dict[str, DataLineageNode] = {}
        self.edges: Dict[str, LineageEdge] = {}
        self.entity_index: Dict[tuple, str] = {}
        self._adjacency: Dict[str, List[str]] = defaultdict(list)  # 出边邻接表
        self._reverse_adjacency: Dict[str, List[str]] = defaultdict(list)  # 入边邻接表
    
    def add_node(self, node: DataLineageNode) -> str:
        """
        添加节点
        
        Args:
            node: 血缘节点
        
        Returns:
            str: 节点ID
        """
        self.nodes[node.node_id] = node
        
        # 建立实体索引
        if node.entity_type and node.entity_id:
            key = (node.entity_type, node.entity_id)
            self.entity_index[key] = node.node_id
        
        return node.node_id
    
    def get_node(self, node_id: str) -> Optional[DataLineageNode]:
        """
        根据ID获取节点
        
        Args:
            node_id: 节点ID
        
        Returns:
            Optional[DataLineageNode]: 节点或None
        """
        return self.nodes.get(node_id)
    
    def get_node_by_entity(
        self,
        entity_type: str,
        entity_id: str
    ) -> Optional[DataLineageNode]:
        """
        根据实体类型和ID获取节点
        
        Args:
            entity_type: 实体类型
            entity_id: 实体ID
        
        Returns:
            Optional[DataLineageNode]: 节点或None
        """
        key = (entity_type, entity_id)
        node_id = self.entity_index.get(key)
        if node_id:
            return self.nodes.get(node_id)
        return None
    
    def add_edge(self, edge: LineageEdge) -> str:
        """
        添加边
        
        Args:
            edge: 血缘边
        
        Returns:
            str: 边ID
        """
        self.edges[edge.edge_id] = edge
        
        # 更新邻接表
        self._adjacency[edge.source_id].append(edge.target_id)
        self._reverse_adjacency[edge.target_id].append(edge.source_id)
        
        # 更新节点的边引用
        if edge.source_id in self.nodes:
            self.nodes[edge.source_id].add_outgoing_edge(edge.edge_id)
        if edge.target_id in self.nodes:
            self.nodes[edge.target_id].add_incoming_edge(edge.edge_id)
        
        return edge.edge_id
    
    def get_edge(self, edge_id: str) -> Optional[LineageEdge]:
        """
        根据ID获取边
        
        Args:
            edge_id: 边ID
        
        Returns:
            Optional[LineageEdge]: 边或None
        """
        return self.edges.get(edge_id)
    
    def get_edges_between(
        self,
        source_id: str,
        target_id: str
    ) -> List[LineageEdge]:
        """
        获取两个节点之间的所有边
        
        Args:
            source_id: 源节点ID
            target_id: 目标节点ID
        
        Returns:
            List[LineageEdge]: 边列表
        """
        result = []
        for edge in self.edges.values():
            if edge.source_id == source_id and edge.target_id == target_id:
                result.append(edge)
        return result
    
    def get_upstream_nodes(
        self,
        node_id: str,
        max_depth: int = 10,
        relation_filter: Optional[Set[LineageRelation]] = None
    ) -> List[DataLineageNode]:
        """
        获取上游节点（依赖）
        
        Args:
            node_id: 起始节点ID
            max_depth: 最大追溯深度
            relation_filter: 关系类型过滤
        
        Returns:
            List[DataLineageNode]: 上游节点列表
        """
        return self._traverse(
            node_id,
            direction="upstream",
            max_depth=max_depth,
            relation_filter=relation_filter
        )
    
    def get_downstream_nodes(
        self,
        node_id: str,
        max_depth: int = 10,
        relation_filter: Optional[Set[LineageRelation]] = None
    ) -> List[DataLineageNode]:
        """
        获取下游节点（被依赖）
        
        Args:
            node_id: 起始节点ID
            max_depth: 最大追溯深度
            relation_filter: 关系类型过滤
        
        Returns:
            List[DataLineageNode]: 下游节点列表
        """
        return self._traverse(
            node_id,
            direction="downstream",
            max_depth=max_depth,
            relation_filter=relation_filter
        )
    
    def _traverse(
        self,
        start_id: str,
        direction: str,
        max_depth: int,
        relation_filter: Optional[Set[LineageRelation]] = None
    ) -> List[DataLineageNode]:
        """
        遍历图
        
        Args:
            start_id: 起始节点ID
            direction: 方向（upstream/downstream）
            max_depth: 最大深度
            relation_filter: 关系类型过滤
        
        Returns:
            List[DataLineageNode]: 节点列表
        """
        if start_id not in self.nodes:
            return []
        
        # 选择邻接表
        if direction == "upstream":
            adjacency = self._reverse_adjacency
        else:
            adjacency = self._adjacency
        
        visited = set()
        result = []
        queue = deque([(start_id, 0)])
        
        while queue:
            current_id, depth = queue.popleft()
            
            if current_id in visited or depth > max_depth:
                continue
            
            visited.add(current_id)
            
            if current_id != start_id:
                node = self.nodes.get(current_id)
                if node:
                    result.append(node)
            
            # 获取邻居
            for neighbor_id in adjacency.get(current_id, []):
                # 检查关系类型
                if relation_filter:
                    edges = self.get_edges_between(current_id, neighbor_id)
                    if not any(e.relation in relation_filter for e in edges):
                        continue
                
                if neighbor_id not in visited:
                    queue.append((neighbor_id, depth + 1))
        
        return result
    
    def find_path(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 10
    ) -> Optional[LineagePath]:
        """
        查找从源节点到目标节点的路径
        
        Args:
            source_id: 源节点ID
            target_id: 目标节点ID
            max_depth: 最大深度
        
        Returns:
            Optional[LineagePath]: 路径或None
        """
        if source_id not in self.nodes or target_id not in self.nodes:
            return None
        
        # BFS查找路径
        queue = deque([(source_id, [source_id])])
        visited = {source_id}
        
        while queue:
            current_id, path = queue.popleft()
            
            if len(path) > max_depth:
                continue
            
            if current_id == target_id:
                # 构建路径对象
                nodes = [self.nodes[nid] for nid in path]
                edges = []
                for i in range(len(path) - 1):
                    edge_list = self.get_edges_between(path[i], path[i + 1])
                    if edge_list:
                        edges.append(edge_list[0])
                
                return LineagePath(
                    nodes=nodes,
                    edges=edges,
                    path_type="downstream"
                )
            
            for neighbor_id in self._adjacency.get(current_id, []):
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, path + [neighbor_id]))
        
        return None
    
    def detect_cycles(self) -> List[List[str]]:
        """
        检测图中的循环
        
        Returns:
            List[List[str]]: 循环路径列表（节点ID列表）
        """
        cycles = []
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node_id: str):
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)
            
            for neighbor_id in self._adjacency.get(node_id, []):
                if neighbor_id not in visited:
                    dfs(neighbor_id)
                elif neighbor_id in rec_stack:
                    # 发现循环
                    cycle_start = path.index(neighbor_id)
                    cycle = path[cycle_start:] + [neighbor_id]
                    cycles.append(cycle)
            
            path.pop()
            rec_stack.remove(node_id)
        
        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id)
        
        return cycles
    
    def get_roots(self) -> List[DataLineageNode]:
        """
        获取根节点（没有上游依赖的节点）
        
        Returns:
            List[DataLineageNode]: 根节点列表
        """
        roots = []
        for node in self.nodes.values():
            if not self._reverse_adjacency.get(node.node_id):
                roots.append(node)
        return roots
    
    def get_leaves(self) -> List[DataLineageNode]:
        """
        获取叶子节点（没有下游依赖的节点）
        
        Returns:
            List[DataLineageNode]: 叶子节点列表
        """
        leaves = []
        for node in self.nodes.values():
            if not self._adjacency.get(node.node_id):
                leaves.append(node)
        return leaves
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取图的统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        node_types = defaultdict(int)
        relation_types = defaultdict(int)
        
        for node in self.nodes.values():
            node_types[node.node_type.name] += 1
        
        for edge in self.edges.values():
            relation_types[edge.relation.value] += 1
        
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": dict(node_types),
            "relation_types": dict(relation_types),
            "roots": len(self.get_roots()),
            "leaves": len(self.get_leaves()),
            "cycles": len(self.detect_cycles()),
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            Dict[str, Any]: 图的字典表示
        """
        return {
            "nodes": {nid: node.to_dict() for nid, node in self.nodes.items()},
            "edges": {eid: edge.to_dict() for eid, edge in self.edges.items()},
            "statistics": self.get_statistics(),
        }
    
    def clear(self):
        """清空图"""
        self.nodes.clear()
        self.edges.clear()
        self.entity_index.clear()
        self._adjacency.clear()
        self._reverse_adjacency.clear()
