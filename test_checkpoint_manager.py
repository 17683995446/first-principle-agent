#!/usr/bin/env python3
"""
测试CheckpointManager（检查点管理器）
"""

import sys
import os
import shutil
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from first_principle_agent.core import (
    AtomicAction, AtomicActionPlan, ActionType, AtomicActionStatus
)
from first_principle_agent.layers import CheckpointManager


def create_test_plan() -> AtomicActionPlan:
    """创建测试计划"""
    plan = AtomicActionPlan("test_plan", "Test Plan")
    
    for i in range(1, 11):
        action = AtomicAction(
            action_id=f"action_{i:02d}",
            action_type=ActionType.COMPUTE,
            name=f"Action {i}"
        )
        plan.add_action(action)
    
    return plan


def test_checkpoint_creation():
    """测试检查点创建"""
    print("=" * 60)
    print("测试1: 检查点创建")
    print("=" * 60)
    
    plan = create_test_plan()
    
    manager = CheckpointManager(storage_path="./test_checkpoints_1")
    manager.clear_checkpoints()
    
    for action in plan.actions[:5]:
        action.mark_running()
        time.sleep(0.01)
        action.mark_success()
    
    checkpoint = manager.create_checkpoint(plan, "first_checkpoint")
    
    assert checkpoint is not None
    assert checkpoint.name == "first_checkpoint"
    assert len(checkpoint.action_ids) == 5
    
    print("✓ 检查点创建成功")
    
    manager.clear_checkpoints()
    shutil.rmtree("./test_checkpoints_1", ignore_errors=True)


def test_checkpoint_listing():
    """测试检查点列表"""
    print("\n" + "=" * 60)
    print("测试2: 检查点列表")
    print("=" * 60)
    
    plan = create_test_plan()
    
    manager = CheckpointManager(storage_path="./test_checkpoints_2")
    manager.clear_checkpoints()
    
    for i, action in enumerate(plan.actions):
        action.mark_running()
        time.sleep(0.01)
        action.mark_success()
        
        if (i + 1) % 3 == 0:
            manager.create_checkpoint(plan, f"checkpoint_{(i + 1) // 3}")
    
    checkpoints = manager.list_checkpoints()
    
    assert len(checkpoints) == 3
    
    print(f"✓ 检查点列表测试通过，共找到 {len(checkpoints)} 个检查点")
    
    manager.clear_checkpoints()
    shutil.rmtree("./test_checkpoints_2", ignore_errors=True)


def test_checkpoint_retrieval():
    """测试检查点获取"""
    print("\n" + "=" * 60)
    print("测试3: 检查点获取")
    print("=" * 60)
    
    plan = create_test_plan()
    
    manager = CheckpointManager(storage_path="./test_checkpoints_3")
    manager.clear_checkpoints()
    
    for action in plan.actions[:5]:
        action.mark_running()
        time.sleep(0.01)
        action.mark_success()
    
    checkpoint = manager.create_checkpoint(plan, "test_checkpoint")
    
    retrieved = manager.get_checkpoint(checkpoint.checkpoint_id)
    
    assert retrieved is not None
    assert retrieved.checkpoint_id == checkpoint.checkpoint_id
    assert retrieved.name == checkpoint.name
    
    print("✓ 检查点获取测试通过")
    
    manager.clear_checkpoints()
    shutil.rmtree("./test_checkpoints_3", ignore_errors=True)


def test_checkpoint_validation():
    """测试检查点验证"""
    print("\n" + "=" * 60)
    print("测试4: 检查点验证")
    print("=" * 60)
    
    plan = create_test_plan()
    
    manager = CheckpointManager(storage_path="./test_checkpoints_4")
    manager.clear_checkpoints()
    
    for action in plan.actions[:3]:
        action.mark_running()
        time.sleep(0.01)
        action.mark_success()
    
    checkpoint = manager.create_checkpoint(plan, "validate_test")
    
    assert checkpoint.validated is False
    
    result = manager.validate_checkpoint(checkpoint.checkpoint_id)
    
    assert result is True
    
    updated = manager.get_checkpoint(checkpoint.checkpoint_id)
    assert updated.validated is True
    
    print("✓ 检查点验证测试通过")
    
    manager.clear_checkpoints()
    shutil.rmtree("./test_checkpoints_4", ignore_errors=True)


def test_checkpoint_rollback():
    """测试检查点回滚"""
    print("\n" + "=" * 60)
    print("测试5: 检查点回滚")
    print("=" * 60)
    
    plan = create_test_plan()
    
    manager = CheckpointManager(storage_path="./test_checkpoints_5")
    manager.clear_checkpoints()
    
    for action in plan.actions[:5]:
        action.mark_running()
        time.sleep(0.01)
        action.mark_success()
    
    checkpoint = manager.create_checkpoint(plan, "rollback_test")
    
    for action in plan.actions[5:10]:
        action.mark_running()
        time.sleep(0.01)
        action.mark_failed()
    
    progress_before = plan.get_progress()
    assert progress_before["completed"] == 5
    assert progress_before["failed"] == 5
    
    result = manager.rollback_to_checkpoint(checkpoint.checkpoint_id, plan)
    
    assert result is True
    
    for action in plan.actions[:5]:
        assert action.status in [AtomicActionStatus.SUCCESS, AtomicActionStatus.SKIPPED]
    
    for action in plan.actions[5:10]:
        assert action.status == AtomicActionStatus.PENDING
    
    print("✓ 检查点回滚测试通过")
    
    manager.clear_checkpoints()
    shutil.rmtree("./test_checkpoints_5", ignore_errors=True)


