#!/usr/bin/env python3
"""
测试AtomicActionMonitor（原子动作监控器）
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from first_principle_agent.core import (
    AtomicAction, AtomicActionPlan, ActionType, AtomicActionStatus
)
from first_principle_agent.layers import AtomicActionMonitor


def test_monitor_creation():
    """测试创建监控器"""
    print("=" * 60)
    print("测试1: 创建监控器")
    print("=" * 60)

    monitor = AtomicActionMonitor(check_interval=0.5)
    assert monitor is not None
    assert monitor.check_interval == 0.5

    print("✓ 监控器创建成功")


def test_start_stop_monitoring():
    """测试开始和停止监控"""
    print("\n" + "=" * 60)
    print("测试2: 开始和停止监控")
    print("=" * 60)

    plan = AtomicActionPlan("test_monitor", "Monitor Test")

    action1 = AtomicAction("a1", ActionType.INIT, "Initialize")
    action2 = AtomicAction("a2", ActionType.COMPUTE, "Compute")

    plan.add_action(action1)
    plan.add_action(action2)

    monitor = AtomicActionMonitor(check_interval=0.1)
    monitor.start_monitoring(plan)

    assert monitor.monitoring is True

    time.sleep(0.5)

    monitor.stop_monitoring()

    assert monitor.monitoring is False

    print("✓ 开始和停止监控测试通过")


def test_metrics_collection():
    """测试指标收集"""
    print("\n" + "=" * 60)
    print("测试3: 指标收集")
    print("=" * 60)

    from first_principle_agent.layers.atomic_action_monitor import ActionMetrics

    metrics = ActionMetrics("test_action")

    metrics.record_start()
    time.sleep(0.1)
    metrics.record_end(status=AtomicActionStatus.SUCCESS)

    assert metrics.attempts == 1
    assert metrics.successes == 1
    assert metrics.duration is not None
    assert metrics.duration > 0

    print("✓ 指标收集测试通过")


def test_success_rate():
    """测试成功率计算"""
    print("\n" + "=" * 60)
    print("测试4: 成功率计算")
    print("=" * 60)

    from first_principle_agent.layers.atomic_action_monitor import ActionMetrics

    metrics = ActionMetrics("test_action")

    metrics.record_start()
    metrics.record_end(status=AtomicActionStatus.SUCCESS)

    metrics.record_start()
    metrics.record_end(status=AtomicActionStatus.SUCCESS)

    metrics.record_start()
    metrics.record_end(status=AtomicActionStatus.FAILED)

    success_rate = metrics.get_success_rate()
    assert 66.0 <= success_rate <= 67.0

    print(f"✓ 成功率计算测试通过，成功率: {success_rate:.2f}%")


def test_monitor_with_execution():
    """测试监控执行过程"""
    print("\n" + "=" * 60)
    print("测试5: 监控执行过程")
    print("=" * 60)

    plan = AtomicActionPlan("test_exec_monitor", "Execution Monitor Test")

    action1 = AtomicAction("a1", ActionType.INIT, "Initialize")
    action2 = AtomicAction("a2", ActionType.COMPUTE, "Compute")

    action2.add_dependency("a1")

    plan.add_action(action1)
    plan.add_action(action2)

    monitor = AtomicActionMonitor(check_interval=0.1)
    monitor.start_monitoring(plan)

    action1.mark_running()
    time.sleep(0.2)
    action1.mark_success()

    action2.mark_running()
    time.sleep(0.2)
    action2.mark_success()

    time.sleep(0.3)

    monitor.stop_monitoring()

    metrics = monitor.get_metrics()
    assert len(metrics) == 2

    summary = monitor.get_summary()
    assert summary["total_actions"] == 2
    assert summary["total_successes"] == 2

    print("✓ 监控执行过程测试通过")


def test_alerts():
    """测试告警"""
    print("\n" + "=" * 60)
    print("测试6: 告警")
    print("=" * 60)

    plan = AtomicActionPlan("test_alerts", "Alerts Test")

    action = AtomicAction("timeout_action", ActionType.COMPUTE, "TimeoutAction")
    action.mark_running()
    action.mark_timeout()

    plan.add_action(action)

    monitor = AtomicActionMonitor(check_interval=0.1)
    monitor.start_monitoring(plan)

    time.sleep(0.5)

    monitor.stop_monitoring()

    alerts = monitor.alerts
    assert len(alerts) > 0

    print(f"✓ 告警测试通过，收到 {len(alerts)} 个告警")


def test_callback():
    """测试回调"""
    print("\n" + "=" * 60)
    print("测试7: 回调")
    print("=" * 60)

    plan = AtomicActionPlan("test_callback", "Callback Test")
    action = AtomicAction("cb_action", ActionType.INIT, "CallbackAction")
    plan.add_action(action)

    callback_count = [0]

    def test_callback(plan, status):
        callback_count[0] += 1

    monitor = AtomicActionMonitor(check_interval=0.1)
    monitor.register_callback(test_callback)

    monitor.start_monitoring(plan)
    time.sleep(0.5)
    monitor.stop_monitoring()

    assert callback_count[0] > 0

    print(f"✓ 回调测试通过，回调被调用 {callback_count[0]} 次")


def test_detailed_report():
    """测试详细报告"""
    print("\n" + "=" * 60)
    print("测试8: 详细报告")
    print("=" * 60)

    plan = AtomicActionPlan("test_report", "Report Test")

    action1 = AtomicAction("a1", ActionType.INIT, "Initialize")
    action2 = AtomicAction("a2", ActionType.COMPUTE, "Compute")

    action2.add_dependency("a1")

    action1.mark_running()
    time.sleep(0.1)
    action1.mark_success()

    action2.mark_running()
    time.sleep(0.1)
    action2.mark_success()

    plan.add_action(action1)
    plan.add_action(action2)

    monitor = AtomicActionMonitor(check_interval=0.1)
    monitor.start_monitoring(plan)
    time.sleep(0.5)
    monitor.stop_monitoring()

    report = monitor.get_detailed_report()

    assert "原子动作监控报告" in report
    assert "总体统计" in report

    print("✓ 详细报告测试通过")


def test_reset():
    """测试重置"""
    print("\n" + "=" * 60)
    print("测试9: 重置")
    print("=" * 60)

    plan = AtomicActionPlan("test_reset", "Reset Test")
    action = AtomicAction("reset_action", ActionType.INIT, "ResetAction")
    plan.add_action(action)

    monitor = AtomicActionMonitor()
    monitor.start_monitoring(plan)
    time.sleep(0.3)

    monitor.reset()

    assert len(monitor.metrics) == 0
    assert len(monitor.alerts) == 0

    print("✓ 重置测试通过")


def test_summary_stats():
    """测试摘要统计"""
    print("\n" + "=" * 60)
    print("测试10: 摘要统计")
    print("=" * 60)

    plan = AtomicActionPlan("test_summary", "Summary Test")

    action1 = AtomicAction("a1", ActionType.INIT, "Initialize")
    action2 = AtomicAction("a2", ActionType.COMPUTE, "Compute")
    action3 = AtomicAction("a3", ActionType.WRITE, "Write")

    plan.add_action(action1)
    plan.add_action(action2)
    plan.add_action(action3)

    monitor = AtomicActionMonitor(check_interval=0.1)
    monitor.start_monitoring(plan)

    action1.mark_running()
    time.sleep(0.2)
    action1.mark_success()

    action2.mark_running()
    time.sleep(0.2)
    action2.mark_success()

    action3.mark_running()
    time.sleep(0.2)
    action3.mark_success()

    time.sleep(0.5)

    monitor.stop_monitoring()

    summary = monitor.get_summary()

    assert summary["total_actions"] == 3
    assert summary["total_successes"] == 3
    assert summary["total_failures"] == 0
    assert "duration_stats" in summary

    print("✓ 摘要统计测试通过")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("开始测试AtomicActionMonitor")
    print("=" * 60)

    try:
        test_monitor_creation()
        test_start_stop_monitoring()
        test_metrics_collection()
        test_success_rate()
        test_monitor_with_execution()
        test_alerts()
        test_callback()
        test_detailed_report()
        test_reset()
        test_summary_stats()

        print("\n" + "=" * 60)
        print("🎉 所有AtomicActionMonitor测试通过！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
