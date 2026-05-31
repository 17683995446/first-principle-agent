import unittest
import time

from first_principle_agent.layers.resilience_orchestrator import (
    ResilienceOrchestrator,
    OrchestratorConfig,
    OrchestratorMetrics,
    ExecutionContext,
    ResilienceStrategy,
    ExecutionStage,
    create_default_orchestrator
)
from first_principle_agent.layers.rate_limiter import (
    RateLimiter, RateLimitConfig, RateLimitStrategy
)
from first_principle_agent.layers.circuit_breaker import (
    CircuitBreaker, CircuitBreakerConfig, CircuitState
)
from first_principle_agent.layers.retry_policy import (
    RetryPolicy, RetryPolicyConfig, BackoffStrategy
)
from first_principle_agent.layers.timeout_manager import (
    TimeoutManager, TimeoutConfig, TimeoutStrategy
)


class TestResilienceOrchestrator(unittest.TestCase):
    """测试韧性编排器"""

    def test_successful_execution_without_strategies(self):
        """测试无策略的成功执行"""
        config = OrchestratorConfig(enabled_strategies=[])
        orchestrator = ResilienceOrchestrator(config=config)
        
        def success_func():
            return "success"
        
        result = orchestrator.execute(success_func)
        self.assertEqual(result, "success")
        self.assertEqual(orchestrator.metrics.total_executions, 1)
        self.assertEqual(orchestrator.metrics.successful_executions, 1)
        
        orchestrator.shutdown()

    def test_successful_execution_with_all_strategies(self):
        """测试所有策略的成功执行"""
        orchestrator = create_default_orchestrator()
        
        def success_func():
            return "success"
        
        result = orchestrator.execute(success_func)
        self.assertEqual(result, "success")
        
        status = orchestrator.get_status()
        self.assertTrue(status["components"]["rate_limiter"])
        self.assertTrue(status["components"]["circuit_breaker"])
        
        orchestrator.shutdown()

    def test_retry_strategy_integration(self):
        """测试重试策略集成"""
        retry_config = RetryPolicyConfig(
            max_attempts=3,
            base_delay_seconds=0.01
        )
        retry_policy = RetryPolicy(config=retry_config)
        
        config = OrchestratorConfig(
            enabled_strategies=[ResilienceStrategy.RETRY]
        )
        orchestrator = ResilienceOrchestrator(
            config=config,
            retry_policy=retry_policy
        )
        
        attempts = {"count": 0}
        
        def flaky_func():
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise ValueError("Temporary error")
            return "success"
        
        result = orchestrator.execute(flaky_func)
        self.assertEqual(result, "success")
        self.assertEqual(attempts["count"], 3)
        
        orchestrator.shutdown()

    def test_circuit_breaker_integration(self):
        """测试熔断器集成"""
        cb_config = CircuitBreakerConfig(
            failure_threshold=2,
            success_threshold=2,
            timeout_seconds=30.0
        )
        circuit_breaker = CircuitBreaker(name="test", config=cb_config)
        
        config = OrchestratorConfig(
            enabled_strategies=[ResilienceStrategy.CIRCUIT_BREAK]
        )
        orchestrator = ResilienceOrchestrator(
            config=config,
            circuit_breaker=circuit_breaker
        )
        
        def fail_func():
            raise ValueError("Failure")
        
        with self.assertRaises(Exception):
            orchestrator.execute(fail_func)
        with self.assertRaises(Exception):
            orchestrator.execute(fail_func)
        
        self.assertEqual(circuit_breaker.state, CircuitState.OPEN)
        
        orchestrator.shutdown()

    def test_rate_limiter_integration(self):
        """测试限流器集成"""
        rate_config = RateLimitConfig(
            strategy=RateLimitStrategy.TOKEN_BUCKET,
            max_tokens=2,
            refill_rate=100.0
        )
        rate_limiter = RateLimiter(config=rate_config)
        
        config = OrchestratorConfig(
            enabled_strategies=[ResilienceStrategy.RATE_LIMIT]
        )
        orchestrator = ResilienceOrchestrator(
            config=config,
            rate_limiter=rate_limiter
        )
        
        def quick_func():
            return "success"
        
        result1 = orchestrator.execute(quick_func)
        result2 = orchestrator.execute(quick_func)
        
        self.assertEqual(result1, "success")
        self.assertEqual(result2, "success")
        
        with self.assertRaises(Exception):
            orchestrator.execute(quick_func)
        
        orchestrator.shutdown()

    def test_timeout_integration(self):
        """测试超时集成"""
        timeout_config = TimeoutConfig(
            default_timeout_seconds=0.1,
            strategy=TimeoutStrategy.FAST_FAIL
        )
        timeout_manager = TimeoutManager(config=timeout_config)
        
        config = OrchestratorConfig(
            enabled_strategies=[ResilienceStrategy.TIMEOUT]
        )
        orchestrator = ResilienceOrchestrator(
            config=config,
            timeout_manager=timeout_manager
        )
        
        def slow_func():
            time.sleep(1)
            return "success"
        
        with self.assertRaises(Exception):
            orchestrator.execute(slow_func)
        
        orchestrator.shutdown()

    def test_fallback_function(self):
        """测试降级函数"""
        orchestrator = create_default_orchestrator()
        
        def fail_func():
            raise ValueError("Always fails")
        
        def fallback_func():
            return "fallback"
        
        result = orchestrator.execute(fail_func, fallback=fallback_func)
        self.assertEqual(result, "fallback")
        
        orchestrator.shutdown()

    def test_logging_callback(self):
        """测试日志回调"""
        log_messages = []
        
        def logger(message):
            log_messages.append(message)
        
        orchestrator = create_default_orchestrator()
        orchestrator.set_logger(logger)
        
        def func():
            return "test"
        
        orchestrator.execute(func)
        
        self.assertEqual(len(log_messages), 0)
        
        orchestrator.shutdown()

    def test_metrics_collection(self):
        """测试指标收集"""
        orchestrator = create_default_orchestrator()
        
        def func():
            return "success"
        
        for _ in range(5):
            orchestrator.execute(func)
        
        self.assertEqual(orchestrator.metrics.total_executions, 5)
        self.assertEqual(orchestrator.metrics.successful_executions, 5)
        
        orchestrator.shutdown()

    def test_reset_metrics(self):
        """测试重置指标"""
        orchestrator = create_default_orchestrator()
        
        def func():
            return "success"
        
        orchestrator.execute(func)
        self.assertEqual(orchestrator.metrics.total_executions, 1)
        
        orchestrator.reset_metrics()
        self.assertEqual(orchestrator.metrics.total_executions, 0)
        
        orchestrator.shutdown()

    def test_execution_context(self):
        """测试执行上下文"""
        orchestrator = create_default_orchestrator()
        
        def func():
            return "success"
        
        orchestrator.execute(func)
        
        recent = orchestrator.metrics.recent_executions
        self.assertEqual(len(recent), 1)
        
        context = recent[0]
        self.assertTrue(context.success)
        self.assertTrue(context.execution_time is not None)
        
        orchestrator.shutdown()

    def test_stage_history(self):
        """测试阶段历史"""
        orchestrator = create_default_orchestrator()
        
        def func():
            return "success"
        
        orchestrator.execute(func)
        
        context = orchestrator.metrics.recent_executions[0]
        stages = [h["stage"] for h in context.stage_history]
        
        self.assertIn("before", stages)
        self.assertIn("after", stages)
        self.assertIn("final", stages)
        
        orchestrator.shutdown()

    def test_decorator_usage(self):
        """测试装饰器用法"""
        orchestrator = create_default_orchestrator()
        
        @orchestrator
        def decorated_func():
            return "decorated"
        
        result = decorated_func()
        self.assertEqual(result, "decorated")
        
        orchestrator.shutdown()

    def test_custom_strategy_order(self):
        """测试自定义策略顺序"""
        config = OrchestratorConfig(
            enabled_strategies=[ResilienceStrategy.RETRY, ResilienceStrategy.CIRCUIT_BREAK],
            execution_order=[ResilienceStrategy.CIRCUIT_BREAK, ResilienceStrategy.RETRY]
        )
        orchestrator = ResilienceOrchestrator(config=config)
        
        self.assertEqual(config.execution_order[0], ResilienceStrategy.CIRCUIT_BREAK)
        self.assertEqual(config.execution_order[1], ResilienceStrategy.RETRY)
        
        orchestrator.shutdown()


