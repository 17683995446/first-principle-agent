import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from first_principle_agent.layers import EndRuleValidator


def test_end_rule_validator():
    print("="*60)
    print("测试1：终止规则解析器基本功能")
    print("="*60)

    validator = EndRuleValidator()

    test_text = "完成项目开发，测试通过率达到100%，文档齐全则成功。如果超过30天未完成则失败。"

    end_rule = validator.parse_end_rule(test_text)

    print(f"原始文本：{test_text}")
    print(f"终止规则：")
    print(f"  成功标准：{end_rule['success_criteria']}")
    print(f"  失败标准：{end_rule['failure_criteria']}")
    print(f"  超时时间：{end_rule['timeout']}秒")
    print(f"  最大重试：{end_rule['max_attempts']}次")

    print("\n✅ 终止规则解析成功！")

    print("\n" + "="*60)
    print("测试2：终止规则验证")
    print("="*60)

    is_valid, errors = validator.validate_end_rule(end_rule)
    print(f"终止规则验证结果：{is_valid}")

    if errors:
        print(f"错误信息：{errors}")
    else:
        print("✅ 终止规则验证通过！")

    print("\n" + "="*60)
    print("测试3：停止判断功能")
    print("="*60)

    test_statuses = [
        "项目开发完成，测试通过率100%，文档齐全",
        "已开发了29天，还在继续中",
        "项目已开发31天，超时了",
        "遇到技术障碍，无法继续"
    ]

    for status in test_statuses:
        should_stop, reason = validator.should_stop(status, end_rule)
        if should_stop:
            status_str = f"🛑 停止（{reason}）"
        else:
            status_str = f"▶️  继续"
        print(f"  状态：{status} → {status_str}")

    print("\n" + "="*60)
    print("测试4：复杂终止规则解析")
    print("="*60)

    complex_text = """
    开发一个电商网站，用户管理、商品管理、订单管理三个模块都完成则成功。
    如果有任何一个模块无法实现，或者预算超支10万元，或者开发时间超过2周则失败。
    """

    end_rule_complex = validator.parse_end_rule(complex_text)

    print(f"终止规则：")
    print(f"  成功标准：{end_rule_complex['success_criteria']}")
    print(f"  失败标准：{end_rule_complex['failure_criteria']}")
    print(f"  超时时间：{end_rule_complex['timeout']}秒")
    print(f"  最大重试：{end_rule_complex['max_attempts']}次")

    print("\n" + "="*60)
    print("测试5：时间单位转换")
    print("="*60)

    time_texts = [
        "需要在1天内完成",
        "要求24小时内完成",
        "3周内必须完成",
        "最多6个月完成项目"
    ]

    for text in time_texts:
        er = validator.parse_end_rule(text)
        print(f"  文本：{text} → 超时：{er['timeout']}秒")

    print("\n" + "="*60)
    print("🎉 所有测试通过！")


if __name__ == "__main__":
    test_end_rule_validator()
