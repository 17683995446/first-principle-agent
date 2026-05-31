#!/usr/bin/env python3
"""
测试原子动作模块
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from first_principle_agent.core import (
    AtomicAction, AtomicActionPlan, ActionType, AtomicActionStatus,
    TaskDAG, DAGNode, DAGEdge
)
from first_principle_agent.layers import (
    AtomicActionSplitter, AtomicActionValidator
)


def test_atomic_action_creation():
    """测试创建原子动作"""
    print("=" * 60)
    print("测试1: 创建原子动作")
    print("=" * 60)
    
    action = AtomicAction(
        action_id="test_001",
        action_type=ActionType.COMPUTE,
        name="TestCompute",
        description="A test computation"
    )
    
    assert action.action_id == "test_001"
    assert action.action_type == ActionType.COMPUTE
    assert action.name == "TestCompute"
    assert action.status == AtomicActionStatus.PENDING
    
    print("✓ 原子动作创建成功")


def test_action_dependencies():
    """测试动作依赖"""
    print("\n" + "=" * 60)
    print("测试2: 动作依赖")
    print("=" * 60)
    
    action1 = AtomicAction(
        action_id="action_1",
        action_type=ActionType.INIT,
        name="Initialize"
    )
    
    action2 = AtomicAction(
        action_id="action_2",
        action_type=ActionType.COMPUTE,
        name="Compute"
    )
    
    action2.add_dependency("action_1")
    
    assert "action_1" in action2.dependencies
    
    completed = ["action_1"]
    assert action2.can_execute(completed) is True
    
    print("✓ 动作依赖测试通过")


def test_action_plan():
    """测试动作计划"""
    print("\n" + "=" * 60)
    print("测试3: 动作计划")
    print("=" * 60)
    
    plan = AtomicActionPlan(
        plan_id="test_plan",
        name="Test Plan"
    )
    
    action1 = AtomicAction("a1", ActionType.INIT, "Init")
    action2 = AtomicAction("a2", ActionType.COMPUTE, "Compute")
    action3 = AtomicAction("a3", ActionType.WRITE, "Write")
    
    action2.add_dependency("a1")
    action3.add_dependency("a2")
    
    plan.add_action(action1)
    plan.add_action(action2)
    plan.add_action(action3)
    
    assert len(plan.actions) == 3
    
    ready_actions = plan.get_ready_actions()
    assert len(ready_actions) == 1
    assert ready_actions[0].action_id == "a1"
    
    print("✓ 动作计划测试通过")


def test_action_splitter():
    """测试动作拆分器"""
    print("\n" + "=" * 60)
    print("测试4: 动作拆分器")
    print("=" * 60)
    
    # 创建DAG
    node1 = DAGNode("task1", "Compute Task")
    node1.node_type = "compute"
    
    nodes = [node1]
    dag = TaskDAG("test_dag", nodes)
    
    splitter = AtomicActionSplitter()
    actions = splitter.split_task(node1)
    
    assert len(actions) > 0
    
    print(f"✓ 动作拆分成功，生成 {len(actions)} 个原子动作")


def test_split_dag():
    """测试拆分整个DAG"""
    print("\n" + "=" * 60)
    print("测试5: 拆分整个DAG")
    print("=" * 60)
    
    nodes = [
        DAGNode("task1", "Read Data"),
        DAGNode("task2", "Process Data"),
        DAGNode("task3", "Write Result")
    ]
    
    edges = [
        DAGEdge("e1", "task1", "task2"),
        DAGEdge("e2", "task2", "task3")
    ]
    
    nodes[0].node_type = "read"
    nodes[1].node_type = "compute"
    nodes[2].node_type = "write"
    
    dag = TaskDAG("test_workflow", nodes, edges)
    
    splitter = AtomicActionSplitter()
    plan = splitter.split_dag(dag)
    
    assert len(plan.actions) > 0
    
    print(f"✓ DAG拆分成功，生成 {len(plan.actions)} 个原子动作")


def test_validator():
    """测试动作验证器"""
    print("\n" + "=" * 60)
    print("测试6: 动作验证器")
    print("=" * 60)
    
    validator = AtomicActionValidator()
    
    # 验证有效动作
    valid_action = AtomicAction("valid_001", ActionType.COMPUTE, "ValidAction")
    result = validator.validate_action(valid_action)
    assert result["valid"] is True
    
    # 验证无效动作
    invalid_action = AtomicAction("", ActionType.COMPUTE, "")
    result = validator.validate_action(invalid_action)
    assert result["valid"] is False
    
    print("✓ 动作验证器测试通过")


def test_plan_validation():
    """测试计划验证"""
    print("\n" + "=" * 60)
    print("测试7: 计划验证")
    print("=" * 60)
    
    plan = AtomicActionPlan("test_plan_validation", "Validation Test")
    
    action1 = AtomicAction("a1", ActionType.INIT, "Init")
    action2 = AtomicAction("a2", ActionType.COMPUTE, "Compute")
    action3 = AtomicAction("a3", ActionType.WRITE, "Write")
    
    action2.add_dependency("a1")
    action3.add_dependency("a2")
    
    plan.add_action(action1)
    plan.add_action(action2)
    plan.add_action(action3)
    
    validator = AtomicActionValidator()
    result = validator.validate_plan(plan)
    
    assert result["valid"] is True
    
    print("✓ 计划验证测试通过")


def test_cycle_detection():
    """测试循环依赖检测"""
    print("\n" + "=" * 60)
    print("测试8: 循环依赖检测")
    print("=" * 60)
    
    plan = AtomicActionPlan("test_cycle", "Cycle Test")
    
    action1 = AtomicAction("a1", ActionType.INIT, "Init")
    action2 = AtomicAction("a2", ActionType.COMPUTE, "Compute")
    
    action1.add_dependency("a2")
    action2.add_dependency("a1")
    
    plan.add_action(action1)
    plan.add_action(action2)
    
    validator = AtomicActionValidator()
    result = validator.validate_plan(plan)
    
    assert result["valid"] is False
    assert len(result["details"].get("cycles", [])) > 0
    
    print("✓ 循环依赖检测测试通过")


def test_execution_validation():
    """测试执行验证"""
    print("\n" + "=" * 60)
    print("测试9: 执行验证")
    print("=" * 60)
    
    plan = AtomicActionPlan("test_exec", "Execution Test")
    
    action1 = AtomicAction("a1", ActionType.INIT, "Init")
    action2 = AtomicAction("a2", ActionType.COMPUTE, "Compute")
    
    action2.add_dependency("a1")
    
    plan.add_action(action1)
    plan.add_action(action2)
    
    validator = AtomicActionValidator()
    result = validator.validate_for_execution(plan)
    
    assert result["executable"] is True
    
    print("✓ 执行验证测试通过")


def test_topological_order():
    """测试拓扑排序"""
    print("\n" + "=" * 60)
    print("测试10: 拓扑排序")
    print("=" * 60)
    
    plan = AtomicActionPlan("test_topo", "Topology Test")
    
    action1 = AtomicAction("a1", ActionType.INIT, "Init")
    action2 = AtomicAction("a2", ActionType.COMPUTE, "Compute")
    action3 = AtomicAction("a3", ActionType.WRITE, "Write")
    
    action2.add_dependency("a1")
    action3.add_dependency("a2")
    
    plan.add_action(action1)
    plan.add_action(action2)
    plan.add_action(action3)
    
    validator = AtomicActionValidator()
    result = validator.check_dependency_order(plan)
    
    assert result["valid"] is True
    assert len(result["topological_order"]) == 3
    
    print(f"✓ 拓扑排序测试通过，顺序: {result['topological_order']}")


def test_improvement_suggestions():
    """测试改进建议"""
    print("\n" + "=" * 60)
    print("测试11: 改进建议")
    print("=" * 60)
    
    plan = AtomicActionPlan("test_improve", "Improvement Test")
    
    # 添加一个孤岛动作
    island_action = AtomicAction("isolated", ActionType.COMPUTE, "Isolated")
    plan.add_action(island_action)
    
    validator = AtomicActionValidator()
    suggestions = validator.suggest_improvements(plan)
    
    assert len(suggestions) > 0
    
    print(f"✓ 改进建议测试通过，共 {len(suggestions)} 条建议")


def test_action_status():
    """测试动作状态管理"""
    print("\n" + "=" * 60)
    print("测试12: 动作状态管理")
    print("=" * 60)
    
    action = AtomicAction("status_test", ActionType.COMPUTE, "StatusTest")
    
    assert action.status == AtomicActionStatus.PENDING
    
    action.mark_running()
    assert action.status == AtomicActionStatus.RUNNING
    
    action.mark_success()
    assert action.status == AtomicActionStatus.SUCCESS
    
    action.reset()
    assert action.status == AtomicActionStatus.PENDING
    
    print("✓ 动作状态管理测试通过")


def test_plan_progress():
    """测试计划进度"""
    print("\n" + "=" * 60)
    print("测试13: 计划进度")
    print("=" * 60)
    
    plan = AtomicActionPlan("progress_test", "Progress Test")
    
    action1 = AtomicAction("a1", ActionType.INIT, "Init")
    action2 = AtomicAction("a2", ActionType.COMPUTE, "Compute")
    action3 = AtomicAction("a3", ActionType.WRITE, "Write")
    
    action2.add_dependency("a1")
    action3.add_dependency("a2")
    
    plan.add_action(action1)
    plan.add_action(action2)
    plan.add_action(action3)
    
    # 标记第一个动作完成
    action1.mark_success()
    
    progress = plan.get_progress()
    
    assert progress["total"] == 3
    assert progress["completed"] == 1
    assert progress["pending"] == 2
    
    print(f"✓ 计划进度测试通过，进度: {progress}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("开始原子动作模块测试")
    print("=" * 60)
    
    try:
        test_atomic_action_creation()
        test_action_dependencies()
        test_action_plan()
        test_action_splitter()
        test_split_dag()
        test_validator()
        test_plan_validation()
        test_cycle_detection()
        test_execution_validation()
        test_topological_order()
        test_improvement_suggestions()
        test_action_status()
        test_plan_progress()
        
        print("\n" + "=" * 60)
        print("🎉 所有原子动作模块测试通过！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
