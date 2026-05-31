import unittest
import time
import threading

from first_principle_agent.core.task_execution_engine import (
    TaskExecutionEngine,
    ExecutionConfig,
    ExecutionStatus,
    ExecutionMode,
    ExecutionPlan,
    ExecutionSummary,
    TaskExecutionResult,
    ExecutionEvent,
    ExecutionEventType,
    ExecutionEventListener,
    create_execution_engine
)
from first_principle_agent.core.task_tuple import TaskTuple


class TestTaskExecutionEngine(unittest.TestCase):
    """测试任务执行引擎"""

    def test_engine_creation(self):
        """测试引擎创建"""
        engine = create_execution_engine()
        
        self.assertIsNotNone(engine.id)
        self.assertEqual(engine.status, ExecutionStatus.PENDING)
        
        engine.shutdown()

    def test_engine_with_resilience(self):
        """测试启用韧性的引擎"""
        config = ExecutionConfig(enable_resilience=True, resilience_preset="default")
        engine = TaskExecutionEngine(config=config)
        
        self.assertIsNotNone(engine.resilience_manager)
        
        engine.shutdown()

    def test_engine_without_resilience(self):
        """测试禁用韧性的引擎"""
        config = ExecutionConfig(enable_resilience=False)
        engine = TaskExecutionEngine(config=config)
        
        self.assertIsNone(engine.resilience_manager)
        
        engine.shutdown()

    def test_execute_sequential_plan(self):
        """测试顺序执行计划"""
        engine = create_execution_engine(mode=ExecutionMode.SEQUENTIAL)
        
        tasks = [
            TaskTuple(target="task1", condition="cond1", boundary="bound1", 
                     end_rule="end1", context="ctx1"),
            TaskTuple(target="task2", condition="cond2", boundary="bound2", 
                     end_rule="end2", context="ctx2"),
            TaskTuple(target="task3", condition="cond3", boundary="bound3", 
                     end_rule="end3", context="ctx3")
        ]
        
        plan = ExecutionPlan(
            id="test_plan_1",
            config=engine.config,
            tasks=tasks
        )
        
        summary = engine.execute_plan(plan)
        
        self.assertEqual(summary.status, ExecutionStatus.COMPLETED)
        self.assertEqual(summary.total_tasks, 3)
        self.assertEqual(summary.completed_tasks, 3)
        self.assertEqual(summary.failed_tasks, 0)
        
        engine.shutdown()

    def test_execute_parallel_plan(self):
        """测试并行执行计划"""
        config = ExecutionConfig(
            mode=ExecutionMode.PARALLEL,
            enable_parallel=True,
            max_parallel_tasks=2
        )
        engine = TaskExecutionEngine(config=config)
        
        tasks = [
            TaskTuple(target="task1", condition="cond1", boundary="bound1", 
                     end_rule="end1", context="ctx1"),
            TaskTuple(target="task2", condition="cond2", boundary="bound2", 
                     end_rule="end2", context="ctx2")
        ]
        
        plan = ExecutionPlan(
            id="test_plan_2",
            config=config,
            tasks=tasks
        )
        
        summary = engine.execute_plan(plan)
        
        self.assertEqual(summary.status, ExecutionStatus.COMPLETED)
        self.assertEqual(summary.total_tasks, 2)
        
        engine.shutdown()

    def test_get_result(self):
        """测试获取执行结果"""
        engine = create_execution_engine()
        
        tasks = [
            TaskTuple(target="task1", condition="cond1", boundary="bound1", 
                     end_rule="end1", context="ctx1")
        ]
        
        plan = ExecutionPlan(
            id="test_plan_3",
            config=engine.config,
            tasks=tasks
        )
        
        engine.execute_plan(plan)
        
        result = engine.get_result("task1")
        self.assertIsNotNone(result)
        self.assertEqual(result.task_id, "task1")
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        
        engine.shutdown()

    def test_execution_history(self):
        """测试执行历史"""
        engine = create_execution_engine()
        
        tasks = [
            TaskTuple(target="task1", condition="cond1", boundary="bound1", 
                     end_rule="end1", context="ctx1")
        ]
        
        plan = ExecutionPlan(
            id="test_plan_4",
            config=engine.config,
            tasks=tasks
        )
        
        engine.execute_plan(plan)
        
        history = engine.get_execution_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].plan_id, "test_plan_4")
        
        engine.shutdown()

    def test_reset(self):
        """测试重置引擎"""
        engine = create_execution_engine()
        
        tasks = [
            TaskTuple(target="task1", condition="cond1", boundary="bound1", 
                     end_rule="end1", context="ctx1")
        ]
        
        plan = ExecutionPlan(
            id="test_plan_5",
            config=engine.config,
            tasks=tasks
        )
        
        engine.execute_plan(plan)
        engine.reset()
        
        self.assertEqual(engine.status, ExecutionStatus.PENDING)
        self.assertEqual(len(engine.get_execution_history()), 1)
        
        engine.shutdown()


