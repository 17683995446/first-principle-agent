import unittest
import time
from first_principle_agent.layers.rate_limiter import (
    RateLimiter,
    RateLimitConfig,
    DistributedRateLimiter,
    RateLimitStrategy,
    RateLimitMetrics
)


class TestRateLimiter(unittest.TestCase):
    """测试限流器"""

    def test_token_bucket_allow(self):
        """测试令牌桶算法 - 正常允许请求"""
        config = RateLimitConfig(
            strategy=RateLimitStrategy.TOKEN_BUCKET,
            max_tokens=10,
            refill_rate=10.0
        )
        limiter = RateLimiter(config)
        
        # 初始应该有足够的令牌
        for i in range(5):
            self.assertTrue(limiter.allow())
        
        self.assertEqual(limiter.metrics.allowed_requests, 5)

    def test_token_bucket_reject(self):
        """测试令牌桶算法 - 请求被拒绝"""
        config = RateLimitConfig(
            strategy=RateLimitStrategy.TOKEN_BUCKET,
            max_tokens=3,
            refill_rate=10.0
        )
        limiter = RateLimiter(config)
        
        # 消耗所有令牌
        for i in range(3):
            self.assertTrue(limiter.allow())
        
        # 第4次应该被拒绝
        self.assertFalse(limiter.allow())
        self.assertEqual(limiter.metrics.rejected_requests, 1)

    def test_token_bucket_refill(self):
        """测试令牌桶算法 - 令牌自动补充"""
        config = RateLimitConfig(
            strategy=RateLimitStrategy.TOKEN_BUCKET,
            max_tokens=5,
            refill_rate=10.0
        )
        limiter = RateLimiter(config)
        
        # 消耗所有令牌
        for i in range(5):
            limiter.allow()
        
        # 等待令牌补充
        time.sleep(0.2)
        
        # 应该又可以请求了
        self.assertTrue(limiter.allow())

    def test_leaky_bucket_allow(self):
        """测试漏桶算法 - 正常允许请求"""
        config = RateLimitConfig(
            strategy=RateLimitStrategy.LEAKY_BUCKET,
            capacity=5,
            leak_rate=10.0
        )
        limiter = RateLimiter(config)
        
        for i in range(5):
            self.assertTrue(limiter.allow())

    def test_leaky_bucket_reject(self):
        """测试漏桶算法 - 请求被拒绝"""
        config = RateLimitConfig(
            strategy=RateLimitStrategy.LEAKY_BUCKET,
            capacity=3,
            leak_rate=1.0
        )
        limiter = RateLimiter(config)
        
        # 填满桶
        for i in range(3):
            self.assertTrue(limiter.allow())
        
        # 第4次应该被拒绝
        self.assertFalse(limiter.allow())

    def test_fixed_window_allow(self):
        """测试固定窗口算法 - 正常允许请求"""
        config = RateLimitConfig(
            strategy=RateLimitStrategy.FIXED_WINDOW,
            window_seconds=1.0,
            max_requests=5
        )
        limiter = RateLimiter(config)
        
        for i in range(5):
            self.assertTrue(limiter.allow())

    def test_fixed_window_reject(self):
        """测试固定窗口算法 - 请求被拒绝"""
        config = RateLimitConfig(
            strategy=RateLimitStrategy.FIXED_WINDOW,
            window_seconds=10.0,
            max_requests=3
        )
        limiter = RateLimiter(config)
        
        for i in range(3):
            self.assertTrue(limiter.allow())
        
        self.assertFalse(limiter.allow())

    def test_fixed_window_reset(self):
        """测试固定窗口算法 - 窗口切换重置"""
        config = RateLimitConfig(
            strategy=RateLimitStrategy.FIXED_WINDOW,
            window_seconds=0.1,
            max_requests=3
        )
        limiter = RateLimiter(config)
        
        for i in range(3):
            limiter.allow()
        
        self.assertFalse(limiter.allow())
        
        # 等待窗口切换
        time.sleep(0.15)
        
        # 应该又可以请求了
        self.assertTrue(limiter.allow())

    def test_sliding_window_allow(self):
        """测试滑动窗口算法 - 正常允许请求"""
        config = RateLimitConfig(
            strategy=RateLimitStrategy.SLIDING_WINDOW,
            window_seconds=1.0,
            max_requests=5
        )
        limiter = RateLimiter(config)
        
        for i in range(5):
            self.assertTrue(limiter.allow())

    def test_sliding_window_reject(self):
        """测试滑动窗口算法 - 请求被拒绝"""
        config = RateLimitConfig(
            strategy=RateLimitStrategy.SLIDING_WINDOW,
            window_seconds=10.0,
            max_requests=3
        )
        limiter = RateLimiter(config)
        
        for i in range(3):
            self.assertTrue(limiter.allow())
        
        self.assertFalse(limiter.allow())

    def test_decorator_usage(self):
        """测试装饰器用法"""
        config = RateLimitConfig(
            strategy=RateLimitStrategy.TOKEN_BUCKET,
            max_tokens=5,
            refill_rate=10.0
        )
        limiter = RateLimiter(config)
        
        call_count = 0
        
        @limiter
        def test_func():
            nonlocal call_count
            call_count += 1
            return "ok"
        
        for i in range(5):
            test_func()
        
        self.assertEqual(call_count, 5)

    def test_execute_function(self):
        """测试执行受保护的函数"""
        config = RateLimitConfig(
            strategy=RateLimitStrategy.TOKEN_BUCKET,
            max_tokens=2,
            refill_rate=10.0
        )
        limiter = RateLimiter(config)
        
        def func():
            return "success"
        
        # 前两次应该成功
        self.assertEqual(limiter.execute(func), "success")
        self.assertEqual(limiter.execute(func), "success")
        
        # 第三次应该被限流，返回None
        self.assertIsNone(limiter.execute(func))

    def test_on_reject_callback(self):
        """测试被限流时的回调函数"""
        callback_called = False
        
        def on_reject():
            nonlocal callback_called
            callback_called = True
        
        config = RateLimitConfig(
            strategy=RateLimitStrategy.TOKEN_BUCKET,
            max_tokens=1,
            refill_rate=10.0
        )
        limiter = RateLimiter(config, on_reject=on_reject)
        
        # 第一次允许
        limiter.allow()
        
        # 第二次被拒绝，回调应该被调用
        limiter.allow()
        self.assertTrue(callback_called)

    def test_reset(self):
        """测试重置限流器"""
        config = RateLimitConfig(
            strategy=RateLimitStrategy.TOKEN_BUCKET,
            max_tokens=3,
            refill_rate=10.0
        )
        limiter = RateLimiter(config)
        
        # 消耗所有令牌
        limiter.allow()
        limiter.allow()
        limiter.allow()
        
        self.assertFalse(limiter.allow())
        
        # 重置
        limiter.reset()
        
        # 应该又可以请求了
        self.assertTrue(limiter.allow())

    def test_reset_metrics(self):
        """测试重置指标"""
        config = RateLimitConfig(
            strategy=RateLimitStrategy.TOKEN_BUCKET,
            max_tokens=10,
            refill_rate=10.0
        )
        limiter = RateLimiter(config)
        
        limiter.allow()
        limiter.allow()
        
        self.assertEqual(limiter.metrics.total_requests, 2)
        
        limiter.reset_metrics()
        
        self.assertEqual(limiter.metrics.total_requests, 0)

    def test_get_available_tokens(self):
        """测试获取可用令牌数"""
        config = RateLimitConfig(
            strategy=RateLimitStrategy.TOKEN_BUCKET,
            max_tokens=10,
            refill_rate=10.0
        )
        limiter = RateLimiter(config)
        
        self.assertEqual(limiter.get_available_tokens(), 10.0)
        
        limiter.allow()
        
        self.assertLess(limiter.get_available_tokens(), 10.0)

    def test_get_rejection_rate(self):
        """测试获取拒绝率"""
        config = RateLimitConfig(
            strategy=RateLimitStrategy.TOKEN_BUCKET,
            max_tokens=2,
            refill_rate=10.0
        )
        limiter = RateLimiter(config)
        
        limiter.allow()  # 允许
        limiter.allow()  # 允许
        limiter.allow()  # 拒绝
        
        self.assertEqual(limiter.get_rejection_rate(), 1.0 / 3.0)

    def test_get_status(self):
        """测试获取限流器状态"""
        config = RateLimitConfig(
            strategy=RateLimitStrategy.TOKEN_BUCKET,
            max_tokens=10,
            refill_rate=10.0
        )
        limiter = RateLimiter(config)
        
        limiter.allow()
        
        status = limiter.get_status()
        
        self.assertEqual(status["strategy"], "token_bucket")
        self.assertIn("metrics", status)
        self.assertIn("token_bucket", status)
        self.assertEqual(status["token_bucket"]["max_tokens"], 10)

    def test_metrics_serialization(self):
        """测试指标序列化"""
        metrics = RateLimitMetrics(
            total_requests=100,
            allowed_requests=80,
            rejected_requests=20
        )
        
        data = metrics.to_dict()
        restored = RateLimitMetrics.from_dict(data)
        
        self.assertEqual(restored.total_requests, 100)
        self.assertEqual(restored.allowed_requests, 80)
        self.assertEqual(restored.rejected_requests, 20)

    def test_config_serialization(self):
        """测试配置序列化"""
        config = RateLimitConfig(
            strategy=RateLimitStrategy.FIXED_WINDOW,
            max_requests=50,
            window_seconds=30.0
        )
        
        data = config.to_dict()
        restored = RateLimitConfig.from_dict(data)
        
        self.assertEqual(restored.strategy, RateLimitStrategy.FIXED_WINDOW)
        self.assertEqual(restored.max_requests, 50)
        self.assertEqual(restored.window_seconds, 30.0)


class TestDistributedRateLimiter(unittest.TestCase):
    """测试分布式限流器"""

    def test_basic_functionality(self):
        """测试分布式限流器基础功能"""
        config = RateLimitConfig(
            strategy=RateLimitStrategy.TOKEN_BUCKET,
            max_tokens=5,
            refill_rate=10.0
        )
        limiter = DistributedRateLimiter(config)
        
        for i in range(5):
            self.assertTrue(limiter.allow())
        
        self.assertFalse(limiter.allow())


if __name__ == "__main__":
    unittest.main()
