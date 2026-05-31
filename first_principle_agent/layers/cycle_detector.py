from typing import Any, Dict, List, Optional, Set, Tuple
from ..core import TaskDAG, DAGNode, DAGEdge


class CycleDetector:
    """DAG环检测器 - 检测任务DAG中的环结构"""

    def __init__(self):
        pass

    def detect_cycles(self, dag: TaskDAG) -> Dict[str, Any]:
        """
        检测DAG中的所有环

        Args:
            dag: 任务DAG

        Returns:
            包含环检测结果的字典
        """
        if not dag.nodes or not dag.edges:
            return {
                "has_cycle": False,
                "cycle_count": 0,
                "cycles": [],
                "message": "DAG为空或无边，无环"
            }

        node_deps = self._build_adjacency_list(dag)
        cycles = self._find_all_cycles(node_deps, dag)

        return {
            "has_cycle": len(cycles) > 0,
            "cycle_count": len(cycles),
            "cycles": cycles,
            "message": f"检测到 {len(cycles)} 个环" if cycles else "未检测到环"
        }

    def _build_adjacency_list(self, dag: TaskDAG) -> Dict[str, List[str]]:
        """构建邻接表（从from_node -> to_nodes）"""
        adjacency = {}
        for node in dag.nodes:
            adjacency[node.id] = []
        for edge in dag.edges:
            if edge.from_node in adjacency:
                adjacency[edge.from_node].append(edge.to_node)
        return adjacency

    def _find_all_cycles(self, adjacency: Dict[str, List[str]], dag: TaskDAG) -> List[List[str]]:
        """查找所有环"""
        cycles = []
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node: str):
            if node in rec_stack:
                idx = path.index(node)
                cycle = path[idx:]
                cycle.append(node)  # 闭合环
                if cycle not in cycles:
                    cycles.append(cycle)
                return
            if node in visited:
                return

            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in adjacency.get(node, []):
                dfs(neighbor)

            path.pop()
            rec_stack.remove(node)

        for node in adjacency.keys():
            if node not in visited:
                dfs(node)

        return cycles

    def has_cycle(self, dag: TaskDAG) -> bool:
        """
        快速检测是否存在环"""
        result = self.detect_cycles(dag)
        return result["has_cycle"]

    def get_cycle_details(self, dag: TaskDAG) -> List[Dict[str, Any]]:
        """
        获取所有环的详细信息

        Args:
            dag: 任务DAG

        Returns:
            环详细信息列表
        """
        cycles = self.detect_cycles(dag)["cycles"]
        cycle_details = []

        for cycle in cycles:
            cycle_info = {
                "path": cycle,
                "length": len(cycle) - 1,
                "nodes": [],
                "edges": []
            }

            for node_id in cycle[:-1]:
                node = self._find_node_by_id(dag, node_id)
                if node:
                    cycle_info["nodes"].append({
                        "id": node.id,
                        "name": node.name
                    })

            for i in range(len(cycle) - 1):
                from_node = cycle[i]
                to_node = cycle[i + 1]
                edge = self._find_edge(dag, from_node, to_node)
                if edge:
                    cycle_info["edges"].append({
                        "id": edge.id,
                        "from": from_node,
                        "to": to_node
                    })

            cycle_details.append(cycle_info)

        return cycle_details

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

    def break_cycles(self, dag: TaskDAG) -> Dict[str, Any]:
        """
        尝试打破环（不修改原DAG，仅提供建议）

        Args:
            dag: 任务DAG

        Returns:
            破环建议
        """
        result = self.detect_cycles(dag)

        if not result["has_cycle"]:
            return {
            "success": True,
            "message": "无环可破",
            "suggestions": []
        }

        suggestions = []
        cycles = result["cycles"]

        for cycle in cycles:
            suggestion = {
                "cycle_path": cycle,
                "suggested_break_edges": [],
                "reason": "环会导致任务无法执行，建议移除一条边"
            }

            if len(cycle) >= 2:
                from_node = cycle[0]
                to_node = cycle[1]
                suggestion["suggested_break_edges"].append({
                    "from": from_node,
                    "to": to_node,
                    "edge_id": self._find_edge(dag, from_node, to_node)
                })

            suggestions.append(suggestion)

        return {
            "success": False,
            "message": f"检测到 {len(cycles)} 个环",
            "suggestions": suggestions
        }

    def validate_dag(self, dag: TaskDAG) -> Dict[str, Any]:
        """
        验证DAG是否真的是一个DAG（无环）

        Args:
            dag: 任务DAG

        Returns:
            验证结果
        """
        cycle_result = self.detect_cycles(dag)
        is_dag = not cycle_result["has_cycle"]

        return {
            "is_dag": is_dag,
            "cycle_check": cycle_result,
            "node_count": len(dag.nodes),
            "edge_count": len(dag.edges),
            "message": "这是一个有效的DAG" if is_dag else "这不是一个有效的DAG，存在环"
        }
