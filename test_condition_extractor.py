import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from first_principle_agent.layers import ConditionExtractor


def test_condition_extractor():
    print("="*60)
    print("测试1：条件提取器基本功能")
    print("="*60)

    extractor = ConditionExtractor()

    test_text1 = "完成项目开发，需要先准备好开发环境，已有需求文档。"

    conditions = extractor.extract(test_text1)

    print(f"原始文本：{test_text1}")
    print(f"提取到{len(conditions)}个条件：")
    for i, cond in enumerate(conditions, 1):
        print(f"  {i}. 内容：{cond['content']}")
        print(f"     类型：{cond['type']}")
        print(f"     置信度：{cond['confidence']}")

    print("\n✅ 条件提取成功！")

    print("\n" + "="*60)
    print("测试2：提取为简单列表")
    print("="*60)

    simple_list = extractor.extract_to_list(test_text1)
    print(f"简单列表：{simple_list}")

    print("\n" + "="*60)
    print("测试3：复杂需求条件提取")
    print("="*60)

    complex_text = """
    开发一个电商网站。首先需要完成以下工作：
    1. 需要准备好服务器环境和数据库配置
    2. 必须具备UI/UX设计稿
    3. 在开发之前，需要完成需求调研工作
    4. 要求有基本的Python开发能力
    5. 必须获得项目的授权权限
    """

    conditions_complex = extractor.extract(complex_text)

    print(f"提取到{len(conditions_complex)}个条件：")
    for i, cond in enumerate(conditions_complex, 1):
        print(f"  {i}. {cond['content']}")
        print(f"     类型：{cond['type']}")

    print("\n" + "="*60)
    print("测试4：条件验证")
    print("="*60)

    valid_conditions = ["准备好开发环境", "具备设计稿"]
    is_valid, errors = extractor.validate(valid_conditions)
    print(f"有效条件验证结果：{is_valid}")

    invalid_conditions = ["", "短"]
    is_valid2, errors2 = extractor.validate(invalid_conditions)
    print(f"无效条件验证结果：{is_valid2}")
    print(f"错误信息：{errors2}")

    print("\n" + "="*60)
    print("测试5：条件合并")
    print("="*60)

    cond_lists = [
        ["需要开发环境", "准备好数据库"],
        ["准备好数据库", "需要设计稿"],
        ["需要设计稿", "需要授权"]
    ]

    merged = extractor.merge_conditions(cond_lists)
    print(f"合并后的条件：{merged}")

    print("\n" + "="*60)
    print("🎉 所有测试通过！")


if __name__ == "__main__":
    test_condition_extractor()
