import unittest
import time
from first_principle_agent.layers.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    CircuitMetrics,
    CircuitBreakerOpenError
)


class TestCircuitBreaker(unittest.TestCase):
    """测试熔断器"""

    def test_initial_state_is_closed(self):
        """测试初始状态为closed"""
        breaker = CircuitBreaker("test")
        self.assertEqual(breaker.state, CircuitState.CLOSED)

    def test_successful_execution(self):
        """测试成功执行"""
        breaker = CircuitBreaker("test")
        
        def success_func():
            return "success"
        
        result = breaker.execute(success_func)
        self.assertEqual(result, "success")
        self.assertEqual(breaker.metrics.success_count, 1)
        self.assertEqual(breaker.metrics.consecutive_successes, 1)

    def test_failure_counting(self):
        """测试失败计数"""
        breaker = CircuitBreaker("test")
        
        def fail_func():
            raise ValueError("test error")
        
        with self.assertRaises(ValueError):
            breaker.execute(fail_func)
        
        self.assertEqual(breaker.metrics.failure_count, 1)
        self.assertEqual(breaker.metrics.consecutive_failures, 1)

    def test_circuit_opens_after_threshold(self):
        """测试达到失败阈值后熔断器打开"""
        config = CircuitBreakerConfig(failure_threshold=3, timeout_seconds=60)
        breaker = CircuitBreaker("test", config=config)
        
        def fail_func():
            raise ValueError("test error")
        
        # 前3次失败
        for i in range(3):
            with self.assertRaises(ValueError):
                breaker.execute(fail_func)
        
        # 第4次应该直接抛出CircuitBreakerOpenError
        with self.assertRaises(CircuitBreakerOpenError):
            breaker.execute(fail_func)
        
        self.assertEqual(breaker.state, CircuitState.OPEN)

    def test_half_open_after_timeout(self):
        """测试超时后进入半打开状态"""
        config = CircuitBreakerConfig(failure_threshold=2, timeout_seconds=0.1)
        breaker = CircuitBreaker("test", config=config)
        
        def fail_func():
            raise ValueError("test error")
        
        # 让熔断器打开
        for i in range(2):
            with self.assertRaises(ValueError):
                breaker.execute(fail_func)
        
        self.assertEqual(breaker.state, CircuitState.OPEN)
        
        # 等待超时
        time.sleep(0.2)
        
        # 应该进入半打开状态
        self.assertEqual(breaker.state, CircuitState.HALF_OPEN)

    def test_half_open_success_closes_circuit(self):
        """测试半打开状态下成功后关闭"""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            success_threshold=2,
            timeout_seconds=0.1
        )
        breaker = CircuitBreaker("test", config=config)
        
        def fail_func():
            raise ValueError("test error")
        
        def success_func():
            return "success"
        
        # 让熔断器打开
        for i in range(2):
            with self.assertRaises(ValueError):
                breaker.execute(fail_func)
        
        self.assertEqual(breaker.state, CircuitState.OPEN)
        
        # 等待超时
        time.sleep(0.2)
        self.assertEqual(breaker.state, CircuitState.HALF_OPEN)
        
        # 连续成功
        breaker.execute(success_func)
        self.assertEqual(breaker.state, CircuitState.HALF_OPEN)
        breaker.execute(success_func)
        
        # 应该关闭
        self.assertEqual(breaker.state, CircuitState.CLOSED)

    def test_half_open_failure_reopens_circuit(self):
        """测试半打开状态下失败后重新打开"""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            timeout_seconds=0.1
        )
        breaker = CircuitBreaker("test", config=config)
        
        def fail_func():
            raise ValueError("test error")
        
        # 让熔断器打开
        for i in range(2):
            with self.assertRaises(ValueError):
                breaker.execute(fail_func)
        
        self.assertEqual(breaker.state, CircuitState.OPEN)
        
        # 等待超时
        time.sleep(0.2)
        self.assertEqual(breaker.state, CircuitState.HALF_OPEN)
        
        # 再次失败
        with self.assertRaises(ValueError):
            breaker.execute(fail_func)
        
        # 应该重新打开
        self.assertEqual(breaker.state, CircuitState.OPEN)

    def test_fallback_function(self):
        """测试降级函数"""
        def fallback():
            return "fallback"
        
        breaker = CircuitBreaker("test", fallback=fallback)
        breaker.force_open()
        
        result = breaker.execute(lambda: "normal")
        self.assertEqual(result, "fallback")

    def test_decorator_usage(self):
        """测试装饰器用法"""
        breaker = CircuitBreaker("test_decorator")
        
        @breaker
        def decorated_func():
            return "decorated"
        
        result = decorated_func()
        self.assertEqual(result, "decorated")
        self.assertEqual(breaker.metrics.success_count, 1)

    def test_force_open_and_close(self):
        """测试强制打开和关闭"""
        breaker = CircuitBreaker("test")
        
        breaker.force_open()
        self.assertEqual(breaker.state, CircuitState.OPEN)
        
        breaker.force_close()
        self.assertEqual(breaker.state, CircuitState.CLOSED)

    def test_reset(self):
        """测试重置"""
        breaker = CircuitBreaker("test")
        
        def fail_func():
            raise ValueError("test error")
        
        # 积累一些失败
        with self.assertRaises(ValueError):
            breaker.execute(fail_func)
        
        breaker.reset()
        
        self.assertEqual(breaker.state, CircuitState.CLOSED)
        self.assertEqual(breaker.metrics.total_requests, 0)
        self.assertEqual(breaker.metrics.failure_count, 0)

    def test_get_state_info(self):
        """测试获取状态信息"""
        breaker = CircuitBreaker("test")
        info = breaker.get_state_info()
        
        self.assertEqual(info["name"], "test")
        self.assertEqual(info["state"], "closed")
        self.assertIn("metrics", info)
        self.assertIn("config", info)

    def test_metrics_serialization(self):
        """测试指标序列化"""
        metrics = CircuitMetrics(
            total_requests=10,
            success_count=8,
            failure_count=2,
            slow_call_count=1
        )
        
        data = metrics.to_dict()
        restored = CircuitMetrics.from_dict(data)
        
        self.assertEqual(restored.total_requests, 10)
        self.assertEqual(restored.success_count, 8)
        self.assertEqual(restored.failure_count, 2)


if __name__ == "__main__":
    unittest.main()
