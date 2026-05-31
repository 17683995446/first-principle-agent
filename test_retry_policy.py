import unittest
import time
from first_principle_agent.layers.retry_policy import (
    RetryPolicy,
    RetryPolicyConfig,
    RetryPolicyWithContext,
    RetryContext,
    BackoffStrategy,
    RetryMetrics
)


class TestRetryPolicy(unittest.TestCase):
    """测试重试策略"""

    def test_successful_execution(self):
        """测试成功执行（不需要重试）"""
        policy = RetryPolicy()
        
        def success_func():
            return "success"
        
        result = policy.execute(success_func)
        self.assertEqual(result, "success")
        self.assertEqual(policy.metrics.total_attempts, 1)
        self.assertEqual(policy.metrics.total_successes, 1)

    def test_retry_on_failure(self):
        """测试失败时重试"""
        config = RetryPolicyConfig(max_attempts=3, base_delay_seconds=0.01)
        policy = RetryPolicy(config=config)
        
        attempts = {"count": 0}
        
        def flaky_func():
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise ValueError("Temporary error")
            return "success"
        
        result = policy.execute(flaky_func)
        self.assertEqual(result, "success")
        self.assertEqual(attempts["count"], 3)
        self.assertEqual(policy.metrics.total_retries, 2)

    def test_max_attempts_exceeded(self):
        """测试超过最大尝试次数"""
        config = RetryPolicyConfig(max_attempts=2, base_delay_seconds=0.01)
        policy = RetryPolicy(config=config)
        
        def always_fail():
            raise ValueError("Always fails")
        
        with self.assertRaises(ValueError):
            policy.execute(always_fail)
        
        # max_attempts=2 表示允许2次尝试
        self.assertEqual(policy.metrics.total_attempts, 2)
        self.assertEqual(policy.metrics.total_failures, 1)
        self.assertEqual(policy.metrics.total_retries, 1)

    def test_exponential_backoff(self):
        """测试指数退避策略"""
        config = RetryPolicyConfig(
            max_attempts=4,
            base_delay_seconds=0.1,
            backoff_strategy=BackoffStrategy.EXPONENTIAL
        )
        policy = RetryPolicy(config=config)
        
        attempts = {"count": 0}
        delays = []
        
        def flaky_func():
            attempts["count"] += 1
            if attempts["count"] < 4:
                raise ValueError("Temporary error")
            return "success"
        
        start = time.time()
        result = policy.execute(flaky_func)
        total_time = time.time() - start
        
        self.assertEqual(result, "success")
        # 指数退避：0.1 + 0.2 + 0.4 = 0.7秒左右
        self.assertGreater(total_time, 0.6)

    def test_fixed_delay(self):
        """测试固定延迟策略"""
        config = RetryPolicyConfig(
            max_attempts=3,
            base_delay_seconds=0.1,
            backoff_strategy=BackoffStrategy.FIXED
        )
        policy = RetryPolicy(config=config)
        
        attempts = {"count": 0}
        
        def flaky_func():
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise ValueError("Temporary error")
            return "success"
        
        start = time.time()
        result = policy.execute(flaky_func)
        total_time = time.time() - start
        
        self.assertEqual(result, "success")
        # 固定延迟：0.1 + 0.1 = 0.2秒左右
        self.assertGreater(total_time, 0.15)

    def test_linear_backoff(self):
        """测试线性退避策略"""
        config = RetryPolicyConfig(
            max_attempts=4,
            base_delay_seconds=0.1,
            backoff_strategy=BackoffStrategy.LINEAR
        )
        policy = RetryPolicy(config=config)
        
        attempts = {"count": 0}
        
        def flaky_func():
            attempts["count"] += 1
            if attempts["count"] < 4:
                raise ValueError("Temporary error")
            return "success"
        
        start = time.time()
        result = policy.execute(flaky_func)
        total_time = time.time() - start
        
        self.assertEqual(result, "success")
        # 线性退避：0.1 + 0.2 + 0.3 = 0.6秒左右
        self.assertGreater(total_time, 0.5)

    def test_timeout(self):
        """测试超时机制"""
        config = RetryPolicyConfig(
            max_attempts=10,
            base_delay_seconds=1.0,
            timeout_seconds=0.5
        )
        policy = RetryPolicy(config=config)
        
        def always_fail():
            raise ValueError("Always fails")
        
        with self.assertRaises(ValueError):
            policy.execute(always_fail)
        
        # 应该在超时后停止
        self.assertLess(policy.metrics.total_attempts, 10)

    def test_non_retryable_exception(self):
        """测试不可重试的异常"""
        config = RetryPolicyConfig(
            max_attempts=3,
            base_delay_seconds=0.01,
            retryable_exceptions=(ValueError,)
        )
        policy = RetryPolicy(config=config)
        
        def raise_type_error():
            raise TypeError("This should not be retried")
        
        with self.assertRaises(TypeError):
            policy.execute(raise_type_error)
        
        self.assertEqual(policy.metrics.total_attempts, 1)

    def test_on_retry_callback(self):
        """测试重试回调"""
        config = RetryPolicyConfig(max_attempts=3, base_delay_seconds=0.01)
        policy = RetryPolicy(config=config, on_retry=lambda a, e: None)
        
        attempts = {"count": 0}
        
        def flaky_func():
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise ValueError("Temporary error")
            return "success"
        
        policy.execute(flaky_func)
        self.assertEqual(attempts["count"], 3)

    def test_decorator_usage(self):
        """测试装饰器用法"""
        config = RetryPolicyConfig(max_attempts=3, base_delay_seconds=0.01)
        policy = RetryPolicy(config=config)
        
        @policy
        def decorated_func():
            return "decorated"
        
        result = decorated_func()
        self.assertEqual(result, "decorated")
        self.assertEqual(policy.metrics.total_successes, 1)

    def test_metrics_summary(self):
        """测试指标摘要"""
        config = RetryPolicyConfig(max_attempts=3, base_delay_seconds=0.01)
        policy = RetryPolicy(config=config)
        
        def success_func():
            return "success"
        
        policy.execute(success_func)
        
        summary = policy.get_metrics_summary()
        self.assertEqual(summary["total_attempts"], 1)
        self.assertEqual(summary["total_successes"], 1)
        self.assertEqual(summary["success_rate"], 1.0)

    def test_reset_metrics(self):
        """测试重置指标"""
        config = RetryPolicyConfig(max_attempts=3, base_delay_seconds=0.01)
        policy = RetryPolicy(config=config)
        
        def fail_func():
            raise ValueError("fail")
        
        try:
            policy.execute(fail_func)
        except:
            pass
        
        self.assertGreater(policy.metrics.total_attempts, 0)
        
        policy.reset_metrics()
        self.assertEqual(policy.metrics.total_attempts, 0)

    def test_metrics_serialization(self):
        """测试指标序列化"""
        metrics = RetryMetrics(
            total_attempts=10,
            total_successes=8,
            total_failures=2,
            total_retries=5
        )
        
        data = metrics.to_dict()
        restored = RetryMetrics.from_dict(data)
        
        self.assertEqual(restored.total_attempts, 10)
        self.assertEqual(restored.total_successes, 8)
        self.assertEqual(restored.total_failures, 2)
        self.assertEqual(restored.total_retries, 5)


