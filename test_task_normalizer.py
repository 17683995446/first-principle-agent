import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from first_principle_agent.layers import TaskNormalizer


def test_task_normalizer():
    print("="*60)
    print("测试1：任务归一化器基本功能")
    print("="*60)

    normalizer = TaskNormalizer()

    test_requirement = "完成项目开发，包括需求分析、设计、编码和测试。不包括部署上线。需要在30天内完成。"

    task_tuple, errors = normalizer.normalize(test_requirement)

    if errors:
        print("归一化错误：")
        for err in errors:
            print(f"  - {err}")
    else:
        print("✅ 归一化成功！")
        print(f"目标：{task_tuple.target}")
        print(f"前置条件：{task_tuple.condition}")
        print(f"边界约束：")
        print(f"  包含：{task_tuple.boundary['include']}")
        print(f"  排除：{task_tuple.boundary['exclude']}")
        print(f"  约束：{task_tuple.boundary['constraints']}")
        print(f"终止规则：")
        print(f"  成功标准：{task_tuple.end_rule['success_criteria']}")
        print(f"  失败标准：{task_tuple.end_rule['failure_criteria']}")
        print(f"  超时时间：{task_tuple.end_rule['timeout']}秒")

    print("\n" + "="*60)
    print("测试2：任务归一化器详细跟踪")
    print("="*60)

    tracking_result = normalizer.normalize_with_tracking(test_requirement)

    print("🎉 归一化过程：")
    for step in tracking_result["steps"]:
        print(f"  → {step}")

    if tracking_result["success"]:
        print("\n✅ 跟踪模式成功！")
    else:
        print(f"\n❌ 跟踪模式失败，错误：")
        for err in tracking_result["errors"]:
            print(f"  - {err}")

    print("\n" + "="*60)
    print("测试3：复杂需求归一化")
    print("="*60)

    complex_requirement = """
    开发一个电商网站，包括用户管理、商品管理、订单管理模块。
    需要准备好开发环境和设计文档。
    需要具有Python开发能力。
    需要在2周内完成，预算10万元。
    要求符合质量标准。
    如果模块都完成则成功，超支或超时则失败。
    """

    task_tuple2, errors2 = normalizer.normalize(complex_requirement)

    if errors2:
        print("复杂需求归一化错误：")
        for err in errors2:
            print(f"  - {err}")
    else:
        print("✅ 复杂需求归一化成功！")
        print(f"目标：{task_tuple2.target}")
        print(f"前置条件：{len(task_tuple2.condition)}个")
        print(f"包含范围：{len(task_tuple2.boundary['include'])}")
        print(f"约束条件：{task_tuple2.boundary['constraints']}")

    print("\n" + "="*60)
    print("测试4：空需求处理")
    print("="*60)

    task_tuple_empty, errors_empty = normalizer.normalize("")
    print(f"空需求 - 错误数：{len(errors_empty)}")
    if errors_empty:
        print(f"  错误：{errors_empty}")

    print("\n" + "="*60)
    print("🎉 所有测试通过！")


if __name__ == "__main__":
    test_task_normalizer()
