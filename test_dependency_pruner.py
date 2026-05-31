#!/usr/bin/env python3
"""
测试DependencyPruner（冗余依赖裁剪器）
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from first_principle_agent.core import TaskDAG, DAGNode, DAGEdge
from first_principle_agent.layers import DependencyPruner


def test_find_redundant_edges():
    """测试查找冗余边"""
    print("=" * 60)
    print("测试1：查找冗余边")
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
        DAGEdge("e3", "B", "C"),  # 冗余边（因为A->B->C已经存在）
        DAGEdge("e4", "C", "D")
    ]

    dag = TaskDAG("test_redundant", nodes, edges)

    pruner = DependencyPruner()
    prune_result = pruner.prune(dag)

    print(f"裁剪结果: {prune_result}")

    assert prune_result["success"] is True, "裁剪应该成功"
    assert prune_result["pruned_edge_count"] > 0, "应该找到冗余边"
    print("✅ 测试1通过")


def test_prune_no_redundancy():
    """测试没有冗余边的DAG"""
    print("\n" + "=" * 60)
    print("测试2：没有冗余边的DAG")
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

    dag = TaskDAG("test_no_redundant", nodes, edges)

    pruner = DependencyPruner()
    prune_result = pruner.prune(dag)

    print(f"裁剪结果: {prune_result}")

    assert prune_result["success"] is True, "裁剪应该成功"
    assert prune_result["pruned_edge_count"] == 0, "不应该有冗余边"
    print("✅ 测试2通过")


def test_transitive_dependencies():
    """测试传递依赖计算"""
    print("\n" + "=" * 60)
    print("测试3：传递依赖计算")
    print("=" * 60)

    nodes = [
        DAGNode("A", "任务A"),
        DAGNode("B", "任务B"),
        DAGNode("C", "任务C"),
        DAGNode("D", "任务D")
    ]

    edges = [
        DAGEdge("e1", "A", "B"),
        DAGEdge("e2", "B", "C"),
        DAGEdge("e3", "C", "D")
    ]

    dag = TaskDAG("test_transitive", nodes, edges)

    pruner = DependencyPruner()
    transitive_deps = pruner.find_transitive_dependencies(dag)

    print(f"传递依赖: {transitive_deps}")

    assert "D" in transitive_deps, "D应该有传递依赖"
    assert "A" in transitive_deps["D"], "D应该依赖A"
    print("✅ 测试3通过")


def test_optimize():
    """测试DAG优化"""
    print("\n" + "=" * 60)
    print("测试4：DAG优化")
    print("=" * 60)

    nodes = [
        DAGNode("A", "任务A"),
        DAGNode("B", "任务B"),
        DAGNode("C", "任务C")
    ]

    edges = [
        DAGEdge("e1", "A", "B"),
        DAGEdge("e2", "A", "C"),
        DAGEdge("e3", "B", "C"),  # 冗余边
        DAGEdge("e4", "A", "C")   # 重复边
    ]

    dag = TaskDAG("test_optimize", nodes, edges)

    pruner = DependencyPruner()
    optimize_result = pruner.optimize(dag)

    print(f"优化结果: {optimize_result}")

    assert optimize_result["success"] is True, "优化应该成功"
    assert optimize_result["edges_removed"] > 0, "应该移除了边"
    print("✅ 测试4通过")


def test_validate_optimization():
    """测试优化验证"""
    print("\n" + "=" * 60)
    print("测试5：优化验证")
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

    original_dag = TaskDAG("test_original", nodes, edges)

    pruner = DependencyPruner()
    prune_result = pruner.prune(original_dag)
    optimized_dag = prune_result["pruned_dag"]

    validation_result = pruner.validate_optimization(original_dag, optimized_dag)

    print(f"验证结果: {validation_result}")

    assert validation_result["valid"] is True, "优化应该正确"
    print("✅ 测试5通过")


def test_dependency_closure():
    """测试依赖闭包"""
    print("\n" + "=" * 60)
    print("测试6：依赖闭包")
    print("=" * 60)

    nodes = [
        DAGNode("A", "任务A"),
        DAGNode("B", "任务B"),
        DAGNode("C", "任务C"),
        DAGNode("D", "任务D")
    ]

    edges = [
        DAGEdge("e1", "A", "B"),
        DAGEdge("e2", "B", "C"),
        DAGEdge("e3", "C", "D")
    ]

    dag = TaskDAG("test_closure", nodes, edges)

    pruner = DependencyPruner()
    closure = pruner.get_dependency_closure(dag)

    print(f"依赖闭包: {closure}")

    assert "D" in closure, "D应该在闭包中"
    assert closure["D"]["total_dependency_count"] == 3, "D应该有3个传递依赖"
    print("✅ 测试6通过")


def test_no_redundancy_chain():
    """测试链式DAG无冗余"""
    print("\n" + "=" * 60)
    print("测试7：链式DAG无冗余")
    print("=" * 60)

    nodes = [
        DAGNode("1", "任务1"),
        DAGNode("2", "任务2"),
        DAGNode("3", "任务3"),
        DAGNode("4", "任务4"),
        DAGNode("5", "任务5")
    ]

    edges = [
        DAGEdge("e1", "1", "2"),
        DAGEdge("e2", "2", "3"),
        DAGEdge("e3", "3", "4"),
        DAGEdge("e4", "4", "5")
    ]

    dag = TaskDAG("test_chain", nodes, edges)

    pruner = DependencyPruner()
    prune_result = pruner.prune(dag)

    print(f"裁剪结果: {prune_result}")

    assert prune_result["pruned_edge_count"] == 0, "链式DAG不应该有冗余边"
    print("✅ 测试7通过")


def test_parallel_with_redundancy():
    """测试并行DAG的冗余"""
    print("\n" + "=" * 60)
    print("测试8：并行DAG的冗余")
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
        DAGEdge("e5", "A", "D")  # 冗余边（通过B或C间接依赖D）
    ]

    dag = TaskDAG("test_parallel_redundancy", nodes, edges)

    pruner = DependencyPruner()
    prune_result = pruner.prune(dag)

    print(f"裁剪结果: {prune_result}")

    assert prune_result["success"] is True, "裁剪应该成功"
    print("✅ 测试8通过")


def test_empty_dag():
    """测试空DAG"""
    print("\n" + "=" * 60)
    print("测试9：空DAG")
    print("=" * 60)

    dag = TaskDAG("test_empty")

    pruner = DependencyPruner()
    prune_result = pruner.prune(dag)

    print(f"裁剪结果: {prune_result}")

    assert prune_result["success"] is True, "空DAG应该处理成功"
    assert prune_result["pruned_edge_count"] == 0, "空DAG不应该有冗余边"
    print("✅ 测试9通过")


def test_suggest_edges():
    """测试建议添加边"""
    print("\n" + "=" * 60)
    print("测试10：建议添加边")
    print("=" * 60)

    nodes = [
        DAGNode("A", "任务A"),
        DAGNode("B", "任务B"),
        DAGNode("C", "任务C"),
        DAGNode("D", "任务D")
    ]

    edges = [
        DAGEdge("e1", "A", "B"),
        DAGEdge("e2", "C", "D")
    ]

    dag = TaskDAG("test_suggest", nodes, edges)

    pruner = DependencyPruner()
    suggestions = pruner.suggest_edges_to_add(dag)

    print(f"建议: {suggestions}")

    assert len(suggestions) > 0, "应该建议添加边来连接孤岛"
    print("✅ 测试10通过")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("开始测试DependencyPruner")
    print("=" * 60)

    try:
        test_find_redundant_edges()
        test_prune_no_redundancy()
        test_transitive_dependencies()
        test_optimize()
        test_validate_optimization()
        test_dependency_closure()
        test_no_redundancy_chain()
        test_parallel_with_redundancy()
        test_empty_dag()
        test_suggest_edges()

        print("\n" + "=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
