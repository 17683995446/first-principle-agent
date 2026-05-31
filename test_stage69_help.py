#!/usr/bin/env python3
"""
第69阶段 - 系统帮助和快速入门向导测试
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from first_principle_agent.core.help_system import (
    HelpSystem,
    HelpCLI,
    QuickStartWizard,
    TutorialStep,
    CommandHelp,
    HelpCategory,
    create_help_system,
    create_help_cli,
    create_wizard
)


def test_1_data_structures():
    """测试1: 数据结构"""
    print("\n" + "="*80)
    print("测试1: 数据结构")
    print("="*80)
    
    try:
        # 测试教程步骤
        step = TutorialStep(
            step_number=1,
            title="测试步骤",
            description="这是一个测试步骤",
            command="test command",
            expected_output="test output",
            tips="测试提示"
        )
        print("✅ TutorialStep 创建成功")
        print(f"   步骤编号: {step.step_number}")
        print(f"   标题: {step.title}")
        print(f"   描述: {step.description}")
        
        # 测试命令帮助
        help_info = CommandHelp(
            command="test",
            description="测试命令",
            usage="test [option]",
            examples=["test example"],
            related_commands=["help"]
        )
        print("\n✅ CommandHelp 创建成功")
        print(f"   命令: {help_info.command}")
        print(f"   描述: {help_info.description}")
        
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_2_help_system():
    """测试2: 帮助系统"""
    print("\n" + "="*80)
    print("测试2: 帮助系统")
    print("="*80)
    
    try:
        help_system = create_help_system()
        print("✅ HelpSystem 创建成功")
        
        # 测试获取命令帮助
        print("\n📚 测试获取命令帮助...")
        help_info = help_system.get_command_help("run")
        if help_info:
            print(f"✅ 获取命令帮助成功: {help_info.command}")
            print(f"   描述: {help_info.description}")
        else:
            print("❌ 获取命令帮助失败")
            return False
        
        # 测试获取所有命令
        print("\n📋 测试获取所有命令...")
        all_commands = help_system.get_all_commands()
        print(f"✅ 获取 {len(all_commands)} 个命令")
        print(f"   命令: {', '.join(all_commands[:5])}...")
        
        # 测试获取教程
        print("\n📖 测试获取教程...")
        tutorial = help_system.get_tutorial("quickstart")
        if tutorial:
            print(f"✅ 获取教程成功: {len(tutorial)} 个步骤")
            for i, step in enumerate(tutorial[:3]):
                print(f"   步骤{step.step_number}: {step.title}")
        else:
            print("❌ 获取教程失败")
            return False
        
        # 测试获取所有教程
        print("\n📖 测试获取所有教程...")
        all_tutorials = help_system.get_all_tutorials()
        print(f"✅ 获取 {len(all_tutorials)} 个教程")
        print(f"   教程: {', '.join(all_tutorials)}")
        
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_3_quickstart_wizard():
    """测试3: 快速入门向导"""
    print("\n" + "="*80)
    print("测试3: 快速入门向导")
    print("="*80)
    
    try:
        wizard = create_wizard()
        print("✅ QuickStartWizard 创建成功")
        
        print("\n🎉 测试欢迎信息...")
        wizard.show_welcome()
        print("✅ 欢迎信息显示成功")
        
        print("\n📋 测试命令摘要...")
        wizard.show_command_summary()
        print("✅ 命令摘要显示成功")
        
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_4_help_cli():
    """测试4: 帮助命令行接口"""
    print("\n" + "="*80)
    print("测试4: 帮助命令行接口")
    print("="*80)
    
    try:
        cli = create_help_cli()
        print("✅ HelpCLI 创建成功")
        
        # 测试显示命令帮助
        print("\n📚 测试显示命令帮助...")
        success = cli._show_command_help("run")
        print(f"   结果: {'成功' if success else '失败'}")
        
        # 测试列出所有命令
        print("\n📋 测试列出所有命令...")
        success = cli._list_commands()
        print(f"   结果: {'成功' if success else '失败'}")
        
        # 测试列出所有教程
        print("\n📖 测试列出所有教程...")
        success = cli._list_tutorials()
        print(f"   结果: {'成功' if success else '失败'}")
        
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_5_integration_test():
    """测试5: 集成测试"""
    print("\n" + "="*80)
    print("测试5: 集成测试")
    print("="*80)
    
    try:
        cli = create_help_cli()
        
        print("\n🧪 运行 help test 命令...")
        success = cli.run(["test"])
        print(f"📋 集成测试: {'成功' if success else '失败'}")
        
        return success
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("第69阶段 - 系统帮助和快速入门向导测试")
    print("="*80)
    
    tests = [
        test_1_data_structures,
        test_2_help_system,
        test_3_quickstart_wizard,
        test_4_help_cli,
        test_5_integration_test
    ]
    
    results = []
    for test_func in tests:
        result = test_func()
        results.append(result)
    
    print("\n" + "="*80)
    print("测试结果汇总")
    print("="*80)
    passed = sum(results)
    total = len(results)
    print(f"✅ 通过: {passed}/{total}")
    print(f"❌ 失败: {total-passed}/{total}")
    
    if passed == total:
        print("\n🎉 所有测试通过！第69阶段完成！")
        return 0
    else:
        print("\n❌ 部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())

