from typing import Any, Dict, List, Optional
from ..core import TaskDAG, TaskTuple
from .dag_builder import DAGBuilder
from .dependency_analyzer import DependencyAnalyzer
from .cycle_detector import CycleDetector
from .topological_sorter import TopologicalSorter
from .critical_path_finder import CriticalPathFinder
from .dag_validator import DAGValidator
from .dependency_pruner import DependencyPruner


class TaskPlanner:
    """任务规划器 - 整合拓扑依赖拆解层的所有组件"""

    def __init__(self):
        self.dag_builder = DAGBuilder()
        self.dependency_analyzer = DependencyAnalyzer()
        self.cycle_detector = CycleDetector()
        self.topological_sorter = TopologicalSorter()
        self.critical_path_finder = CriticalPathFinder()
        self.dag_validator = DAGValidator()
        self.dependency_pruner = DependencyPruner()

    def plan(self, task_tuple: TaskTuple, optimize: bool = True) -> Dict[str, Any]:
        """
        执行完整的任务规划流程

        Args:
            task_tuple: 任务四元组
            optimize: 是否优化DAG

        Returns:
            包含规划结果的字典
        """
        results = {
            "success": True,
            "task_tuple_id": task_tuple.target if hasattr(task_tuple, 'target') else "unknown",
            "steps": [],
            "dag": None,
            "validation": None,
            "critical_path": None,
            "execution_order": None,
            "optimization": None,
            "errors": []
        }

        try:
            results["steps"].append({
                "step": "构建DAG",
                "status": "pending"
            })

            dag = self.dag_builder.build_from_task_tuple(task_tuple)
            results["steps"].append({
                "step": "构建DAG",
                "status": "success",
                "message": f"构建了包含 {len(dag.nodes)} 个节点和 {len(dag.edges)} 条边的DAG"
            })
            results["dag"] = dag

            results["steps"].append({
                "step": "验证DAG",
                "status": "pending"
            })

            validation = self.dag_validator.validate(dag)
            results["validation"] = validation

            if not validation["valid"]:
                results["success"] = False
                results["errors"].extend(validation["errors"])
                results["steps"].append({
                    "step": "验证DAG",
                    "status": "failed",
                    "errors": validation["errors"]
                })
                return results

            results["steps"].append({
                "step": "验证DAG",
                "status": "success",
                "message": "DAG验证通过"
            })

            if optimize:
                results["steps"].append({
                    "step": "优化DAG",
                    "status": "pending"
                })

                optimization = self.dependency_pruner.optimize(dag)
                results["optimization"] = optimization
                dag = optimization["optimized_dag"]
                results["dag"] = dag

                results["steps"].append({
                    "step": "优化DAG",
                    "status": "success",
                    "message": optimization["message"]
                })

            results["steps"].append({
                "step": "分析关键路径",
                "status": "pending"
            })

            critical_path = self.critical_path_finder.find_critical_path(dag)
            results["critical_path"] = critical_path

            results["steps"].append({
                "step": "分析关键路径",
                "status": "success",
                "message": f"关键路径长度为 {critical_path.get('critical_path_length', 0)}"
            })

            results["steps"].append({
                "step": "计算执行顺序",
                "status": "pending"
            })

            topo_result = self.topological_sorter.sort(dag)
            results["execution_order"] = topo_result

            results["steps"].append({
                "step": "计算执行顺序",
                "status": "success",
                "message": f"执行顺序包含 {len(topo_result['sorted_order'])} 个节点"
            })

            results["message"] = "任务规划完成"

        except Exception as e:
            results["success"] = False
            results["errors"].append(str(e))
            results["steps"].append({
                "step": "规划过程",
                "status": "failed",
                "error": str(e)
            })

        return results

    def validate_dag(self, dag: TaskDAG) -> Dict[str, Any]:
        """
        验证DAG

        Args:
            dag: 任务DAG

        Returns:
            验证结果
        """
        return self.dag_validator.validate(dag)

    def get_execution_plan(self, dag: TaskDAG) -> Dict[str, Any]:
        """
        获取执行计划

        Args:
            dag: 任务DAG

        Returns:
            详细的执行计划
        """
        validation = self.dag_validator.validate(dag)
        if not validation["valid"]:
            return {
                "success": False,
                "errors": validation["errors"]
            }

        topo_result = self.topological_sorter.sort(dag)
        if not topo_result["success"]:
            return {
                "success": False,
                "errors": [topo_result.get("message", "拓扑排序失败")]
            }

        levels = self.topological_sorter.get_levels(dag)
        parallel_groups = self.topological_sorter.get_parallel_groups(dag)
        critical_path = self.critical_path_finder.find_critical_path(dag)

        return {
            "success": True,
            "execution_order": topo_result["sorted_order"],
            "parallel_groups": parallel_groups,
            "levels": levels,
            "critical_path": critical_path,
            "node_count": len(dag.nodes),
            "edge_count": len(dag.edges),
            "estimated_parallelism": len(parallel_groups),
            "message": f"执行计划包含 {len(topo_result['sorted_order'])} 个节点，分为 {len(parallel_groups)} 个层级"
        }

    def suggest_improvements(self, dag: TaskDAG) -> List[Dict[str, Any]]:
        """
        建议DAG改进

        Args:
            dag: 任务DAG

        Returns:
            改进建议列表
        """
        suggestions = []

        validation = self.dag_validator.validate(dag, strict=False)
        if not validation["valid"]:
            for error in validation["errors"]:
                suggestions.append({
                    "type": "error",
                    "message": error
                })

        for warning in validation.get("warnings", []):
            suggestions.append({
                "type": "warning",
                "message": warning
            })

        optimization = self.dependency_pruner.optimize(dag)
        if optimization["edges_removed"] > 0:
            suggestions.append({
                "type": "optimization",
                "message": f"可以优化 {optimization['edges_removed']} 条边以提高效率"
            })

        analysis = self.dependency_analyzer.analyze_dependencies(dag)
        if analysis.get("islands") and len(analysis["islands"]) > 1:
            suggestions.append({
                "type": "warning",
                "message": f"发现 {len(analysis['islands'])} 个孤岛，建议连接以提高并行性"
            })

        critical_path = self.critical_path_finder.find_critical_path(dag)
        if critical_path["success"]:
            critical_nodes = critical_path.get("critical_path", [])
            if len(critical_nodes) > 5:
                suggestions.append({
                    "type": "info",
                    "message": f"关键路径较长（{len(critical_nodes)} 个节点），考虑是否可以进一步并行化"
                })

        return suggestions

    def compare_dags(self, dag1: TaskDAG, dag2: TaskDAG) -> Dict[str, Any]:
        """
        比较两个DAG

        Args:
            dag1: 第一个DAG
            dag2: 第二个DAG

        Returns:
            比较结果
        """
        comparison = {
            "node_count_diff": len(dag1.nodes) - len(dag2.nodes),
            "edge_count_diff": len(dag1.edges) - len(dag2.edges),
            "dag1_nodes": len(dag1.nodes),
            "dag2_nodes": len(dag2.nodes),
            "dag1_edges": len(dag1.edges),
            "dag2_edges": len(dag2.edges),
            "similarity": self._calculate_similarity(dag1, dag2)
        }

        return comparison

    def _calculate_similarity(self, dag1: TaskDAG, dag2: TaskDAG) -> float:
        """计算两个DAG的相似度"""
        if not dag1.nodes or not dag2.nodes:
            return 0.0

        nodes1 = {n.id for n in dag1.nodes}
        nodes2 = {n.id for n in dag2.nodes}

        common_nodes = len(nodes1 & nodes2)
        total_nodes = len(nodes1 | nodes2)

        if total_nodes == 0:
            return 0.0

        node_similarity = common_nodes / total_nodes

        edges1 = {(e.from_node, e.to_node) for e in dag1.edges}
        edges2 = {(e.from_node, e.to_node) for e in dag2.edges}

        common_edges = len(edges1 & edges2)
        total_edges = len(edges1 | edges2)

        if total_edges == 0:
            return node_similarity

        edge_similarity = common_edges / total_edges

        return (node_similarity + edge_similarity) / 2

    def generate_report(self, dag: TaskDAG) -> str:
        """
        生成DAG报告

        Args:
            dag: 任务DAG

        Returns:
            格式化的报告
        """
        lines = []
        lines.append("=" * 60)
        lines.append("任务规划报告")
        lines.append("=" * 60)
        lines.append("")

        lines.append(f"DAG ID: {dag.id}")
        lines.append(f"节点数: {len(dag.nodes)}")
        lines.append(f"边数: {len(dag.edges)}")
        lines.append("")

        validation = self.dag_validator.validate(dag)
        lines.append(f"验证状态: {'✅ 通过' if validation['valid'] else '❌ 失败'}")
        lines.append("")

        if not validation["valid"]:
            lines.append("错误:")
            for error in validation["errors"]:
                lines.append(f"  - {error}")
            lines.append("")

        if validation.get("warnings"):
            lines.append("警告:")
            for warning in validation["warnings"]:
                lines.append(f"  - {warning}")
            lines.append("")

        topo_result = self.topological_sorter.sort(dag)
        if topo_result["success"]:
            lines.append("执行顺序:")
            for i, node_id in enumerate(topo_result["sorted_order"], 1):
                lines.append(f"  {i}. {node_id}")
            lines.append("")

        parallel_groups = self.topological_sorter.get_parallel_groups(dag)
        if parallel_groups:
            lines.append("并行分组:")
            for i, group in enumerate(parallel_groups, 1):
                lines.append(f"  层级 {i}: {', '.join(group)}")
            lines.append("")

        critical_path = self.critical_path_finder.find_critical_path(dag)
        if critical_path["success"]:
            lines.append(f"关键路径: {' → '.join(critical_path['critical_path'])}")
            lines.append(f"关键路径长度: {critical_path['critical_path_length']}")
            lines.append("")

        suggestions = self.suggest_improvements(dag)
        if suggestions:
            lines.append("改进建议:")
            for suggestion in suggestions:
                lines.append(f"  [{suggestion['type'].upper()}] {suggestion['message']}")
            lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)
