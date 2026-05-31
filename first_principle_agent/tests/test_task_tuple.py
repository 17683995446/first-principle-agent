import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from first_principle_agent.core import TaskTuple, TaskTupleValidator


class TestTaskTuple:
    """Task四元组测试类"""

    def test_task_tuple_creation(self):
        """测试Task四元组的基本创建"""
        task = TaskTuple(
            target="完成项目开发",
            condition=["已有需求文档", "开发环境已准备"],
            boundary={
                "include": ["需求分析", "设计", "编码", "测试"],
                "exclude": ["部署上线"],
                "constraints": {"时间限制": "30天", "预算": "10万元"}
            },
            end_rule={
                "success_criteria": ["所有功能实现", "测试通过率100%", "文档齐全"],
                "failure_criteria": ["时间超过30天", "严重bug超过5个"],
                "timeout": 2592000,
                "max_attempts": 3
            },
            priority=1,
            metadata={"id": "test-001", "created_at": "2026-05-25"}
        )

        assert task.target == "完成项目开发"
        assert len(task.condition) == 2
        assert task.boundary["constraints"]["时间限制"] == "30天"
        assert task.priority == 1

    def test_task_tuple_serialization(self):
        """测试JSON序列化和反序列化"""
        task = TaskTuple(
            target="完成项目开发",
            condition=["已有需求文档"],
            boundary={
                "include": ["需求分析"],
                "exclude": [],
                "constraints": {}
            },
            end_rule={
                "success_criteria": ["完成"],
                "failure_criteria": ["失败"],
                "timeout": 86400,
                "max_attempts": 1
            }
        )

        json_str = task.to_json()
        task2 = TaskTuple.from_json(json_str)

        assert task.target == task2.target
        assert task.condition == task2.condition
        assert task.boundary == task2.boundary

    def test_task_tuple_validator(self):
        """测试完整验证功能"""
        valid_task = TaskTuple(
            target="完成项目开发",
            condition=["已有需求文档", "开发环境已准备"],
            boundary={
                "include": ["需求分析", "设计", "编码", "测试"],
                "exclude": ["部署上线"],
                "constraints": {"时间限制": "30天", "预算": "10万元"}
            },
            end_rule={
                "success_criteria": ["所有功能实现", "测试通过率100%", "文档齐全"],
                "failure_criteria": ["时间超过30天", "严重bug超过5个"],
                "timeout": 2592000,
                "max_attempts": 3
            }
        )

        valid, errors = TaskTupleValidator.validate(valid_task)
        assert valid is True

    def test_invalid_empty_target(self):
        """测试空目标验证失败"""
        invalid_task = TaskTuple(
            target="",
            condition=["条件1"],
            boundary={
                "include": [],
                "exclude": [],
                "constraints": {}
            },
            end_rule={
                "success_criteria": ["成功"],
                "failure_criteria": ["失败"],
                "timeout": 86400,
                "max_attempts": 1
            }
        )

        valid, errors = TaskTupleValidator.validate(invalid_task)
        assert valid is False
        assert "目标不能为空" in errors

    def test_invalid_ambiguous_target(self):
        """测试模糊目标验证失败"""
        invalid_task = TaskTuple(
            target="大概完成一些工作",
            condition=["条件1"],
            boundary={
                "include": [],
                "exclude": [],
                "constraints": {}
            },
            end_rule={
                "success_criteria": ["成功"],
                "failure_criteria": ["失败"],
                "timeout": 86400,
                "max_attempts": 1
            }
        )

        valid, errors = TaskTupleValidator.validate(invalid_task)
        assert valid is False
        assert any("模糊词汇" in error for error in errors)

    def test_invalid_missing_end_rule_keys(self):
        """测试缺少终止规则关键字段"""
        invalid_task = TaskTuple(
            target="完成任务",
            condition=["条件1"],
            boundary={
                "include": [],
                "exclude": [],
                "constraints": {}
            },
            end_rule={
                "success_criteria": ["成功"]
            }
        )

        valid, errors = TaskTupleValidator.validate(invalid_task)
        assert valid is False
        assert any("缺少" in error for error in errors)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
