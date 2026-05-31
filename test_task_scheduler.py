import unittest
import time
import threading

from first_principle_agent.core.task_scheduler import (
    TaskScheduler,
    SchedulerConfig,
    SchedulerStatus,
    SchedulerStrategy,
    SchedulerMetrics,
    TaskPriority,
    ScheduledTask,
    create_scheduler
)
from first_principle_agent.core.task_execution_engine import ExecutionStatus


class TestTaskScheduler(unittest.TestCase):
    """测试任务调度器"""

    def test_scheduler_creation(self):
        """测试调度器创建"""
        scheduler = create_scheduler()
        
        self.assertIsNotNone(scheduler.id)
        self.assertEqual(scheduler.status, SchedulerStatus.IDLE)
        self.assertEqual(scheduler.queue_size, 0)
        
        scheduler.stop()

    def test_submit_task(self):
        """测试提交任务"""
        scheduler = create_scheduler(max_workers=2)
        scheduler.start()
        
        def simple_task():
            return "done"
        
        task_id = scheduler.submit(simple_task, priority=TaskPriority.NORMAL)
        
        self.assertIsNotNone(task_id)
        self.assertEqual(scheduler.metrics.total_tasks, 1)
        
        scheduler.wait_for_completion(timeout=2.0)
        scheduler.stop()
        
        self.assertEqual(scheduler.metrics.completed_tasks, 1)

    def test_submit_with_priority(self):
        """测试优先级提交"""
        scheduler = create_scheduler(max_workers=2)
        scheduler.start()
        
        execution_order = []
        
        def task1():
            time.sleep(0.1)
            execution_order.append("low")
        
        def task2():
            execution_order.append("high")
        
        # 提交低优先级任务
        scheduler.submit(task1, priority=TaskPriority.LOW)
        # 提交高优先级任务
        scheduler.submit(task2, priority=TaskPriority.HIGH)
        
        scheduler.wait_for_completion(timeout=2.0)
        scheduler.stop()
        
        # 高优先级任务应该先完成
        self.assertEqual(execution_order[0], "high")

    def test_batch_submit(self):
        """测试批量提交"""
        scheduler = create_scheduler(max_workers=4)
        scheduler.start()
        
        tasks = [lambda: i for i in range(10)]
        priorities = [TaskPriority.NORMAL] * 10
        
        task_ids = scheduler.submit_batch(tasks, priorities)
        
        self.assertEqual(len(task_ids), 10)
        self.assertEqual(scheduler.metrics.total_tasks, 10)
        
        scheduler.wait_for_completion(timeout=3.0)
        scheduler.stop()
        
        self.assertEqual(scheduler.metrics.completed_tasks, 10)

    def test_get_task_status(self):
        """测试获取任务状态"""
        scheduler = create_scheduler(max_workers=2)
        scheduler.start()
        
        task_id = scheduler.submit(lambda: time.sleep(0.1), priority=TaskPriority.HIGH)
        
        # 等待任务开始
        time.sleep(0.05)
        
        status = scheduler.get_task_status(task_id)
        self.assertIn(status, [ExecutionStatus.PENDING, ExecutionStatus.RUNNING])
        
        scheduler.wait_for_completion(timeout=2.0)
        scheduler.stop()
        
        final_status = scheduler.get_task_status(task_id)
        self.assertEqual(final_status, ExecutionStatus.COMPLETED)

    def test_cancel_task(self):
        """测试取消任务"""
        scheduler = create_scheduler(max_workers=2)
        scheduler.start()
        
        task_id = scheduler.submit(lambda: time.sleep(10), priority=TaskPriority.LOW)
        
        time.sleep(0.05)
        
        success = scheduler.cancel_task(task_id)
        self.assertTrue(success)
        
        scheduler.stop()

    def test_task_dependencies(self):
        """测试任务依赖"""
        scheduler = create_scheduler(max_workers=2)
        scheduler.start()
        
        execution_order = []
        
        def task1():
            execution_order.append("task1")
            return "task1"
        
        def task2():
            execution_order.append("task2")
            return "task2"
        
        def task3():
            execution_order.append("task3")
            return "task3"
        
        # 提交任务
        id1 = scheduler.submit(task1)
        id2 = scheduler.submit(task2, dependencies={id1})
        id3 = scheduler.submit(task3, dependencies={id2})
        
        scheduler.wait_for_completion(timeout=3.0)
        scheduler.stop()
        
        # 按顺序执行
        self.assertEqual(execution_order[0], "task1")
        self.assertEqual(execution_order[1], "task2")
        self.assertEqual(execution_order[2], "task3")

    def test_metrics(self):
        """测试指标收集"""
        scheduler = create_scheduler(max_workers=2)
        scheduler.start()
        
        for i in range(5):
            scheduler.submit(lambda: time.sleep(0.05))
        
        scheduler.wait_for_completion(timeout=3.0)
        
        metrics = scheduler.get_metrics()
        
        self.assertEqual(metrics.total_tasks, 5)
        self.assertEqual(metrics.completed_tasks, 5)
        self.assertGreater(metrics.throughput, 0)
        
        scheduler.stop()

    def test_pause_and_resume(self):
        """测试暂停和恢复"""
        scheduler = create_scheduler(max_workers=2)
        scheduler.start()
        
        scheduler.submit(lambda: time.sleep(0.1))
        
        time.sleep(0.05)
        
        scheduler.pause()
        self.assertEqual(scheduler.status, SchedulerStatus.PAUSED)
        
        scheduler.resume()
        self.assertEqual(scheduler.status, SchedulerStatus.RUNNING)
        
        scheduler.wait_for_completion(timeout=2.0)
        scheduler.stop()

    def test_callbacks(self):
        """测试回调函数"""
        scheduler = create_scheduler(max_workers=2)
        scheduler.start()
        
        submit_events = []
        complete_events = []
        
        scheduler.set_callbacks(
            on_submit=lambda t: submit_events.append(t.task_id),
            on_complete=lambda t: complete_events.append(t.task_id)
        )
        
        task_id = scheduler.submit(lambda: "done")
        
        scheduler.wait_for_completion(timeout=2.0)
        
        self.assertEqual(len(submit_events), 1)
        self.assertEqual(len(complete_events), 1)
        
        scheduler.stop()