class TestExecutionConfig(unittest.TestCase):
    """测试执行配置"""

    def test_config_serialization(self):
        """测试配置序列化"""
        config = ExecutionConfig(
            mode=ExecutionMode.SEQUENTIAL,
            enable_parallel=True,
            max_parallel_tasks=4
        )
        
        data = config.to_dict()
        restored = ExecutionConfig.from_dict(data)
        
        self.assertEqual(restored.mode, ExecutionMode.SEQUENTIAL)
        self.assertTrue(restored.enable_parallel)
        self.assertEqual(restored.max_parallel_tasks, 4)

    def test_default_config(self):
        """测试默认配置"""
        config = ExecutionConfig()
        
        self.assertEqual(config.mode, ExecutionMode.SEQUENTIAL)
        self.assertFalse(config.enable_parallel)
        self.assertEqual(config.max_parallel_tasks, 4)


class TestExecutionEvent(unittest.TestCase):
    """测试执行事件"""

    def test_event_creation(self):
        """测试事件创建"""
        event = ExecutionEvent(
            event_type=ExecutionEventType.TASK_STARTED,
            timestamp=time.time(),
            plan_id="plan1",
            task_id="task1"
        )
        
        self.assertEqual(event.event_type, ExecutionEventType.TASK_STARTED)
        self.assertEqual(event.plan_id, "plan1")
        self.assertEqual(event.task_id, "task1")

    def test_event_listener(self):
        """测试事件监听器"""
        received_events = []
        
        def callback(event):
            received_events.append(event)
        
        listener = ExecutionEventListener(callback)
        
        event = ExecutionEvent(
            event_type=ExecutionEventType.TASK_STARTED,
            timestamp=time.time(),
            plan_id="plan1"
        )
        
        listener.on_event(event)
        
        self.assertEqual(len(received_events), 1)
        self.assertEqual(received_events[0].event_type, ExecutionEventType.TASK_STARTED)


class TestTaskExecutionResult(unittest.TestCase):
    """测试任务执行结果"""

    def test_result_creation(self):
        """测试结果创建"""
        result = TaskExecutionResult(
            task_id="task1",
            status=ExecutionStatus.COMPLETED,
            start_time=time.time(),
            result="success"
        )
        
        self.assertEqual(result.task_id, "task1")
        self.assertEqual(result.status, ExecutionStatus.COMPLETED)
        self.assertEqual(result.result, "success")

    def test_result_serialization(self):
        """测试结果序列化"""
        result = TaskExecutionResult(
            task_id="task1",
            status=ExecutionStatus.COMPLETED,
            start_time=time.time(),
            result="success"
        )
        
        data = result.to_dict()
        
        self.assertEqual(data["task_id"], "task1")
        self.assertEqual(data["status"], "completed")


class TestExecutionPlan(unittest.TestCase):
    """测试执行计划"""

    def test_plan_creation(self):
        """测试计划创建"""
        config = ExecutionConfig()
        tasks = [
            TaskTuple(target="task1", condition="cond1", boundary="bound1", 
                     end_rule="end1", context="ctx1")
        ]
        
        plan = ExecutionPlan(
            id="plan1",
            config=config,
            tasks=tasks
        )
        
        self.assertEqual(plan.id, "plan1")
        self.assertEqual(len(plan.tasks), 1)

    def test_plan_serialization(self):
        """测试计划序列化"""
        config = ExecutionConfig()
        plan = ExecutionPlan(
            id="plan1",
            config=config
        )
        
        data = plan.to_dict()
        
        self.assertEqual(data["id"], "plan1")


class TestExecutionSummary(unittest.TestCase):
    """测试执行摘要"""

    def test_summary_creation(self):
        """测试摘要创建"""
        summary = ExecutionSummary(
            plan_id="plan1",
            status=ExecutionStatus.COMPLETED,
            total_tasks=10,
            completed_tasks=10,
            failed_tasks=0,
            total_time=100.0,
            start_time=time.time()
        )
        
        self.assertEqual(summary.plan_id, "plan1")
        self.assertEqual(summary.total_tasks, 10)
        self.assertEqual(summary.completed_tasks, 10)

    def test_summary_serialization(self):
        """测试摘要序列化"""
        summary = ExecutionSummary(
            plan_id="plan1",
            status=ExecutionStatus.COMPLETED,
            total_tasks=10,
            completed_tasks=10,
            failed_tasks=0,
            total_time=100.0,
            start_time=time.time()
        )
        
        data = summary.to_dict()
        
        self.assertEqual(data["plan_id"], "plan1")
        self.assertEqual(data["total_tasks"], 10)


if __name__ == "__main__":
    unittest.main()
