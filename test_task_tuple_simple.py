import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from first_principle_agent.core import TaskTuple, TaskTupleValidator


def test_task_tuple_basic():
    print("="*50)
    print("测试1：Task四元组基本功能")
    print("="*50)

    # 测试创建
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

    print(f"目标：{task.target}")
    print(f"前置条件：{task.condition}")
    print(f"边界约束：{task.boundary}")
    print(f"终止规则：{task.end_rule}")

    print("\n✅ Task四元组创建成功！")

    # 测试序列化
    print("\n" + "="*50)
    print("测试2：Task四元组JSON序列化")
    print("="*50)
    json_str = task.to_json()
    print(f"JSON序列化成功！长度：{len(json_str)}")

    task2 = TaskTuple.from_json(json_str)
    assert task.target == task2.target
    print("✅ JSON反序列化成功！")

    # 测试验证
    print("\n" + "="*50)
    print("测试3：Task四元组验证")
    print("="*50)

    valid, errors = TaskTupleValidator.validate(task)
    if valid:
        print("✅ Task四元组验证通过！")
    else:
        print("❌ Task四元组验证失败：")
        for err in errors:
            print(f"  - {err}")

    # 测试错误场景
    print("\n" + "="*50)
    print("测试4：测试错误场景验证")
    print("="*50)

    invalid_task1 = TaskTuple(
        target="",  # 空目标
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
    valid1, errors1 = TaskTupleValidator.validate(invalid_task1)
    if not valid1:
        print(f"✅ 空目标验证正确识别：{errors1}")

    print("\n" + "="*50)
    print("🎉 所有测试通过！")


if __name__ == "__main__":
    test_task_tuple_basic()
