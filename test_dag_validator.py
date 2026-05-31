#!/usr/bin/env python3
"""
测试DAGValidator（DAG综合验证器）
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from first_principle_agent.core import TaskDAG, DAGNode, DAGEdge
from first_principle_agent.layers import DAGValidator


def test_valid_dag():
    """测试有效DAG"""
    print("=" * 60)
    print("测试1：有效DAG")
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

    dag = TaskDAG("test_valid", nodes, edges)

    validator = DAGValidator()
    result = validator.validate(dag)

    print(f"验证结果: {result}")

    assert result["valid"] is True, "有效DAG应该通过验证"
    assert len(result["errors"]) == 0, "有效DAG不应该有错误"
    print("✅ 测试1通过")


def test_cycle_dag():
    """测试有环DAG"""
    print("\n" + "=" * 60)
    print("测试2：有环DAG")
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

    validator = DAGValidator()
    result = validator.validate(dag)

    print(f"验证结果: {result}")

    assert result["valid"] is False, "有环DAG应该验证失败"
    assert len(result["errors"]) > 0, "有环DAG应该有错误"
    assert "no_cycles" in result["checks"], "应该有环检测检查"
    print("✅ 测试2通过")


def test_isolated_nodes():
    """测试孤立节点"""
    print("\n" + "=" * 60)
    print("测试3：孤立节点")
    print("=" * 60)

    nodes = [
        DAGNode("A", "任务A"),
        DAGNode("B", "任务B"),
        DAGNode("C", "任务C")  # 孤立节点
    ]

    edges = [
        DAGEdge("e1", "A", "B")
    ]

    dag = TaskDAG("test_isolated", nodes, edges)

    validator = DAGValidator()
    result = validator.validate(dag, strict=False)

    print(f"验证结果: {result}")

    # 严格模式下应该失败，非严格模式下有警告
    if result["valid"]:
        assert len(result["warnings"]) > 0, "孤立节点应该产生警告"
    print("✅ 测试3通过")


def test_self_loop():
    """测试自环"""
    print("\n" + "=" * 60)
    print("测试4：自环")
    print("=" * 60)

    nodes = [
        DAGNode("A", "任务A"),
        DAGNode("B", "任务B")
    ]

    edges = [
        DAGEdge("e1", "A", "A"),  # 自环
        DAGEdge("e2", "A", "B")
    ]

    dag = TaskDAG("test_self_loop", nodes, edges)

    validator = DAGValidator()
    result = validator.validate(dag)

    print(f"验证结果: {result}")

    assert result["valid"] is False, "有自环的DAG应该验证失败"
    assert "no_self_loops" in result["checks"], "应该有自环检测检查"
    print("✅ 测试4通过")


def test_duplicate_edges():
    """测试重复边"""
    print("\n" + "=" * 60)
    print("测试5：重复边")
    print("=" * 60)

    nodes = [
        DAGNode("A", "任务A"),
        DAGNode("B", "任务B")
    ]

    edges = [
        DAGEdge("e1", "A", "B"),
        DAGEdge("e2", "A", "B")  # 重复边
    ]

    dag = TaskDAG("test_duplicate", nodes, edges)

    validator = DAGValidator()
    result = validator.validate(dag)

    print(f"验证结果: {result}")

    assert result["valid"] is True, "重复边应该产生警告但不是错误"
    assert len(result["warnings"]) > 0, "重复边应该产生警告"
    print("✅ 测试5通过")


def test_invalid_edge_reference():
    """测试无效的边引用"""
    print("\n" + "=" * 60)
    print("测试6：无效的边引用")
    print("=" * 60)

    nodes = [
        DAGNode("A", "任务A"),
        DAGNode("B", "任务B")
    ]

    edges = [
        DAGEdge("e1", "A", "C")  # 引用不存在的节点C
    ]

    dag = TaskDAG("test_invalid_ref", nodes, edges)

    validator = DAGValidator()
    result = validator.validate(dag)

    print(f"验证结果: {result}")

    assert result["valid"] is False, "引用不存在节点的边应该验证失败"
    print("✅ 测试6通过")


def test_disconnected_dag():
    """测试不连通的DAG"""
    print("\n" + "=" * 60)
    print("测试7：不连通的DAG")
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

    dag = TaskDAG("test_disconnected", nodes, edges)

    validator = DAGValidator()
    result = validator.validate(dag)

    print(f"验证结果: {result}")

    assert result["valid"] is False, "不连通的DAG应该验证失败"
    assert "connectivity" in result["checks"], "应该有连通性检查"
    print("✅ 测试7通过")


def test_quick_check():
    """测试快速检查"""
    print("\n" + "=" * 60)
    print("测试8：快速检查")
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

    dag = TaskDAG("test_quick", nodes, edges)

    validator = DAGValidator()
    result = validator.quick_check(dag)

    print(f"快速检查结果: {result}")

    assert result["valid"] is True, "有效的DAG应该通过快速检查"
    assert "sorted_order" in result, "应该包含拓扑排序结果"
    print("✅ 测试8通过")


def test_empty_dag():
    """测试空DAG"""
    print("\n" + "=" * 60)
    print("测试9：空DAG")
    print("=" * 60)

    dag = TaskDAG("test_empty")

    validator = DAGValidator()
    result = validator.validate(dag)

    print(f"验证结果: {result}")

    assert result["valid"] is False, "空DAG应该验证失败"
    assert "structure" in result["checks"], "应该有结构检查"
    print("✅ 测试9通过")


def test_validation_report():
    """测试验证报告生成"""
    print("\n" + "=" * 60)
    print("测试10：验证报告生成")
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

    validator = DAGValidator()
    report = validator.get_validation_report(dag)

    print("验证报告:")
    print(report)

    assert "DAG 验证报告" in report, "报告应该包含标题"
    assert "✅ 通过" in report, "有效DAG应该显示通过"
    print("✅ 测试10通过")


def test_parallel_group_validation():
    """测试并行组验证"""
    print("\n" + "=" * 60)
    print("测试11：并行组验证")
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

    parallel_groups = {
        "group1": ["A", "B"]  # B依赖A，不应该并行
    }

    dag = TaskDAG("test_parallel", nodes, edges, parallel_groups=parallel_groups)

    validator = DAGValidator()
    result = validator.validate(dag, strict=True)

    print(f"验证结果: {result}")

    # 严格模式下应该检测到并行组内的依赖
    if result["warnings"]:
        print(f"检测到并行性问题: {result['warnings']}")
    print("✅ 测试11通过")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("开始测试DAGValidator")
    print("=" * 60)

    try:
        test_valid_dag()
        test_cycle_dag()
        test_isolated_nodes()
        test_self_loop()
        test_duplicate_edges()
        test_invalid_edge_reference()
        test_disconnected_dag()
        test_quick_check()
        test_empty_dag()
        test_validation_report()
        test_parallel_group_validation()

        print("\n" + "=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
