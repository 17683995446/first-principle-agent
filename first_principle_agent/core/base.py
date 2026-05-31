import json
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod


class JSONSerializable(ABC):
    """所有数据结构的基础类，提供JSON序列化和反序列化能力"""

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """将对象转换为字典"""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JSONSerializable':
        """从字典创建对象"""
        pass

    def to_json(self, indent: int = 2, ensure_ascii: bool = False) -> str:
        """将对象转换为JSON字符串"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=ensure_ascii)

    @classmethod
    def from_json(cls, json_str: str) -> 'JSONSerializable':
        """从JSON字符串创建对象"""
        return cls.from_dict(json.loads(json_str))

    def save_to_file(self, filepath: str, indent: int = 2) -> None:
        """将对象保存到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json(indent=indent))

    @classmethod
    def load_from_file(cls, filepath: str) -> 'JSONSerializable':
        """从文件加载对象"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return cls.from_json(f.read())


# 错误码约定
ErrorCode = {
    "SUCCESS": 0,
    "INVALID_INPUT": 1001,
    "INVALID_CONFIG": 1002,
    "TARGET_EXTRACTION_FAILED": 2001,
    "DAG_HAS_CYCLE": 3001,
    "DAG_HAS_UNREACHABLE": 3002,
    "ATOMIC_ACTION_INVALID": 4001,
    "CHECKPOINT_FAILED": 5001,
    "CIRCUIT_BREAKER_OPEN": 5002,
    "ROLLBACK_FAILED": 5003
}


class TaskPlanningError(Exception):
    """任务规划异常基类"""
    def __init__(self, code: int, message: str, details: Dict[str, Any] = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(f"[{code}] {message}")