class TestSchedulerConfig(unittest.TestCase):
    """测试调度器配置"""

    def test_config_defaults(self):
        """测试默认配置"""
        config = SchedulerConfig()
        
        self.assertEqual(config.strategy, SchedulerStrategy.PRIORITY)
        self.assertEqual(config.max_workers, 4)
        self.assertTrue(config.enable_priorities)
        self.assertTrue(config.enable_deduplication)

    def test_config_serialization(self):
        """测试配置序列化"""
        config = SchedulerConfig(
            strategy=SchedulerStrategy.FIFO,
            max_workers=8,
            enable_priorities=False
        )
        
        data = config.to_dict()
        restored = SchedulerConfig.from_dict(data)
        
        self.assertEqual(restored.strategy, SchedulerStrategy.FIFO)
        self.assertEqual(restored.max_workers, 8)
        self.assertFalse(restored.enable_priorities)


class TestScheduledTask(unittest.TestCase):
    """测试调度任务"""

    def test_task_creation(self):
        """测试任务创建"""
        task = ScheduledTask(
            task_id="test-1",
            task=lambda: "test",
            priority=TaskPriority.HIGH
        )
        
        self.assertEqual(task.task_id, "test-1")
        self.assertEqual(task.priority, TaskPriority.HIGH)
        self.assertEqual(task.status, ExecutionStatus.PENDING)

    def test_task_priority_comparison(self):
        """测试优先级比较"""
        task_high = ScheduledTask(task_id="1", task=lambda: None, priority=TaskPriority.HIGH)
        task_low = ScheduledTask(task_id="2", task=lambda: None, priority=TaskPriority.LOW)
        
        self.assertLess(task_high, task_low)  # HIGH < LOW

    def test_task_serialization(self):
        """测试任务序列化"""
        task = ScheduledTask(
            task_id="test-1",
            task=lambda: "test",
            priority=TaskPriority.CRITICAL,
            dependencies={"dep1", "dep2"}
        )
        
        data = task.to_dict()
        restored = ScheduledTask.from_dict(data)
        
        self.assertEqual(restored.task_id, "test-1")
        self.assertEqual(restored.priority, TaskPriority.CRITICAL)
        self.assertEqual(restored.dependencies, {"dep1", "dep2"})


class TestSchedulerMetrics(unittest.TestCase):
    """测试调度器指标"""

    def test_metrics_serialization(self):
        """测试指标序列化"""
        metrics = SchedulerMetrics(
            total_tasks=100,
            completed_tasks=90,
            failed_tasks=10,
            throughput=5.5
        )
        
        data = metrics.to_dict()
        
        self.assertEqual(data["total_tasks"], 100)
        self.assertEqual(data["completed_tasks"], 90)
        self.assertEqual(data["throughput"], 5.5)


class TestTaskPriority(unittest.TestCase):
    """测试任务优先级"""

    def test_priority_order(self):
        """测试优先级顺序"""
        priorities = [
            TaskPriority.BACKGROUND,
            TaskPriority.LOW,
            TaskPriority.NORMAL,
            TaskPriority.HIGH,
            TaskPriority.CRITICAL
        ]
        
        # 从低到高排序
        sorted_priorities = sorted(priorities)
        self.assertEqual(sorted_priorities[0], TaskPriority.CRITICAL)
        self.assertEqual(sorted_priorities[-1], TaskPriority.BACKGROUND)


if __name__ == "__main__":
    unittest.main()
