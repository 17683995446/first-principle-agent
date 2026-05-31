from typing import Any, Dict, List, Optional
import re


class ConditionExtractor:
    """前置条件自动识别和提取器"""

    def __init__(self):
        self.condition_keywords_zh = [
            "需要", "要求", "必须", "需要先", "前提是", "前提条件",
            "前提", "需要准备", "已有", "具备", "有了", "有了才能",
            "在...之前", "先...然后", "首先", "先得", "得先"
        ]

        self.condition_keywords_en = [
            "need", "require", "must", "have", "before",
            "first", "then", "provided", "if", "assuming"
        ]

        self.condition_types = {
            "environment": ["环境", "系统", "服务器", "配置", "setting", "environment"],
            "resource": ["资源", "数据", "文件", "库", "依赖", "resource", "data", "file"],
            "skill": ["技能", "能力", "知识", "了解", "熟悉", "skill", "knowledge"],
            "permission": ["权限", "授权", "批准", "permission", "authorization"],
            "time": ["时间", "日期", "在...前", "time", "date", "before"]
        }

    def extract(self, text: str) -> List[Dict[str, Any]]:
        """
        从文本中提取前置条件

        Args:
            text: 原始文本

        Returns:
            条件列表，每个条件包含内容、类型、置信度等
        """
        conditions = []

        sentences = self._split_sentences(text)

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 3:
                continue

            if self._is_condition_sentence(sentence):
                condition = self._parse_condition(sentence)
                if condition and condition["content"]:
                    conditions.append(condition)

        if not conditions:
            conditions.append(self._create_default_condition(text))

        return conditions

    def extract_to_list(self, text: str) -> List[str]:
        """
        提取条件为简单字符串列表

        Args:
            text: 原始文本

        Returns:
            条件字符串列表
        """
        conditions = self.extract(text)
        return [c["content"] for c in conditions]

    def _split_sentences(self, text: str) -> List[str]:
        """将文本拆分为句子"""
        text = re.sub(r'[\n\r]+', ' ', text)
        sentences = []
        buffer = []

        for char in text:
            buffer.append(char)
            if char in ['。', '.', '！', '!', '？', '?', '；', ';']:
                sentences.append(''.join(buffer).strip())
                buffer = []

        if buffer:
            sentences.append(''.join(buffer).strip())

        return sentences

    def _is_condition_sentence(self, sentence: str) -> bool:
        """判断句子是否包含条件"""
        sentence_lower = sentence.lower()

        for keyword in self.condition_keywords_zh + self.condition_keywords_en:
            if keyword in sentence_lower:
                return True

        return False

    def _parse_condition(self, sentence: str) -> Dict[str, Any]:
        """解析条件句子"""
        content = sentence
        condition_type = "general"
        confidence = 0.5

        for c_type, keywords in self.condition_types.items():
            for keyword in keywords:
                if keyword in sentence.lower():
                    condition_type = c_type
                    confidence = 0.8
                    break
            if condition_type != "general":
                break

        content = self._clean_condition(content)

        return {
            "content": content,
            "type": condition_type,
            "confidence": confidence,
            "is_required": True
        }

    def _clean_condition(self, condition: str) -> str:
        """清理条件文本"""
        cleaned = condition.strip()

        remove_prefixes = [
            "需要", "要求", "必须", "前提是", "前提条件",
            "前提", "已有", "具备", "在...之前", "首先",
            "need", "require", "must", "have", "before",
            "first", "then", "provided", "if"
        ]

        for prefix in remove_prefixes:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()

        cleaned = re.sub(r'^\W+', '', cleaned)
        cleaned = re.sub(r'\W+$', '', cleaned)

        return cleaned

    def _create_default_condition(self, text: str) -> Dict[str, Any]:
        """创建默认条件"""
        return {
            "content": "任务需求已明确",
            "type": "general",
            "confidence": 1.0,
            "is_required": True
        }

    def validate(self, conditions: List[str]) -> tuple[bool, List[str]]:
        """
        验证条件是否有效

        Args:
            conditions: 条件列表

        Returns:
            (是否有效, 错误列表)
        """
        errors = []

        if not conditions:
            errors.append("条件列表不能为空")
            return False, errors

        for i, condition in enumerate(conditions):
            if not condition or len(condition.strip()) < 3:
                errors.append(f"第{i+1}个条件描述太短，需要更明确")

        return len(errors) == 0, errors

    def merge_conditions(self, condition_lists: List[List[str]]) -> List[str]:
        """
        合并多个条件列表，去重

        Args:
            condition_lists: 多个条件列表

        Returns:
            合并后的条件列表
        """
        all_conditions = set()
        merged = []

        for cond_list in condition_lists:
            for cond in cond_list:
                cond_key = cond.strip().lower()
                if cond_key not in all_conditions:
                    all_conditions.add(cond_key)
                    merged.append(cond)

        return merged
