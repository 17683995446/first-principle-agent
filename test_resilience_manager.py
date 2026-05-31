import unittest
import time

from first_principle_agent.layers.resilience_manager import (
    ResilienceManager,
    ResilienceManagerConfig,
    ResiliencePreset,
    SystemHealthStatus,
    create_resilience_manager
)


class TestResilienceManager(unittest.TestCase):
    """测试韧性管理器"""

    def test_creation_with_default_preset(self):
        """测试使用默认预设创建"""
        manager = create_resilience_manager()
        
        self.assertIsNotNone(manager.orchestrator)
        self.assertIsNotNone(manager.rate_limiter)
        self.assertIsNotNone(manager.circuit_breaker)
        self.assertIsNotNone(manager.retry_policy)
        self.assertIsNotNone(manager.timeout_manager)
        
        manager.shutdown()

    def test_creation_with_high_availability_preset(self):
        """测试使用高可用预设创建"""
        manager = create_resilience_manager(ResiliencePreset.HIGH_AVAILABILITY)
        
        self.assertEqual(manager.config.preset, ResiliencePreset.HIGH_AVAILABILITY)
        self.assertEqual(manager.config.max_retries, 5)
        self.assertEqual(manager.config.failure_threshold, 3)
        
        manager.shutdown()

    def test_creation_with_high_performance_preset(self):
        """测试使用高性能预设创建"""
        manager = create_resilience_manager(ResiliencePreset.HIGH_PERFORMANCE)
        
        self.assertEqual(manager.config.preset, ResiliencePreset.HIGH_PERFORMANCE)
        self.assertEqual(manager.config.max_retries, 2)
        self.assertEqual(manager.config.default_timeout_seconds, 10.0)
        
        manager.shutdown()

    def test_creation_with_development_preset(self):
        """测试使用开发环境预设创建"""
        manager = create_resilience_manager(ResiliencePreset.DEVELOPMENT)
        
        self.assertEqual(manager.config.preset, ResiliencePreset.DEVELOPMENT)
        self.assertFalse(manager.config.enable_all_strategies)
        self.assertFalse(manager.config.enable_checkpoint)
        
        manager.shutdown()

    def test_successful_execution(self):
        """测试成功执行"""
        manager = create_resilience_manager()
        
        def success_func():
            return "success"
        
        result = manager.execute(success_func)
        self.assertEqual(result, "success")
        
        manager.shutdown()

    def test_fallback_on_failure(self):
        """测试失败时降级"""
        manager = create_resilience_manager()
        
        def fail_func():
            raise ValueError("Always fails")
        
        def fallback_func():
            return "fallback"
        
        result = manager.execute(fail_func, fallback=fallback_func)
        self.assertEqual(result, "fallback")
        
        manager.shutdown()

    def test_decorator_usage(self):
        """测试装饰器用法"""
        manager = create_resilience_manager()
        
        @manager
        def decorated_func():
            return "decorated"
        
        result = decorated_func()
        self.assertEqual(result, "decorated")
        
        manager.shutdown()

    def test_health_status_healthy(self):
        """测试健康状态 - 健康"""
        manager = create_resilience_manager()
        
        def func():
            return "success"
        
        for _ in range(5):
            manager.execute(func)
        
        status = manager.get_health_status()
        
        self.assertEqual(status.overall_health, "healthy")
        self.assertIn("rate_limiter", status.components)
        self.assertIn("circuit_breaker", status.components)
        self.assertIn("orchestrator", status.components)
        
        manager.shutdown()

    def test_get_all_metrics(self):
        """测试获取所有指标"""
        manager = create_resilience_manager()
        
        def func():
            return "success"
        
        manager.execute(func)
        
        metrics = manager.get_all_metrics()
        
        self.assertIn("orchestrator", metrics)
        self.assertEqual(metrics["orchestrator"]["total_executions"], 1)
        
        manager.shutdown()

    def test_reset_all_metrics(self):
        """测试重置所有指标"""
        manager = create_resilience_manager()
        
        def func():
            return "success"
        
        manager.execute(func)
        
        metrics_before = manager.get_all_metrics()
        self.assertEqual(metrics_before["orchestrator"]["total_executions"], 1)
        
        manager.reset_all_metrics()
        
        metrics_after = manager.get_all_metrics()
        self.assertEqual(metrics_after["orchestrator"]["total_executions"], 0)
        
        manager.shutdown()

    def test_config_serialization(self):
        """测试配置序列化"""
        config = ResilienceManagerConfig.from_preset(ResiliencePreset.DEFAULT)
        
        data = config.to_dict()
        
        self.assertEqual(data["preset"], "default")
        self.assertEqual(data["max_retries"], 3)

    def test_config_from_preset(self):
        """测试从预设创建配置"""
        config = ResilienceManagerConfig.from_preset(ResiliencePreset.HIGH_AVAILABILITY)
        
        self.assertEqual(config.preset, ResiliencePreset.HIGH_AVAILABILITY)
        self.assertEqual(config.max_retries, 5)
        self.assertEqual(config.retry_base_delay, 0.5)

    def test_context_manager(self):
        """测试上下文管理器"""
        with create_resilience_manager() as manager:
            def func():
                return "success"
            
            result = func()
            self.assertEqual(result, "success")


class TestSystemHealthStatus(unittest.TestCase):
    """测试系统健康状态"""

    def test_health_status_serialization(self):
        """测试健康状态序列化"""
        status = SystemHealthStatus(
            overall_health="healthy",
            timestamp=time.time(),
            components={"test": {}},
            recommendations=["Test recommendation"]
        )
        
        data = status.to_dict()
        
        self.assertEqual(data["overall_health"], "healthy")
        self.assertIn("test", data["components"])
        self.assertEqual(len(data["recommendations"]), 1)


if __name__ == "__main__":
    unittest.main()
