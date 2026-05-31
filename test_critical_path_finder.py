#!/usr/bin/env python3
"""
测试CriticalPathFinder关键路径识别器
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from first_principle_agent.core import TaskDAG, DAGNode, DAGEdge
from first_principle_agent.layers import CriticalPathFinder


def test_simple_critical_path():
    """测试简单DAG的关键路径"""
    print("=" * 60)
    print("测试1：简单DAG关键路径")
    print("=" * 60)

    nodes = [
        DAGNode("A", "任务A"),
        DAGNode("B", "任务B"),
        DAGNode("C", "任务C"),
        DAGNode("D", "任务D")
    ]

    edges = [
        DAGEdge("e1", "A", "B", "requires", 1.0),
        DAGEdge("e2", "A", "C", "requires", 0.5),
        DAGEdge("e3", "B", "D", "requires", 1.0),
        DAGEdge("e4", "C", "D", "requires", 1.0)
    ]

    dag = TaskDAG("test_simple_critical", nodes, edges)

    finder = CriticalPathFinder()
    result = finder.find_critical_path(dag)
    print(f"关键路径识别结果: {result}")

    assert result["success"] is True, "关键路径识别应该成功"
    assert result["critical_path"] == ["A", "B", "D"], f"关键路径应该是A-B-D，但得到的是 {result['critical_path']}"
    assert abs(result["critical_path_length"] - 2.0) < 0.001, f"关键路径长度应该是2.0，但得到的是 {result['critical_path_length']}"
    print("✅ 测试1通过")


def test_chain_critical_path():
    """测试链式DAG的关键路径"""
    print("\n" + "=" * 60)
    print("测试2：链式DAG关键路径")
    print("=" * 60)

    nodes = [
        DAGNode("1", "任务1"),
        DAGNode("2", "任务2"),
        DAGNode("3", "任务3"),
        DAGNode("4", "任务4"),
        DAGNode("5", "任务5")
    ]

    edges = [
        DAGEdge("e1", "1", "2", "requires", 1.0),
        DAGEdge("e2", "2", "3", "requires", 1.0),
        DAGEdge("e3", "3", "4", "requires", 1.0),
        DAGEdge("e4", "4", "5", "requires", 1.0)
    ]

    dag = TaskDAG("test_chain_critical", nodes, edges)

    finder = CriticalPathFinder()
    result = finder.find_critical_path(dag)
    print(f"关键路径识别结果: {result}")

    assert result["success"] is True, "关键路径识别应该成功"
    assert result["critical_path"] == ["1", "2", "3", "4", "5"], f"关键路径应该是1-2-3-4-5"
    assert abs(result["critical_path_length"] - 4.0) < 0.001
    print("✅ 测试2通过")


def test_parallel_critical_path():
    """测试并行DAG的关键路径"""
    print("\n" + "=" * 60)
    print("测试3：并行DAG关键路径")
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
        DAGEdge("e1", "A", "B", "requires", 1.0),
        DAGEdge("e2", "A", "C", "requires", 1.0),
        DAGEdge("e3", "B", "D", "requires", 1.0),
        DAGEdge("e4", "C", "D", "requires", 1.0),
        DAGEdge("e5", "D", "E", "requires", 1.0),
        DAGEdge("e6", "D", "F", "requires", 1.5)  # F路径更长
    ]

    dag = TaskDAG("test_parallel_critical", nodes, edges)

    finder = CriticalPathFinder()
    result = finder.find_critical_path(dag)
    print(f"关键路径识别结果: {result}")

    assert result["success"] is True, "关键路径识别应该成功"
    assert result["critical_path"] in [["A", "B", "D", "F"], ["A", "C", "D", "F"]], f"关键路径应该是A-B-D-F或A-C-D-F"
    print("✅ 测试3通过")


def test_all_critical_paths():
    """测试多条关键路径识别"""
    print("\n" + "=" * 60)
    print("测试4：多条关键路径识别")
    print("=" * 60)

    nodes = [
        DAGNode("A", "任务A"),
        DAGNode("B", "任务B"),
        DAGNode("C", "任务C"),
        DAGNode("D", "任务D")
    ]

    edges = [
        DAGEdge("e1", "A", "B", "requires", 1.0),
        DAGEdge("e2", "A", "C", "requires", 1.0),
        DAGEdge("e3", "B", "D", "requires", 1.0),
        DAGEdge("e4", "C", "D", "requires", 1.0)
    ]

    dag = TaskDAG("test_multi_critical", nodes, edges)

    finder = CriticalPathFinder()
    result = finder.find_all_critical_paths(dag)
    print(f"所有关键路径: {result}")

    assert result["success"] is True, "关键路径识别应该成功"
    assert result["critical_path_count"] == 2, f"应该有2条关键路径，但得到 {result['critical_path_count']}"
    print("✅ 测试4通过")


def test_critical_path_details():
    """测试关键路径详细信息"""
    print("\n" + "=" * 60)
    print("测试5：关键路径详细信息")
    print("=" * 60)

    nodes = [
        DAGNode("A", "任务A"),
        DAGNode("B", "任务B"),
        DAGNode("C", "任务C")
    ]

    edges = [
        DAGEdge("e1", "A", "B", "requires", 2.0),
        DAGEdge("e2", "B", "C", "requires", 3.0)
    ]

    dag = TaskDAG("test_details", nodes, edges)

    finder = CriticalPathFinder()
    details = finder.get_critical_path_details(dag)
    print(f"关键路径详细信息: {details}")

    assert details["nodes"] is not None, "应该有节点信息"
    assert details["edges"] is not None, "应该有边信息"
    assert len(details["nodes"]) == 3, "应该有3个节点"
    assert len(details["edges"]) == 2, "应该有2条边"
    assert abs(details["total_weight"] - 5.0) < 0.001
    print("✅ 测试5通过")


def test_critical_tasks():
    """测试关键任务识别"""
    print("\n" + "=" * 60)
    print("测试6：关键任务识别")
    print("=" * 60)

    nodes = [
        DAGNode("A", "任务A"),
        DAGNode("B", "任务B"),
        DAGNode("C", "任务C"),
        DAGNode("D", "任务D"),
        DAGNode("E", "任务E")
    ]

    edges = [
        DAGEdge("e1", "A", "B", "requires", 1.0),
        DAGEdge("e2", "A", "C", "requires", 0.5),
        DAGEdge("e3", "B", "D", "requires", 1.0),
        DAGEdge("e4", "C", "D", "requires", 1.0),
        DAGEdge("e5", "D", "E", "requires", 1.0)
    ]

    dag = TaskDAG("test_critical_tasks", nodes, edges)

    finder = CriticalPathFinder()
    result = finder.identify_critical_tasks(dag)
    print(f"关键任务: {result}")

    assert result["success"] is True, "关键任务识别应该成功"
    assert "A" in result["critical_nodes"], "A应该是关键任务"
    assert "B" in result["critical_nodes"], "B应该是关键任务"
    assert "D" in result["critical_nodes"], "D应该是关键任务"
    assert "E" in result["critical_nodes"], "E应该是关键任务"
    print("✅ 测试6通过")


def test_cycle_detection():
    """测试有环DAG的错误处理"""
    print("\n" + "=" * 60)
    print("测试7：有环DAG的错误处理")
    print("=" * 60)

    nodes = [
        DAGNode("A", "任务A"),
        DAGNode("B", "任务B"),
        DAGNode("C", "任务C")
    ]

    edges = [
        DAGEdge("e1", "A", "B", "requires", 1.0),
        DAGEdge("e2", "B", "C", "requires", 1.0),
        DAGEdge("e3", "C", "A", "requires", 1.0)
    ]

    dag = TaskDAG("test_cycle", nodes, edges)

    finder = CriticalPathFinder()
    result = finder.find_critical_path(dag)
    print(f"有环DAG的结果: {result}")

    assert result["success"] is False, "有环DAG应该返回失败"
    print("✅ 测试7通过")


def test_empty_dag():
    """测试空DAG"""
    print("\n" + "=" * 60)
    print("测试8：空DAG")
    print("=" * 60)

    dag = TaskDAG("test_empty")

    finder = CriticalPathFinder()
    result = finder.find_critical_path(dag)
    print(f"空DAG的结果: {result}")

    assert result["success"] is True, "空DAG应该成功"
    assert len(result["critical_path"]) == 0, "空DAG的关键路径应该是空"
    print("✅ 测试8通过")


def test_single_node():
    """测试单个节点DAG"""
    print("\n" + "=" * 60)
    print("测试9：单个节点DAG")
    print("=" * 60)

    nodes = [DAGNode("A", "任务A")]
    dag = TaskDAG("test_single", nodes)

    finder = CriticalPathFinder()
    result = finder.find_critical_path(dag)
    print(f"单个节点的结果: {result}")

    assert result["success"] is True, "单个节点DAG应该成功"
    assert result["critical_path"] == ["A"], "关键路径应该是[A]"
    print("✅ 测试9通过")


def test_calculate_slack():
    """测试松弛时间计算"""
    print("\n" + "=" * 60)
    print("测试10：松弛时间计算")
    print("=" * 60)

    nodes = [
        DAGNode("A", "任务A"),
        DAGNode("B", "任务B"),
        DAGNode("C", "任务C"),
        DAGNode("D", "任务D")
    ]

    edges = [
        DAGEdge("e1", "A", "B", "requires", 1.0),
        DAGEdge("e2", "A", "C", "requires", 0.5),
        DAGEdge("e3", "B", "D", "requires", 1.0),
        DAGEdge("e4", "C", "D", "requires", 1.0)
    ]

    dag = TaskDAG("test_slack", nodes, edges)

    finder = CriticalPathFinder()
    result = finder.calculate_slack(dag)
    print(f"松弛时间计算结果: {result}")

    assert result["success"] is True, "松弛时间计算应该成功"
    assert "slack" in result, "应该有slack信息"
    print("✅ 测试10通过")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("开始测试CriticalPathFinder")
    print("=" * 60)

    try:
        test_simple_critical_path()
        test_chain_critical_path()
        test_parallel_critical_path()
        test_all_critical_paths()
        test_critical_path_details()
        test_critical_tasks()
        test_cycle_detection()
        test_empty_dag()
        test_single_node()
        test_calculate_slack()

        print("\n" + "=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
