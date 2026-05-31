from typing import Any, Dict, List, Optional
import re


class EndRuleValidator:
    """终止规则机器可识别解析器"""

    def __init__(self):
        self.success_keywords_zh = [
            "完成", "成功", "实现", "达成", "结束",
            "圆满", "满足", "符合", "通过", "验收"
        ]
        self.success_keywords_en = [
            "complete", "finish", "success", "achieve",
            "done", "pass", "accept", "meet"
        ]

        self.failure_keywords_zh = [
            "失败", "无法", "超过", "超时", "中断",
            "终止", "放弃", "无法完成", "未通过"
        ]
        self.failure_keywords_en = [
            "fail", "cannot", "exceed", "timeout",
            "abort", "stop", "give up", "not pass"
        ]

        self.timeout_patterns_zh = [
            r'(\d+)\s*天',
            r'(\d+)\s*小时',
            r'(\d+)\s*分钟',
            r'(\d+)\s*周',
            r'(\d+)\s*个月'
        ]
        self.timeout_patterns_en = [
            r'(\d+)\s*(days?|hours?|minutes?|weeks?|months?)'
        ]

    def parse_end_rule(self, text: str) -> Dict[str, Any]:
        """
        解析终止规则

        Args:
            text: 原始需求文本

        Returns:
            包含success_criteria、failure_criteria、timeout、max_attempts的规则字典
        """
        end_rule = {
            "success_criteria": [],
            "failure_criteria": [],
            "timeout": 86400,
            "max_attempts": 3
        }

        sentences = self._split_sentences(text)

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 3:
                continue

            self._extract_success_criteria(sentence, end_rule["success_criteria"])
            self._extract_failure_criteria(sentence, end_rule["failure_criteria"])
            self._extract_timeout(sentence, end_rule)

        if not end_rule["success_criteria"]:
            end_rule["success_criteria"] = ["任务目标达成"]

        if not end_rule["failure_criteria"]:
            end_rule["failure_criteria"] = [
                "无法在规定时间内完成",
                "遇到不可克服的技术障碍"
            ]

        return end_rule

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

    def _extract_success_criteria(self, sentence: str, success_list: List[str]):
        """提取成功标准"""
        sentence_lower = sentence.lower()

        for keyword in self.success_keywords_zh + self.success_keywords_en:
            if keyword in sentence_lower:
                content = self._extract_content(sentence, keyword)
                if content and len(content) > 3:
                    success_list.append(content)
                break

    def _extract_failure_criteria(self, sentence: str, failure_list: List[str]):
        """提取失败标准"""
        sentence_lower = sentence.lower()

        for keyword in self.failure_keywords_zh + self.failure_keywords_en:
            if keyword in sentence_lower:
                content = self._extract_content(sentence, keyword)
                if content and len(content) > 3:
                    failure_list.append(content)
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

    def _extract_timeout(self, sentence: str, end_rule: Dict[str, Any]):
        """提取超时时间"""
        sentence_lower = sentence.lower()

        for pattern in self.timeout_patterns_zh + self.timeout_patterns_en:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                try:
                    number = int(match.group(1))
                    unit = match.group(2).lower() if len(match.groups()) > 1 else 'hours'

                    timeout_seconds = self._convert_to_seconds(number, unit)
                    if timeout_seconds > 0:
                        end_rule["timeout"] = timeout_seconds
                except:
                    pass
                break

    def _convert_to_seconds(self, number: int, unit: str) -> int:
        """将时间转换为秒"""
        unit = unit.lower()
        if 'second' in unit or '秒' in unit:
            return number
        elif 'minute' in unit or '分钟' in unit:
            return number * 60
        elif 'hour' in unit or '小时' in unit:
            return number * 3600
        elif 'day' in unit or '天' in unit:
            return number * 86400
        elif 'week' in unit or '周' in unit:
            return number * 604800
        elif 'month' in unit or '月' in unit:
            return number * 2592000
        else:
            return number * 3600

    def validate_end_rule(self, end_rule: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        验证终止规则是否有效

        Args:
            end_rule: 终止规则字典

        Returns:
            (是否有效, 错误列表)
        """
        errors = []

        required_fields = ["success_criteria", "failure_criteria", "timeout", "max_attempts"]
        for field in required_fields:
            if field not in end_rule:
                errors.append(f"终止规则缺少 {field} 字段")

        if "success_criteria" in end_rule and not end_rule["success_criteria"]:
            errors.append("成功标准不能为空")

        if "failure_criteria" in end_rule and not end_rule["failure_criteria"]:
            errors.append("失败标准不能为空")

        if "timeout" in end_rule and end_rule["timeout"] <= 0:
            errors.append("超时时间必须大于0")

        if "max_attempts" in end_rule and end_rule["max_attempts"] <= 0:
            errors.append("最大重试次数必须大于0")

        return len(errors) == 0, errors

    def should_stop(self, current_status: str, end_rule: Dict[str, Any]) -> tuple[bool, str]:
        """
        判断任务是否应该停止

        Args:
            current_status: 当前状态描述
            end_rule: 终止规则

        Returns:
            (是否应该停止, 停止原因)
        """
        current_status_lower = current_status.lower()

        for criteria in end_rule["success_criteria"]:
            if criteria.lower() in current_status_lower:
                return True, "success"

        for criteria in end_rule["failure_criteria"]:
            if criteria.lower() in current_status_lower:
                return True, "failure"

        return False, "continue"
