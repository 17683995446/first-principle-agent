import unittest
import time
from first_principle_agent.layers.timeout_manager import (
    TimeoutManager,
    TimeoutConfig,
    TimeoutContext,
    TimeoutError,
    SoftTimeoutError,
    TimeoutStrategy,
    TimeoutMetrics
)


class TestTimeoutManager(unittest.TestCase):
    """测试超时管理器"""

    def test_successful_execution(self):
        """测试成功执行（不超时）"""
        config = TimeoutConfig(default_timeout_seconds=5.0)
        manager = TimeoutManager(config)
        
        def quick_func():
            return "success"
        
        result = manager.execute(quick_func)
        self.assertEqual(result, "success")
        self.assertEqual(manager.metrics.total_executions, 1)
        self.assertEqual(manager.metrics.successful_executions, 1)
        
        manager.shutdown()

    def test_timeout_fast_fail(self):
        """测试快速失败策略超时"""
        config = TimeoutConfig(
            default_timeout_seconds=0.1,
            strategy=TimeoutStrategy.FAST_FAIL
        )
        manager = TimeoutManager(config)
        
        def slow_func():
            time.sleep(1)
            return "done"
        
        with self.assertRaises(TimeoutError):
            manager.execute(slow_func)
        
        self.assertEqual(manager.metrics.timeout_executions, 1)
        
        manager.shutdown()

    def test_timeout_graceful(self):
        """测试优雅降级策略超时"""
        config = TimeoutConfig(
            default_timeout_seconds=0.1,
            strategy=TimeoutStrategy.GRACEFUL
        )
        manager = TimeoutManager(config)
        
        def slow_func():
            time.sleep(1)
            return "done"
        
        def fallback():
            return "fallback"
        
        result = manager.execute(slow_func, fallback=fallback)
        self.assertEqual(result, "fallback")
        self.assertEqual(manager.metrics.timeout_executions, 1)
        
        manager.shutdown()

    def test_timeout_no_fallback(self):
        """测试无降级函数的超时"""
        config = TimeoutConfig(
            default_timeout_seconds=0.1,
            strategy=TimeoutStrategy.GRACEFUL,
            propagate_timeout_exception=True
        )
        manager = TimeoutManager(config)
        
        def slow_func():
            time.sleep(1)
            return "done"
        
        with self.assertRaises(TimeoutError):
            manager.execute(slow_func)
        
        manager.shutdown()

    def test_custom_timeout(self):
        """测试自定义超时时间"""
        config = TimeoutConfig(default_timeout_seconds=5.0)
        manager = TimeoutManager(config)
        
        def slow_func():
            time.sleep(0.2)
            return "done"
        
        result = manager.execute(slow_func, timeout_seconds=0.5)
        self.assertEqual(result, "done")
        
        manager.shutdown()

    def test_timeout_callback(self):
        """测试超时回调"""
        callback_called = {"value": False}
        
        def on_timeout(context):
            callback_called["value"] = True
        
        config = TimeoutConfig(
            default_timeout_seconds=0.1,
            strategy=TimeoutStrategy.FAST_FAIL
        )
        manager = TimeoutManager(config, on_timeout=on_timeout)
        
        def slow_func():
            time.sleep(1)
            return "done"
        
        with self.assertRaises(TimeoutError):
            manager.execute(slow_func)
        
        self.assertTrue(callback_called["value"])
        
        manager.shutdown()

    def test_decorator_usage(self):
        """测试装饰器用法"""
        config = TimeoutConfig(default_timeout_seconds=0.5)
        manager = TimeoutManager(config)
        
        @manager.timeout(0.1)
        def slow_func():
            time.sleep(0.5)
            return "done"
        
        with self.assertRaises(TimeoutError):
            slow_func()
        
        manager.shutdown()

    def test_context_manager(self):
        """测试上下文管理器"""
        with TimeoutManager() as manager:
            def quick_func():
                return "success"
            
            result = manager.execute(quick_func)
            self.assertEqual(result, "success")

    def test_metrics_recording(self):
        """测试指标记录"""
        config = TimeoutConfig(default_timeout_seconds=1.0)
        manager = TimeoutManager(config)
        
        def quick_func():
            time.sleep(0.01)
            return "success"
        
        for _ in range(5):
            manager.execute(quick_func)
        
        self.assertEqual(manager.metrics.total_executions, 5)
        self.assertEqual(manager.metrics.successful_executions, 5)
        self.assertEqual(manager.metrics.timeout_executions, 0)
        
        manager.shutdown()

    def test_reset_metrics(self):
        """测试重置指标"""
        config = TimeoutConfig(default_timeout_seconds=1.0)
        manager = TimeoutManager(config)
        
        def quick_func():
            return "success"
        
        manager.execute(quick_func)
        self.assertEqual(manager.metrics.total_executions, 1)
        
        manager.reset_metrics()
        self.assertEqual(manager.metrics.total_executions, 0)
        
        manager.shutdown()

    def test_metrics_summary(self):
        """测试指标摘要"""
        config = TimeoutConfig(default_timeout_seconds=1.0)
        manager = TimeoutManager(config)
        
        def quick_func():
            time.sleep(0.01)
            return "success"
        
        for _ in range(3):
            manager.execute(quick_func)
        
        summary = manager.get_metrics_summary()
        
        self.assertEqual(summary["total_executions"], 3)
        self.assertEqual(summary["successful_executions"], 3)
        self.assertEqual(summary["timeout_executions"], 0)
        self.assertEqual(summary["timeout_rate"], 0.0)
        
        manager.shutdown()

    def test_execution_with_args(self):
        """测试带参数的函数执行"""
        config = TimeoutConfig(default_timeout_seconds=1.0)
        manager = TimeoutManager(config)
        
        def func_with_args(a, b, c=10):
            return a + b + c
        
        result = manager.execute(func_with_args, 1, 2, c=3)
        self.assertEqual(result, 6)
        
        manager.shutdown()

    def test_parallel_strategy(self):
        """测试并行策略"""
        config = TimeoutConfig(
            default_timeout_seconds=0.1,
            strategy=TimeoutStrategy.PARALLEL
        )
        manager = TimeoutManager(config)
        
        def slow_func():
            time.sleep(1)
            return "done"
        
        def fallback():
            return "fallback"
        
        result = manager.execute(slow_func, fallback=fallback)
        self.assertEqual(result, "fallback")
        
        manager.shutdown()

    def test_timeout_context(self):
        """测试超时上下文"""
        config = TimeoutConfig(default_timeout_seconds=0.5)
        manager = TimeoutManager(config)
        
        def quick_func():
            time.sleep(0.01)
            return "success"
        
        def on_timeout(ctx):
            self.assertIsInstance(ctx, TimeoutContext)
            self.assertEqual(ctx.operation_name, "quick_func")
            self.assertGreater(ctx.timeout_seconds, 0)
        
        manager.execute(quick_func)
        
        manager.shutdown()


