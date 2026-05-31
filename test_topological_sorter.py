#!/usr/bin/env python3
"""
测试TopologicalSorter（拓扑排序器）
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from first_principle_agent.core import TaskDAG, DAGNode, DAGEdge
from first_principle_agent.layers import TopologicalSorter


def test_simple_topological_sort():
    """测试简单拓扑排序"""
    print("=" * 60)
    print("测试1：简单拓扑排序")
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

    dag = TaskDAG("test_simple", nodes, edges)

    sorter = TopologicalSorter()
    result = sorter.sort(dag)
    print(f"排序结果: {result}")

    validation = sorter.validate_topological_order(dag, result["sorted_order"])
    print(f"验证结果: {validation}")

    assert result["success"] == True, "简单DAG应该能成功排序"
    assert validation["valid"] == True, "排序应该有效"
    print("✅ 测试1通过")


def test_chain_topological_sort():
    """测试链式拓扑排序"""
    print("\n" + "=" * 60)
    print("测试2：链式拓扑排序")
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

    sorter = TopologicalSorter()
    result = sorter.sort(dag)
    print(f"排序结果: {result}")

    assert result["success"] == True, "链式DAG应该能成功排序"
    expected_order = ["1", "2", "3", "4", "5"]
    assert result["sorted_order"] == expected_order, f"链式排序应该按顺序，结果: {result['sorted_order']}"
    print("✅ 测试2通过")


def test_parallel_topological_sort():
    """测试并行拓扑排序"""
    print("\n" + "=" * 60)
    print("测试3：并行拓扑排序")
    print("=" * 60)

    nodes = [
        DAGNode("A", "任务A"),
        DAGNode("B", "任务B"),
        DAGNode("C", "任务C"),
        DAGNode("D", "任务D"),
        DAGNode("E", "任务E"),
        DAGNode("F", "任务F")
    ]

    edges = [
        DAGEdge("e1", "A", "B"),
        DAGEdge("e2", "A", "C"),
        DAGEdge("e3", "B", "D"),
        DAGEdge("e4", "C", "D"),
        DAGEdge("e5", "D", "E"),
        DAGEdge("e6", "D", "F")
    ]

    dag = TaskDAG("test_parallel", nodes, edges)

    sorter = TopologicalSorter()
    result = sorter.sort(dag)
    print(f"排序结果: {result}")

    levels = sorter.get_levels(dag)
    print(f"节点层级: {levels}")

    groups = sorter.get_parallel_groups(dag)
    print(f"并行分组: {groups}")

    assert result["success"] == True, "并行DAG应该能成功排序"
    assert len(groups) == 4, "应该有4个层级"
    assert groups[0] == ["A"], "第0层只有A"
    assert set(groups[1]) == {"B", "C"}, "第1层是B和C"
    assert groups[2] == ["D"], "第2层是D"
    assert set(groups[3]) == {"E", "F"}, "第3层是E和F"
    print("✅ 测试3通过")


def test_cycle_detection():
    """测试有环DAG的拓扑排序失败"""
    print("\n" + "=" * 60)
    print("测试4：有环DAG的拓扑排序")
    print("=" * 60)

    nodes = [
        DAGNode("A", "任务A"),
        DAGNode("B", "任务B"),
        DAGNode("C", "任务C")
    ]

    edges = [
        DAGEdge("e1", "A", "B"),
        DAGEdge("e2", "B", "C"),
        DAGEdge("e3", "C", "A")
    ]

    dag = TaskDAG("test_cycle", nodes, edges)

    sorter = TopologicalSorter()
    result = sorter.sort(dag)
    print(f"排序结果: {result}")

    assert result["success"] == False, "有环DAG应该排序失败"
    assert len(result["cycles"]) > 0, "应该检测到环"
    print("✅ 测试4通过")


def test_validate_order():
    """测试拓扑排序验证"""
    print("\n" + "=" * 60)
    print("测试5：拓扑排序验证")
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

    dag = TaskDAG("test_validate", nodes, edges)

    sorter = TopologicalSorter()

    valid_order = ["A", "B", "C"]
    valid_result = sorter.validate_topological_order(dag, valid_order)
    print(f"有效顺序验证: {valid_result}")

    invalid_order = ["B", "A", "C"]
    invalid_result = sorter.validate_topological_order(dag, invalid_order)
    print(f"无效顺序验证: {invalid_result}")

    assert valid_result["valid"] == True, "正确顺序应该通过验证"
    assert invalid_result["valid"] == False, "错误顺序应该失败"
    print("✅ 测试5通过")


def test_get_levels():
    """测试获取节点层级"""
    print("\n" + "=" * 60)
    print("测试6：获取节点层级")
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

    dag = TaskDAG("test_levels", nodes, edges)

    sorter = TopologicalSorter()
    levels = sorter.get_levels(dag)
    print(f"节点层级: {levels}")

    assert levels["A"] == 0, "A应该在第0层"
    assert levels["B"] == 1, "B应该在第1层"
    assert levels["C"] == 1, "C应该在第1层"
    assert levels["D"] == 2, "D应该在第2层"
    print("✅ 测试6通过")


def test_execution_order():
    """测试执行顺序获取"""
    print("\n" + "=" * 60)
    print("测试7：执行顺序获取")
    print("=" * 60)

    nodes = [
        DAGNode("A", "任务A"),
        DAGNode("B", "任务B"),
        DAGNode("C", "任务C"),
        DAGNode("D", "任务D")
    ]

    edges = [
        DAGEdge("e1", "A", "B"),
        DAGEdge("e2", "B", "D"),
        DAGEdge("e3", "A", "C"),
        DAGEdge("e4", "C", "D")
    ]

    dag = TaskDAG("test_execution", nodes, edges)

    sorter = TopologicalSorter()
    result = sorter.get_execution_order(dag)
    print(f"执行顺序: {result}")

    assert result["success"] == True, "应该能获取执行顺序"
    assert result["execution_order"][0] == "A", "A应该是第一个执行的"
    print("✅ 测试7通过")


def test_empty_dag():
    """测试空DAG"""
    print("\n" + "=" * 60)
    print("测试8：空DAG")
    print("=" * 60)

    dag = TaskDAG("test_empty")

    sorter = TopologicalSorter()
    result = sorter.sort(dag)
    print(f"排序结果: {result}")

    assert result["success"] == True, "空DAG应该能成功排序"
    assert result["sorted_order"] == [], "空DAG排序结果应该为空"
    print("✅ 测试8通过")


def test_single_node():
    """测试单个节点"""
    print("\n" + "=" * 60)
    print("测试9：单个节点")
    print("=" * 60)

    nodes = [DAGNode("A", "任务A")]
    dag = TaskDAG("test_single", nodes)

    sorter = TopologicalSorter()
    result = sorter.sort(dag)
    print(f"排序结果: {result}")

    assert result["success"] == True, "单个节点应该能成功排序"
    assert result["sorted_order"] == ["A"], "排序结果应该是['A']"
    print("✅ 测试9通过")


def test_complex_dag():
    """测试复杂DAG"""
    print("\n" + "=" * 60)
    print("测试10：复杂DAG")
    print("=" * 60)

    nodes = [
        DAGNode("1", "任务1"),
        DAGNode("2", "任务2"),
        DAGNode("3", "任务3"),
        DAGNode("4", "任务4"),
        DAGNode("5", "任务5"),
        DAGNode("6", "任务6"),
        DAGNode("7", "任务7")
    ]

    edges = [
        DAGEdge("e1", "1", "2"),
        DAGEdge("e2", "1", "3"),
        DAGEdge("e3", "2", "4"),
        DAGEdge("e4", "3", "4"),
        DAGEdge("e5", "4", "5"),
        DAGEdge("e6", "4", "6"),
        DAGEdge("e7", "5", "7"),
        DAGEdge("e8", "6", "7")
    ]

    dag = TaskDAG("test_complex", nodes, edges)

    sorter = TopologicalSorter()
    result = sorter.sort(dag)
    print(f"排序结果: {result}")

    groups = sorter.get_parallel_groups(dag)
    print(f"并行分组: {groups}")

    validation = sorter.validate_topological_order(dag, result["sorted_order"])
    print(f"验证结果: {validation}")

    assert result["success"] == True, "复杂DAG应该能成功排序"
    assert validation["valid"] == True, "排序应该有效"
    print("✅ 测试10通过")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("开始测试TopologicalSorter")
    print("=" * 60)

    try:
        test_simple_topological_sort()
        test_chain_topological_sort()
        test_parallel_topological_sort()
        test_cycle_detection()
        test_validate_order()
        test_get_levels()
        test_execution_order()
        test_empty_dag()
        test_single_node()
        test_complex_dag()

        print("\n" + "=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
