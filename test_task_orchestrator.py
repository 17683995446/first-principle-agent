"""
Test TaskOrchestrator
基于第一性原理AI Agent任务规划系统 - 第57阶段测试
"""

import unittest
import time
from first_principle_agent.core.task_orchestrator import (
    TaskOrchestrator,
    OrchestrationConfig,
    OrchestrationStrategy,
    OrchestrationPhase,
    OrchestrationResult,
    OrchestrationMetrics,
    create_orchestrator
)
from first_principle_agent.core.dag_structures import TaskDAG, DAGNode, DAGEdge


class TestTaskOrchestrator(unittest.TestCase):
    """测试TaskOrchestrator类"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.orchestrator = TaskOrchestrator()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.orchestrator.orchestrator_id)
        self.assertIsNotNone(self.orchestrator.planning_system)
        self.assertIsNotNone(self.orchestrator.execution_engine)
        self.assertIsNotNone(self.orchestrator.pipeline)
        self.assertIsNotNone(self.orchestrator.scheduler)
        self.assertIsNotNone(self.orchestrator.analytics)
        self.assertIsNotNone(self.orchestrator.workflow_executor)
        self.assertEqual(len(self.orchestrator.orchestrations), 0)
    
    def test_create_orchestrator(self):
        """测试工厂函数创建编排器"""
        orchestrator = create_orchestrator(
            strategy=OrchestrationStrategy.SEQUENTIAL,
            enable_analytics=False
        )
        self.assertIsInstance(orchestrator, TaskOrchestrator)
        self.assertEqual(orchestrator.config.strategy, OrchestrationStrategy.SEQUENTIAL)
        self.assertFalse(orchestrator.config.enable_analytics)
    
    def test_orchestration_config(self):
        """测试编排配置"""
        config = OrchestrationConfig(
            strategy=OrchestrationStrategy.PARALLEL,
            enable_analytics=True,
            auto_retry=True,
            max_retries=5
        )
        self.assertEqual(config.strategy, OrchestrationStrategy.PARALLEL)
        self.assertTrue(config.enable_analytics)
        self.assertTrue(config.auto_retry)
        self.assertEqual(config.max_retries, 5)
    
    def test_orchestration_metrics(self):
        """测试编排指标"""
        metrics = OrchestrationMetrics()
        metrics.total_tasks = 10
        metrics.completed_tasks = 8
        metrics.failed_tasks = 2
        metrics.pending_tasks = 0
        
        self.assertEqual(metrics.total_tasks, 10)
        self.assertEqual(metrics.completed_tasks, 8)
        self.assertEqual(metrics.failed_tasks, 2)
        self.assertEqual(metrics.pending_tasks, 0)
    
    def test_orchestration_result(self):
        """测试编排结果"""
        result = OrchestrationResult(
            orchestration_id="test-123",
            status=OrchestrationPhase.COMPLETED,
            metrics=OrchestrationMetrics(),
            task_results={"task1": {"success": True}}
        )
        self.assertEqual(result.orchestration_id, "test-123")
        self.assertEqual(result.status, OrchestrationPhase.COMPLETED)
        self.assertIn("task1", result.task_results)
    
    def test_register_callback(self):
        """测试回调注册"""
        callback_called = []
        
        def test_callback(result):
            callback_called.append(result)
        
        self.orchestrator.register_callback("test_event", test_callback)
        self.orchestrator._emit_event("test_event", "test_data")
        
        self.assertEqual(len(callback_called), 1)
        self.assertEqual(callback_called[0], "test_data")
    
    def test_orchestrate_simple(self):
        """测试简单编排流程"""
        requirement = "Build a simple website with homepage and about page"
        
        result = self.orchestrator.orchestrate(requirement)
        
        self.assertIsInstance(result, OrchestrationResult)
        self.assertIsNotNone(result.orchestration_id)
        self.assertIn(result.status, [OrchestrationPhase.COMPLETED, OrchestrationPhase.FAILED])
        self.assertIsNotNone(result.metrics)
    
    def test_orchestrate_with_sequential_strategy(self):
        """测试顺序执行策略"""
        config = OrchestrationConfig(strategy=OrchestrationStrategy.SEQUENTIAL)
        requirement = "Create a blog post with title, content, and tags"
        
        result = self.orchestrator.orchestrate(requirement, config=config)
        
        self.assertIsInstance(result, OrchestrationResult)
        self.assertIn(result.status, [OrchestrationPhase.COMPLETED, OrchestrationPhase.FAILED])
    
    def test_orchestrate_with_workflow_strategy(self):
        """测试工作流执行策略"""
        config = OrchestrationConfig(strategy=OrchestrationStrategy.WORKFLOW)
        requirement = "Deploy a web application with database setup"
        
        result = self.orchestrator.orchestrate(requirement, config=config)
        
        self.assertIsInstance(result, OrchestrationResult)
        self.assertIn(result.status, [OrchestrationPhase.COMPLETED, OrchestrationPhase.FAILED])
    
    def test_get_orchestration(self):
        """测试获取编排结果"""
        requirement = "Test requirement"
        result = self.orchestrator.orchestrate(requirement)
        
        retrieved = self.orchestrator.get_orchestration(result.orchestration_id)
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.orchestration_id, result.orchestration_id)
    
    def test_get_all_orchestrations(self):
        """测试获取所有编排结果"""
        requirement1 = "First requirement"
        requirement2 = "Second requirement"
        
        self.orchestrator.orchestrate(requirement1)
        self.orchestrator.orchestrate(requirement2)
        
        all_orchestrations = self.orchestrator.get_all_orchestrations()
        
        self.assertEqual(len(all_orchestrations), 2)
    
    def test_reset(self):
        """测试重置编排器"""
        requirement = "Test requirement"
        self.orchestrator.orchestrate(requirement)
        
        self.orchestrator.reset()
        
        self.assertEqual(len(self.orchestrator.orchestrations), 0)
        self.assertEqual(self.orchestrator.metrics.total_tasks, 0)
    
    def test_orchestration_phase_enum(self):
        """测试编排阶段枚举"""
        self.assertEqual(OrchestrationPhase.INITIALIZING.value, "initializing")
        self.assertEqual(OrchestrationPhase.ANALYZING.value, "analyzing")
        self.assertEqual(OrchestrationPhase.PLANNING.value, "planning")
        self.assertEqual(OrchestrationPhase.EXECUTING.value, "executing")
        self.assertEqual(OrchestrationPhase.COMPLETED.value, "completed")
        self.assertEqual(OrchestrationPhase.FAILED.value, "failed")
    
    def test_orchestration_strategy_enum(self):
        """测试编排策略枚举"""
        self.assertEqual(OrchestrationStrategy.SEQUENTIAL.value, "sequential")
        self.assertEqual(OrchestrationStrategy.PARALLEL.value, "parallel")
        self.assertEqual(OrchestrationStrategy.WORKFLOW.value, "workflow")
        self.assertEqual(OrchestrationStrategy.PIPELINE.value, "pipeline")
        self.assertEqual(OrchestrationStrategy.ADAPTIVE.value, "adaptive")
    
    def test_orchestration_with_callbacks(self):
        """测试带回调的编排"""
        complete_called = []
        failure_called = []
        
        def on_complete(result):
            complete_called.append(result)
        
        def on_failure(result):
            failure_called.append(result)
        
        config = OrchestrationConfig(
            callback_on_complete=on_complete,
            callback_on_failure=on_failure
        )
        
        requirement = "Test with callbacks"
        result = self.orchestrator.orchestrate(requirement, config=config)
        
        if result.status == OrchestrationPhase.COMPLETED:
            self.assertEqual(len(complete_called), 1)
            self.assertEqual(len(failure_called), 0)
        else:
            self.assertEqual(len(failure_called), 1)
            self.assertEqual(len(complete_called), 0)
    
    def test_orchestration_metrics_phase_durations(self):
        """测试编排指标的阶段时长"""
        requirement = "Test phase durations"
        result = self.orchestrator.orchestrate(requirement)
        
        self.assertIsNotNone(result.metrics)
        self.assertIn("analyzing", result.metrics.phase_durations)
        self.assertIn("planning", result.metrics.phase_durations)
        self.assertIn("executing", result.metrics.phase_durations)
    
    def test_recommendations(self):
        """测试建议生成"""
        requirement = "Test recommendations"
        result = self.orchestrator.orchestrate(requirement)
        
        self.assertIsInstance(result.recommendations, list)
    
    def test_orchestration_without_analytics(self):
        """测试禁用分析功能的编排"""
        config = OrchestrationConfig(enable_analytics=False)
        requirement = "Test without analytics"
        
        result = self.orchestrator.orchestrate(requirement, config=config)
        
        self.assertIn(result.status, [OrchestrationPhase.COMPLETED, OrchestrationPhase.FAILED])


class TestTaskOrchestratorIntegration(unittest.TestCase):
    """TaskOrchestrator集成测试"""
    
    def test_end_to_end_orchestration(self):
        """端到端编排测试"""
        orchestrator = TaskOrchestrator()
        
        # 执行完整的编排流程
        requirement = (
            "Create a project structure with src, tests, and docs directories, "
            "then add a README file and a simple Python script"
        )
        
        result = orchestrator.orchestrate(requirement)
        
        # 验证结果
        self.assertIsInstance(result, OrchestrationResult)
        self.assertEqual(result.status, OrchestrationPhase.COMPLETED)
        self.assertIsNotNone(result.task_results)
        self.assertIsNotNone(result.analytics_report)
        self.assertIsNotNone(result.metrics)
        
        # 验证指标
        self.assertGreater(result.metrics.total_tasks, 0)
        self.assertIsNotNone(result.metrics.total_duration)
        
        print(f"\nEnd-to-end test completed:")
        print(f"  Orchestration ID: {result.orchestration_id}")
        print(f"  Status: {result.status.value}")
        print(f"  Total tasks: {result.metrics.total_tasks}")
        print(f"  Completed: {result.metrics.completed_tasks}")
        print(f"  Duration: {result.metrics.total_duration:.2f}s")


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)
