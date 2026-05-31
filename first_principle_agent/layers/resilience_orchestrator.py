from enum import Enum
import time
import threading
from typing import Callable, Optional, Any, Dict, List, Set, Tuple
from dataclasses import dataclass, field
from collections import OrderedDict

from first_principle_agent.core.base import JSONSerializable
from first_principle_agent.layers.circuit_breaker import (
    CircuitBreaker, CircuitBreakerConfig, CircuitState
)
from first_principle_agent.layers.retry_policy import (
    RetryPolicy, RetryPolicyConfig, BackoffStrategy
)
from first_principle_agent.layers.rate_limiter import (
    RateLimiter, RateLimitConfig, RateLimitStrategy
)
from first_principle_agent.layers.timeout_manager import (
    TimeoutManager, TimeoutConfig, TimeoutStrategy
)
from first_principle_agent.layers.rollback_manager import (
    RollbackManager, RollbackTransaction
)


class ExecutionStage(Enum):
    """执行阶段"""
    BEFORE = "before"  # 执行前
    MAIN = "main"  # 主执行
    AFTER = "after"  # 执行后
    ERROR = "error"  # 错误处理
    FINAL = "final"  # 最终阶段


class ResilienceStrategy(Enum):
    """韧性策略"""
    RATE_LIMIT = "rate_limit"  # 限流
    CIRCUIT_BREAK = "circuit_break"  # 熔断
    RETRY = "retry"  # 重试
    TIMEOUT = "timeout"  # 超时
    ROLLBACK = "rollback"  # 回滚


