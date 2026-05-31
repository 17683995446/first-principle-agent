#!/usr/bin/env python3
"""
任务规划系统完整集成运行 - 第58阶段
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("🎯 任务规划系统 - 第58阶段：完整集成演示")
print("=" * 80)
print()

# 导入核心组件
try:
    from first_principle_agent.core.task_tuple import TaskTuple
    from first_principle_agent.core.dag_structures import TaskDAG, DAGNode, DAGEdge
    from first_principle_agent.core.task_orchestrator import TaskOrchestrator, OrchestrationPhase, OrchestrationStrategy
    
    print("✅ 核心组件导入成功！")
    print()
    
    # 演示 1：任务四元组
    print("📋 演示 1：任务四元组")
    task = TaskTuple(
        target="创建一个任务规划系统演示",
        condition=["Python环境", "项目依赖"],
        boundary={
            "include": ["核心组件", "集成示例"],
            "exclude": ["生产部署"],
            "constraints": {"时间": "1小时", "复杂度": "中等"}
        },
        end_rule={
            "success_criteria": ["所有组件测试通过", "集成成功"],
            "failure_criteria": ["导入失败", "测试不通过"],
            "timeout": 3600,
            "max_attempts": 3
        }
    )
    print(f"   目标: {task.target}")
    print(f"   条件: {task.condition}")
    print()
    
    # 演示 2：DAG 结构
    print("🌐 演示 2：任务 DAG 结构")
    node1 = DAGNode(node_id="setup", name="环境准备", node_type="setup")
    node2 = DAGNode(node_id="components", name="组件测试", node_type="task")
    node3 = DAGNode(node_id="integration", name="集成测试", node_type="integration")
    edge1 = DAGEdge(edge_id="e1", from_node="setup", to_node="components", edge_type="requires")
    edge2 = DAGEdge(edge_id="e2", from_node="components", to_node="integration", edge_type="requires")
    dag = TaskDAG(dag_id="demo_dag", nodes=[node1, node2, node3], edges=[edge1, edge2])
    print(f"   DAG ID: {dag.id}")
    print(f"   节点: {len(dag.nodes)} 个, 边: {len(dag.edges)} 个")
    print()
    
    # 演示 3：任务编排器
    print("🎼 演示 3：任务编排器 - 完整流程")
    orchestrator = TaskOrchestrator()
    requirement = "开发一个用户管理系统，包含创建、读取、更新和删除功能"
    
    print(f"   📝 用户需求: {requirement}")
    print(f"   🚀 开始编排...")
    result = orchestrator.orchestrate(requirement)
    
    print(f"   ✅ 编排状态: {result.status.value}")
    print(f"   📊 总任务数: {result.metrics.total_tasks}")
    print(f"   ✔️  成功: {result.metrics.completed_tasks}")
    print(f"   ❌ 失败: {result.metrics.failed_tasks}")
    print(f"   ⏱️  总耗时: {result.metrics.total_duration:.3f}秒")
    
    if hasattr(result, 'recommendations') and result.recommendations:
        print(f"   💡 建议:")
        for rec in result.recommendations:
            print(f"      - {rec}")
    print()
    
    # 演示 4：不同的编排策略
    print("🔄 演示 4：不同的编排策略")
    strategies = [
        OrchestrationStrategy.SEQUENTIAL,
        OrchestrationStrategy.PARALLEL,
        OrchestrationStrategy.WORKFLOW
    ]
    for strategy in strategies:
        print(f"   🎯 策略: {strategy.value}")
        result = orchestrator.orchestrate("测试不同策略", config=OrchestrationConfig(strategy=strategy))
        print(f"      结果: {result.status.value}")
    print()
    
    print("=" * 80)
    print("🎉 第58阶段：完整集成演示完成！")
    print("=" * 80)
    print()
    print("📊 项目进度: 58/100 阶段完成")
    print()
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print()
    print("请确保项目结构正确，所有核心组件已实现。")
except Exception as e:
    print(f"❌ 运行错误: {e}")
    import traceback
    print()
    print("详细错误信息:")
    traceback.print_exc()

# 定义 OrchestrationConfig （临时定义，避免导入问题）
from dataclasses import dataclass

@dataclass
class OrchestrationConfig:
    strategy: OrchestrationStrategy = OrchestrationStrategy.SEQUENTIAL
    max_retries: int = 3
    timeout_seconds: int = 3600
    callback_on_complete: callable = None
    callback_on_failure: callable = None
