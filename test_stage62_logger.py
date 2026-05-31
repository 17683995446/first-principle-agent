#!/usr/bin/env python3
"""
第62阶段：日志系统和记录器测试
"""

import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("🧪 第62阶段：日志系统和记录器测试")
print("=" * 80)
print()


def test_system_logger():
    """测试系统日志记录器"""
    print("\n📝 测试 1: 系统日志记录器")
    print("=" * 80)
    
    try:
        from first_principle_agent.core.system_logger import (
            SystemLogger, LogLevel, LogConfig
        )
        
        # 创建临时配置
        temp_config = LogConfig(
            level=LogLevel.DEBUG,
            log_to_file=True,
            log_file_path="/tmp/test_logs/system.log",
            log_to_console=False
        )
        
        # 创建日志记录器
        logger = SystemLogger("test", temp_config)
        print("✅ SystemLogger 创建成功")
        
        # 测试各种日志级别
        logger.debug("这是DEBUG级别的消息", debug_info="test")
        logger.info("这是INFO级别的消息", info_data="value")
        logger.warning("这是WARNING级别的消息", warning_type="low")
        logger.error("这是ERROR级别的消息", error_code="E001")
        logger.critical("这是CRITICAL级别的消息", critical=True)
        
        print(f"✅ 日志记录成功，共 {len(logger.log_entries)} 条日志")
        
        # 检查日志条目
        assert len(logger.log_entries) == 5, f"期望5条日志，实际{len(logger.log_entries)}条"
        
        # 验证日志级别
        levels = [entry.level for entry in logger.log_entries]
        assert "DEBUG" in levels
        assert "INFO" in levels
        assert "WARNING" in levels
        assert "ERROR" in levels
        assert "CRITICAL" in levels
        
        print("✅ 所有日志级别验证通过")
        
        # 测试获取最近日志
        recent_logs = logger.get_recent_logs(3)
        assert len(recent_logs) == 3
        print(f"✅ 获取最近日志成功，{len(recent_logs)} 条")
        
        return True
        
    except Exception as e:
        print(f"❌ 系统日志记录器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_logger_manager():
    """测试日志管理器"""
    print("\n📋 测试 2: 日志管理器")
    print("=" * 80)
    
    try:
        from first_principle_agent.core.system_logger import (
            LoggerManager, SystemLogger, LogLevel
        )
        
        # 创建日志管理器
        manager = LoggerManager()
        print("✅ LoggerManager 创建成功")
        
        # 创建多个日志记录器
        logger1 = manager.get_logger("component1")
        logger2 = manager.get_logger("component2")
        logger3 = manager.get_logger("component3")
        
        print(f"✅ 创建了 {len(manager.get_all_loggers())} 个日志记录器")
        
        # 测试全局日志级别设置
        manager.set_global_level(LogLevel.DEBUG)
        print("✅ 全局日志级别设置成功")
        
        # 记录一些日志
        logger1.info("组件1启动")
        logger2.warning("组件2警告")
        logger3.error("组件3错误")
        
        print("✅ 多日志器记录成功")
        
        # 获取所有日志
        all_logs = manager.get_all_logs()
        assert "component1" in all_logs
        assert "component2" in all_logs
        assert "component3" in all_logs
        
        print(f"✅ 获取所有日志成功，共 {len(all_logs)} 个日志器")
        
        return True
        
    except Exception as e:
        print(f"❌ 日志管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_logger_cli():
    """测试日志命令行接口"""
    print("\n💻 测试 3: 日志命令行接口")
    print("=" * 80)
    
    try:
        from first_principle_agent.core.system_logger import LoggerCLI
        
        # 创建CLI
        cli = LoggerCLI()
        print("✅ LoggerCLI 创建成功")
        
        # 测试 status 命令
        print("\n📌 测试 log status:")
        success = cli.run(["status"])
        assert success, "status 命令失败"
        print("✅ status 命令执行成功")
        
        # 测试 test 命令
        print("\n📌 测试 log test:")
        success = cli.run(["test"])
        assert success, "test 命令失败"
        print("✅ test 命令执行成功")
        
        # 测试 logs 命令
        print("\n📌 测试 log logs:")
        success = cli.run(["logs"])
        assert success, "logs 命令失败"
        print("✅ logs 命令执行成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 日志CLI测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_quick_log():
    """测试快速日志记录"""
    print("\n⚡ 测试 4: 快速日志记录")
    print("=" * 80)
    
    try:
        from first_principle_agent.core.system_logger import (
            quick_log, create_logger, get_logger_manager
        )
        
        # 测试快速记录
        quick_log("info", "这是快速记录的INFO日志", quick_test=True)
        quick_log("warning", "这是快速记录的WARNING日志")
        quick_log("error", "这是快速记录的ERROR日志")
        
        print("✅ 快速日志记录成功")
        
        # 测试工厂函数
        logger = create_logger("factory_test")
        assert logger is not None
        print("✅ 日志工厂函数工作正常")
        
        manager = get_logger_manager()
        assert manager is not None
        print("✅ 日志管理器工厂函数工作正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 快速日志测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_log_export():
    """测试日志导出"""
    print("\n📤 测试 5: 日志导出")
    print("=" * 80)
    
    try:
        from first_principle_agent.core.system_logger import SystemLogger
        import json
        
        # 创建测试日志
        logger = SystemLogger("export_test")
        logger.info("测试导出日志1", test="export")
        logger.warning("测试导出日志2")
        logger.error("测试导出日志3")
        
        # 导出为JSON
        temp_file = "/tmp/test_log_export.json"
        logger.export_logs(temp_file, "json")
        print(f"✅ JSON日志导出成功到 {temp_file}")
        
        # 验证导出的文件
        with open(temp_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert len(data) == 3, f"期望3条日志，实际{len(data)}条"
            print(f"✅ 导出的JSON文件验证成功，共 {len(data)} 条日志")
        
        # 导出为TXT
        temp_file_txt = "/tmp/test_log_export.txt"
        logger.export_logs(temp_file_txt, "txt")
        print(f"✅ TXT日志导出成功到 {temp_file_txt}")
        
        return True
        
    except Exception as e:
        print(f"❌ 日志导出测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    results = []
    
    # 运行测试
    results.append(("系统日志记录器", test_system_logger()))
    results.append(("日志管理器", test_logger_manager()))
    results.append(("日志CLI", test_logger_cli()))
    results.append(("快速日志记录", test_quick_log()))
    results.append(("日志导出", test_log_export()))
    
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
        print("\n🎉 所有测试通过！第62阶段完成！")
        print(f"📈 项目进度: 62/100 阶段完成")
        return 0
    else:
        print(f"\n⚠️  部分测试失败，请检查！")
        return 1


if __name__ == "__main__":
    sys.exit(main())
