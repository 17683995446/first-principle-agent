from typing import Any, Dict, List, Optional, Set
from ..core import TaskDAG, DAGNode, DAGEdge


class DependencyAnalyzer:
    """DAG依赖分析器 - 分析节点之间的依赖关系"""

    def __init__(self):
        pass

    def analyze_dependencies(self, dag: TaskDAG) -> Dict[str, Any]:
        """
        分析DAG的所有依赖关系

        Args:
            dag: 任务DAG

        Returns:
            包含依赖分析结果的字典
        """
        analysis_result = {
            "node_count": len(dag.nodes),
            "edge_count": len(dag.edges),
            "node_dependencies": self._build_node_dependencies(dag),
            "node_dependents": self._build_node_dependents(dag),
            "islands": self._find_islands(dag),
            "source_nodes": self._find_source_nodes(dag),
            "sink_nodes": self._find_sink_nodes(dag),
            "longest_path_length": self._calculate_longest_path_length(dag)
        }
        return analysis_result

    def _build_node_dependencies(self, dag: TaskDAG) -> Dict[str, List[str]]:
        """构建每个节点的直接依赖列表"""
        dependencies = {}
        for node in dag.nodes:
            node_id = node.id
            deps = []
            for edge in dag.edges:
                if edge.to_node == node_id:
                    deps.append(edge.from_node)
            dependencies[node_id] = deps
        return dependencies

    def _build_node_dependents(self, dag: TaskDAG) -> Dict[str, List[str]]:
        """构建每个节点的被依赖列表"""
        dependents = {}
        for node in dag.nodes:
            node_id = node.id
            deps = []
            for edge in dag.edges:
                if edge.from_node == node_id:
                    deps.append(edge.to_node)
            dependents[node_id] = deps
        return dependents

    def _find_islands(self, dag: TaskDAG) -> List[List[str]]:
        """找到DAG中的孤岛（不连通的子图）"""
        if not dag.nodes:
            return []

        visited = set()
        islands = []

        node_ids = [node.id for node in dag.nodes]
        node_dependencies = self._build_node_dependencies(dag)
        node_dependents = self._build_node_dependents(dag)

        for node_id in node_ids:
            if node_id not in visited:
                island = self._dfs_traverse(node_id, node_dependencies, node_dependents, visited)
                islands.append(island)

        return islands

    def _dfs_traverse(self, node_id: str, node_deps: Dict[str, List[str]], node_deps_of: Dict[str, List[str]], visited: Set[str]) -> List[str]:
        """深度优先遍历，找到连通的节点"""
        stack = [node_id]
        component = []
        while stack:
            current = stack.pop()
            if current not in visited:
                visited.add(current)
                component.append(current)
                for dep in node_deps.get(current, []):
                    if dep not in visited:
                        stack.append(dep)
                for dep_of in node_deps_of.get(current, []):
                    if dep_of not in visited:
                        stack.append(dep_of)
        return component

    def _find_source_nodes(self, dag: TaskDAG) -> List[str]:
        """找到源节点（没有入边的节点）"""
        node_ids = [node.id for node in dag.nodes]
        has_incoming = set()
        for edge in dag.edges:
            has_incoming.add(edge.to_node)
        source_nodes = [nid for nid in node_ids if nid not in has_incoming]
        return source_nodes

    def _find_sink_nodes(self, dag: TaskDAG) -> List[str]:
        """找到汇节点（没有出边的节点）"""
        node_ids = [node.id for node in dag.nodes]
        has_outgoing = set()
        for edge in dag.edges:
            has_outgoing.add(edge.from_node)
        sink_nodes = [nid for nid in node_ids if nid not in has_outgoing]
        return sink_nodes

    def _calculate_longest_path_length(self, dag: TaskDAG) -> int:
        """计算DAG中最长路径的长度（边数）"""
        if not dag.nodes:
            return 0

        node_dependencies = self._build_node_dependencies(dag)
        node_dependents = self._build_node_dependents(dag)
        source_nodes = self._find_source_nodes(dag)

        max_length = 0
        for source in source_nodes:
            length = self._dfs_path_length(source, node_dependents)
            if length > max_length:
                max_length = length
        return max_length

    def _dfs_path_length(self, current: str, node_deps_of: Dict[str, List[str]]) -> int:
        """计算从当前节点出发的最长路径长度"""
        max_len = 0
        for next_node in node_deps_of.get(current, []):
            path_len = 1 + self._dfs_path_length(next_node, node_deps_of)
            if path_len > max_len:
                max_len = path_len
        return max_len

    def get_node_dependencies(self, dag: TaskDAG, node_id: str) -> List[str]:
        """获取指定节点的直接依赖"""
        dependencies = self._build_node_dependencies(dag)
        return dependencies.get(node_id, [])

    def get_node_dependents(self, dag: TaskDAG, node_id: str) -> List[str]:
        """获取指定节点的被依赖节点"""
        dependents = self._build_node_dependents(dag)
        return dependents.get(node_id, [])

    def get_full_dependency_chain(self, dag: TaskDAG, node_id: str) -> List[str]:
        """获取指定节点的完整依赖链（包括间接依赖）"""
        all_deps = []
        visited = set()
        stack = [node_id]
        node_deps = self._build_node_dependencies(dag)

        while stack:
            current = stack.pop()
            if current not in visited:
                visited.add(current)
                if current != node_id:
                    all_deps.append(current)
                for dep in node_deps.get(current, []):
                    if dep not in visited:
                        stack.append(dep)

        return all_deps

    def get_full_dependent_chain(self, dag: TaskDAG, node_id: str) -> List[str]:
        """获取指定节点的完整被依赖链（包括间接依赖）"""
        all_deps = []
        visited = set()
        stack = [node_id]
        node_deps_of = self._build_node_dependents(dag)

        while stack:
            current = stack.pop()
            if current not in visited:
                visited.add(current)
                if current != node_id:
                    all_deps.append(current)
                for dep in node_deps_of.get(current, []):
                    if dep not in visited:
                        stack.append(dep)

        return all_deps

    def has_cycle(self, dag: TaskDAG) -> bool:
        """初步判断是否可能存在环（基于节点入度变化检查）"""
        if not dag.nodes or not dag.edges:
            return False

        node_deps = self._build_node_dependencies(dag)
        temp_deps = {nid: deps.copy() for nid, deps in node_deps.items()}
        node_ids = [node.id for node in dag.nodes]
        processed = 0

        while node_ids:
            updated = False
            for nid in list(node_ids):
                if len(temp_deps.get(nid, [])) == 0:
                    processed += 1
                    node_ids.remove(nid)
                    for other in node_ids:
                        if nid in temp_deps.get(other, []):
                            temp_deps[other].remove(nid)
                            updated = True
            if not updated:
                break

        return processed < len(temp_deps)
