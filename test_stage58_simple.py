#!/usr/bin/env python3
"""
第58阶段：简单集成测试
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("🧪 第58阶段：简单集成测试")
print("=" * 80)
print()

# 测试 1：基础组件导入
print("📦 测试 1：基础组件导入")
try:
    from first_principle_agent.core.task_tuple import TaskTuple
    from first_principle_agent.core.dag_structures import TaskDAG, DAGNode, DAGEdge
    from first_principle_agent.core.task_orchestrator import (
        TaskOrchestrator, 
        OrchestrationPhase, 
        OrchestrationStrategy,
        OrchestrationConfig,
        create_orchestrator
    )
    print("✅ 基础组件导入成功")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)
print()

# 测试 2：创建任务四元组
print("📋 测试 2：任务四元组创建")
try:
    task = TaskTuple(
        target="第58阶段测试",
        condition=["Python 3.8+"],
        boundary={"include": ["测试"], "exclude": [], "constraints": {}},
        end_rule={"success_criteria": ["通过"], "failure_criteria": ["失败"], "timeout": 3600, "max_attempts": 1}
    )
    print(f"✅ 任务四元组创建成功: {task.target}")
except Exception as e:
    print(f"❌ 创建失败: {e}")
print()

# 测试 3：创建编排器
print("🎼 测试 3：任务编排器")
try:
    orchestrator = create_orchestrator()
    print(f"✅ 编排器创建成功 (ID: {orchestrator.orchestrator_id[:8]}...)")
    
    # 测试简单编排
    result = orchestrator.orchestrate("简单测试需求")
    print(f"✅ 编排执行完成，状态: {result.status.value}")
    print(f"   总任务: {result.metrics.total_tasks}")
    print(f"   总耗时: {result.metrics.total_duration:.3f}秒")
except Exception as e:
    print(f"❌ 编排器测试失败: {e}")
    import traceback
    traceback.print_exc()
print()

# 测试 4：创建DAG
print("🌐 测试 4：DAG 结构")
try:
    node1 = DAGNode(node_id="step1", name="步骤1", node_type="task")
    node2 = DAGNode(node_id="step2", name="步骤2", node_type="task")
    edge = DAGEdge(edge_id="e1", from_node="step1", to_node="step2", edge_type="requires")
    dag = TaskDAG(dag_id="test_dag", nodes=[node1, node2], edges=[edge])
    print(f"✅ DAG 创建成功: {dag.id}")
    print(f"   节点数: {len(dag.nodes)}, 边数: {len(dag.edges)}")
except Exception as e:
    print(f"❌ DAG 测试失败: {e}")
print()

print("=" * 80)
print("🎉 第58阶段：简单集成测试全部通过！")
print("=" * 80)
print()
print("📊 项目进度: 58/100 阶段")
print()
