from typing import Any, Dict, List, Optional, Set
from ..core import TaskDAG, DAGNode, DAGEdge
from .cycle_detector import CycleDetector
from .topological_sorter import TopologicalSorter
from .dependency_analyzer import DependencyAnalyzer


class DAGValidator:
    """DAG综合验证器 - 验证DAG的完整性和有效性"""

    def __init__(self):
        self.cycle_detector = CycleDetector()
        self.topological_sorter = TopologicalSorter()
        self.dependency_analyzer = DependencyAnalyzer()

    def validate(self, dag: TaskDAG, strict: bool = False) -> Dict[str, Any]:
        """
        对DAG进行完整验证

        Args:
            dag: 任务DAG
            strict: 是否严格模式（严格模式会检查所有规则）

        Returns:
            包含验证结果的字典
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "checks": {}
        }

        # 1. 基础结构验证
        structure_result = self._validate_structure(dag)
        results["checks"]["structure"] = structure_result
        if not structure_result["valid"]:
            results["valid"] = False
            results["errors"].extend(structure_result["errors"])

        # 2. 无环验证
        if structure_result["valid"]:
            no_cycle_result = self._validate_no_cycles(dag)
            results["checks"]["no_cycles"] = no_cycle_result
            if not no_cycle_result["valid"]:
                results["valid"] = False
                results["errors"].extend(no_cycle_result["errors"])

        # 3. 连通性验证
        if structure_result["valid"]:
            connectivity_result = self._validate_connectivity(dag)
            results["checks"]["connectivity"] = connectivity_result
            if not connectivity_result["valid"]:
                results["valid"] = False
                results["errors"].extend(connectivity_result["errors"])

        # 4. 依赖完备性验证
        if structure_result["valid"] and strict:
            completeness_result = self._validate_dependency_completeness(dag)
            results["checks"]["dependency_completeness"] = completeness_result
            if not completeness_result["valid"]:
                results["valid"] = False
                results["errors"].extend(completeness_result["errors"])

        # 5. 并行性验证
        if structure_result["valid"] and strict:
            parallelism_result = self._validate_parallelism(dag)
            results["checks"]["parallelism"] = parallelism_result
            if not parallelism_result["valid"]:
                results["warnings"].extend(parallelism_result["warnings"])

        # 6. 自环验证
        if structure_result["valid"]:
            self_loop_result = self._validate_no_self_loops(dag)
            results["checks"]["no_self_loops"] = self_loop_result
            if not self_loop_result["valid"]:
                results["valid"] = False
                results["errors"].extend(self_loop_result["errors"])

        # 7. 重复边验证
        if structure_result["valid"]:
            duplicate_result = self._validate_no_duplicate_edges(dag)
            results["checks"]["no_duplicate_edges"] = duplicate_result
            if not duplicate_result["valid"]:
                results["warnings"].extend(duplicate_result["warnings"])

        # 8. 孤立节点验证
        if structure_result["valid"]:
            isolated_result = self._validate_no_isolated_nodes(dag)
            results["checks"]["no_isolated_nodes"] = isolated_result
            if not isolated_result["valid"]:
                if strict:
                    results["valid"] = False
                    results["errors"].extend(isolated_result["errors"])
                else:
                    results["warnings"].extend(isolated_result["warnings"])

        # 汇总消息
        results["message"] = self._generate_summary(results)

        return results

    def _validate_structure(self, dag: TaskDAG) -> Dict[str, Any]:
        """验证基础结构"""
        errors = []

        if not dag.nodes:
            errors.append("DAG没有节点")
            return {"valid": False, "errors": errors}

        # 检查节点ID唯一性
        node_ids = [node.id for node in dag.nodes]
        if len(node_ids) != len(set(node_ids)):
            errors.append("存在重复的节点ID")
            return {"valid": False, "errors": errors}

        # 检查边引用的节点是否存在
        node_set = set(node_ids)
        for edge in dag.edges:
            if edge.from_node not in node_set:
                errors.append(f"边 {edge.id} 引用了不存在的起始节点 {edge.from_node}")
            if edge.to_node not in node_set:
                errors.append(f"边 {edge.id} 引用了不存在的目标节点 {edge.to_node}")

        # 检查边ID唯一性
        if dag.edges:
            edge_ids = [edge.id for edge in dag.edges]
            if len(edge_ids) != len(set(edge_ids)):
                errors.append("存在重复的边ID")

        return {"valid": len(errors) == 0, "errors": errors}

    def _validate_no_cycles(self, dag: TaskDAG) -> Dict[str, Any]:
        """验证无环"""
        cycle_result = self.cycle_detector.detect_cycles(dag)
        if cycle_result["has_cycle"]:
            return {
                "valid": False,
                "errors": [f"DAG中存在 {cycle_result['cycle_count']} 个环"],
                "cycles": cycle_result["cycles"]
            }
        return {"valid": True, "errors": [], "cycles": []}

    def _validate_connectivity(self, dag: TaskDAG) -> Dict[str, Any]:
        """验证连通性"""
        analysis = self.dependency_analyzer.analyze_dependencies(dag)
        islands = analysis.get("islands", [])

        if len(islands) > 1:
            return {
                "valid": False,
                "errors": [f"DAG不连通，存在 {len(islands)} 个孤岛"],
                "islands": islands
            }
        return {"valid": True, "errors": [], "islands": []}

    def _validate_dependency_completeness(self, dag: TaskDAG) -> Dict[str, Any]:
        """验证依赖完备性"""
        errors = []

        # 检查每个节点的依赖是否都存在
        for node in dag.nodes:
            dependencies = self.dependency_analyzer.get_node_dependencies(dag, node.id)
            for dep in dependencies:
                dep_exists = any(n.id == dep for n in dag.nodes)
                if not dep_exists:
                    errors.append(f"节点 {node.id} 依赖的节点 {dep} 不存在")

        return {"valid": len(errors) == 0, "errors": errors}

    def _validate_parallelism(self, dag: TaskDAG) -> Dict[str, Any]:
        """验证并行性约束"""
        warnings = []

        # 检查并行组内是否有依赖关系
        if dag.parallel_groups:
            for group_id, node_ids in dag.parallel_groups.items():
                for i, node_a in enumerate(node_ids):
                    for node_b in node_ids[i + 1:]:
                        # 检查是否有依赖关系
                        if self._has_path(dag, node_a, node_b) or self._has_path(dag, node_b, node_a):
                            warnings.append(
                                f"并行组 '{group_id}' 中的任务 {node_a} 和 {node_b} "
                                f"存在依赖关系，不能并行执行"
                            )

        return {"valid": len(warnings) == 0, "warnings": warnings}

    def _validate_no_self_loops(self, dag: TaskDAG) -> Dict[str, Any]:
        """验证无自环"""
        errors = []

        for edge in dag.edges:
            if edge.from_node == edge.to_node:
                errors.append(f"边 {edge.id} 存在自环（{edge.from_node} → {edge.to_node}）")

        return {"valid": len(errors) == 0, "errors": errors}

    def _validate_no_duplicate_edges(self, dag: TaskDAG) -> Dict[str, Any]:
        """验证无重复边"""
        warnings = []
        edge_pairs = set()

        for edge in dag.edges:
            pair = (edge.from_node, edge.to_node)
            if pair in edge_pairs:
                warnings.append(f"存在重复边：{edge.from_node} → {edge.to_node}")
            else:
                edge_pairs.add(pair)

        return {"valid": len(warnings) == 0, "warnings": warnings}

    def _validate_no_isolated_nodes(self, dag: TaskDAG) -> Dict[str, Any]:
        """验证无孤立节点"""
        errors = []
        warnings = []

        node_dependencies = self.dependency_analyzer._build_node_dependencies(dag)
        node_dependents = self.dependency_analyzer._build_node_dependents(dag)

        for node in dag.nodes:
            has_deps = len(node_dependencies.get(node.id, [])) > 0
            has_dependents = len(node_dependents.get(node.id, [])) > 0

            # 没有依赖且没有被依赖 = 完全孤立
            if not has_deps and not has_dependents:
                errors.append(f"节点 {node.id} 是完全孤立的（无依赖且无被依赖）")
            # 没有依赖且有被依赖 = 源节点（可能是正常的）
            elif not has_deps and has_dependents:
                warnings.append(f"节点 {node.id} 是源节点（无依赖）")
            # 有依赖且没有被依赖 = 汇节点（可能是正常的）
            elif has_deps and not has_dependents:
                warnings.append(f"节点 {node.id} 是汇节点（无被依赖）")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def _has_path(self, dag: TaskDAG, from_node: str, to_node: str) -> bool:
        """检查是否存在从from_node到to_node的路径"""
        visited = set()
        queue = [from_node]

        while queue:
            current = queue.pop(0)
            if current == to_node:
                return True
            if current in visited:
                continue
            visited.add(current)

            for edge in dag.edges:
                if edge.from_node == current:
                    queue.append(edge.to_node)

        return False

    def _generate_summary(self, results: Dict[str, Any]) -> str:
        """生成验证结果摘要"""
        if results["valid"]:
            return f"✅ DAG验证通过（{len(results['checks'])} 项检查）"
        else:
            return f"❌ DAG验证失败（{len(results['errors'])} 个错误，{len(results['warnings'])} 个警告）"

    def quick_check(self, dag: TaskDAG) -> Dict[str, Any]:
        """
        快速检查DAG的基本有效性

        Args:
            dag: 任务DAG

        Returns:
            快速检查结果
        """
        basic_check = self._validate_structure(dag)
        if not basic_check["valid"]:
            return {
                "valid": False,
                "reason": "基础结构无效",
                "errors": basic_check["errors"]
            }

        cycle_check = self._validate_no_cycles(dag)
        if not cycle_check["valid"]:
            return {
                "valid": False,
                "reason": "存在环",
                "cycles": cycle_check["cycles"]
            }

        topo_result = self.topological_sorter.sort(dag)
        if not topo_result["success"]:
            return {
                "valid": False,
                "reason": "无法进行拓扑排序"
            }

        return {
            "valid": True,
            "node_count": len(dag.nodes),
            "edge_count": len(dag.edges),
            "sorted_order": topo_result["sorted_order"]
        }

    def get_validation_report(self, dag: TaskDAG) -> str:
        """
        生成详细的验证报告

        Args:
            dag: 任务DAG

        Returns:
            格式化的验证报告
        """
        result = self.validate(dag, strict=True)

        lines = []
        lines.append("=" * 60)
        lines.append("DAG 验证报告")
        lines.append("=" * 60)
        lines.append("")

        # 基本信息
        lines.append(f"节点数: {len(dag.nodes)}")
        lines.append(f"边数: {len(dag.edges)}")
        lines.append(f"并行组数: {len(dag.parallel_groups)}")
        lines.append("")

        # 验证结果
        lines.append(f"验证状态: {'✅ 通过' if result['valid'] else '❌ 失败'}")
        lines.append("")

        # 错误
        if result["errors"]:
            lines.append(f"错误 ({len(result['errors'])}):")
            for error in result["errors"]:
                lines.append(f"  - {error}")
            lines.append("")

        # 警告
        if result["warnings"]:
            lines.append(f"警告 ({len(result['warnings'])}):")
            for warning in result["warnings"]:
                lines.append(f"  - {warning}")
            lines.append("")

        # 检查详情
        lines.append("检查详情:")
        for check_name, check_result in result["checks"].items():
            status = "✅" if check_result["valid"] else "❌"
            lines.append(f"  {status} {check_name}")
        lines.append("")

        # 总结消息
        lines.append(f"总结: {result['message']}")
        lines.append("=" * 60)

        return "\n".join(lines)
