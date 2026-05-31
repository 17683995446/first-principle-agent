import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from first_principle_agent.layers import RequirementParser


def test_requirement_parser():
    print("="*60)
    print("测试1：需求解析器基本功能")
    print("="*60)

    parser = RequirementParser()

    test_requirement = "完成项目开发，包括需求分析、设计、编码和测试。不包括部署上线。需要在30天内完成。"

    print(f"原始需求：{test_requirement}")
    print()

    task_tuple, errors = parser.parse(test_requirement)

    if errors:
        print("解析错误：")
        for err in errors:
            print(f"  - {err}")
    else:
        print("✅ 解析成功！")
        print(f"目标：{task_tuple.target}")
        print(f"前置条件：{task_tuple.condition}")
        print(f"边界约束：")
        print(f"  包含：{task_tuple.boundary['include']}")
        print(f"  排除：{task_tuple.boundary['exclude']}")
        print(f"  约束：{task_tuple.boundary['constraints']}")
        print(f"终止规则：")
        print(f"  成功标准：{task_tuple.end_rule['success_criteria']}")
        print(f"  失败标准：{task_tuple.end_rule['failure_criteria']}")

    print("\n" + "="*60)
    print("测试2：复杂需求解析")
    print("="*60)

    complex_requirement = """
    开发一个用户登录系统，包括注册、登录、修改密码功能。
    需要具备基本的前端界面和后端API。
    包括数据库设计、接口开发、前端页面、安全加固。
    不包括第三方登录集成。
    需要在两周内完成。
    """

    print(f"复杂需求：{complex_requirement[:100]}...")
    print()

    task_tuple2, errors2 = parser.parse(complex_requirement)

    if errors2:
        print("解析错误：")
        for err in errors2:
            print(f"  - {err}")
    else:
        print("✅ 解析成功！")
        print(f"目标：{task_tuple2.target}")
        print(f"前置条件：{task_tuple2.condition}")
        print(f"边界约束包含：{task_tuple2.boundary['include']}")
        print(f"边界约束排除：{task_tuple2.boundary['exclude']}")

    print("\n" + "="*60)
    print("测试3：错误处理 - 空输入")
    print("="*60)

    task_tuple3, errors3 = parser.parse("")

    if errors3:
        print(f"✅ 正确识别空输入：{errors3}")
    else:
        print("❌ 未识别空输入")

    print("\n" + "="*60)
    print("测试4：JSON序列化")
    print("="*60)

    if task_tuple:
        json_str = task_tuple.to_json()
        print(f"✅ JSON序列化成功，长度：{len(json_str)}")

        task_tuple_restored = task_tuple.from_json(json_str)
        if task_tuple.target == task_tuple_restored.target:
            print("✅ JSON反序列化成功")

    print("\n" + "="*60)
    print("🎉 所有测试完成！")


if __name__ == "__main__":
    test_requirement_parser()
