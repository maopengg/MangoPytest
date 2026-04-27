# -*- coding: utf-8 -*-
"""
数据血缘图管理 - BDD 版本

管理血缘节点和边的图结构，提供：
- 节点和边的增删改查
- 拓扑排序（用于确定数据清理顺序）
- 上游/下游追溯
"""

from collections import defaultdict, deque
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field


@dataclass
class Edge:
    """图边"""
    from_node: str
    to_node: str
    relation_type: str = "creates"
    metadata: Dict[str, Any] = field(default_factory=dict)


class DataLineageGraph:
    """
    数据血缘图
    
    使用邻接表存储节点和边的关系，支持高效的上游/下游追溯。
    
    Attributes:
        nodes: 节点字典 {node_id: LineageNode}
        edges: 边列表
        _adjacency: 出边邻接表 {node_id: [to_node_id, ...]}
        _reverse_adjacency: 入边邻接表 {node_id: [from_node_id, ...]}
    """

    def __init__(self):
        self.nodes: Dict[str, Any] = {}
        self.edges: List[Edge] = []
        self._adjacency: Dict[str, List[str]] = defaultdict(list)
        self._reverse_adjacency: Dict[str, List[str]] = defaultdict(list)

    def add_node(self, node: Any) -> str:
        """
        添加节点
        
        Args:
            node: 血缘节点
        
        Returns:
            str: 节点ID
        """
        node_id = node.node_id
        self.nodes[node_id] = node
        return node_id

    def add_edge(self, from_node: str, to_node: str, relation_type: str = "creates") -> None:
        """
        添加边
        
        Args:
            from_node: 源节点ID
            to_node: 目标节点ID
            relation_type: 关系类型
        """
        if from_node not in self.nodes or to_node not in self.nodes:
            return

        edge = Edge(from_node, to_node, relation_type)
        self.edges.append(edge)
        self._adjacency[from_node].append(to_node)
        self._reverse_adjacency[to_node].append(from_node)

    def get_node(self, node_id: str) -> Optional[Any]:
        """根据ID获取节点"""
        return self.nodes.get(node_id)

    def get_downstream_nodes(self, node_id: str, max_depth: int = 10) -> List[Any]:
        """
        获取下游节点（被当前节点依赖的节点）
        
        Args:
            node_id: 起始节点ID
            max_depth: 最大遍历深度
        
        Returns:
            List[LineageNode]: 下游节点列表
        """
        if node_id not in self.nodes:
            return []

        result = []
        visited = {node_id}
        queue = deque([(node_id, 0)])

        while queue:
            current_id, depth = queue.popleft()
            if depth >= max_depth:
                continue

            for next_id in self._adjacency[current_id]:
                if next_id not in visited:
                    visited.add(next_id)
                    if next_id in self.nodes:
                        result.append(self.nodes[next_id])
                    queue.append((next_id, depth + 1))

        return result

    def get_upstream_nodes(self, node_id: str, max_depth: int = 10) -> List[Any]:
        """
        获取上游节点（依赖当前节点的节点）
        
        Args:
            node_id: 起始节点ID
            max_depth: 最大遍历深度
        
        Returns:
            List[LineageNode]: 上游节点列表
        """
        if node_id not in self.nodes:
            return []

        result = []
        visited = {node_id}
        queue = deque([(node_id, 0)])

        while queue:
            current_id, depth = queue.popleft()
            if depth >= max_depth:
                continue

            for prev_id in self._reverse_adjacency[current_id]:
                if prev_id not in visited:
                    visited.add(prev_id)
                    if prev_id in self.nodes:
                        result.append(self.nodes[prev_id])
                    queue.append((prev_id, depth + 1))

        return result

    def get_topological_order(self, node_ids: Optional[List[str]] = None) -> List[str]:
        """
        获取拓扑排序（创建顺序）
        
        Args:
            node_ids: 指定节点ID列表，None表示所有节点
        
        Returns:
            List[str]: 按创建顺序排列的节点ID列表
        """
        if node_ids is None:
            node_ids = list(self.nodes.keys())

        # 计算入度
        in_degree = {node_id: 0 for node_id in node_ids}
        for node_id in node_ids:
            if node_id in self._adjacency:
                for next_id in self._adjacency[node_id]:
                    if next_id in in_degree:
                        in_degree[next_id] += 1

        # Kahn算法
        queue = deque([nid for nid in node_ids if in_degree[nid] == 0])
        result = []

        while queue:
            current = queue.popleft()
            result.append(current)

            if current in self._adjacency:
                for next_id in self._adjacency[current]:
                    if next_id in in_degree:
                        in_degree[next_id] -= 1
                        if in_degree[next_id] == 0:
                            queue.append(next_id)

        # 如果有剩余节点，说明有环，直接追加
        for node_id in node_ids:
            if node_id not in result:
                result.append(node_id)

        return result

    def get_reverse_topological_order(self, node_ids: Optional[List[str]] = None) -> List[str]:
        """
        获取逆拓扑排序（清理顺序）
        
        先创建的后清理，避免外键约束错误
        
        Args:
            node_ids: 指定节点ID列表，None表示所有节点
        
        Returns:
            List[str]: 按清理顺序排列的节点ID列表
        """
        order = self.get_topological_order(node_ids)
        return list(reversed(order))

    def get_dependency_chain(self, node_id: str) -> Dict[str, Any]:
        """
        获取完整的依赖链
        
        Args:
            node_id: 起始节点ID
        
        Returns:
            Dict: 包含上下游的完整依赖信息
        """
        if node_id not in self.nodes:
            return {}

        node = self.nodes[node_id]
        upstream = self.get_upstream_nodes(node_id)
        downstream = self.get_downstream_nodes(node_id)

        return {
            "node": node,
            "upstream": upstream,
            "downstream": downstream,
            "upstream_count": len(upstream),
            "downstream_count": len(downstream)
        }

    def find_path(self, from_node: str, to_node: str) -> Optional[List[str]]:
        """
        查找从 from_node 到 to_node 的路径
        
        Args:
            from_node: 起始节点ID
            to_node: 目标节点ID
        
        Returns:
            Optional[List[str]]: 路径节点ID列表，无路径返回None
        """
        if from_node not in self.nodes or to_node not in self.nodes:
            return None

        # BFS查找路径
        queue = deque([(from_node, [from_node])])
        visited = {from_node}

        while queue:
            current, path = queue.popleft()
            if current == to_node:
                return path

            for next_id in self._adjacency[current]:
                if next_id not in visited:
                    visited.add(next_id)
                    queue.append((next_id, path + [next_id]))

        return None

    def has_cycle(self) -> bool:
        """
        检测图中是否存在环
        
        Returns:
            bool: 是否存在环
        """
        visited = set()
        rec_stack = set()

        def dfs(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)

            for next_id in self._adjacency[node_id]:
                if next_id not in visited:
                    if dfs(next_id):
                        return True
                elif next_id in rec_stack:
                    return True

            rec_stack.remove(node_id)
            return False

        for node_id in self.nodes:
            if node_id not in visited:
                if dfs(node_id):
                    return True

        return False

    def get_stats(self) -> Dict[str, Any]:
        """
        获取图的统计信息
        
        Returns:
            Dict: 统计信息
        """
        entity_types = {}
        for node in self.nodes.values():
            etype = getattr(node, 'entity_type', 'unknown')
            entity_types[etype] = entity_types.get(etype, 0) + 1

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "entity_types": entity_types,
            "has_cycle": self.has_cycle()
        }

    def clear(self) -> None:
        """清空图"""
        self.nodes.clear()
        self.edges.clear()
        self._adjacency.clear()
        self._reverse_adjacency.clear()