class TestOrchestratorMetrics(unittest.TestCase):
    """测试编排器指标"""

    def test_metrics_serialization(self):
        """测试指标序列化"""
        metrics = OrchestratorMetrics(
            total_executions=10,
            successful_executions=8,
            failed_executions=2,
            total_retries=5
        )
        
        data = metrics.to_dict()
        restored = OrchestratorMetrics.from_dict(data)
        
        self.assertEqual(restored.total_executions, 10)
        self.assertEqual(restored.successful_executions, 8)
        self.assertEqual(restored.failed_executions, 2)
        self.assertEqual(restored.total_retries, 5)


class TestExecutionContext(unittest.TestCase):
    """测试执行上下文"""

    def test_context_serialization(self):
        """测试上下文序列化"""
        context = ExecutionContext(
            operation_name="test",
            start_time=time.time(),
            success=True
        )
        
        data = context.to_dict()
        restored = ExecutionContext.from_dict(data)
        
        self.assertEqual(restored.operation_name, "test")
        self.assertTrue(restored.success)

    def test_record_stage(self):
        """测试记录阶段"""
        context = ExecutionContext(
            operation_name="test",
            start_time=time.time()
        )
        
        context.record_stage(ExecutionStage.BEFORE)
        context.record_stage(ExecutionStage.AFTER)
        
        self.assertEqual(len(context.stage_history), 2)


class TestOrchestratorConfig(unittest.TestCase):
    """测试编排器配置"""

    def test_config_serialization(self):
        """测试配置序列化"""
        config = OrchestratorConfig(
            enabled_strategies=[ResilienceStrategy.RETRY],
            execution_order=[ResilienceStrategy.RETRY],
            enable_logging=False
        )
        
        data = config.to_dict()
        restored = OrchestratorConfig.from_dict(data)
        
        self.assertFalse(restored.enable_logging)


if __name__ == "__main__":
    unittest.main()
