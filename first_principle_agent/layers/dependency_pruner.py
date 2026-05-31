from typing import Any, Dict, List, Optional, Set, Tuple
from ..core import TaskDAG, DAGNode, DAGEdge
from .dependency_analyzer import DependencyAnalyzer


class DependencyPruner:
    """DAG冗余依赖裁剪器 - 移除DAG中的冗余依赖"""

    def __init__(self):
        self.dependency_analyzer = DependencyAnalyzer()

    def prune(self, dag: TaskDAG) -> Dict[str, Any]:
        """
        裁剪DAG中的冗余依赖

        Args:
            dag: 任务DAG

        Returns:
            包含裁剪结果的字典
        """
        redundant_edges = self._find_redundant_edges(dag)

        pruned_edges = []
        for edge in dag.edges:
            if not self._is_redundant(edge, redundant_edges):
                pruned_edges.append(edge)

        pruned_dag = TaskDAG(
            dag_id=dag.id + "_pruned",
            nodes=dag.nodes.copy(),
            edges=pruned_edges,
            metadata=dag.metadata.copy(),
            critical_path=dag.critical_path.copy() if dag.critical_path else [],
            parallel_groups=dag.parallel_groups.copy() if dag.parallel_groups else {}
        )

        return {
            "success": True,
            "original_edge_count": len(dag.edges),
            "pruned_edge_count": len(dag.edges) - len(pruned_edges),
            "remaining_edge_count": len(pruned_edges),
            "redundant_edges": redundant_edges,
            "pruned_dag": pruned_dag,
            "message": f"裁剪了 {len(dag.edges) - len(pruned_edges)} 条冗余依赖"
        }

    def _find_redundant_edges(self, dag: TaskDAG) -> List[DAGEdge]:
        """找出所有冗余边"""
        redundant = []
        adjacency = self._build_adjacency(dag)

        for edge in dag.edges:
            from_node = edge.from_node
            to_node = edge.to_node

            # 如果存在从from_node到to_node的替代路径（不经过这条边），则这条边是冗余的
            if self._has_alternative_path(dag, from_node, to_node, edge.id, adjacency):
                redundant.append(edge)

        return redundant

    def _is_redundant(self, edge: DAGEdge, redundant_edges: List[DAGEdge]) -> bool:
        """判断边是否冗余"""
        for redundant in redundant_edges:
            if redundant.id == edge.id:
                return True
        return False

    def _build_adjacency(self, dag: TaskDAG) -> Dict[str, List[str]]:
        """构建邻接表"""
        adjacency = {}
        for node in dag.nodes:
            adjacency[node.id] = []
        for edge in dag.edges:
            if edge.from_node in adjacency:
                adjacency[edge.from_node].append(edge.to_node)
        return adjacency

    def _has_alternative_path(
        self, dag: TaskDAG, from_node: str, to_node: str, exclude_edge_id: str, adjacency: Dict[str, List[str]]
    ) -> bool:
        """检查是否存在替代路径（不经过指定的边）"""
        visited = set()
        queue = [from_node]

        while queue:
            current = queue.pop(0)
            if current == to_node:
                return True
            if current in visited:
                continue
            visited.add(current)

            for neighbor in adjacency.get(current, []):
                edge = self._find_edge_by_nodes(dag, current, neighbor)
                if edge and edge.id != exclude_edge_id:
                    queue.append(neighbor)

        return False

    def _find_edge_by_nodes(self, dag: TaskDAG, from_node: str, to_node: str) -> Optional[DAGEdge]:
        """通过节点对查找边"""
        for edge in dag.edges:
            if edge.from_node == from_node and edge.to_node == to_node:
                return edge
        return None

    def find_transitive_dependencies(self, dag: TaskDAG) -> Dict[str, List[str]]:
        """
        找出每个节点的传递依赖闭包

        Args:
            dag: 任务DAG

        Returns:
            每个节点的传递依赖字典
        """
        transitive_deps = {}

        for node in dag.nodes:
            node_id = node.id
            deps = self._get_all_dependencies(dag, node_id)
            transitive_deps[node_id] = deps

        return transitive_deps

    def _get_all_dependencies(self, dag: TaskDAG, node_id: str) -> List[str]:
        """获取节点的所有传递依赖"""
        all_deps = []
        visited = set()
        queue = [node_id]

        adjacency = self._build_dependency_adjacency(dag)

        while queue:
            current = queue.pop(0)
            for dep in adjacency.get(current, []):
                if dep not in visited:
                    visited.add(dep)
                    all_deps.append(dep)
                    queue.append(dep)

        return all_deps

    def _build_dependency_adjacency(self, dag: TaskDAG) -> Dict[str, List[str]]:
        """构建依赖邻接表（从被依赖者到依赖者）"""
        adjacency = {}
        for node in dag.nodes:
            adjacency[node.id] = []
        for edge in dag.edges:
            if edge.to_node in adjacency:
                adjacency[edge.to_node].append(edge.from_node)
        return adjacency

    def optimize(self, dag: TaskDAG) -> Dict[str, Any]:
        """
        优化DAG结构

        Args:
            dag: 任务DAG

        Returns:
            优化结果
        """
        prune_result = self.prune(dag)

        # 检查是否有重复边
        duplicate_edges = self._find_duplicate_edges(dag)

        # 检查是否有自环
        self_loops = self._find_self_loops(dag)

        optimized_edges = []
        seen_pairs = set()

        for edge in prune_result["pruned_dag"].edges:
            pair = (edge.from_node, edge.to_node)
            if pair not in seen_pairs:
                seen_pairs.add(pair)
                if edge.from_node != edge.to_node:
                    optimized_edges.append(edge)

        optimized_dag = TaskDAG(
            dag_id=dag.id + "_optimized",
            nodes=dag.nodes.copy(),
            edges=optimized_edges,
            metadata=dag.metadata.copy(),
            critical_path=dag.critical_path.copy() if dag.critical_path else [],
            parallel_groups=dag.parallel_groups.copy() if dag.parallel_groups else {}
        )

        return {
            "success": True,
            "original_edge_count": len(dag.edges),
            "optimized_edge_count": len(optimized_edges),
            "edges_removed": len(dag.edges) - len(optimized_edges),
            "redundant_edges_pruned": prune_result["pruned_edge_count"],
            "duplicate_edges_removed": len(duplicate_edges),
            "self_loops_removed": len(self_loops),
            "optimized_dag": optimized_dag,
            "optimization_details": {
                "redundant_edges": [e.id for e in prune_result["redundant_edges"]],
                "duplicate_edges": duplicate_edges,
                "self_loops": self_loops
            },
            "message": f"优化完成：移除了 {len(dag.edges) - len(optimized_edges)} 条边"
        }

    def _find_duplicate_edges(self, dag: TaskDAG) -> List[Tuple[str, str]]:
        """找出重复边"""
        seen_pairs = set()
        duplicates = []

        for edge in dag.edges:
            pair = (edge.from_node, edge.to_node)
            if pair in seen_pairs:
                duplicates.append(pair)
            else:
                seen_pairs.add(pair)

        return duplicates

    def _find_self_loops(self, dag: TaskDAG) -> List[str]:
        """找出自环"""
        self_loops = []

        for edge in dag.edges:
            if edge.from_node == edge.to_node:
                self_loops.append(edge.id)

        return self_loops

    def validate_optimization(self, original_dag: TaskDAG, optimized_dag: TaskDAG) -> Dict[str, Any]:
        """
        验证优化是否正确（优化后的DAG与原DAG等效）

        Args:
            original_dag: 原始DAG
            optimized_dag: 优化后的DAG

        Returns:
            验证结果
        """
        # 检查节点是否一致
        original_nodes = {n.id for n in original_dag.nodes}
        optimized_nodes = {n.id for n in optimized_dag.nodes}

        if original_nodes != optimized_nodes:
            return {
                "valid": False,
                "message": "节点不一致",
                "missing_in_optimized": original_nodes - optimized_nodes,
                "extra_in_optimized": optimized_nodes - original_nodes
            }

        # 检查依赖关系是否保持
        for node in original_dag.nodes:
            original_deps = self.dependency_analyzer.get_full_dependency_chain(original_dag, node.id)
            optimized_deps = self.dependency_analyzer.get_full_dependency_chain(optimized_dag, node.id)

            original_set = set(original_deps)
            optimized_set = set(optimized_deps)

            if original_set != optimized_set:
                return {
                    "valid": False,
                    "message": f"节点 {node.id} 的依赖关系发生了变化",
                    "original_deps": original_set,
                    "optimized_deps": optimized_set
                }

        return {
            "valid": True,
            "message": "优化正确，依赖关系保持不变"
        }

    def get_dependency_closure(self, dag: TaskDAG) -> Dict[str, Dict[str, Any]]:
        """
        获取完整的依赖闭包信息

        Args:
            dag: 任务DAG

        Returns:
            依赖闭包详细信息
        """
        closure = {}

        for node in dag.nodes:
            node_id = node.id
            direct_deps = self.dependency_analyzer.get_node_dependencies(dag, node_id)
            all_deps = self._get_all_dependencies(dag, node_id)

            closure[node_id] = {
                "direct_dependencies": direct_deps,
                "all_dependencies": all_deps,
                "dependency_count": len(direct_deps),
                "total_dependency_count": len(all_deps),
                "redundant_count": len(all_deps) - len(direct_deps)
            }

        return closure

    def suggest_edges_to_add(self, dag: TaskDAG) -> List[Dict[str, str]]:
        """
        建议需要添加的边（用于连接孤岛）

        Args:
            dag: 任务DAG

        Returns:
            建议添加的边列表
        """
        suggestions = []
        analysis = self.dependency_analyzer.analyze_dependencies(dag)
        islands = analysis.get("islands", [])

        if len(islands) <= 1:
            return suggestions

        for i in range(len(islands) - 1):
            current_island = islands[i]
            next_island = islands[i + 1]

            last_node_of_current = current_island[-1]
            first_node_of_next = next_island[0]

            suggestions.append({
                "from_node": last_node_of_current,
                "to_node": first_node_of_next,
                "reason": f"连接孤岛 {i+1} 和 {i+2}"
            })

        return suggestions