class TestTimeoutContext(unittest.TestCase):
    """测试超时上下文"""

    def test_context_creation(self):
        """测试上下文创建"""
        context = TimeoutContext(
            operation_name="test_op",
            start_time=time.time(),
            timeout_seconds=10.0
        )
        
        self.assertEqual(context.operation_name, "test_op")
        self.assertEqual(context.timeout_seconds, 10.0)
        self.assertFalse(context.is_timed_out)
        self.assertFalse(context.is_soft_timed_out)

    def test_elapsed_time(self):
        """测试流逝时间"""
        context = TimeoutContext(
            operation_name="test_op",
            start_time=time.time() - 5.0,
            timeout_seconds=10.0
        )
        
        elapsed = context.elapsed_time()
        self.assertGreater(elapsed, 4.0)
        self.assertLess(elapsed, 6.0)

    def test_remaining_time(self):
        """测试剩余时间"""
        context = TimeoutContext(
            operation_name="test_op",
            start_time=time.time() - 3.0,
            timeout_seconds=10.0
        )
        
        remaining = context.remaining_time()
        self.assertGreater(remaining, 6.0)
        self.assertLess(remaining, 8.0)

    def test_progress_percentage(self):
        """测试进度百分比"""
        context = TimeoutContext(
            operation_name="test_op",
            start_time=time.time() - 5.0,
            timeout_seconds=10.0
        )
        
        progress = context.progress_percentage()
        self.assertGreater(progress, 40.0)
        self.assertLess(progress, 60.0)


class TestTimeoutMetrics(unittest.TestCase):
    """测试超时指标"""

    def test_metrics_serialization(self):
        """测试指标序列化"""
        metrics = TimeoutMetrics(
            total_executions=100,
            successful_executions=90,
            timeout_executions=10
        )
        
        data = metrics.to_dict()
        restored = TimeoutMetrics.from_dict(data)
        
        self.assertEqual(restored.total_executions, 100)
        self.assertEqual(restored.successful_executions, 90)
        self.assertEqual(restored.timeout_executions, 10)

    def test_metrics_to_dict(self):
        """测试指标转字典"""
        metrics = TimeoutMetrics()
        data = metrics.to_dict()
        
        self.assertIn("total_executions", data)
        self.assertIn("successful_executions", data)
        self.assertIn("timeout_executions", data)
        self.assertIn("average_execution_time", data)


class TestTimeoutConfig(unittest.TestCase):
    """测试超时配置"""

    def test_config_serialization(self):
        """测试配置序列化"""
        config = TimeoutConfig(
            default_timeout_seconds=30.0,
            strategy=TimeoutStrategy.GRACEFUL,
            enable_soft_timeout=True
        )
        
        data = config.to_dict()
        restored = TimeoutConfig.from_dict(data)
        
        self.assertEqual(restored.default_timeout_seconds, 30.0)
        self.assertEqual(restored.strategy, TimeoutStrategy.GRACEFUL)
        self.assertTrue(restored.enable_soft_timeout)


if __name__ == "__main__":
    unittest.main()
