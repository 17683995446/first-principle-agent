#!/usr/bin/env python3
"""
第61阶段：系统监控与健康检查测试
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("🧪 第61阶段：系统监控与健康检查测试")
print("=" * 80)
print()


def test_system_monitor():
    """测试系统监控器"""
    print("\n📊 测试 1: 系统监控器")
    print("=" * 80)
    
    try:
        from first_principle_agent.core.system_monitor import (
            SystemMonitor, SystemMetrics, MetricType
        )
        
        # 创建监控器
        monitor = SystemMonitor(collection_interval=1)
        print("✅ SystemMonitor 创建成功")
        
        # 收集指标
        metrics = monitor.collect_metrics()
        print("✅ 指标收集成功")
        print(f"   CPU: {metrics.cpu_percent:.1f}%")
        print(f"   内存: {metrics.memory_percent:.1f}%")
        print(f"   磁盘: {metrics.disk_percent:.1f}%")
        
        # 添加指标到历史
        monitor.add_metrics(metrics)
        print("✅ 指标历史记录成功")
        
        # 获取最新指标
        latest = monitor.get_latest_metrics()
        if latest:
            print("✅ 获取最新指标成功")
        
        # 获取指标摘要
        summary = monitor.get_metrics_summary()
        if "status" not in summary:
            print("✅ 获取指标摘要成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 系统监控器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_health_checker():
    """测试健康检查器"""
    print("\n🏥 测试 2: 健康检查器")
    print("=" * 80)
    
    try:
        from first_principle_agent.core.system_monitor import (
            HealthChecker, HealthStatus
        )
        
        # 创建健康检查器
        checker = HealthChecker()
        print("✅ HealthChecker 创建成功")
        
        # 执行所有健康检查
        results = checker.check_all()
        print(f"✅ 健康检查执行成功 ({len(results)} 项)")
        
        # 显示检查结果
        for result in results:
            print(f"   {result.component}: {result.status.value} - {result.message}")
        
        # 获取整体状态
        overall = checker.get_overall_status()
        print(f"✅ 整体健康状态: {overall.value}")
        
        # 生成报告
        report = checker.generate_report()
        print(f"✅ 健康检查报告生成成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 健康检查器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_monitor_cli():
    """测试监控CLI"""
    print("\n💻 测试 3: 监控CLI")
    print("=" * 80)
    
    try:
        from first_principle_agent.core.system_monitor import MonitorCLI
        
        # 创建监控CLI
        cli = MonitorCLI()
        print("✅ MonitorCLI 创建成功")
        
        # 测试 status 命令
        print("\n📌 测试 monitor status:")
        success = cli.run(["status"])
        if success:
            print("✅ status 命令执行成功")
        else:
            print("❌ status 命令执行失败")
            return False
        
        # 测试 health 命令
        print("\n📌 测试 monitor health:")
        success = cli.run(["health"])
        if success:
            print("✅ health 命令执行成功")
        else:
            print("❌ health 命令执行失败")
            return False
        
        # 测试 metrics 命令
        print("\n📌 测试 monitor metrics:")
        success = cli.run(["metrics"])
        if success:
            print("✅ metrics 命令执行成功")
        else:
            print("❌ metrics 命令执行失败")
            return False
        
        # 测试 report 命令
        print("\n📌 测试 monitor report:")
        success = cli.run(["report"])
        if success:
            print("✅ report 命令执行成功")
        else:
            print("❌ report 命令执行失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 监控CLI测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_quick_health_check():
    """测试快速健康检查"""
    print("\n⚡ 测试 4: 快速健康检查")
    print("=" * 80)
    
    try:
        from first_principle_agent.core.system_monitor import quick_health_check, HealthStatus
        
        # 执行快速健康检查
        status = quick_health_check()
        print(f"✅ 快速健康检查成功")
        print(f"   状态: {status.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ 快速健康检查测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_main_integration():
    """测试主CLI集成"""
    print("\n🎯 测试 5: 主CLI集成")
    print("=" * 80)
    
    try:
        # 导入主模块
        import first_principle_agent.__main__ as main_module
        
        print("✅ 主模块导入成功")
        
        # 检查函数是否存在
        assert hasattr(main_module, 'run_monitor'), "run_monitor 函数不存在"
        print("✅ run_monitor 函数存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 主CLI集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    results = []
    
    # 运行测试
    results.append(("系统监控器", test_system_monitor()))
    results.append(("健康检查器", test_health_checker()))
    results.append(("监控CLI", test_monitor_cli()))
    results.append(("快速健康检查", test_quick_health_check()))
    results.append(("主CLI集成", test_main_integration()))
    
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
        print("\n🎉 所有测试通过！第61阶段完成！")
        print(f"📈 项目进度: 61/100 阶段完成")
        return 0
    else:
        print(f"\n⚠️  部分测试失败，请检查！")
        return 1


if __name__ == "__main__":
    sys.exit(main())
