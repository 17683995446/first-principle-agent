#!/usr/bin/env python3
"""
测试TaskPlanner（任务规划器）
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from first_principle_agent.core import TaskDAG, DAGNode, DAGEdge, TaskTuple
from first_principle_agent.layers import TaskPlanner


def test_create_planner():
    """测试创建规划器"""
    print("=" * 60)
    print("测试1：创建任务规划器")
    print("=" * 60)

    planner = TaskPlanner()
    print(f"创建了TaskPlanner: {planner}")
    print(f"包含组件: DAGBuilder, DependencyAnalyzer, CycleDetector, TopologicalSorter, CriticalPathFinder, DAGValidator, DependencyPruner")

    assert planner is not None
    print("✅ 测试1通过")


def test_validate_dag():
    """测试验证DAG"""
    print("\n" + "=" * 60)
    print("测试2：验证DAG")
    print("=" * 60)

    nodes = [
        DAGNode("A", "任务A"),
        DAGNode("B", "任务B"),
        DAGNode("C", "任务C")
    ]

    edges = [
        DAGEdge("e1", "A", "B"),
        DAGEdge("e2", "B", "C")
    ]

    dag = TaskDAG("test_dag", nodes, edges)

    planner = TaskPlanner()
    result = planner.validate_dag(dag)

    print(f"验证结果: {result}")

    assert result["valid"] is True, "有效DAG应该验证通过"
    print("✅ 测试2通过")


def test_get_execution_plan():
    """测试获取执行计划"""
    print("\n" + "=" * 60)
    print("测试3：获取执行计划")
    print("=" * 60)

    nodes = [
        DAGNode("A", "任务A"),
        DAGNode("B", "任务B"),
        DAGNode("C", "任务C"),
        DAGNode("D", "任务D")
    ]

    edges = [
        DAGEdge("e1", "A", "B"),
        DAGEdge("e2", "A", "C"),
        DAGEdge("e3", "B", "D"),
        DAGEdge("e4", "C", "D")
    ]

    dag = TaskDAG("test_execution", nodes, edges)

    planner = TaskPlanner()
    plan = planner.get_execution_plan(dag)

    print(f"执行计划: {plan}")

    assert plan["success"] is True, "应该成功生成执行计划"
    assert "execution_order" in plan, "应该有执行顺序"
    print("✅ 测试3通过")


def test_suggest_improvements():
    """测试建议改进"""
    print("\n" + "=" * 60)
    print("测试4：建议改进")
    print("=" * 60)

    nodes = [
        DAGNode("A", "任务A"),
        DAGNode("B", "任务B"),
        DAGNode("C", "任务C"),
        DAGNode("D", "任务D")
    ]

    edges = [
        DAGEdge("e1", "A", "B"),
        DAGEdge("e2", "A", "C"),
        DAGEdge("e3", "B", "D"),
        DAGEdge("e4", "C", "D"),
        DAGEdge("e5", "A", "D")  # 冗余边
    ]

    dag = TaskDAG("test_improvements", nodes, edges)

    planner = TaskPlanner()
    suggestions = planner.suggest_improvements(dag)

    print(f"改进建议: {suggestions}")

    assert len(suggestions) > 0, "应该有改进建议"
    print("✅ 测试4通过")


def test_compare_dags():
    """测试比较DAG"""
    print("\n" + "=" * 60)
    print("测试5：比较DAG")
    print("=" * 60)

    nodes1 = [
        DAGNode("A", "任务A"),
        DAGNode("B", "任务B")
    ]

    edges1 = [
        DAGEdge("e1", "A", "B")
    ]

    dag1 = TaskDAG("dag1", nodes1, edges1)

    nodes2 = [
        DAGNode("A", "任务A"),
        DAGNode("B", "任务B"),
        DAGNode("C", "任务C")
    ]

    edges2 = [
        DAGEdge("e1", "A", "B"),
        DAGEdge("e2", "B", "C")
    ]

    dag2 = TaskDAG("dag2", nodes2, edges2)

    planner = TaskPlanner()
    comparison = planner.compare_dags(dag1, dag2)

    print(f"DAG比较结果: {comparison}")

    assert "node_count_diff" in comparison, "应该有节点数差异"
    assert "edge_count_diff" in comparison, "应该有边数差异"
    print("✅ 测试5通过")


def test_generate_report():
    """测试生成报告"""
    print("\n" + "=" * 60)
    print("测试6：生成报告")
    print("=" * 60)

    nodes = [
        DAGNode("A", "任务A"),
        DAGNode("B", "任务B"),
        DAGNode("C", "任务C")
    ]

    edges = [
        DAGEdge("e1", "A", "B"),
        DAGEdge("e2", "B", "C")
    ]

    dag = TaskDAG("test_report", nodes, edges)

    planner = TaskPlanner()
    report = planner.generate_report(dag)

    print("报告内容:")
    print(report)

    assert "任务规划报告" in report, "报告应该包含标题"
    assert "DAG ID" in report, "报告应该包含DAG ID"
    print("✅ 测试6通过")


def test_plan_with_invalid_dag():
    """测试规划有问题的DAG"""
    print("\n" + "=" * 60)
    print("测试7：规划有环的DAG")
    print("=" * 60)

    nodes = [
        DAGNode("A", "任务A"),
        DAGNode("B", "任务B"),
        DAGNode("C", "任务C")
    ]

    edges = [
        DAGEdge("e1", "A", "B"),
        DAGEdge("e2", "B", "C"),
        DAGEdge("e3", "C", "A")  # 环
    ]

    dag = TaskDAG("test_cycle", nodes, edges)

    planner = TaskPlanner()
    validation = planner.validate_dag(dag)

    print(f"验证结果: {validation}")

    assert validation["valid"] is False, "有环的DAG应该验证失败"
    print("✅ 测试7通过")


def test_plan_empty_dag():
    """测试空DAG"""
    print("\n" + "=" * 60)
    print("测试8：空DAG")
    print("=" * 60)

    dag = TaskDAG("test_empty")

    planner = TaskPlanner()
    validation = planner.validate_dag(dag)

    print(f"验证结果: {validation}")

    assert validation["valid"] is False, "空DAG应该验证失败"
    print("✅ 测试8通过")


def test_execution_plan_details():
    """测试执行计划详细信息"""
    print("\n" + "=" * 60)
    print("测试9：执行计划详细信息")
    print("=" * 60)

    nodes = [
        DAGNode("A", "任务A"),
        DAGNode("B", "任务B"),
        DAGNode("C", "任务C"),
        DAGNode("D", "任务D"),
        DAGNode("E", "任务E")
    ]

    edges = [
        DAGEdge("e1", "A", "B"),
        DAGEdge("e2", "A", "C"),
        DAGEdge("e3", "B", "D"),
        DAGEdge("e4", "C", "D"),
        DAGEdge("e5", "D", "E")
    ]

    dag = TaskDAG("test_details", nodes, edges)

    planner = TaskPlanner()
    plan = planner.get_execution_plan(dag)

    print(f"执行计划: {plan}")

    assert plan["success"] is True, "应该成功生成执行计划"
    assert "parallel_groups" in plan, "应该有并行分组"
    assert "levels" in plan, "应该有层级信息"
    assert "critical_path" in plan, "应该有关键路径"
    print("✅ 测试9通过")


def test_optimization_suggestion():
    """测试优化建议"""
    print("\n" + "=" * 60)
    print("测试10：优化建议")
    print("=" * 60)

    nodes = [
        DAGNode("A", "任务A"),
        DAGNode("B", "任务B"),
        DAGNode("C", "任务C")
    ]

    edges = [
        DAGEdge("e1", "A", "B"),
        DAGEdge("e2", "A", "C"),
        DAGEdge("e3", "B", "C")  # 冗余边
    ]

    dag = TaskDAG("test_optimization", nodes, edges)

    planner = TaskPlanner()
    suggestions = planner.suggest_improvements(dag)

    print(f"优化建议: {suggestions}")

    optimization_suggestions = [s for s in suggestions if s["type"] == "optimization"]
    assert len(optimization_suggestions) > 0, "应该有优化建议"
    print("✅ 测试10通过")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("开始测试TaskPlanner")
    print("=" * 60)

    try:
        test_create_planner()
        test_validate_dag()
        test_get_execution_plan()
        test_suggest_improvements()
        test_compare_dags()
        test_generate_report()
        test_plan_with_invalid_dag()
        test_plan_empty_dag()
        test_execution_plan_details()
        test_optimization_suggestion()

        print("\n" + "=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
