#!/usr/bin/env python3
"""
测试任务规划系统完整集成 - 第58阶段
"""

import unittest
import sys
import os
import time

# 添加路径以导入模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from first_principle_agent.examples.system_integration_example import SystemIntegrationExample
from first_principle_agent.core.task_tuple import TaskTuple
from first_principle_agent.core.dag_structures import TaskDAG, DAGNode, DAGEdge
from first_principle_agent.core.task_orchestrator import TaskOrchestrator, OrchestrationPhase


class TestSystemIntegration(unittest.TestCase):
    """测试任务规划系统完整集成"""
    
    def setUp(self):
        """测试前设置"""
        self.example = SystemIntegrationExample()
    
    def test_1_task_tuple_creation(self):
        """测试1：任务四元组创建"""
        task = self.example.example_1_task_tuple()
        self.assertIsInstance(task, TaskTuple)
        self.assertEqual(task.target, "创建一个简单的Web应用")
        self.assertIsInstance(task.condition, list)
        self.assertIsInstance(task.boundary, dict)
        self.assertIsInstance(task.end_rule, dict)
    
    def test_2_task_dag_creation(self):
        """测试2：任务DAG创建"""
        dag = self.example.example_2_task_dag()
        self.assertIsInstance(dag, TaskDAG)
        self.assertEqual(dag.id, "web_app_dev")
        self.assertEqual(len(dag.nodes), 5)
        self.assertEqual(len(dag.edges), 5)
        
        # 验证节点
        node_ids = [node.id for node in dag.nodes]
        self.assertIn("setup_env", node_ids)
        self.assertIn("create_db", node_ids)
        self.assertIn("develop_api", node_ids)
    
    def test_3_task_execution_engine(self):
        """测试3：任务执行引擎"""
        engine = self.example.example_3_task_execution_engine()
        self.assertIsNotNone(engine)
        
        # 简单测试执行功能
        def test_task():
            return "test_result"
        
        results = engine.execute_sequential([test_task])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], "test_result")
    
    def test_4_task_pipeline(self):
        """测试4：任务管道"""
        pipeline = self.example.example_4_task_pipeline()
        self.assertIsNotNone(pipeline)
        
        # 测试管道执行
        test_input = "test data"
        result = pipeline.execute(test_input)
        self.assertIsNotNone(result)
    
    def test_5_task_scheduler(self):
        """测试5：任务调度器"""
        scheduler = self.example.example_5_task_scheduler()
        self.assertIsNotNone(scheduler)
        
        # 验证调度器状态
        self.assertEqual(scheduler.status.value, "stopped")
    
    def test_6_task_analytics(self):
        """测试6：任务分析引擎"""
        analytics = self.example.example_6_task_analytics()
        self.assertIsNotNone(analytics)
        
        # 验证分析结果
        self.assertGreater(len(analytics.results), 0)
    
    def test_7_workflow_executor(self):
        """测试7：工作流执行器"""
        executor = self.example.example_7_task_workflow_executor()
        self.assertIsNotNone(executor)
        
        # 验证工作流创建
        self.assertGreater(len(executor.workflows), 0)
    
    def test_8_task_orchestrator(self):
        """测试8：任务编排器"""
        orchestrator = self.example.example_8_task_orchestrator()
        self.assertIsInstance(orchestrator, TaskOrchestrator)
        
        # 再次测试编排功能
        result = orchestrator.orchestrate("测试简单需求")
        self.assertIsNotNone(result)
        self.assertIn(result.status, [OrchestrationPhase.COMPLETED, OrchestrationPhase.FAILED])
    
    def test_9_full_integration_workflow(self):
        """测试9：完整集成工作流"""
        print("\n" + "=" * 80)
        print("🔄 测试9：完整集成工作流")
        print("=" * 80)
        
        # 1. 创建任务四元组
        task = TaskTuple(
            target="完成集成测试",
            condition=["测试环境就绪"],
            boundary={"include": ["测试步骤"], "exclude": [], "constraints": {}},
            end_rule={"success_criteria": ["所有测试通过"], "failure_criteria": ["测试失败"], "timeout": 3600, "max_attempts": 1}
        )
        self.assertIsNotNone(task)
        
        # 2. 创建DAG
        node1 = DAGNode(node_id="step1", name="初始化", node_type="task")
        node2 = DAGNode(node_id="step2", name="执行", node_type="task")
        edge = DAGEdge(edge_id="e1", from_node="step1", to_node="step2", edge_type="requires")
        dag = TaskDAG(dag_id="test_dag", nodes=[node1, node2], edges=[edge])
        self.assertIsNotNone(dag)
        
        # 3. 使用编排器
        orchestrator = TaskOrchestrator()
        result = orchestrator.orchestrate("完整集成测试")
        
        # 验证结果
        self.assertIsNotNone(result)
        print(f"✅ 集成工作流完成，状态: {result.status.value}")
    
    def test_10_run_all_examples(self):
        """测试10：运行所有示例"""
        print("\n" + "=" * 80)
        print("🎯 测试10：运行所有示例")
        print("=" * 80)
        
        try:
            # 运行示例（但不打印过多输出）
            # 只测试核心功能
            task = self.example.example_1_task_tuple()
            self.assertIsNotNone(task)
            
            dag = self.example.example_2_task_dag()
            self.assertIsNotNone(dag)
            
            orchestrator = self.example.example_8_task_orchestrator()
            self.assertIsNotNone(orchestrator)
            
            print("✅ 所有示例核心功能测试通过！")
            
        except Exception as e:
            self.fail(f"运行示例失败: {e}")


class TestSystemIntegrationAdvanced(unittest.TestCase):
    """高级集成测试"""
    
    def test_error_handling(self):
        """测试错误处理"""
        print("\n" + "=" * 80)
        print("⚠️ 测试：错误处理")
        print("=" * 80)
        
        orchestrator = TaskOrchestrator()
        
        # 测试错误处理
        try:
            # 传入空需求应该能处理
            result = orchestrator.orchestrate("")
            self.assertIsNotNone(result)
            print("✅ 空需求处理正确")
        except Exception as e:
            self.fail(f"错误处理失败: {e}")
    
    def test_performance_basic(self):
        """测试基本性能"""
        print("\n" + "=" * 80)
        print("⚡ 测试：基本性能")
        print("=" * 80)
        
        orchestrator = TaskOrchestrator()
        
        # 测试多次执行的性能
        start_time = time.time()
        for i in range(3):
            result = orchestrator.orchestrate(f"测试需求{i}")
            self.assertIsNotNone(result)
        
        total_time = time.time() - start_time
        print(f"✅ 3次编排总耗时: {total_time:.3f}秒")
        
        # 验证性能在可接受范围内
        self.assertLess(total_time, 10.0)


if __name__ == "__main__":
    print("=" * 80)
    print("🧪 任务规划系统 - 完整集成测试")
    print("=" * 80)
    print()
    
    unittest.main(verbosity=2)
