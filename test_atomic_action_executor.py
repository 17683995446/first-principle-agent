#!/usr/bin/env python3
"""
测试AtomicActionExecutor（原子动作执行器）
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from first_principle_agent.core import (
    AtomicAction, AtomicActionPlan, ActionType, AtomicActionStatus
)
from first_principle_agent.layers import AtomicActionExecutor


def test_sequential_execution():
    """测试顺序执行"""
    print("=" * 60)
    print("测试1: 顺序执行")
    print("=" * 60)

    plan = AtomicActionPlan("test_seq", "Sequential Test")

    action1 = AtomicAction("a1", ActionType.INIT, "Initialize")
    action2 = AtomicAction("a2", ActionType.COMPUTE, "Compute")
    action3 = AtomicAction("a3", ActionType.WRITE, "Write")

    action2.add_dependency("a1")
    action3.add_dependency("a2")

    plan.add_action(action1)
    plan.add_action(action2)
    plan.add_action(action3)

    executor = AtomicActionExecutor(enable_parallel=False)
    result = executor.execute_plan(plan)

    print(f"执行结果: {result}")
    assert result["success"] is True
    assert result["completed_count"] == 3

    print("✓ 顺序执行测试通过")


def test_parallel_execution():
    """测试并发执行"""
    print("\n" + "=" * 60)
    print("测试2: 并发执行")
    print("=" * 60)

    plan = AtomicActionPlan("test_par", "Parallel Test")

    action1 = AtomicAction("a1", ActionType.INIT, "Initialize")
    action2 = AtomicAction("a2", ActionType.COMPUTE, "Compute")
    action3 = AtomicAction("a3", ActionType.WRITE, "Write")

    action2.add_dependency("a1")
    action3.add_dependency("a2")

    plan.add_action(action1)
    plan.add_action(action2)
    plan.add_action(action3)

    executor = AtomicActionExecutor(enable_parallel=True, max_workers=4)
    result = executor.execute_plan(plan)

    print(f"执行结果: {result}")
    assert result["success"] is True
    assert result["completed_count"] == 3

    print("✓ 并发执行测试通过")


def test_callback_execution():
    """测试带回调的执行"""
    print("\n" + "=" * 60)
    print("测试3: 带回调的执行")
    print("=" * 60)

    plan = AtomicActionPlan("test_cb", "Callback Test")

    action1 = AtomicAction("a1", ActionType.INIT, "Initialize")
    action2 = AtomicAction("a2", ActionType.COMPUTE, "Compute")

    action2.add_dependency("a1")

    plan.add_action(action1)
    plan.add_action(action2)

    callbacks_received = []

    def callback(action, result, progress):
        callbacks_received.append({
            "action_id": action.action_id,
            "success": result.success
        })

    executor = AtomicActionExecutor(enable_parallel=False)
    result = executor.execute_plan(plan, callback=callback)

    print(f"执行结果: {result}")
    print(f"收到回调: {len(callbacks_received)}")
    assert result["success"] is True
    assert len(callbacks_received) == 2

    print("✓ 带回调的执行测试通过")


def test_custom_handler():
    """测试自定义处理器"""
    print("\n" + "=" * 60)
    print("测试4: 自定义处理器")
    print("=" * 60)

    plan = AtomicActionPlan("test_custom", "Custom Handler Test")

    action = AtomicAction("custom", ActionType.COMPUTE, "CustomAction")
    plan.add_action(action)

    def custom_handler(act: AtomicAction):
        return ExecutionResult(True, {"custom": "value"})

    from first_principle_agent.layers.atomic_action_executor import ExecutionResult

    executor = AtomicActionExecutor()
    executor.register_handler(ActionType.COMPUTE, custom_handler)

    result = executor.execute_plan(plan)

    print(f"执行结果: {result}")
    assert result["success"] is True

    completed_action = plan.get_action("custom")
    assert completed_action.outputs.get("custom") == "value"

    print("✓ 自定义处理器测试通过")


def test_validation_before_execution():
    """测试执行前验证"""
    print("\n" + "=" * 60)
    print("测试5: 执行前验证")
    print("=" * 60)

    plan = AtomicActionPlan("test_valid", "Validation Test")

    action1 = AtomicAction("a1", ActionType.INIT, "Initialize")
    action2 = AtomicAction("a2", ActionType.COMPUTE, "Compute")

    action2.add_dependency("a1")
    action2.add_dependency("a3")

    plan.add_action(action1)
    plan.add_action(action2)

    executor = AtomicActionExecutor()
    validation = executor.validate_before_execution(plan)

    print(f"验证结果: {validation}")
    assert validation["ready"] is False
    assert len(validation["errors"]) > 0

    print("✓ 执行前验证测试通过")


def test_execution_stats():
    """测试执行统计"""
    print("\n" + "=" * 60)
    print("测试6: 执行统计")
    print("=" * 60)

    plan = AtomicActionPlan("test_stats", "Stats Test")

    action1 = AtomicAction("a1", ActionType.INIT, "Initialize")
    action2 = AtomicAction("a2", ActionType.COMPUTE, "Compute")
    action3 = AtomicAction("a3", ActionType.WRITE, "Write")

    action2.add_dependency("a1")
    action3.add_dependency("a2")

    plan.add_action(action1)
    plan.add_action(action2)
    plan.add_action(action3)

    executor = AtomicActionExecutor(enable_parallel=False)
    result = executor.execute_plan(plan)

    stats = executor.get_execution_stats(plan)

    print(f"统计信息: {stats}")
    assert stats["total"] == 3
    assert stats["by_status"]["success"] == 3

    print("✓ 执行统计测试通过")


def test_empty_plan():
    """测试空计划"""
    print("\n" + "=" * 60)
    print("测试7: 空计划")
    print("=" * 60)

    plan = AtomicActionPlan("test_empty", "Empty Test")

    executor = AtomicActionExecutor()
    validation = executor.validate_before_execution(plan)

    print(f"验证结果: {validation}")
    assert validation["ready"] is False

    print("✓ 空计划测试通过")


def test_parallel_independent_actions():
    """测试并行执行独立动作"""
    print("\n" + "=" * 60)
    print("测试8: 并行执行独立动作")
    print("=" * 60)

    plan = AtomicActionPlan("test_parallel", "Parallel Independent Test")

    action1 = AtomicAction("a1", ActionType.INIT, "Init1")
    action2 = AtomicAction("a2", ActionType.INIT, "Init2")
    action3 = AtomicAction("a3", ActionType.INIT, "Init3")

    plan.add_action(action1)
    plan.add_action(action2)
    plan.add_action(action3)

    executor = AtomicActionExecutor(enable_parallel=True, max_workers=4)
    start_time = time.time()
    result = executor.execute_plan(plan)
    duration = time.time() - start_time

    print(f"执行结果: {result}")
    print(f"执行时间: {duration:.2f}秒")

    assert result["success"] is True
    assert result["completed_count"] == 3

    print("✓ 并行执行独立动作测试通过")


def test_execution_result():
    """测试执行结果类"""
    print("\n" + "=" * 60)
    print("测试9: 执行结果类")
    print("=" * 60)

    from first_principle_agent.layers.atomic_action_executor import ExecutionResult

    success_result = ExecutionResult(True, {"data": "value"})
    assert success_result.success is True
    assert success_result.output["data"] == "value"

    failure_result = ExecutionResult(False, error="Test error")
    assert failure_result.success is False
    assert failure_result.error == "Test error"

    print("✓ 执行结果类测试通过")


def test_stop_execution():
    """测试停止执行"""
    print("\n" + "=" * 60)
    print("测试10: 停止执行")
    print("=" * 60)

    plan = AtomicActionPlan("test_stop", "Stop Test")

    for i in range(10):
        action = AtomicAction(f"a{i}", ActionType.COMPUTE, f"Action{i}")
        if i > 0:
            action.add_dependency(f"a{i-1}")
        plan.add_action(action)

    executor = AtomicActionExecutor(enable_parallel=True)
    executor.stop()

    print("✓ 停止执行测试通过")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("开始测试AtomicActionExecutor")
    print("=" * 60)

    try:
        test_sequential_execution()
        test_parallel_execution()
        test_callback_execution()
        test_custom_handler()
        test_validation_before_execution()
        test_execution_stats()
        test_empty_plan()
        test_parallel_independent_actions()
        test_execution_result()
        test_stop_execution()

        print("\n" + "=" * 60)
        print("🎉 所有AtomicActionExecutor测试通过！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
