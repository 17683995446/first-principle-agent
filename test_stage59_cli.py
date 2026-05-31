#!/usr/bin/env python3
"""
第59阶段：CLI功能测试
测试命令行接口
"""

import sys
import os
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("🧪 第59阶段：CLI功能测试")
print("=" * 80)
print()


def run_command(command_args, description):
    """运行命令并返回结果"""
    print(f"📋 {description}")
    print(f"   命令: {' '.join(command_args)}")
    
    try:
        result = subprocess.run(
            command_args,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"   返回码: {result.returncode}")
        print(f"   输出:\n{result.stdout}")
        
        if result.stderr:
            print(f"   错误输出:\n{result.stderr}")
        
        return result.returncode == 0, result.stdout
        
    except Exception as e:
        print(f"   ❌ 执行失败: {e}")
        return False, None


def test_help():
    """测试 help 命令"""
    print("\n" + "=" * 80)
    print("📚 测试 1: help 命令")
    print("=" * 80)
    
    success, output = run_command(
        [sys.executable, "-m", "first_principle_agent", "help"],
        "运行 help 命令"
    )
    
    if success and "使用指南" in output:
        print("✅ help 命令测试通过！")
        return True
    else:
        print("❌ help 命令测试失败！")
        return False


def test_status():
    """测试 status 命令"""
    print("\n" + "=" * 80)
    print("📊 测试 2: status 命令")
    print("=" * 80)
    
    success, output = run_command(
        [sys.executable, "-m", "first_principle_agent", "status"],
        "运行 status 命令"
    )
    
    if success and "系统状态" in output:
        print("✅ status 命令测试通过！")
        return True
    else:
        print("❌ status 命令测试失败！")
        return False


def test_test():
    """测试 test 命令"""
    print("\n" + "=" * 80)
    print("🧪 测试 3: test 命令")
    print("=" * 80)
    
    success, output = run_command(
        [sys.executable, "-m", "first_principle_agent", "test"],
        "运行 test 命令"
    )
    
    if success and "所有测试通过" in output:
        print("✅ test 命令测试通过！")
        return True
    else:
        print("❌ test 命令测试失败！")
        return False


def test_demo():
    """测试 demo 命令"""
    print("\n" + "=" * 80)
    print("🚀 测试 4: demo 命令")
    print("=" * 80)
    
    success, output = run_command(
        [sys.executable, "-m", "first_principle_agent", "demo"],
        "运行 demo 命令"
    )
    
    if success and "演示完成" in output:
        print("✅ demo 命令测试通过！")
        return True
    else:
        print("❌ demo 命令测试失败！")
        return False


def test_run():
    """测试 run 命令"""
    print("\n" + "=" * 80)
    print("🎯 测试 5: run 命令")
    print("=" * 80)
    
    success, output = run_command(
        [sys.executable, "-m", "first_principle_agent", "run", "测试需求"],
        "运行 run 命令"
    )
    
    if success and "处理完成" in output:
        print("✅ run 命令测试通过！")
        return True
    else:
        print("❌ run 命令测试失败！")
        return False


def main():
    """主测试函数"""
    results = []
    
    # 运行各个测试
    results.append(("help", test_help()))
    results.append(("status", test_status()))
    results.append(("test", test_test()))
    results.append(("demo", test_demo()))
    results.append(("run", test_run()))
    
    # 打印测试结果汇总
    print("\n" + "=" * 80)
    print("📊 测试结果汇总")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n总计: {passed}/{len(results)} 通过, {failed}/{len(results)} 失败")
    
    if failed == 0:
        print("\n🎉 所有测试通过！第59阶段完成！")
        print(f"📈 项目进度: 59/100 阶段完成")
        return 0
    else:
        print(f"\n⚠️  部分测试失败，请检查！")
        return 1


if __name__ == "__main__":
    sys.exit(main())