def test_checkpoint_deletion():
    """测试检查点删除"""
    print("\n" + "=" * 60)
    print("测试6: 检查点删除")
    print("=" * 60)
    
    plan = create_test_plan()
    
    manager = CheckpointManager(storage_path="./test_checkpoints_6")
    manager.clear_checkpoints()
    
    for action in plan.actions[:2]:
        action.mark_running()
        time.sleep(0.01)
        action.mark_success()
    
    checkpoint = manager.create_checkpoint(plan, "delete_test")
    
    checkpoints_before = manager.list_checkpoints()
    assert len(checkpoints_before) == 1
    
    result = manager.delete_checkpoint(checkpoint.checkpoint_id)
    
    assert result is True
    
    checkpoints_after = manager.list_checkpoints()
    assert len(checkpoints_after) == 0
    
    print("✓ 检查点删除测试通过")
    
    manager.clear_checkpoints()
    shutil.rmtree("./test_checkpoints_6", ignore_errors=True)


def test_automatic_checkpoints():
    """测试自动检查点"""
    print("\n" + "=" * 60)
    print("测试7: 自动检查点")
    print("=" * 60)
    
    plan = create_test_plan()
    
    manager = CheckpointManager(storage_path="./test_checkpoints_7")
    manager.clear_checkpoints()
    
    for action in plan.actions:
        action.mark_running()
        time.sleep(0.01)
        action.mark_success()
    
    checkpoints = manager.create_automatic_checkpoints(plan, interval=3)
    
    assert len(checkpoints) >= 3
    
    print(f"✓ 自动检查点测试通过，创建了 {len(checkpoints)} 个检查点")
    
    manager.clear_checkpoints()
    shutil.rmtree("./test_checkpoints_7", ignore_errors=True)


def test_latest_checkpoint():
    """测试获取最新检查点"""
    print("\n" + "=" * 60)
    print("测试8: 获取最新检查点")
    print("=" * 60)
    
    plan = create_test_plan()
    
    manager = CheckpointManager(storage_path="./test_checkpoints_8")
    manager.clear_checkpoints()
    
    for action in plan.actions[:3]:
        action.mark_running()
        time.sleep(0.01)
        action.mark_success()
    
    manager.create_checkpoint(plan, "checkpoint_1")
    
    time.sleep(0.1)
    
    for action in plan.actions[3:6]:
        action.mark_running()
        time.sleep(0.01)
        action.mark_success()
    
    manager.create_checkpoint(plan, "checkpoint_2")
    
    latest = manager.get_latest_checkpoint(plan.plan_id)
    
    assert latest is not None
    assert latest.name == "checkpoint_2"
    
    print("✓ 获取最新检查点测试通过")
    
    manager.clear_checkpoints()
    shutil.rmtree("./test_checkpoints_8", ignore_errors=True)


def test_checkpoint_state_capture():
    """测试检查点状态捕获"""
    print("\n" + "=" * 60)
    print("测试9: 检查点状态捕获")
    print("=" * 60)
    
    plan = create_test_plan()
    
    manager = CheckpointManager(storage_path="./test_checkpoints_9")
    manager.clear_checkpoints()
    
    for action in plan.actions[:4]:
        action.mark_running()
        time.sleep(0.01)
        action.mark_success()
    
    checkpoint = manager.create_checkpoint(plan, "state_test")
    
    assert "progress" in checkpoint.state
    assert "actions" in checkpoint.state
    
    print("✓ 检查点状态捕获测试通过")
    
    manager.clear_checkpoints()
    shutil.rmtree("./test_checkpoints_9", ignore_errors=True)


def test_clear_checkpoints():
    """测试清除检查点"""
    print("\n" + "=" * 60)
    print("测试10: 清除检查点")
    print("=" * 60)
    
    plan = create_test_plan()
    
    manager = CheckpointManager(storage_path="./test_checkpoints_10")
    manager.clear_checkpoints()
    
    for i in range(3):
        for action in plan.actions[:2]:
            action.mark_running()
            time.sleep(0.01)
            action.mark_success()
        
        manager.create_checkpoint(plan, f"clear_test_{i}")
    
    checkpoints_before = manager.list_checkpoints()
    assert len(checkpoints_before) == 3
    
    manager.clear_checkpoints(plan.plan_id)
    
    checkpoints_after = manager.list_checkpoints()
    assert len(checkpoints_after) == 0
    
    print("✓ 清除检查点测试通过")
    
    manager.clear_checkpoints()
    shutil.rmtree("./test_checkpoints_10", ignore_errors=True)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("开始测试CheckpointManager")
    print("=" * 60)
    
    try:
        test_checkpoint_creation()
        test_checkpoint_listing()
        test_checkpoint_retrieval()
        test_checkpoint_validation()
        test_checkpoint_rollback()
        test_checkpoint_deletion()
        test_automatic_checkpoints()
        test_latest_checkpoint()
        test_checkpoint_state_capture()
        test_clear_checkpoints()
        
        print("\n" + "=" * 60)
        print("🎉 所有CheckpointManager测试通过！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
