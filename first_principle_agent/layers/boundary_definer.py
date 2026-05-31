from typing import Any, Dict, List, Optional
import re


class BoundaryDefiner:
    """任务边界约束定义和提取器"""

    def __init__(self):
        self.include_keywords_zh = [
            "包括", "包含", "涵盖", "包含于", "范围包括",
            "包含了", "范围是", "涉及", "涵盖范围"
        ]
        self.include_keywords_en = [
            "include", "including", "cover", "covers",
            "containing", "within", "scope", "involves"
        ]

        self.exclude_keywords_zh = [
            "不包括", "排除", "不含", "不包含", "不涵盖",
            "不包含于", "排除在...外", "除了", "不包含"
        ]
        self.exclude_keywords_en = [
            "exclude", "excluding", "not include", "except",
            "without", "exclusive", "out of"
        ]

        self.constraint_keywords_zh = [
            "限制", "约束", "必须在", "在...范围内",
            "最多", "最少", "不超过", "必须", "要求"
        ]
        self.constraint_keywords_en = [
            "limit", "constraint", "within", "must",
            "require", "at most", "at least", "no more than"
        ]

    def define_boundary(self, text: str) -> Dict[str, Any]:
        """
        定义任务边界约束

        Args:
            text: 原始需求文本

        Returns:
            包含include/exclude/constraints的边界字典
        """
        boundary = {
            "include": [],
            "exclude": [],
            "constraints": {}
        }

        sentences = self._split_sentences(text)

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 3:
                continue

            self._extract_include(sentence, boundary["include"])
            self._extract_exclude(sentence, boundary["exclude"])
            self._extract_constraints(sentence, boundary["constraints"])

        boundary["include"] = list(set(boundary["include"]))
        boundary["exclude"] = list(set(boundary["exclude"]))

        if not boundary["include"]:
            boundary["include"] = ["未明确指定范围"]

        return boundary

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

    def _extract_include(self, sentence: str, include_list: List[str]):
        """提取包含的范围"""
        sentence_lower = sentence.lower()

        for keyword in self.include_keywords_zh + self.include_keywords_en:
            if keyword in sentence_lower:
                content = self._extract_content(sentence, keyword)
                if content and len(content) > 1:
                    items = self._parse_list(content)
                    include_list.extend(items)
                break

    def _extract_exclude(self, sentence: str, exclude_list: List[str]):
        """提取排除的范围"""
        sentence_lower = sentence.lower()

        for keyword in self.exclude_keywords_zh + self.exclude_keywords_en:
            if keyword in sentence_lower:
                content = self._extract_content(sentence, keyword)
                if content and len(content) > 1:
                    items = self._parse_list(content)
                    exclude_list.extend(items)
                break

    def _extract_content(self, sentence: str, keyword: str) -> str:
        """提取关键词后的内容"""
        keyword_len = len(keyword)
        idx = sentence.lower().find(keyword.lower())
        if idx != -1:
            content = sentence[idx + keyword_len:].strip()

            for end_punct in ['。', '.', '；', ';', '！', '!', '？', '?']:
                if end_punct in content:
                    idx_end = content.find(end_punct)
                    content = content[:idx_end].strip()
                    break

            return content
        return ""

    def _parse_list(self, content: str) -> List[str]:
        """解析列表内容"""
        items = []

        separators = ['、', ',', '，', ';', '；', '和', 'and', '与']
        for sep in separators:
            if sep in content:
                parts = content.split(sep)
                for part in parts:
                    item = part.strip()
                    if item and len(item) > 1:
                        items.append(item)
                return items

        if content:
            items = [content.strip()]

        return items

    def _extract_constraints(self, sentence: str, constraints: Dict[str, Any]):
        """提取约束条件"""
        sentence_lower = sentence.lower()

        time_patterns = [
            r'(\d+)\s*天',
            r'(\d+)\s*小时',
            r'(\d+)\s*周',
            r'(\d+)\s*个月',
            r'within\s*(\d+)\s*(days?|hours?|weeks?)'
        ]

        for pattern in time_patterns:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                constraints["时间限制"] = match.group(0)
                break

        cost_patterns = [
            r'(\d+)\s*元',
            r'(\d+)\s*(万|千)?\s*(元|块|钱)',
            r'budget\s*[:：]?\s*(\d+)'
        ]

        for pattern in cost_patterns:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                constraints["预算限制"] = match.group(0)
                break

        quality_patterns = [
            r'质量.*要求',
            r'性能.*要求',
            r'标准.*要求'
        ]

        for pattern in quality_patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                constraints["质量要求"] = "按规定要求"
                break

    def validate_boundary(self, boundary: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        验证边界约束是否有效

        Args:
            boundary: 边界字典

        Returns:
            (是否有效, 错误列表)
        """
        errors = []

        if "include" not in boundary or not isinstance(boundary["include"], list):
            errors.append("边界缺少include字段或格式错误")

        if "exclude" not in boundary or not isinstance(boundary["exclude"], list):
            errors.append("边界缺少exclude字段或格式错误")

        if "constraints" not in boundary or not isinstance(boundary["constraints"], dict):
            errors.append("边界缺少constraints字段或格式错误")

        return len(errors) == 0, errors

    def is_in_scope(self, task: str, boundary: Dict[str, Any]) -> bool:
        """
        判断任务是否在边界范围内

        Args:
            task: 任务名称
            boundary: 边界字典

        Returns:
            是否在范围内
        """
        task_lower = task.lower()

        for item in boundary["exclude"]:
            if item.lower() in task_lower:
                return False

        if boundary["include"] == ["未明确指定范围"]:
            return True

        for item in boundary["include"]:
            if item.lower() in task_lower:
                return True

        return False
