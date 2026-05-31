from typing import Any, Dict, List, Optional, Set, Tuple
from ..core import TaskDAG, DAGNode, DAGEdge
from .topological_sorter import TopologicalSorter


class CriticalPathFinder:
    """DAG关键路径识别器 - 识别任务DAG中的关键路径和依赖关系"""

    def __init__(self):
        self.topological_sorter = TopologicalSorter()

    def find_critical_path(self, dag: TaskDAG) -> Dict[str, Any]:
        """
        识别DAG的关键路径（最长路径）

        Args:
            dag: 任务DAG

        Returns:
            包含关键路径信息的字典
        """
        # 先检查是否有环
        cycle_result = self.topological_sorter.cycle_detector.detect_cycles(dag)
        if cycle_result["has_cycle"]:
            return {
                "success": False,
                "message": "DAG中存在环，无法计算关键路径",
                "cycles": cycle_result["cycles"],
                "critical_path": [],
                "critical_path_length": 0.0,
                "node_distances": {}
            }

        # 拓扑排序
        topo_result = self.topological_sorter.sort(dag)
        if not topo_result["success"]:
            return {
                "success": False,
                "message": "拓扑排序失败，无法计算关键路径",
                "critical_path": [],
                "critical_path_length": 0.0,
                "node_distances": {}
            }

        topo_order = topo_result["sorted_order"]

        # 构建邻接表
        adjacency = self._build_adjacency(dag)

        # 计算最长路径
        dist, prev = self._calculate_longest_path(dag, topo_order, adjacency)

        # 找到最长路径的终点
        end_node = max(dist, key=dist.get) if dist else None

        # 回溯构建路径
        critical_path = []
        if end_node:
            current = end_node
            while current is not None:
                critical_path.append(current)
                current = prev.get(current)
            critical_path = list(reversed(critical_path))

        return {
            "success": True,
            "critical_path": critical_path,
            "critical_path_length": dist.get(end_node, 0.0) if end_node else 0.0,
            "node_distances": dist,
            "message": f"成功找到关键路径，长度为 {dist.get(end_node, 0.0) if end_node else 0.0}"
        }

    def _build_adjacency(self, dag: TaskDAG) -> Dict[str, List[Tuple[str, float]]]:
        """构建邻接表，(后继节点, 权重)"""
        adjacency = {}
        for node in dag.nodes:
            adjacency[node.id] = []
        for edge in dag.edges:
            if edge.from_node in adjacency:
                adjacency[edge.from_node].append((edge.to_node, edge.weight))
        return adjacency

    def _calculate_longest_path(
        self, dag: TaskDAG, topo_order: List[str], adjacency: Dict[str, List[Tuple[str, float]]]
    ) -> Tuple[Dict[str, float], Dict[str, Optional[str]]]:
        """计算从源节点到每个节点的最长路径"""
        dist = {node.id: 0.0 for node in dag.nodes}
        prev = {node.id: None for node in dag.nodes}

        for node_id in topo_order:
            for neighbor, weight in adjacency.get(node_id, []):
                if dist[neighbor] < dist[node_id] + weight:
                    dist[neighbor] = dist[node_id] + weight
                    prev[neighbor] = node_id

        return dist, prev

    def find_all_critical_paths(self, dag: TaskDAG) -> Dict[str, Any]:
        """
        找到所有关键路径（可能有多条）

        Args:
            dag: 任务DAG

        Returns:
            包含所有关键路径信息的字典
        """
        critical_result = self.find_critical_path(dag)
        if not critical_result["success"]:
            return critical_result

        max_length = critical_result["critical_path_length"]
        dist = critical_result["node_distances"]

        # 找到所有最大距离的节点
        max_nodes = [node_id for node_id, d in dist.items() if d == max_length]

        # 回溯找到所有路径
        adjacency = self._build_reverse_adjacency(dag)
        all_critical_paths = []

        def backtrack(current: str, path: List[str]):
            path.append(current)
            if dist[current] == 0:
                all_critical_paths.append(list(reversed(path)))
                path.pop()
                return
            for neighbor in adjacency.get(current, []):
                if dist[neighbor] + self._get_edge_weight(dag, neighbor, current) == dist[current]:
                    backtrack(neighbor, path)
            path.pop()

        for end_node in max_nodes:
            backtrack(end_node, [])

        # 去重
        unique_paths = []
        for path in all_critical_paths:
            if path not in unique_paths:
                unique_paths.append(path)

        return {
            "success": True,
            "all_critical_paths": unique_paths,
            "critical_path_length": max_length,
            "critical_path_count": len(unique_paths),
            "message": f"找到 {len(unique_paths)} 条关键路径"
        }

    def _build_reverse_adjacency(self, dag: TaskDAG) -> Dict[str, List[str]]:
        """构建反向邻接表，(前驱节点)"""
        reverse_adj = {}
        for node in dag.nodes:
            reverse_adj[node.id] = []
        for edge in dag.edges:
            if edge.to_node in reverse_adj:
                reverse_adj[edge.to_node].append(edge.from_node)
        return reverse_adj

    def _get_edge_weight(self, dag: TaskDAG, from_node: str, to_node: str) -> float:
        """获取边的权重"""
        for edge in dag.edges:
            if edge.from_node == from_node and edge.to_node == to_node:
                return edge.weight
        return 0.0

    def get_critical_path_details(self, dag: TaskDAG) -> Dict[str, Any]:
        """
        获取关键路径的详细信息

        Args:
            dag: 任务DAG

        Returns:
            关键路径详细信息
        """
        critical_result = self.find_critical_path(dag)
        if not critical_result["success"]:
            return critical_result

        critical_path = critical_result["critical_path"]
        path_details = {
            "nodes": [],
            "edges": [],
            "total_weight": critical_result["critical_path_length"],
            "node_count": len(critical_path),
            "edge_count": len(critical_path) - 1 if critical_path else 0
        }

        for node_id in critical_path:
            node = self._find_node_by_id(dag, node_id)
            if node:
                path_details["nodes"].append({
                    "id": node.id,
                    "name": node.name,
                    "distance": critical_result["node_distances"].get(node_id, 0.0)
                })

        for i in range(len(critical_path) - 1):
            from_node = critical_path[i]
            to_node = critical_path[i + 1]
            edge = self._find_edge(dag, from_node, to_node)
            if edge:
                path_details["edges"].append({
                    "id": edge.id,
                    "from": from_node,
                    "to": to_node,
                    "weight": edge.weight
                })

        return path_details

    def _find_node_by_id(self, dag: TaskDAG, node_id: str) -> Optional[DAGNode]:
        """通过ID查找节点"""
        for node in dag.nodes:
            if node.id == node_id:
                return node
        return None

    def _find_edge(self, dag: TaskDAG, from_node: str, to_node: str) -> Optional[DAGEdge]:
        """查找从from_node到to_node的边"""
        for edge in dag.edges:
            if edge.from_node == from_node and edge.to_node == to_node:
                return edge
        return None

    def identify_critical_tasks(self, dag: TaskDAG) -> Dict[str, Any]:
        """
        识别所有关键任务（在任何关键路径上的任务）

        Args:
            dag: 任务DAG

        Returns:
            关键任务信息
        """
        all_paths_result = self.find_all_critical_paths(dag)
        if not all_paths_result["success"]:
            return all_paths_result

        critical_nodes = set()
        for path in all_paths_result["all_critical_paths"]:
            critical_nodes.update(path)

        critical_node_details = []
        for node_id in critical_nodes:
            node = self._find_node_by_id(dag, node_id)
            if node:
                critical_node_details.append({
                    "id": node.id,
                    "name": node.name,
                    "type": node.type
                })

        return {
            "success": True,
            "critical_nodes": list(critical_nodes),
            "critical_node_details": critical_node_details,
            "critical_node_count": len(critical_nodes),
            "all_critical_paths": all_paths_result["all_critical_paths"],
            "message": f"识别到 {len(critical_nodes)} 个关键任务"
        }

    def calculate_slack(self, dag: TaskDAG) -> Dict[str, Any]:
        """
        计算每个任务的松弛时间（slack time）

        Args:
            dag: 任务DAG

        Returns:
            每个任务的松弛时间
        """
        critical_result = self.find_critical_path(dag)
        if not critical_result["success"]:
            return critical_result

        max_length = critical_result["critical_path_length"]
        dist = critical_result["node_distances"]

        # 计算反向最长路径
        reverse_adj = self._build_reverse_adjacency_for_slack(dag)
        reverse_topo_order = list(reversed(critical_result["critical_path"]))
        reverse_dist = self._calculate_reverse_longest_path(dag, reverse_topo_order, reverse_adj)

        slack = {}
        for node in dag.nodes:
            # 松弛时间 = 总长度 - 正向最长路径 - 反向最长路径
            slack[node.id] = max_length - dist.get(node.id, 0.0) - reverse_dist.get(node.id, 0.0)

        return {
            "success": True,
            "slack": slack,
            "critical_path_length": max_length,
            "message": f"成功计算 {len(slack)} 个任务的松弛时间"
        }

    def _build_reverse_adjacency_for_slack(self, dag: TaskDAG) -> Dict[str, List[Tuple[str, float]]]:
        """构建反向邻接表用于计算松弛时间"""
        reverse_adj = {}
        for node in dag.nodes:
            reverse_adj[node.id] = []
        for edge in dag.edges:
            if edge.to_node in reverse_adj:
                reverse_adj[edge.to_node].append((edge.from_node, edge.weight))
        return reverse_adj

    def _calculate_reverse_longest_path(
        self, dag: TaskDAG, reverse_topo_order: List[str], reverse_adj: Dict[str, List[Tuple[str, float]]]
    ) -> Dict[str, float]:
        """计算反向最长路径"""
        dist = {node.id: 0.0 for node in dag.nodes}

        # 先进行完整的拓扑排序
        topo_result = self.topological_sorter.sort(dag)
        if topo_result["success"]:
            full_reverse_order = list(reversed(topo_result["sorted_order"]))
            for node_id in full_reverse_order:
                for neighbor, weight in reverse_adj.get(node_id, []):
                    if dist[neighbor] < dist[node_id] + weight:
                        dist[neighbor] = dist[node_id] + weight

        return dist
