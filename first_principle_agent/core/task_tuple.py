from typing import Any, Dict, List, Optional
from .base import JSONSerializable, TaskPlanningError, ErrorCode


class TaskTuple(JSONSerializable):
    """任务四元组 - 第1层的核心数据结构"""

    def __init__(
        self,
        target: str,
        condition: List[str],
        boundary: Dict[str, Any],
        end_rule: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.target = target
        self.condition = condition or []
        self.boundary = boundary or {}
        self.end_rule = end_rule or {}
        self.context = context or {}
        self.priority = priority
        self.metadata = metadata or {}
        self.id = metadata.get('id') if metadata else None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'target': self.target,
            'condition': self.condition,
            'boundary': self.boundary,
            'end_rule': self.end_rule,
            'context': self.context,
            'priority': self.priority,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskTuple':
        return cls(
            target=data.get('target', ''),
            condition=data.get('condition', []),
            boundary=data.get('boundary', {}),
            end_rule=data.get('end_rule', {}),
            context=data.get('context', {}),
            priority=data.get('priority', 0),
            metadata=data.get('metadata', {})
        )


class TaskTupleValidator:
    """任务四元组验证器 - 基于目标归一化公理"""

    @staticmethod
    def validate(task_tuple: TaskTuple) -> tuple[bool, List[str]]:
        """完整验证任务四元组"""
        errors = []

        valid, target_errors = TaskTupleValidator.validate_target(task_tuple.target)
        if not valid:
            errors.extend(target_errors)

        valid, condition_errors = TaskTupleValidator.validate_condition(task_tuple.condition)
        if not valid:
            errors.extend(condition_errors)

        valid, boundary_errors = TaskTupleValidator.validate_boundary(task_tuple.boundary)
        if not valid:
            errors.extend(boundary_errors)

        valid, end_rule_errors = TaskTupleValidator.validate_end_rule(task_tuple.end_rule)
        if not valid:
            errors.extend(end_rule_errors)

        return len(errors) == 0, errors

    @staticmethod
    def validate_target(target: str) -> tuple[bool, List[str]]:
        """验证目标 - 确保唯一、明确、可验证"""
        errors = []

        if not target or not target.strip():
            errors.append("目标不能为空")
        elif len(target.strip()) < 3:
            errors.append("目标太短，需要更明确的描述")
        else:
            ambiguous_words = ['差不多', '大概', '可能', '应该', '也许', '或许', '好像', '尽量', '尽可能']
            for word in ambiguous_words:
                if word in target:
                    errors.append(f"目标包含模糊词汇：'{word}'，需要更明确的表述")

            if '和' in target or '及' in target or '以及' in target:
                if not TaskTupleValidator._check_single_target(target):
                    errors.append("目标可能包含多个子目标，需要拆分为单一目标")

        return len(errors) == 0, errors

    @staticmethod
    def _check_single_target(target: str) -> bool:
        """检查是否真的是单一目标（简单启发式）"""
        conjunctions = ['和', '及', '以及', '与']
        parts = []
        for conj in conjunctions:
            if conj in target:
                parts = target.split(conj)
                break

        if len(parts) <= 1:
            return True

        all_parts_related = True
        for part in parts:
            part = part.strip()
            if len(part) < 2:
                continue

        return True

    @staticmethod
    def validate_condition(condition: List[str]) -> tuple[bool, List[str]]:
        """验证前置条件 - 确保必要、可验证、原子"""
        errors = []

        if not condition:
            errors.append("前置条件不能为空，至少需要一个基本条件")

        for i, cond in enumerate(condition):
            if not cond or not cond.strip():
                errors.append(f"前置条件 {i+1} 不能为空")
            elif len(cond.strip()) < 3:
                errors.append(f"前置条件 {i+1} 太短，需要更明确的描述")

        return len(errors) == 0, errors

    @staticmethod
    def validate_boundary(boundary: Dict[str, Any]) -> tuple[bool, List[str]]:
        """验证边界约束 - 确保明确、可判定"""
        errors = []

        required_keys = ['include', 'exclude', 'constraints']
        for key in required_keys:
            if key not in boundary:
                errors.append(f"边界约束缺少 '{key}' 定义")

        return len(errors) == 0, errors

    @staticmethod
    def validate_end_rule(end_rule: Dict[str, Any]) -> tuple[bool, List[str]]:
        """验证终止规则 - 确保可判定、完整、收敛、可量化"""
        errors = []

        required_keys = ['success_criteria', 'failure_criteria', 'timeout', 'max_attempts']
        for key in required_keys:
            if key not in end_rule:
                errors.append(f"终止规则缺少 '{key}' 定义")

        timeout = end_rule.get('timeout', 0)
        if timeout <= 0:
            errors.append("超时时间必须大于0")

        max_attempts = end_rule.get('max_attempts', 0)
        if max_attempts <= 0:
            errors.append("最大重试次数必须大于0")

        success_criteria = end_rule.get('success_criteria', [])
        if not success_criteria:
            errors.append("成功标准不能为空")

        return len(errors) == 0, errors
