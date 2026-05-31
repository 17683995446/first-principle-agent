from typing import Any, Dict, List, Optional, Set, Tuple
from ..core import TaskDAG, DAGNode, DAGEdge
from .cycle_detector import CycleDetector


class TopologicalSorter:
    """DAG拓扑排序器 - 对任务DAG进行拓扑排序"""

    def __init__(self):
        self.cycle_detector = CycleDetector()

    def sort(self, dag: TaskDAG) -> Dict[str, Any]:
        """
        对DAG进行拓扑排序

        Args:
            dag: 任务DAG

        Returns:
            包含排序结果的字典
        """
        cycle_result = self.cycle_detector.detect_cycles(dag)
        if cycle_result["has_cycle"]:
            return {
                "success": False,
                "sorted_order": [],
                "message": f"无法进行拓扑排序：DAG中存在 {cycle_result['cycle_count']} 个环",
                "cycles": cycle_result["cycles"]
            }

        in_degree = self._calculate_in_degree(dag)
        queue = self._get_zero_in_degree_nodes(in_degree)
        sorted_order = []

        node_in_degree = in_degree.copy()
        dag_edges = [(edge.from_node, edge.to_node) for edge in dag.edges]

        while queue:
            node_id = queue.pop(0)
            sorted_order.append(node_id)

            for from_node, to_node in dag_edges:
                if from_node == node_id:
                    node_in_degree[to_node] -= 1
                    if node_in_degree[to_node] == 0 and to_node not in sorted_order:
                        queue.append(to_node)

        if len(sorted_order) != len(dag.nodes):
            return {
                "success": False,
                "sorted_order": sorted_order,
                "message": "拓扑排序不完整，可能存在环"
            }

        return {
            "success": True,
            "sorted_order": sorted_order,
            "message": f"成功完成拓扑排序，共 {len(sorted_order)} 个节点"
        }

    def _calculate_in_degree(self, dag: TaskDAG) -> Dict[str, int]:
        """计算每个节点的入度"""
        in_degree = {node.id: 0 for node in dag.nodes}
        for edge in dag.edges:
            in_degree[edge.to_node] += 1
        return in_degree

    def _get_zero_in_degree_nodes(self, in_degree: Dict[str, int]) -> List[str]:
        """获取入度为0的节点列表"""
        return [node_id for node_id, degree in in_degree.items() if degree == 0]

    def get_levels(self, dag: TaskDAG) -> Dict[str, int]:
        """
        获取每个节点的层级（从0开始）

        Args:
            dag: 任务DAG

        Returns:
            节点ID到层级的映射
        """
        cycle_result = self.cycle_detector.detect_cycles(dag)
        if cycle_result["has_cycle"]:
            return {}

        node_dependencies = self._build_dependencies_map(dag)
        node_dependents = self._build_dependents_map(dag)

        source_nodes = [node.id for node in dag.nodes if not node_dependencies.get(node.id, [])]
        sink_nodes = [node.id for node in dag.nodes if not node_dependents.get(node.id, [])]

        levels = {}

        def calculate_level(node_id: str, visited: Set[str]) -> int:
            if node_id in levels:
                return levels[node_id]

            if node_id in visited:
                return 0

            visited.add(node_id)

            deps = node_dependencies.get(node_id, [])
            if not deps:
                levels[node_id] = 0
            else:
                max_dep_level = 0
                for dep in deps:
                    dep_level = calculate_level(dep, visited)
                    max_dep_level = max(max_dep_level, dep_level)
                levels[node_id] = max_dep_level + 1

            visited.remove(node_id)
            return levels[node_id]

        for node in dag.nodes:
            calculate_level(node.id, set())

        return levels

    def _build_dependents_map(self, dag: TaskDAG) -> Dict[str, List[str]]:
        """构建节点被依赖关系映射（从节点到依赖它的节点列表）"""
        dependents = {node.id: [] for node in dag.nodes}
        for edge in dag.edges:
            if edge.from_node in dependents:
                dependents[edge.from_node].append(edge.to_node)
        return dependents

    def get_parallel_groups(self, dag: TaskDAG) -> List[List[str]]:
        """
        获取可并行执行的节点分组

        Args:
            dag: 任务DAG

        Returns:
            可并行执行的节点分组列表
        """
        levels = self.get_levels(dag)
        if not levels:
            return []

        max_level = max(levels.values()) if levels else 0
        groups = [[] for _ in range(max_level + 1)]

        for node_id, level in levels.items():
            groups[level].append(node_id)

        return groups

    def validate_topological_order(self, dag: TaskDAG, order: List[str]) -> Dict[str, Any]:
        """
        验证拓扑排序是否正确

        Args:
            dag: 任务DAG
            order: 拓扑排序顺序

        Returns:
            验证结果
        """
        if len(order) != len(dag.nodes):
            return {
                "valid": False,
                "message": f"排序长度不匹配：期望 {len(dag.nodes)}，实际 {len(order)}"
            }

        node_set = set(order)
        dag_node_ids = {node.id for node in dag.nodes}
        if node_set != dag_node_ids:
            return {
                "valid": False,
                "message": "排序中的节点与DAG节点不一致"
            }

        position = {node_id: idx for idx, node_id in enumerate(order)}
        edge_violations = []

        for edge in dag.edges:
            if position[edge.from_node] >= position[edge.to_node]:
                edge_violations.append({
                    "from": edge.from_node,
                    "to": edge.to_node,
                    "from_position": position[edge.from_node],
                    "to_position": position[edge.to_node]
                })

        if edge_violations:
            return {
                "valid": False,
                "message": f"发现 {len(edge_violations)} 个违反拓扑顺序的边",
                "violations": edge_violations
            }

        return {
            "valid": True,
            "message": "拓扑排序有效"
        }

    def get_execution_order(self, dag: TaskDAG, start_nodes: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        获取从指定起始节点开始的执行顺序

        Args:
            dag: 任务DAG
            start_nodes: 可选的起始节点列表，默认为源节点

        Returns:
            执行顺序信息
        """
        if start_nodes is None:
            start_nodes = self._find_source_nodes(dag)

        cycle_result = self.cycle_detector.detect_cycles(dag)
        if cycle_result["has_cycle"]:
            return {
                "success": False,
                "message": "DAG中存在环，无法确定执行顺序"
            }

        full_order = self.sort(dag)
        if not full_order["success"]:
            return full_order

        relevant_order = [node for node in full_order["sorted_order"] if node in set(start_nodes) or self._is_reachable_from_start(node, start_nodes, dag)]

        return {
            "success": True,
            "execution_order": relevant_order,
            "start_nodes": start_nodes,
            "message": f"从节点 {start_nodes} 开始的执行顺序，共 {len(relevant_order)} 个节点"
        }

    def _find_source_nodes(self, dag: TaskDAG) -> List[str]:
        """找到源节点（没有入边的节点）"""
        has_incoming = set()
        for edge in dag.edges:
            has_incoming.add(edge.to_node)
        return [node.id for node in dag.nodes if node.id not in has_incoming]

    def _is_reachable_from_start(self, node_id: str, start_nodes: List[str], dag: TaskDAG) -> bool:
        """判断节点是否从起始节点可达"""
        node_dependencies = self._build_dependencies_map(dag)

        def dfs(current: str, visited: Set[str]) -> bool:
            if current in visited:
                return False
            visited.add(current)

            for dep in node_dependencies.get(current, []):
                if dep in start_nodes or dfs(dep, visited):
                    return True
            return False

        return dfs(node_id, set())

    def _build_dependencies_map(self, dag: TaskDAG) -> Dict[str, List[str]]:
        """构建节点依赖映射（从节点到它依赖的节点列表）"""
        dependencies = {node.id: [] for node in dag.nodes}
        for edge in dag.edges:
            if edge.to_node in dependencies:
                dependencies[edge.to_node].append(edge.from_node)
        return dependencies
