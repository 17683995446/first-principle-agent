from typing import Any, Dict, List, Optional
from first_principle_agent.core import TaskTuple, TaskTupleValidator


class RequirementParser:
    """用户原始需求解析器 - 第1层的核心入口"""

    def __init__(self):
        self.preprocessing_rules = []
        self._init_preprocessing_rules()

    def _init_preprocessing_rules(self):
        """初始化预处理规则"""
        self.preprocessing_rules = [
            ("multiple_spaces", self._remove_multiple_spaces),
            ("trailing_spaces", self._remove_trailing_spaces),
            ("normalize_punctuation", self._normalize_punctuation),
            ("remove_special_chars", self._remove_special_chars)
        ]

    @staticmethod
    def _remove_multiple_spaces(text: str) -> str:
        """移除多个连续空格"""
        import re
        return re.sub(r'\s+', ' ', text)

    @staticmethod
    def _remove_trailing_spaces(text: str) -> str:
        """移除首尾空格"""
        return text.strip()

    @staticmethod
    def _normalize_punctuation(text: str) -> str:
        """规范化标点符号"""
        import re
        text = text.replace('，', ',')
        text = text.replace('。', '.')
        text = text.replace('！', '!')
        text = text.replace('？', '?')
        text = text.replace('：', ':')
        text = text.replace('；', ';')
        text = re.sub(r'\s*([,.:;!?])\s*', r'\1 ', text)
        return text

    @staticmethod
    def _remove_special_chars(text: str) -> str:
        """移除特殊字符"""
        import re
        return re.sub(r'[^\w\s\u4e00-\u9fff,.:;!?\-_()（）【】\[\]]', '', text)

    def preprocess(self, raw_text: str) -> str:
        """对原始文本进行预处理"""
        text = raw_text
        for rule_name, rule_func in self.preprocessing_rules:
            text = rule_func(text)
        return text

    def parse(self, raw_requirement: str) -> tuple[Optional[TaskTuple], List[str]]:
        """
        解析用户原始需求为TaskTuple

        Args:
            raw_requirement: 用户原始需求（自然语言）

        Returns:
            tuple[TaskTuple, List[str]]: 解析结果和错误列表
        """
        errors = []

        if not raw_requirement or not raw_requirement.strip():
            errors.append("需求不能为空")
            return None, errors

        preprocessed = self.preprocess(raw_requirement)

        if len(preprocessed) < 5:
            errors.append("需求描述太短，请提供更详细的说明")
            return None, errors

        extracted = self._extract_components(preprocessed)

        task_tuple = self._build_task_tuple(extracted)

        valid, validation_errors = TaskTupleValidator.validate(task_tuple)
        if not valid:
            errors.extend(validation_errors)

        return task_tuple, errors

    def _extract_components(self, text: str) -> Dict[str, Any]:
        """提取需求中的关键组件"""
        components = {
            "target": "",
            "condition": [],
            "boundary": {
                "include": [],
                "exclude": [],
                "constraints": {}
            },
            "end_rule": {
                "success_criteria": [],
                "failure_criteria": [],
                "timeout": 86400,
                "max_attempts": 3
            }
        }

        components["target"] = self._extract_target(text)

        components["condition"] = self._extract_conditions(text)

        include_list, exclude_list, constraints = self._extract_boundary(text)
        components["boundary"]["include"] = include_list
        components["boundary"]["exclude"] = exclude_list
        components["boundary"]["constraints"] = constraints

        success, failure = self._extract_end_criteria(text)
        components["end_rule"]["success_criteria"] = success
        components["end_rule"]["failure_criteria"] = failure

        return components

    def _extract_target(self, text: str) -> str:
        """提取目标"""
        text_lower = text.lower()

        keywords = [
            "完成", "实现", "开发", "构建", "创建", "制作",
            "完成", "实现", "开发", "构建", "创建", "制作",
            "build", "create", "develop", "implement", "finish", "complete"
        ]

        for keyword in keywords:
            if keyword in text_lower:
                idx = text_lower.find(keyword)
                target = text[idx:].strip()
                if len(target) > 5:
                    if '.' in target or '。' in target:
                        for punct in ['.', '。']:
                            if punct in target:
                                idx_punct = target.index(punct)
                                target = target[:idx_punct+1]
                                break
                    return target

        sentences = text.split('.')
        if len(sentences) > 0:
            return sentences[0].strip()

        return text

    def _extract_conditions(self, text: str) -> List[str]:
        """提取前置条件"""
        conditions = []

        condition_keywords = ["已有", "已有", "具备", "需要", "前提", "条件",
                              "have", "with", "need", "require", "前提", "具备"]

        for keyword in condition_keywords:
            if keyword in text:
                idx = text.find(keyword)
                sentence = text[idx:]
                for end_punct in ['。', '.', ',', '，']:
                    if end_punct in sentence[1:]:
                        idx_end = sentence.index(end_punct, 1)
                        condition = sentence[:idx_end+1].strip()
                        if len(condition) > 3:
                            conditions.append(condition)
                        break

        if not conditions:
            conditions = ["用户已明确表达需求"]

        return conditions[:5]

    def _extract_boundary(self, text: str) -> tuple[List[str], List[str], Dict[str, Any]]:
        """提取边界约束"""
        include = []
        exclude = []
        constraints = {}

        include_keywords = ["包括", "包含", "涵盖", "范围", "包括",
                           "include", "including", "cover"]

        exclude_keywords = ["不包括", "排除", "不含", "不包括", "不含",
                           "exclude", "excluding", "not include"]

        for keyword in include_keywords:
            if keyword in text:
                idx = text.find(keyword)
                segment = text[idx:]
                for punct in ['。', '.', ',', '，']:
                    if punct in segment[1:]:
                        idx_end = segment.index(punct, 1)
                        content = segment[len(keyword):idx_end].strip()
                        if len(content) > 1:
                            items = [item.strip() for item in content.split('、') if item.strip()]
                            include.extend(items[:10])
                        break

        for keyword in exclude_keywords:
            if keyword in text:
                idx = text.find(keyword)
                segment = text[idx:]
                for punct in ['。', '.', ',', '，']:
                    if punct in segment[1:]:
                        idx_end = segment.index(punct, 1)
                        content = segment[len(keyword):idx_end].strip()
                        if len(content) > 1:
                            items = [item.strip() for item in content.split('、') if item.strip()]
                            exclude.extend(items[:10])
                        break

        time_constraint = self._extract_time_constraint(text)
        if time_constraint:
            constraints["时间限制"] = time_constraint

        if not include:
            include = ["未明确指定范围"]

        if not exclude:
            exclude = []

        return include, exclude, constraints

    def _extract_time_constraint(self, text: str) -> Optional[str]:
        """提取时间约束"""
        import re

        patterns = [
            r'(\d+)\s*天',
            r'(\d+)\s*小时',
            r'(\d+)\s*周',
            r'(\d+)\s*个月',
            r'within\s*(\d+)\s*(days?|hours?|weeks?)',
            r'before\s*(.+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)

        return None

    def _extract_end_criteria(self, text: str) -> tuple[List[str], List[str]]:
        """提取终止标准"""
        success = []
        failure = []

        success_keywords = ["完成", "成功", "达到", "实现",
                           "complete", "finish", "achieve", "success"]

        for keyword in success_keywords:
            if keyword in text.lower():
                idx = text.lower().find(keyword)
                sentence = text[idx:]
                for punct in ['。', '.', ',', '，']:
                    if punct in sentence[1:]:
                        idx_end = sentence.index(punct, 1)
                        criterion = sentence[:idx_end+1].strip()
                        if len(criterion) > 3:
                            success.append(criterion)
                        break

        if not success:
            success = ["任务目标达成"]

        failure = [
            "无法在规定时间内完成",
            "关键功能无法实现",
            "遇到不可克服的技术障碍"
        ]

        return success[:5], failure[:5]

    def _build_task_tuple(self, components: Dict[str, Any]) -> TaskTuple:
        """构建TaskTuple对象"""
        return TaskTuple(
            target=components["target"],
            condition=components["condition"],
            boundary=components["boundary"],
            end_rule=components["end_rule"],
            context={},
            priority=0,
            metadata={"parser": "RequirementParser", "version": "0.1.0"}
        )
