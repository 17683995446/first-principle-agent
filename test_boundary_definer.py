import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from first_principle_agent.layers import BoundaryDefiner


def test_boundary_definer():
    print("="*60)
    print("测试1：边界定义器基本功能")
    print("="*60)

    definer = BoundaryDefiner()

    test_text = "完成项目开发，包括需求分析、设计、编码和测试。不包括部署上线。需要在30天内完成。"

    boundary = definer.define_boundary(test_text)

    print(f"原始文本：{test_text}")
    print(f"边界约束：")
    print(f"  包含范围：{boundary['include']}")
    print(f"  排除范围：{boundary['exclude']}")
    print(f"  其他约束：{boundary['constraints']}")

    print("\n✅ 边界定义成功！")

    print("\n" + "="*60)
    print("测试2：边界验证")
    print("="*60)

    is_valid, errors = definer.validate_boundary(boundary)
    print(f"边界验证结果：{is_valid}")

    if errors:
        print(f"错误信息：{errors}")
    else:
        print("✅ 边界验证通过！")

    print("\n" + "="*60)
    print("测试3：范围判定")
    print("="*60)

    test_tasks = [
        "需求分析",
        "编码开发",
        "部署上线",
        "系统运维"
    ]

    for task in test_tasks:
        in_scope = definer.is_in_scope(task, boundary)
        status = "✅ 在范围内" if in_scope else "❌ 不在范围内"
        print(f"  任务：{task} → {status}")

    print("\n" + "="*60)
    print("测试4：复杂边界定义")
    print("="*60)

    complex_text = """
    开发一个电商网站，包括用户管理、商品管理、订单管理模块。
    不包括支付系统集成、物流系统对接。
    需要在2周内完成，预算10万元。
    要求符合电商系统质量标准。
    """

    boundary_complex = definer.define_boundary(complex_text)

    print(f"边界约束：")
    print(f"  包含范围：{boundary_complex['include']}")
    print(f"  排除范围：{boundary_complex['exclude']}")
    print(f"  其他约束：{boundary_complex['constraints']}")

    print("\n" + "="*60)
    print("测试5：边界交叉验证")
    print("="*60)

    complex_tasks = [
        "用户管理模块开发",
        "商品管理功能实现",
        "支付宝支付接口集成",
        "订单管理系统开发"
    ]

    for task in complex_tasks:
        in_scope = definer.is_in_scope(task, boundary_complex)
        status = "✅ 在范围内" if in_scope else "❌ 不在范围内"
        print(f"  任务：{task} → {status}")

    print("\n" + "="*60)
    print("🎉 所有测试通过！")


if __name__ == "__main__":
    test_boundary_definer()