@dataclass
class OrchestratorConfig(JSONSerializable):
    """编排器配置"""
    enabled_strategies: List[ResilienceStrategy] = field(
        default_factory=lambda: [
            ResilienceStrategy.RATE_LIMIT,
            ResilienceStrategy.CIRCUIT_BREAK,
            ResilienceStrategy.RETRY,
            ResilienceStrategy.TIMEOUT
        ]
    )
    execution_order: List[ResilienceStrategy] = field(
        default_factory=lambda: [
            ResilienceStrategy.RATE_LIMIT,
            ResilienceStrategy.CIRCUIT_BREAK,
            ResilienceStrategy.RETRY,
            ResilienceStrategy.TIMEOUT,
            ResilienceStrategy.ROLLBACK
        ]
    )
    enable_logging: bool = True
    enable_metrics: bool = True

    def to_dict(self) -> Dict:
        return {
            "enabled_strategies": [s.value for s in self.enabled_strategies],
            "execution_order": [s.value for s in self.execution_order],
            "enable_logging": self.enable_logging,
            "enable_metrics": self.enable_metrics
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "OrchestratorConfig":
        return cls(
            enabled_strategies=[
                ResilienceStrategy(s) for s in data.get("enabled_strategies", [])
            ],
            execution_order=[
                ResilienceStrategy(s) for s in data.get("execution_order", [])
            ],
            enable_logging=data.get("enable_logging", True),
            enable_metrics=data.get("enable_metrics", True)
        )


@dataclass
class ExecutionContext(JSONSerializable):
    """执行上下文"""
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    execution_time: Optional[float] = None
    success: bool = True
    error: Optional[str] = None
    error_type: Optional[str] = None
    retry_count: int = 0
    stage_history: List[Dict] = field(default_factory=list)
    circuit_state: Optional[str] = None
    final_result: Any = None
    metrics: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "operation_name": self.operation_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "execution_time": self.execution_time,
            "success": self.success,
            "error": self.error,
            "error_type": self.error_type,
            "retry_count": self.retry_count,
            "stage_history": self.stage_history,
            "circuit_state": self.circuit_state,
            "metrics": self.metrics
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ExecutionContext":
        return cls(**data)

    def record_stage(self, stage: ExecutionStage, details: Dict = None):
        """记录执行阶段"""
        self.stage_history.append({
            "stage": stage.value,
            "timestamp": time.time(),
            "details": details or {}
        })


@dataclass
class OrchestratorMetrics(JSONSerializable):
    """编排器指标"""
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_retries: int = 0
    circuit_breaks: int = 0
    rate_limits: int = 0
    timeouts: int = 0
    rollbacks: int = 0
    average_execution_time: float = 0.0
    total_execution_time: float = 0.0
    strategy_stats: Dict[str, int] = field(default_factory=dict)
    recent_executions: List[ExecutionContext] = field(default_factory=list)
    max_recent_executions: int = 100

    def to_dict(self) -> Dict:
        return {
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "failed_executions": self.failed_executions,
            "total_retries": self.total_retries,
            "circuit_breaks": self.circuit_breaks,
            "rate_limits": self.rate_limits,
            "timeouts": self.timeouts,
            "rollbacks": self.rollbacks,
            "average_execution_time": self.average_execution_time,
            "total_execution_time": self.total_execution_time,
            "strategy_stats": self.strategy_stats
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "OrchestratorMetrics":
        return cls(**data)

    def record_execution(self, context: ExecutionContext):
        """记录执行"""
        self.total_executions += 1
        if context.success:
            self.successful_executions += 1
        else:
            self.failed_executions += 1
        
        if context.execution_time:
            self.total_execution_time += context.execution_time
            self.average_execution_time = (
                self.total_execution_time / self.total_executions
            )
        
        self.recent_executions.append(context)
        if len(self.recent_executions) > self.max_recent_executions:
            self.recent_executions.pop(0)

    def increment_strategy(self, strategy: ResilienceStrategy):
        """增加策略计数"""
        key = strategy.value
        self.strategy_stats[key] = self.strategy_stats.get(key, 0) + 1


class ResilienceOrchestrator:
    """韧性编排器 - 整合多种韧性策略"""

    def __init__(
        self,
        config: Optional[OrchestratorConfig] = None,
        rate_limiter: Optional[RateLimiter] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        retry_policy: Optional[RetryPolicy] = None,
        timeout_manager: Optional[TimeoutManager] = None,
        rollback_manager: Optional[RollbackManager] = None
    ):
        """
        初始化韧性编排器
        
        Args:
            config: 编排器配置
            rate_limiter: 限流器
            circuit_breaker: 熔断器
            retry_policy: 重试策略
            timeout_manager: 超时管理器
            rollback_manager: 回滚管理器
        """
        self.config = config or OrchestratorConfig()
        self._lock = threading.RLock()
        self._metrics = OrchestratorMetrics()
        self._logger: Optional[Callable] = None
        
        self.rate_limiter = rate_limiter
        self.circuit_breaker = circuit_breaker
        self.retry_policy = retry_policy
        self.timeout_manager = timeout_manager
        self.rollback_manager = rollback_manager

    @property
    def metrics(self) -> OrchestratorMetrics:
        """获取编排器指标"""
        return self._metrics

    def set_logger(self, logger: Callable):
        """设置日志回调"""
        self._logger = logger

    def _log(self, message: str, level: str = "INFO"):
        """记录日志"""
        if self._logger:
            self._logger(f"[{level}] {message}")
        elif self.config.enable_logging:
            print(f"[{level}] {message}")

    def execute(
        self,
        func: Callable,
        operation_name: Optional[str] = None,
        rollback_func: Optional[Callable] = None,
        fallback: Optional[Callable] = None,
        *args,
        **kwargs
    ) -> Any:
        """
        执行带多种韧性策略保护的函数
        
        Args:
            func: 要执行的函数
            operation_name: 操作名称
            rollback_func: 回滚函数
            fallback: 降级函数
            *args: 函数位置参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果
        """
        start_time = time.time()
        context = ExecutionContext(
            operation_name=operation_name or getattr(func, '__name__', 'unknown'),
            start_time=start_time
        )
        
        context.record_stage(ExecutionStage.BEFORE)
        result = None
        error = None
        
        try:
            result = self._execute_with_strategies(
                func, context, rollback_func, fallback, *args, **kwargs
            )
            context.final_result = result
            context.record_stage(ExecutionStage.AFTER)
            
        except Exception as e:
            error = e
            context.error = str(e)
            context.error_type = type(e).__name__
            context.success = False
            context.record_stage(ExecutionStage.ERROR, {"error": str(e)})
            
            if rollback_func and ResilienceStrategy.ROLLBACK in self.config.enabled_strategies:
                self._execute_rollback(context, rollback_func, *args, **kwargs)
            
            if fallback:
                result = fallback(*args, **kwargs)
                context.final_result = result
                context.success = True
            else:
                raise
            
        finally:
            end_time = time.time()
            context.end_time = end_time
            context.execution_time = end_time - start_time
            context.record_stage(ExecutionStage.FINAL)
            
            if self.config.enable_metrics:
                self._metrics.record_execution(context)
            
        return result

    def _execute_with_strategies(
        self,
        func: Callable,
        context: ExecutionContext,
        rollback_func: Optional[Callable],
        fallback: Optional[Callable],
        *args,
        **kwargs
    ) -> Any:
        """按顺序执行多种韧性策略"""
        
        enabled_strategies = set(self.config.enabled_strategies)
        execution_order = [
            s for s in self.config.execution_order
            if s in enabled_strategies
        ]
        
        current_func = func
        rollback_transaction = None
        
        for strategy in execution_order:
            current_func = self._wrap_with_strategy(
                strategy, current_func, context, fallback
            )
            
            if strategy == ResilienceStrategy.ROLLBACK and rollback_func:
                if self.rollback_manager:
                    rollback_transaction = self.rollback_manager.begin_transaction()
        
        result = current_func(*args, **kwargs)
        
        if rollback_transaction:
            rollback_transaction.commit()
            
        return result

    def _wrap_with_strategy(
        self,
        strategy: ResilienceStrategy,
        func: Callable,
        context: ExecutionContext,
        fallback: Optional[Callable]
    ) -> Callable:
        """用策略包装函数"""
        
        if strategy == ResilienceStrategy.RATE_LIMIT:
            return self._wrap_rate_limit(func, context)
        
        elif strategy == ResilienceStrategy.CIRCUIT_BREAK:
            return self._wrap_circuit_break(func, context)
        
        elif strategy == ResilienceStrategy.RETRY:
            return self._wrap_retry(func, context)
        
        elif strategy == ResilienceStrategy.TIMEOUT:
            return self._wrap_timeout(func, context)
        
        elif strategy == ResilienceStrategy.ROLLBACK:
            return self._wrap_rollback(func, context)
        
        return func

    def _wrap_rate_limit(self, func: Callable, context: ExecutionContext) -> Callable:
        """包装限流器"""
        def wrapper(*args, **kwargs):
            if not self.rate_limiter:
                return func(*args, **kwargs)
            
            allowed = self.rate_limiter.allow()
            if not allowed:
                context.circuit_state = "RATE_LIMITED"
                self._metrics.increment_strategy(ResilienceStrategy.RATE_LIMIT)
                self._metrics.rate_limits += 1
                self._log(f"Rate limit exceeded for {context.operation_name}", "WARN")
                raise Exception("Rate limit exceeded")
            
            return func(*args, **kwargs)
        
        return wrapper

    def _wrap_circuit_break(self, func: Callable, context: ExecutionContext) -> Callable:
        """包装熔断器"""
        def wrapper(*args, **kwargs):
            if not self.circuit_breaker:
                return func(*args, **kwargs)
            
            state = self.circuit_breaker.state
            context.circuit_state = state.value
            
            if state == CircuitState.OPEN:
                self._metrics.increment_strategy(ResilienceStrategy.CIRCUIT_BREAK)
                self._metrics.circuit_breaks += 1
                self._log(f"Circuit breaker open for {context.operation_name}", "WARN")
                raise Exception("Circuit breaker is open")
            
            try:
                result = self.circuit_breaker.execute(func, *args, **kwargs)
                return result
            except Exception as e:
                self._metrics.increment_strategy(ResilienceStrategy.CIRCUIT_BREAK)
                raise
        
        return wrapper

    def _wrap_retry(self, func: Callable, context: ExecutionContext) -> Callable:
        """包装重试策略"""
        def wrapper(*args, **kwargs):
            if not self.retry_policy:
                return func(*args, **kwargs)
            
            retry_count = 0
            
            def on_retry(attempt, exception):
                nonlocal retry_count
                retry_count = attempt
                context.retry_count = retry_count
                self._metrics.increment_strategy(ResilienceStrategy.RETRY)
                self._log(f"Retry {attempt} for {context.operation_name}: {str(exception)}", "INFO")
            
            self.retry_policy.on_retry = on_retry
            result = self.retry_policy.execute(func, *args, **kwargs)
            self._metrics.total_retries += retry_count
            
            return result
        
        return wrapper

    def _wrap_timeout(self, func: Callable, context: ExecutionContext) -> Callable:
        """包装超时管理器"""
        def wrapper(*args, **kwargs):
            if not self.timeout_manager:
                return func(*args, **kwargs)
            
            def on_timeout(ctx):
                self._metrics.increment_strategy(ResilienceStrategy.TIMEOUT)
                self._metrics.timeouts += 1
                self._log(f"Timeout for {context.operation_name}", "WARN")
            
            self.timeout_manager.on_timeout = on_timeout
            result = self.timeout_manager.execute(func, *args, **kwargs)
            
            return result
        
        return wrapper

    def _wrap_rollback(self, func: Callable, context: ExecutionContext) -> Callable:
        """包装回滚策略"""
        def wrapper(*args, **kwargs):
            if not self.rollback_manager:
                return func(*args, **kwargs)
            
            transaction = self.rollback_manager.begin_transaction()
            
            try:
                result = func(*args, **kwargs)
                transaction.commit()
                return result
            except Exception as e:
                transaction.rollback()
                self._metrics.increment_strategy(ResilienceStrategy.ROLLBACK)
                self._metrics.rollbacks += 1
                self._log(f"Rollback executed for {context.operation_name}", "WARN")
                raise
        
        return wrapper

    def _execute_rollback(
        self,
        context: ExecutionContext,
        rollback_func: Callable,
        *args,
        **kwargs
    ):
        """执行回滚"""
        try:
            rollback_func(*args, **kwargs)
            self._metrics.rollbacks += 1
            self._log(f"Manual rollback executed for {context.operation_name}", "INFO")
        except Exception as e:
            self._log(f"Rollback failed for {context.operation_name}: {str(e)}", "ERROR")

    def __call__(self, func: Callable) -> Callable:
        """支持装饰器用法"""
        def wrapper(*args, **kwargs):
            return self.execute(func, *args, **kwargs)
        return wrapper

    def reset_metrics(self):
        """重置指标"""
        with self._lock:
            self._metrics = OrchestratorMetrics()

    def get_status(self) -> Dict:
        """获取编排器状态"""
        with self._lock:
            return {
                "config": self.config.to_dict(),
                "metrics": self._metrics.to_dict(),
                "components": {
                    "rate_limiter": self.rate_limiter is not None,
                    "circuit_breaker": self.circuit_breaker is not None,
                    "retry_policy": self.retry_policy is not None,
                    "timeout_manager": self.timeout_manager is not None,
                    "rollback_manager": self.rollback_manager is not None
                }
            }

    def shutdown(self):
        """关闭所有组件"""
        if self.timeout_manager:
            self.timeout_manager.shutdown()


def create_default_orchestrator() -> ResilienceOrchestrator:
    """创建默认配置的韧性编排器"""
    
    config = OrchestratorConfig()
    
    rate_limiter = RateLimiter(
        RateLimitConfig(
            strategy=RateLimitStrategy.TOKEN_BUCKET,
            max_tokens=100,
            refill_rate=10.0
        )
    )
    
    circuit_breaker = CircuitBreaker(
        name="default",
        config=CircuitBreakerConfig(
            failure_threshold=5,
            success_threshold=2,
            timeout_seconds=30.0
        )
    )
    
    retry_policy = RetryPolicy(
        RetryPolicyConfig(
            max_attempts=3,
            base_delay_seconds=0.1,
            backoff_strategy=BackoffStrategy.EXPONENTIAL
        )
    )
    
    timeout_manager = TimeoutManager(
        TimeoutConfig(
            default_timeout_seconds=30.0,
            strategy=TimeoutStrategy.FAST_FAIL
        )
    )
    
    return ResilienceOrchestrator(
        config=config,
        rate_limiter=rate_limiter,
        circuit_breaker=circuit_breaker,
        retry_policy=retry_policy,
        timeout_manager=timeout_manager
    )