class TestRetryContext(unittest.TestCase):
    """测试重试上下文"""

    def test_context_creation(self):
        """测试上下文创建"""
        ctx = RetryContext(max_attempts=3)
        self.assertEqual(ctx.max_attempts, 3)
        self.assertEqual(ctx.current_attempt, 0)

    def test_increment_attempt(self):
        """测试增加尝试次数"""
        ctx = RetryContext(max_attempts=3)
        ctx.increment_attempt()
        self.assertEqual(ctx.current_attempt, 1)
        ctx.increment_attempt()
        self.assertEqual(ctx.current_attempt, 2)

    def test_add_error(self):
        """测试添加错误"""
        ctx = RetryContext()
        ctx.add_error("Error 1")
        ctx.add_error("Error 2")
        self.assertEqual(len(ctx.errors), 2)

    def test_remaining_attempts(self):
        """测试剩余尝试次数"""
        ctx = RetryContext(max_attempts=3)
        self.assertEqual(ctx.get_remaining_attempts(), 3)
        ctx.increment_attempt()
        self.assertEqual(ctx.get_remaining_attempts(), 2)

    def test_is_last_attempt(self):
        """测试是否最后尝试"""
        ctx = RetryContext(max_attempts=3)
        self.assertFalse(ctx.is_last_attempt())
        ctx.current_attempt = 3
        self.assertTrue(ctx.is_last_attempt())


class TestRetryPolicyWithContext(unittest.TestCase):
    """测试带上下文的重试策略"""

    def test_context_provided_to_function(self):
        """测试上下文被传递给函数"""
        config = RetryPolicyConfig(max_attempts=3, base_delay_seconds=0.01)
        policy = RetryPolicyWithContext(config=config)
        
        attempts = {"count": 0}
        
        def func_with_context(ctx, *args, **kwargs):
            # 注意：这里不需要再调用 ctx.increment_attempt()
            # execute_with_context 会自动管理尝试次数
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise ValueError("Temporary error")
            return "success"
        
        result = policy.execute_with_context(
            func_with_context,
            lambda: RetryContext(max_attempts=3)
        )
        
        self.assertEqual(result, "success")
        self.assertEqual(attempts["count"], 3)


if __name__ == "__main__":
    unittest.main()
