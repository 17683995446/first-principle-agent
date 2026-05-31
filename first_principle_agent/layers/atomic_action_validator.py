from typing import Any, Dict, List, Optional, Set
from ..core import AtomicAction, AtomicActionPlan, ActionType, AtomicActionStatus


class AtomicActionValidator:
    """原子动作验证器 - 验证原子动作和动作计划的有效性"""

    def __init__(self):
        pass

    def validate_action(self, action: AtomicAction) -> Dict[str, Any]:
        """
        验证单个原子动作
        
        Args:
            action: 原子动作
            
        Returns:
            验证结果
        """
        errors = []
        warnings = []
        
        # 验证基本字段
        if not action.action_id:
            errors.append("Action ID is required")
        if not action.name:
            errors.append("Action name is required")
        if not action.action_type:
            errors.append("Action type is required")
        
        # 验证超时设置
        if action.timeout <= 0:
            warnings.append(f"Timeout should be positive: {action.timeout}")
        
        # 验证重试次数
        if action.retries < 0:
            warnings.append(f"Retries should be non-negative: {action.retries}")
        
        # 验证依赖
        for dep_id in action.dependencies:
            if not dep_id:
                errors.append(f"Invalid dependency ID: {dep_id}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def validate_plan(self, plan: AtomicActionPlan) -> Dict[str, Any]:
        """
        验证整个动作计划
        
        Args:
            plan: 原子动作计划
            
        Returns:
            验证结果
        """
        errors = []
        warnings = []
        details = {}
        
        # 验证基本信息
        if not plan.plan_id:
            errors.append("Plan ID is required")
        if not plan.actions:
            errors.append("Plan has no actions")
        
        # 验证每个动作
        action_validations = []
        for action in plan.actions:
            validation = self.validate_action(action)
            action_validations.append(validation)
            if not validation["valid"]:
                errors.extend([f"Action {action.action_id}: {e}" for e in validation["errors"]])
            warnings.extend([f"Action {action.action_id}: {w}" for w in validation["warnings"]])
        details["action_validations"] = action_validations
        
        # 检查ID唯一性
        ids = set()
        duplicate_ids = set()
        for action in plan.actions:
            if action.action_id in ids:
                duplicate_ids.add(action.action_id)
            ids.add(action.action_id)
        if duplicate_ids:
            errors.append(f"Duplicate action IDs: {sorted(duplicate_ids)}")
        
        # 检查依赖有效性
        valid_ids = {action.action_id for action in plan.actions}
        invalid_deps = []
        for action in plan.actions:
            for dep_id in action.dependencies:
                if dep_id not in valid_ids:
                    invalid_deps.append((action.action_id, dep_id))
        if invalid_deps:
            errors.extend([f"Action {act_id} has invalid dependency {dep_id}" for act_id, dep_id in invalid_deps])
        
        # 检查循环依赖
        cycles = self._detect_cycles(plan)
        if cycles:
            errors.append(f"Detected {len(cycles)} cycles in dependencies")
            details["cycles"] = cycles
        
        # 检查孤岛（没有依赖且没有被依赖的动作）
        islands = self._find_islands(plan)
        if islands:
            warnings.append(f"Found {len(islands)} isolated actions")
            details["islands"] = islands
        
        # 检查动作类型分布
        type_distribution = self._analyze_type_distribution(plan)
        details["type_distribution"] = type_distribution
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "details": details
        }

    def _detect_cycles(self, plan: AtomicActionPlan) -> List[List[str]]:
        """检测循环依赖"""
        cycles = []
        visited = set()
        recursion_stack = set()
        
        # 构建邻接表
        adjacency = {action.action_id: [] for action in plan.actions}
        for action in plan.actions:
            adjacency[action.action_id] = action.dependencies.copy()
        
        # 检查每个节点
        for action_id in adjacency:
            if action_id not in visited:
                current_path = []
                self._dfs_cycle_detection(action_id, adjacency, visited, recursion_stack, current_path, cycles)
        
        return cycles

    def _dfs_cycle_detection(
        self,
        node: str,
        adjacency: Dict[str, List[str]],
        visited: Set[str],
        recursion_stack: Set[str],
        current_path: List[str],
        cycles: List[List[str]]
    ) -> None:
        """DFS循环依赖检测"""
        visited.add(node)
        recursion_stack.add(node)
        current_path.append(node)
        
        for neighbor in adjacency.get(node, []):
            if neighbor not in visited:
                self._dfs_cycle_detection(neighbor, adjacency, visited, recursion_stack, current_path, cycles)
            elif neighbor in recursion_stack:
                # 找到一个环
                start_idx = current_path.index(neighbor)
                cycle = current_path[start_idx:]
                if cycle not in cycles:
                    cycles.append(cycle)
        
        recursion_stack.remove(node)
        current_path.pop()

    def _find_islands(self, plan: AtomicActionPlan) -> List[str]:
        """找到孤岛动作（没有依赖且没有被依赖）"""
        all_ids = {action.action_id for action in plan.actions}
        has_dependency = set()
        is_dependency = set()
        
        for action in plan.actions:
            if action.dependencies:
                has_dependency.add(action.action_id)
            for dep_id in action.dependencies:
                is_dependency.add(dep_id)
        
        islands = []
        for action_id in all_ids:
            if action_id not in has_dependency and action_id not in is_dependency:
                islands.append(action_id)
        
        return islands

    def _analyze_type_distribution(self, plan: AtomicActionPlan) -> Dict[str, int]:
        """分析动作类型分布"""
        distribution: Dict[str, int] = {}
        for action in plan.actions:
            type_name = action.action_type.value
            distribution[type_name] = distribution.get(type_name, 0) + 1
        return distribution

    def check_dependency_order(self, plan: AtomicActionPlan) -> Dict[str, Any]:
        """
        检查依赖顺序的正确性
        
        Args:
            plan: 原子动作计划
            
        Returns:
            检查结果
        """
        # 尝试进行拓扑排序
        try:
            topological_order = self._topological_sort(plan)
            return {
                "valid": True,
                "topological_order": topological_order
            }
        except ValueError as e:
            return {
                "valid": False,
                "error": str(e)
            }

    def _topological_sort(self, plan: AtomicActionPlan) -> List[str]:
        """拓扑排序"""
        # 构建入度表和邻接表
        in_degree = {action.action_id: 0 for action in plan.actions}
        adjacency = {action.action_id: [] for action in plan.actions}
        
        for action in plan.actions:
            for dep_id in action.dependencies:
                adjacency[dep_id].append(action.action_id)
                in_degree[action.action_id] += 1
        
        # 使用Kahn算法
        queue = [node for node in in_degree if in_degree[node] == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            for neighbor in adjacency[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if len(result) != len(plan.actions):
            raise ValueError("Cycle detected in dependencies")
        
        return result

    def validate_for_execution(self, plan: AtomicActionPlan) -> Dict[str, Any]:
        """
        验证计划是否可以执行
        
        Args:
            plan: 原子动作计划
            
        Returns:
            验证结果
        """
        # 首先进行完整验证
        plan_validation = self.validate_plan(plan)
        
        if not plan_validation["valid"]:
            return {
                "executable": False,
                "reason": "Plan validation failed",
                "errors": plan_validation["errors"]
            }
        
        # 检查是否有可执行的起始动作
        ready_actions = plan.get_ready_actions()
        if not ready_actions:
            return {
                "executable": False,
                "reason": "No ready actions to start execution",
                "errors": ["No actions have all dependencies met"]
            }
        
        return {
            "executable": True,
            "ready_actions": [action.action_id for action in ready_actions]
        }

    def suggest_improvements(self, plan: AtomicActionPlan) -> List[Dict[str, Any]]:
        """
        建议改进
        
        Args:
            plan: 原子动作计划
            
        Returns:
            改进建议列表
        """
        suggestions = []
        
        # 分析计划
        validation = self.validate_plan(plan)
        
        # 检查孤岛
        if validation.get("details", {}).get("islands"):
            suggestions.append({
                "type": "dependency",
                "severity": "warning",
                "message": "Found isolated actions. Consider adding dependencies to integrate them."
            })
        
        # 检查类型分布
        type_dist = validation.get("details", {}).get("type_distribution", {})
        if "validate" in type_dist and type_dist["validate"] < len(plan.actions) * 0.2:
            suggestions.append({
                "type": "validation",
                "severity": "info",
                "message": "Consider adding more validation actions for robustness."
            })
        
        # 检查超时设置
        actions_without_timeout = [a.action_id for a in plan.actions if a.timeout <= 0]
        if actions_without_timeout:
            suggestions.append({
                "type": "timeout",
                "severity": "warning",
                "message": f"Actions {actions_without_timeout} have no timeout set."
            })
        
        return suggestions
