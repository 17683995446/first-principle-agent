#!/usr/bin/env python3
"""
测试CycleDetector（环检测器）
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from first_principle_agent.core import TaskDAG, DAGNode, DAGEdge
from first_principle_agent.layers import CycleDetector


def test_no_cycle():
    """测试无环DAG"""
    print("=" * 60)
    print("测试1：无环DAG")
    print("=" * 60)

    nodes = [
        DAGNode("1", "任务1"),
        DAGNode("2", "任务2"),
        DAGNode("3", "任务3"),
        DAGNode("4", "任务4")
    ]

    edges = [
        DAGEdge("e1", "1", "2"),
        DAGEdge("e2", "1", "3"),
        DAGEdge("e3", "2", "4"),
        DAGEdge("e4", "3", "4")
    ]

    dag = TaskDAG("test_no_cycle", nodes, edges)

    detector = CycleDetector()
    result = detector.detect_cycles(dag)
    print(f"检测结果: {result}")

    validation = detector.validate_dag(dag)
    print(f"验证结果: {validation}")

    assert result["has_cycle"] == False, "无环DAG应该没有检测到环"
    assert validation["is_dag"] == True, "无环DAG应该被验证为有效DAG"
    print("✅ 测试1通过")


def test_simple_cycle():
    """测试简单环"""
    print("\n" + "=" * 60)
    print("测试2：简单环（A→B→A）")
    print("=" * 60)

    nodes = [
        DAGNode("A", "任务A"),
        DAGNode("B", "任务B")
    ]

    edges = [
        DAGEdge("e1", "A", "B"),
        DAGEdge("e2", "B", "A")
    ]

    dag = TaskDAG("test_simple_cycle", nodes, edges)

    detector = CycleDetector()
    result = detector.detect_cycles(dag)
    print(f"检测结果: {result}")

    details = detector.get_cycle_details(dag)
    print(f"环详细信息: {details}")

    validation = detector.validate_dag(dag)
    print(f"验证结果: {validation}")

    assert result["has_cycle"] == True, "应该检测到环"
    assert len(result["cycles"]) >= 1, "应该找到至少一个环"
    assert validation["is_dag"] == False, "有环的图不应该被验证为有效DAG"
    print("✅ 测试2通过")


def test_triangle_cycle():
    """测试三角形环（A→B→C→A）"""
    print("\n" + "=" * 60)
    print("测试3：三角形环（A→B→C→A）")
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

    dag = TaskDAG("test_triangle_cycle", nodes, edges)

    detector = CycleDetector()
    result = detector.detect_cycles(dag)
    print(f"检测结果: {result}")

    details = detector.get_cycle_details(dag)
    print(f"环详细信息: {details}")

    assert result["has_cycle"] == True, "应该检测到环"
    print("✅ 测试3通过")


def test_multiple_cycles():
    """测试多个环"""
    print("\n" + "=" * 60)
    print("测试4：多个环")
    print("=" * 60)

    nodes = [
        DAGNode("1", "任务1"),
        DAGNode("2", "任务2"),
        DAGNode("3", "任务3"),
        DAGNode("4", "任务4")
    ]

    edges = [
        DAGEdge("e1", "1", "2"),
        DAGEdge("e2", "2", "1"),  # 第一个环
        DAGEdge("e3", "3", "4"),
        DAGEdge("e4", "4", "3")   # 第二个环
    ]

    dag = TaskDAG("test_multiple_cycles", nodes, edges)

    detector = CycleDetector()
    result = detector.detect_cycles(dag)
    print(f"检测结果: {result}")

    assert result["has_cycle"] == True, "应该检测到环"
    assert result["cycle_count"] >= 2, "应该找到至少两个环"
    print("✅ 测试4通过")


def test_empty_dag():
    """测试空DAG"""
    print("\n" + "=" * 60)
    print("测试5：空DAG")
    print("=" * 60)

    dag = TaskDAG("test_empty")

    detector = CycleDetector()
    result = detector.detect_cycles(dag)
    print(f"检测结果: {result}")

    assert result["has_cycle"] == False, "空DAG应该没有环"
    print("✅ 测试5通过")


def test_single_node():
    """测试单个节点（无环）"""
    print("\n" + "=" * 60)
    print("测试6：单个节点（无环）")
    print("=" * 60)

    nodes = [DAGNode("1", "任务1")]
    dag = TaskDAG("test_single_node", nodes)

    detector = CycleDetector()
    result = detector.detect_cycles(dag)
    print(f"检测结果: {result}")

    assert result["has_cycle"] == False, "单个节点应该没有环"
    print("✅ 测试6通过")


def test_self_cycle():
    """测试自环（A→A）"""
    print("\n" + "=" * 60)
    print("测试7：自环（A→A）")
    print("=" * 60)

    nodes = [DAGNode("A", "任务A")]
    edges = [DAGEdge("e1", "A", "A")]

    dag = TaskDAG("test_self_cycle", nodes, edges)

    detector = CycleDetector()
    result = detector.detect_cycles(dag)
    print(f"检测结果: {result}")

    details = detector.get_cycle_details(dag)
    print(f"环详细信息: {details}")

    assert result["has_cycle"] == True, "自环应该被检测到"
    print("✅ 测试7通过")


def test_break_cycles():
    """测试破环建议功能"""
    print("\n" + "=" * 60)
    print("测试8：破环建议功能")
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

    dag = TaskDAG("test_break_cycles", nodes, edges)

    detector = CycleDetector()
    suggestions = detector.break_cycles(dag)
    print(f"破环建议: {suggestions}")

    assert len(suggestions["suggestions"]) > 0, "应该提供破环建议"
    print("✅ 测试8通过")


def test_has_cycle_shortcut():
    """测试has_cycle快捷方法"""
    print("\n" + "=" * 60)
    print("测试9：has_cycle快捷方法")
    print("=" * 60)

    nodes1 = [DAGNode("A", "任务A"), DAGNode("B", "任务B")]
    edges1 = [DAGEdge("e1", "A", "B")]
    dag1 = TaskDAG("test_shortcut1", nodes1, edges1)

    nodes2 = [DAGNode("A", "任务A"), DAGNode("B", "任务B")]
    edges2 = [DAGEdge("e1", "A", "B"), DAGEdge("e2", "B", "A")]
    dag2 = TaskDAG("test_shortcut2", nodes2, edges2)

    detector = CycleDetector()
    result1 = detector.has_cycle(dag1)
    result2 = detector.has_cycle(dag2)

    print(f"无环DAG结果: {result1}")
    print(f"有环DAG结果: {result2}")

    assert result1 == False, "无环DAG应该返回False"
    assert result2 == True, "有环DAG应该返回True"
    print("✅ 测试9通过")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("开始测试CycleDetector")
    print("=" * 60)

    try:
        test_no_cycle()
        test_simple_cycle()
        test_triangle_cycle()
        test_multiple_cycles()
        test_empty_dag()
        test_single_node()
        test_self_cycle()
        test_break_cycles()
        test_has_cycle_shortcut()

        print("\n" + "=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
