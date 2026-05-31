from typing import Any, Dict, List, Optional, Tuple
from .requirement_parser import RequirementParser
from .condition_extractor import ConditionExtractor
from .boundary_definer import BoundaryDefiner
from .end_rule_validator import EndRuleValidator
from ..core import TaskTuple, TaskTupleValidator


class TaskNormalizer:
    """任务归一化器 - 整合所有组件，生成归一化的TaskTuple"""

    def __init__(self):
        self.requirement_parser = RequirementParser()
        self.condition_extractor = ConditionExtractor()
        self.boundary_definer = BoundaryDefiner()
        self.end_rule_validator = EndRuleValidator()

    def normalize(self, raw_requirement: str, metadata: Optional[Dict[str, Any]] = None) -> Tuple[Optional[TaskTuple], List[str]]:
        """
        将用户原始需求归一化为TaskTuple

        Args:
            raw_requirement: 用户原始需求（自然语言）
            metadata: 可选的元数据

        Returns:
            (TaskTuple对象, 错误列表)
        """
        all_errors = []

        if not raw_requirement or not raw_requirement.strip():
            all_errors.append("需求不能为空")
            return None, all_errors

        normalized_requirement = self.requirement_parser.preprocess(raw_requirement)

        task_tuple, parser_errors = self.requirement_parser.parse(normalized_requirement)
        all_errors.extend(parser_errors)

        if task_tuple:
            conditions = self.condition_extractor.extract_to_list(normalized_requirement)
            task_tuple.condition = conditions

            boundary = self.boundary_definer.define_boundary(normalized_requirement)
            task_tuple.boundary = boundary

            end_rule = self.end_rule_validator.parse_end_rule(normalized_requirement)
            task_tuple.end_rule = end_rule

            task_tuple.context = {"raw_requirement": raw_requirement, "normalized_requirement": normalized_requirement}
            task_tuple.metadata = metadata or {}

            is_valid, validation_errors = TaskTupleValidator.validate(task_tuple)
            if not is_valid:
                all_errors.extend(validation_errors)

            if all_errors:
                return task_tuple, all_errors
            else:
                return task_tuple, []

        return None, all_errors

    def normalize_with_tracking(self, raw_requirement: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        归一化需求并返回详细的跟踪信息

        Args:
            raw_requirement: 用户原始需求
            metadata: 可选的元数据

        Returns:
            包含归一化结果和详细信息的字典
        """
        result = {
            "success": False,
            "task_tuple": None,
            "errors": [],
            "steps": []
        }

        if not raw_requirement or not raw_requirement.strip():
            result["errors"] = ["需求不能为空"]
            return result

        try:
            result["steps"].append("开始需求预处理")
            normalized_requirement = self.requirement_parser.preprocess(raw_requirement)
            result["steps"].append(f"预处理完成: {normalized_requirement[:50]}...")

            result["steps"].append("开始需求解析")
            task_tuple, parser_errors = self.requirement_parser.parse(normalized_requirement)
            result["steps"].append(f"需求解析完成，错误数: {len(parser_errors)}")
            result["errors"].extend(parser_errors)

            if task_tuple:
                result["steps"].append("开始条件提取")
                conditions = self.condition_extractor.extract_to_list(normalized_requirement)
                task_tuple.condition = conditions
                result["steps"].append(f"条件提取完成: {len(conditions)}个条件")

                result["steps"].append("开始边界定义")
                boundary = self.boundary_definer.define_boundary(normalized_requirement)
                task_tuple.boundary = boundary
                result["steps"].append("边界定义完成")

                result["steps"].append("开始终止规则解析")
                end_rule = self.end_rule_validator.parse_end_rule(normalized_requirement)
                task_tuple.end_rule = end_rule
                result["steps"].append("终止规则解析完成")

                task_tuple.context = {"raw_requirement": raw_requirement, "normalized_requirement": normalized_requirement}
                task_tuple.metadata = metadata or {}

                result["steps"].append("开始任务验证")
                is_valid, validation_errors = TaskTupleValidator.validate(task_tuple)
                result["errors"].extend(validation_errors)

                if is_valid:
                    result["success"] = True
                    result["task_tuple"] = task_tuple
                    result["steps"].append("✅ 归一化完成！")
                else:
                    result["steps"].append("❌ 验证失败")

        except Exception as e:
            result["errors"].append(f"归一化过程出错: {str(e)}")
            result["steps"].append(f"❌ 异常: {str(e)}")

        return result
