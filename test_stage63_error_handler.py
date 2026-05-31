#!/usr/bin/env python3
"""
第63阶段：错误处理与异常管理系统测试
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("🧪 第63阶段：错误处理与异常管理系统测试")
print("=" * 80)
print()


def test_custom_exceptions():
    """测试自定义异常类"""
    print("\n🔧 测试 1: 自定义异常类")
    print("=" * 80)
    
    try:
        from first_principle_agent.core.error_handler import (
            ValidationError, ExecutionError, TimeoutError, ResourceError,
            BaseSystemException, ErrorSeverity, ErrorCategory
        )
        
        # 测试验证错误
        validation_error = ValidationError("测试验证错误", {"field": "username"})
        assert validation_error.error_type == "ValidationError"
        assert validation_error.severity == ErrorSeverity.LOW
        assert validation_error.category == ErrorCategory.VALIDATION
        print("✅ ValidationError 测试通过")
        
        # 测试执行错误
        execution_error = ExecutionError("测试执行错误", {"task": "task_1"})
        assert execution_error.error_type == "ExecutionError"
        assert execution_error.severity == ErrorSeverity.HIGH
        print("✅ ExecutionError 测试通过")
        
        # 测试超时错误
        timeout_error = TimeoutError("测试超时错误", {"timeout": 30})
        assert timeout_error.error_type == "TimeoutError"
        assert timeout_error.category == ErrorCategory.TIMEOUT
        print("✅ TimeoutError 测试通过")
        
        # 测试资源错误
        resource_error = ResourceError("测试资源错误", {"resource": "memory"})
        assert resource_error.error_type == "ResourceError"
        assert resource_error.severity == ErrorSeverity.HIGH
        print("✅ ResourceError 测试通过")
        
        # 测试错误信息转换
        error_info = validation_error.to_error_info()
        assert error_info.error_type == "ValidationError"
        assert error_info.error_id is not None
        assert error_info.timestamp is not None
        print("✅ 错误信息转换测试通过")
        
        return True
        
    except Exception as e:
        print(f"❌ 自定义异常类测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handler():
    """测试错误处理器"""
    print("\n🎯 测试 2: 错误处理器")
    print("=" * 80)
    
    try:
        from first_principle_agent.core.error_handler import (
            ErrorHandler, ErrorSeverity, ErrorCategory
        )
        
        # 创建错误处理器
        handler = ErrorHandler()
        print("✅ ErrorHandler 创建成功")
        
        # 测试异常处理
        try:
            raise ValueError("测试异常")
        except Exception as e:
            error_info = handler.handle_exception(e, context="test")
            assert error_info.error_id is not None
            assert error_info.error_type == "ValueError"
            print("✅ 异常处理测试通过")
        
        # 测试自定义异常处理
        from first_principle_agent.core.error_handler import ValidationError
        validation_error = ValidationError("字段验证失败", {"field": "email"})
        error_info = handler.handle_exception(validation_error, context="validation")
        assert error_info.category == ErrorCategory.VALIDATION
        print("✅ 自定义异常处理测试通过")
        
        # 测试错误历史
        assert len(handler.error_history) >= 2
        print(f"✅ 错误历史记录成功 ({len(handler.error_history)} 条)")
        
        # 测试错误统计
        stats = handler.get_error_statistics()
        assert "total" in stats
        assert "by_severity" in stats
        assert "by_category" in stats
        print(f"✅ 错误统计成功 (总数: {stats['total']})")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误处理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_recovery_manager():
    """测试错误恢复管理器"""
    print("\n🔄 测试 3: 错误恢复管理器")
    print("=" * 80)
    
    try:
        from first_principle_agent.core.error_handler import (
            ErrorRecoveryManager, RecoveryAction
        )
        
        # 创建恢复管理器
        manager = ErrorRecoveryManager()
        print("✅ ErrorRecoveryManager 创建成功")
        
        # 测试带恢复的函数执行
        def failing_function():
            raise ValueError("测试失败")
        
        def successful_function():
            return "成功!"
        
        # 测试失败函数的恢复（使用safe策略，它有fallback值）
        result = manager.execute_with_recovery(
            failing_function,
            strategy_name="safe"
        )
        assert result == "fallback_value"
        print("✅ 失败函数恢复测试通过（使用fallback值）")
        
        # 测试失败函数使用默认策略（应该抛出异常）
        try:
            manager.execute_with_recovery(
                failing_function,
                strategy_name="default"
            )
            print("❌ 应该抛出异常")
            return False
        except ValueError as e:
            print("✅ 默认策略在无fallback时抛出异常测试通过")
        
        # 测试成功函数
        result = manager.execute_with_recovery(successful_function)
        assert result == "成功!"
        print("✅ 成功函数执行测试通过")
        
        # 测试恢复统计
        stats = manager.get_recovery_statistics()
        assert "total_attempts" in stats
        assert "successful" in stats
        assert "failed" in stats
        assert "success_rate" in stats
        print(f"✅ 恢复统计成功 (尝试: {stats['total_attempts']}, 成功率: {stats['success_rate']:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误恢复管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_cli():
    """测试错误处理命令行接口"""
    print("\n💻 测试 4: 错误处理CLI")
    print("=" * 80)
    
    try:
        from first_principle_agent.core.error_handler import ErrorCLI
        
        # 创建CLI
        cli = ErrorCLI()
        print("✅ ErrorCLI 创建成功")
        
        # 测试 status 命令
        print("\n📌 测试 error status:")
        success = cli.run(["status"])
        assert success, "status 命令失败"
        print("✅ status 命令执行成功")
        
        # 测试 test 命令
        print("\n📌 测试 error test:")
        success = cli.run(["test"])
        assert success, "test 命令失败"
        print("✅ test 命令执行成功")
        
        # 测试 history 命令
        print("\n📌 测试 error history:")
        success = cli.run(["history"])
        assert success, "history 命令失败"
        print("✅ history 命令执行成功")
        
        # 测试 recovery 命令
        print("\n📌 测试 error recovery:")
        success = cli.run(["recovery"])
        assert success, "recovery 命令失败"
        print("✅ recovery 命令执行成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误处理CLI测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_quick_error_handling():
    """测试快速错误处理"""
    print("\n⚡ 测试 5: 快速错误处理")
    print("=" * 80)
    
    try:
        from first_principle_agent.core.error_handler import (
            create_error_handler, create_recovery_manager, handle_error
        )
        
        # 测试工厂函数
        handler = create_error_handler()
        assert handler is not None
        print("✅ create_error_handler 工厂函数工作正常")
        
        recovery_manager = create_recovery_manager()
        assert recovery_manager is not None
        print("✅ create_recovery_manager 工厂函数工作正常")
        
        # 测试快速处理
        try:
            raise Exception("快速测试异常")
        except Exception as e:
            error_info = handle_error(e, context="quick_test")
            assert error_info is not None
            assert error_info.error_id is not None
            print("✅ handle_error 快速处理函数工作正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 快速错误处理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    results = []
    
    # 运行测试
    results.append(("自定义异常类", test_custom_exceptions()))
    results.append(("错误处理器", test_error_handler()))
    results.append(("错误恢复管理器", test_error_recovery_manager()))
    results.append(("错误处理CLI", test_error_cli()))
    results.append(("快速错误处理", test_quick_error_handling()))
    
    # 打印汇总
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
        print("\n🎉 所有测试通过！第63阶段完成！")
        print(f"📈 项目进度: 63/100 阶段完成")
        return 0
    else:
        print(f"\n⚠️  部分测试失败，请检查！")
        return 1


if __name__ == "__main__":
    sys.exit(main())
