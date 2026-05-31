#!/usr/bin/env python3
"""
任务规划系统完整集成示例 - 第58阶段
展示所有核心组件如何协同工作
"""

import sys
import os
import time
from typing import Dict, Any, List

# 添加根目录到路径以导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from first_principle_agent.core.task_tuple import TaskTuple
from first_principle_agent.core.dag_structures import TaskDAG, DAGNode, DAGEdge
from first_principle_agent.core.task_execution_engine import TaskExecutionEngine
from first_principle_agent.core.task_pipeline import TaskPipeline
from first_principle_agent.core.task_scheduler import TaskScheduler, TaskPriority, SchedulerStrategy
from first_principle_agent.core.task_analytics import TaskAnalytics, TaskReportGenerator, AnalysisType, ReportFormat
from first_principle_agent.core.task_workflow_executor import TaskWorkflowExecutor, WorkflowStepType, WorkflowStatus
from first_principle_agent.core.task_orchestrator import TaskOrchestrator, OrchestrationStrategy, OrchestrationPhase


class SystemIntegrationExample:
    """任务规划系统完整集成示例"""
    
    def __init__(self):
        print("=" * 80)
        print("🎯 任务规划系统 - 完整集成示例")
        print("=" * 80)
        print()
    
    def example_1_task_tuple(self):
        """示例1：任务四元组 - 归一建模层"""
        print("\n" + "=" * 80)
        print("📋 示例1：任务四元组 - 归一建模层")
        print("=" * 80)
        
        # 创建任务四元组
        task = TaskTuple(
            target="创建一个简单的Web应用",
            condition=["已安装Python", "已安装pip"],
            boundary={
                "include": ["前端页面", "后端API", "数据库"],
                "exclude": ["复杂的认证系统", "大规模用户"],
                "constraints": {"开发时间": "1周", "技术栈": "Python+Flask"}
            },
            end_rule={
                "success_criteria": ["应用可以正常运行", "所有功能测试通过"],
                "failure_criteria": ["代码无法编译", "超过开发时间"],
                "timeout": 604800,  # 1周（秒）
                "max_attempts": 3
            }
        )
        
        print(f"✅ 任务目标: {task.target}")
        print(f"✅ 前置条件: {task.condition}")
        print(f"✅ 边界约束: {task.boundary}")
        print(f"✅ 终止规则: {task.end_rule}")
        
        return task
    
    def example_2_task_dag(self):
        """示例2：任务DAG - 拓扑依赖拆解层"""
        print("\n" + "=" * 80)
        print("🌐 示例2：任务DAG - 拓扑依赖拆解层")
        print("=" * 80)
        
        # 创建DAG节点
        node1 = DAGNode(
            node_id="setup_env",
            name="设置开发环境",
            node_type="task"
        )
        
        node2 = DAGNode(
            node_id="create_db",
            name="创建数据库",
            node_type="task"
        )
        
        node3 = DAGNode(
            node_id="develop_api",
            name="开发后端API",
            node_type="task"
        )
        
        node4 = DAGNode(
            node_id="develop_ui",
            name="开发前端界面",
            node_type="task"
        )
        
        node5 = DAGNode(
            node_id="test_app",
            name="测试应用",
            node_type="task"
        )
        
        # 创建依赖边
        edge1 = DAGEdge(
            edge_id="edge1",
            from_node="setup_env",
            to_node="create_db",
            edge_type="requires"
        )
        
        edge2 = DAGEdge(
            edge_id="edge2",
            from_node="create_db",
            to_node="develop_api",
            edge_type="requires"
        )
        
        edge3 = DAGEdge(
            edge_id="edge3",
            from_node="setup_env",
            to_node="develop_ui",
            edge_type="requires"
        )
        
        edge4 = DAGEdge(
            edge_id="edge4",
            from_node="develop_api",
            to_node="test_app",
            edge_type="requires"
        )
        
        edge5 = DAGEdge(
            edge_id="edge5",
            from_node="develop_ui",
            to_node="test_app",
            edge_type="requires"
        )
        
        # 创建DAG
        dag = TaskDAG(
            dag_id="web_app_dev",
            nodes=[node1, node2, node3, node4, node5],
            edges=[edge1, edge2, edge3, edge4, edge5]
        )
        
        print(f"✅ DAG ID: {dag.id}")
        print(f"✅ 节点数量: {len(dag.nodes)}")
        for node in dag.nodes:
            print(f"   - {node.id}: {node.name}")
        print(f"✅ 边数量: {len(dag.edges)}")
        
        return dag
    
    def example_3_task_execution_engine(self):
        """示例3：任务执行引擎 - 核心执行层"""
        print("\n" + "=" * 80)
        print("⚙️ 示例3：任务执行引擎 - 核心执行层")
        print("=" * 80)
        
        # 创建执行引擎
        engine = TaskExecutionEngine()
        
        # 定义示例任务
        def task1():
            time.sleep(0.1)
            return "✅ 任务1完成"
        
        def task2():
            time.sleep(0.1)
            return "✅ 任务2完成"
        
        def task3():
            time.sleep(0.1)
            return "✅ 任务3完成"
        
        # 顺序执行
        print("📌 顺序执行模式:")
        results = engine.execute_sequential([task1, task2, task3])
        for result in results:
            print(f"   {result}")
        
        return engine
    
    def example_4_task_pipeline(self):
        """示例4：任务管道 - 数据处理流"""
        print("\n" + "=" * 80)
        print("🔗 示例4：任务管道 - 数据处理流")
        print("=" * 80)
        
        # 创建管道
        pipeline = TaskPipeline(name="数据处理管道")
        
        # 添加阶段
        def stage1(data):
            return data.upper()
        
        def stage2(data):
            return data.replace(" ", "_")
        
        def stage3(data):
            return f"PROCESSED_{data}"
        
        pipeline.add_task_stage("转换大写", stage1)
        pipeline.add_task_stage("替换空格", stage2)
        pipeline.add_task_stage("添加前缀", stage3)
        
        # 执行管道
        input_data = "hello world"
        print(f"📌 输入数据: {input_data}")
        
        result = pipeline.execute(input_data)
        print(f"✅ 最终结果: {result}")
        
        return pipeline
    
    def example_5_task_scheduler(self):
        """示例5：任务调度器 - 优先级与队列管理"""
        print("\n" + "=" * 80)
        print("📅 示例5：任务调度器 - 优先级与队列管理")
        print("=" * 80)
        
        # 创建调度器
        scheduler = TaskScheduler()
        scheduler.start()
        
        # 定义任务
        task_count = [0]
        
        def create_task(name):
            def task():
                task_count[0] += 1
                time.sleep(0.05)
                return f"{name}完成"
            return task
        
        # 提交不同优先级的任务
        print("📌 提交任务（不同优先级）:")
        scheduler.submit(create_task("低优先级任务1"), priority=TaskPriority.LOW)
        scheduler.submit(create_task("高优先级任务"), priority=TaskPriority.HIGH)
        scheduler.submit(create_task("普通任务1"), priority=TaskPriority.NORMAL)
        scheduler.submit(create_task("低优先级任务2"), priority=TaskPriority.LOW)
        
        # 等待完成
        scheduler.wait_for_completion(timeout=2)
        scheduler.stop()
        
        print(f"✅ 完成任务数: {task_count[0]}")
        
        return scheduler
    
    def example_6_task_analytics(self):
        """示例6：任务分析引擎 - 指标与报告"""
        print("\n" + "=" * 80)
        print("📊 示例6：任务分析引擎 - 指标与报告")
        print("=" * 80)
        
        # 创建分析引擎
        analytics = TaskAnalytics()
        
        # 添加一些模拟数据
        analytics.analyze_success_rate(
            total_tasks=100,
            successful_tasks=95,
            failed_tasks=5
        )
        
        analytics.analyze_execution_time([0.5, 0.8, 0.3, 0.6, 0.9, 0.4, 0.7, 0.5, 0.6, 0.8])
        
        # 生成报告
        generator = TaskReportGenerator(analytics)
        report = generator.generate_summary_report()
        
        print("📌 分析报告:")
        print(report.to_text())
        
        return analytics
    
    def example_7_task_workflow_executor(self):
        """示例7：工作流编排器 - 复杂流程管理"""
        print("\n" + "=" * 80)
        print("🔄 示例7：工作流编排器 - 复杂流程管理")
        print("=" * 80)
        
        # 创建工作流执行器
        executor = TaskWorkflowExecutor()
        
        # 创建工作流
        workflow = executor.create_workflow(
            name="Web应用部署工作流",
            description="完整的Web应用开发部署流程"
        )
        
        # 添加步骤
        executor.add_step(
            workflow_id=workflow.workflow_id,
            step_id="init",
            step_name="项目初始化",
            step_type=WorkflowStepType.TASK
        )
        
        executor.add_step(
            workflow_id=workflow.workflow_id,
            step_id="dev",
            step_name="开发阶段",
            step_type=WorkflowStepType.TASK
        )
        
        executor.add_step(
            workflow_id=workflow.workflow_id,
            step_id="test",
            step_name="测试阶段",
            step_type=WorkflowStepType.TASK
        )
        
        executor.add_step(
            workflow_id=workflow.workflow_id,
            step_id="deploy",
            step_name="部署阶段",
            step_type=WorkflowStepType.TASK
        )
        
        # 添加依赖
        executor.add_dependency(workflow.workflow_id, "dev", "init")
        executor.add_dependency(workflow.workflow_id, "test", "dev")
        executor.add_dependency(workflow.workflow_id, "deploy", "test")
        
        # 执行工作流
        print(f"📌 执行工作流: {workflow.name}")
        execution = executor.execute_workflow(workflow.workflow_id)
        
        print(f"✅ 工作流状态: {execution.status.value}")
        print(f"✅ 步骤执行: {len(execution.step_executions)}个步骤")
        
        return executor
    
    def example_8_task_orchestrator(self):
        """示例8：任务编排器 - 端到端协调"""
        print("\n" + "=" * 80)
        print("🎼 示例8：任务编排器 - 端到端协调")
        print("=" * 80)
        
        # 创建编排器
        orchestrator = TaskOrchestrator()
        
        # 执行完整编排
        requirement = "开发一个用户管理系统，包含用户CRUD功能"
        
        print(f"📌 用户需求: {requirement}")
        print("🔄 开始编排流程...")
        
        result = orchestrator.orchestrate(requirement)
        
        print(f"✅ 编排完成，状态: {result.status.value}")
        print(f"✅ 总任务数: {result.metrics.total_tasks}")
        print(f"✅ 完成任务: {result.metrics.completed_tasks}")
        print(f"✅ 失败任务: {result.metrics.failed_tasks}")
        
        if result.recommendations:
            print(f"💡 建议:")
            for rec in result.recommendations:
                print(f"   - {rec}")
        
        return orchestrator
    
    def run_all_examples(self):
        """运行所有示例"""
        print("开始运行完整的系统集成示例...\n")
        
        # 运行各个示例
        self.example_1_task_tuple()
        self.example_2_task_dag()
        self.example_3_task_execution_engine()
        self.example_4_task_pipeline()
        self.example_5_task_scheduler()
        self.example_6_task_analytics()
        self.example_7_task_workflow_executor()
        self.example_8_task_orchestrator()
        
        print("\n" + "=" * 80)
        print("🎉 所有示例运行完成！")
        print("=" * 80)
        print("\n✅ 任务规划系统完整集成成功！")


def main():
    """主函数"""
    example = SystemIntegrationExample()
    example.run_all_examples()


if __name__ == "__main__":
    main()
