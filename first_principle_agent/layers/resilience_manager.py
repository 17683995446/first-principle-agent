"""
韧性管理器 - 提供高级统一API
"""

from enum import Enum
import time
import threading
from typing import Callable, Optional, Any, Dict, List
from dataclasses import dataclass, field
from first_principle_agent.core.base import JSONSerializable

from first_principle_agent.layers.resilience_orchestrator import (
    ResilienceOrchestrator, OrchestratorConfig, OrchestratorMetrics, ExecutionContext,
    ResilienceStrategy, ExecutionStage
)
from first_principle_agent.layers.circuit_breaker import (
    CircuitBreaker, CircuitBreakerConfig, CircuitState, CircuitBreakerOpenError
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
from first_principle_agent.layers.checkpoint_manager import CheckpointManager


class ResiliencePreset(Enum):
    """韧性预设"""
    DEFAULT = "default"
    HIGH_AVAILABILITY = "high_availability"
    HIGH_PERFORMANCE = "high_performance"
    DEVELOPMENT = "development"


@dataclass
class ResilienceManagerConfig(JSONSerializable):
    """韧性管理器配置"""
    preset: ResiliencePreset = ResiliencePreset.DEFAULT
    enable_all_strategies: bool = True
    enable_checkpoint: bool = True
    enable_monitoring: bool = True
    log_level: str = "INFO"
    max_requests_per_second: int = 100
    burst_size: int = 20
    max_retries: int = 3
    retry_base_delay: float = 0.1
    enable_exponential_backoff: bool = True
    default_timeout_seconds: float = 30.0
    enable_soft_timeout: bool = True
    soft_timeout_percentage: float = 0.8
    failure_threshold: int = 5
    success_threshold: int = 2
    reset_timeout_seconds: float = 30.0
    enable_auto_checkpoint: bool = True
    checkpoint_interval: int = 10

    def to_dict(self) -> Dict:
        return {
            "preset": self.preset.value,
            "enable_all_strategies": self.enable_all_strategies,
            "enable_checkpoint": self.enable_checkpoint,
            "enable_monitoring": self.enable_monitoring,
            "log_level": self.log_level,
            "max_requests_per_second": self.max_requests_per_second,
            "burst_size": self.burst_size,
            "max_retries": self.max_retries,
            "retry_base_delay": self.retry_base_delay,
            "enable_exponential_backoff": self.enable_exponential_backoff,
            "default_timeout_seconds": self.default_timeout_seconds,
            "enable_soft_timeout": self.enable_soft_timeout,
            "soft_timeout_percentage": self.soft_timeout_percentage,
            "failure_threshold": self.failure_threshold,
            "success_threshold": self.success_threshold,
            "reset_timeout_seconds": self.reset_timeout_seconds,
            "enable_auto_checkpoint": self.enable_auto_checkpoint,
            "checkpoint_interval": self.checkpoint_interval
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ResilienceManagerConfig":
        return cls(
            preset=ResiliencePreset(data.get("preset", "default")),
            enable_all_strategies=data.get("enable_all_strategies", True),
            enable_checkpoint=data.get("enable_checkpoint", True),
            enable_monitoring=data.get("enable_monitoring", True),
            log_level=data.get("log_level", "INFO"),
            max_requests_per_second=data.get("max_requests_per_second", 100),
            burst_size=data.get("burst_size", 20),
            max_retries=data.get("max_retries", 3),
            retry_base_delay=data.get("retry_base_delay", 0.1),
            enable_exponential_backoff=data.get("enable_exponential_backoff", True),
            default_timeout_seconds=data.get("default_timeout_seconds", 30.0),
            enable_soft_timeout=data.get("enable_soft_timeout", True),
            soft_timeout_percentage=data.get("soft_timeout_percentage", 0.8),
            failure_threshold=data.get("failure_threshold", 5),
            success_threshold=data.get("success_threshold", 2),
            reset_timeout_seconds=data.get("reset_timeout_seconds", 30.0),
            enable_auto_checkpoint=data.get("enable_auto_checkpoint", True),
            checkpoint_interval=data.get("checkpoint_interval", 10)
        )

    @classmethod
    def from_preset(cls, preset: ResiliencePreset) -> "ResilienceManagerConfig":
        """从预设创建配置"""
        if preset == ResiliencePreset.DEFAULT:
            return cls(preset=preset)
        elif preset == ResiliencePreset.HIGH_AVAILABILITY:
            return cls(
                preset=preset,
                max_retries=5,
                retry_base_delay=0.5,
                failure_threshold=3,
                reset_timeout_seconds=60.0,
                default_timeout_seconds=60.0
            )
        elif preset == ResiliencePreset.HIGH_PERFORMANCE:
            return cls(
                preset=preset,
                max_retries=2,
                retry_base_delay=0.05,
                failure_threshold=10,
                reset_timeout_seconds=10.0,
                default_timeout_seconds=10.0
            )
        elif preset == ResiliencePreset.DEVELOPMENT:
            return cls(
                preset=preset,
                enable_all_strategies=False,
                enable_checkpoint=False,
                max_retries=1,
                default_timeout_seconds=5.0
            )
        else:
            return cls(preset=preset)


@dataclass 
class SystemHealthStatus(JSONSerializable):
    """系统健康状态"""
    overall_health: str
    timestamp: float
    components: Dict[str, Any] = field(default_factory=dict)
    metrics_summary: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "overall_health": self.overall_health,
            "timestamp": self.timestamp,
            "components": self.components,
            "metrics_summary": self.metrics_summary,
            "recommendations": self.recommendations
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "SystemHealthStatus":
        return cls(
            overall_health=data.get("overall_health", "healthy"),
            timestamp=data.get("timestamp", time.time()),
            components=data.get("components", {}),
            metrics_summary=data.get("metrics_summary", {}),
            recommendations=data.get("recommendations", [])
        )


class ResilienceManager:
    """韧性管理器 - 提供高级统一API"""
    
    def __init__(
        self,
        config: Optional[ResilienceManagerConfig] = None,
        preset: Optional[ResiliencePreset] = None
    ):
        if preset:
            self.config = ResilienceManagerConfig.from_preset(preset)
        else:
            self.config = config or ResilienceManagerConfig()
        
        self._lock = threading.RLock()
        self._initialized = False
        self._components: Dict[str, Any] = {}
        
        self._initialize_components()
    
    def _initialize_components(self):
        """初始化所有组件"""
        with self._lock:
            if self._initialized:
                return
            
            if self.config.enable_all_strategies:
                rate_config = RateLimitConfig(
                    strategy=RateLimitStrategy.TOKEN_BUCKET,
                    max_tokens=self.config.burst_size,
                    refill_rate=self.config.max_requests_per_second
                )
                self._components["rate_limiter"] = RateLimiter(config=rate_config)
            
            if self.config.enable_all_strategies:
                cb_config = CircuitBreakerConfig(
                    failure_threshold=self.config.failure_threshold,
                    success_threshold=self.config.success_threshold,
                    timeout_seconds=self.config.reset_timeout_seconds
                )
                self._components["circuit_breaker"] = CircuitBreaker(
                    name="resilience_manager",
                    config=cb_config
                )
            
            if self.config.enable_all_strategies:
                backoff = (
                    BackoffStrategy.EXPONENTIAL 
                    if self.config.enable_exponential_backoff 
                    else BackoffStrategy.FIXED
                )
                retry_config = RetryPolicyConfig(
                    max_attempts=self.config.max_retries,
                    base_delay_seconds=self.config.retry_base_delay,
                    backoff_strategy=backoff
                )
                self._components["retry_policy"] = RetryPolicy(config=retry_config)
            
            timeout_config = TimeoutConfig(
                default_timeout_seconds=self.config.default_timeout_seconds,
                strategy=TimeoutStrategy.FAST_FAIL,
                enable_soft_timeout=self.config.enable_soft_timeout,
                soft_timeout_percentage=self.config.soft_timeout_percentage
            )
            self._components["timeout_manager"] = TimeoutManager(config=timeout_config)
            
            orchestrator_config = OrchestratorConfig(
                enable_logging=self.config.enable_monitoring,
                enable_metrics=self.config.enable_monitoring
            )
            
            strategies = []
            if self.config.enable_all_strategies:
                strategies = [
                    ResilienceStrategy.RATE_LIMIT,
                    ResilienceStrategy.CIRCUIT_BREAK,
                    ResilienceStrategy.RETRY,
                    ResilienceStrategy.TIMEOUT
                ]
            else:
                strategies = [ResilienceStrategy.TIMEOUT]
            
            orchestrator_config.enabled_strategies = strategies
            orchestrator_config.execution_order = strategies
            
            self._components["orchestrator"] = ResilienceOrchestrator(
                config=orchestrator_config,
                rate_limiter=self._components.get("rate_limiter"),
                circuit_breaker=self._components.get("circuit_breaker"),
                retry_policy=self._components.get("retry_policy"),
                timeout_manager=self._components.get("timeout_manager")
            )
            
            if self.config.enable_checkpoint and self.config.enable_auto_checkpoint:
                self._components["checkpoint_manager"] = CheckpointManager()
            
            self._initialized = True
    
    @property
    def orchestrator(self) -> Optional[ResilienceOrchestrator]:
        """获取编排器"""
        return self._components.get("orchestrator")
    
    @property
    def rate_limiter(self) -> Optional[RateLimiter]:
        """获取限流器"""
        return self._components.get("rate_limiter")
    
    @property
    def circuit_breaker(self) -> Optional[CircuitBreaker]:
        """获取熔断器"""
        return self._components.get("circuit_breaker")
    
    @property
    def retry_policy(self) -> Optional[RetryPolicy]:
        """获取重试策略"""
        return self._components.get("retry_policy")
    
    @property
    def timeout_manager(self) -> Optional[TimeoutManager]:
        """获取超时管理器"""
        return self._components.get("timeout_manager")
    
    @property
    def checkpoint_manager(self) -> Optional[CheckpointManager]:
        """获取检查点管理器"""
        return self._components.get("checkpoint_manager")
    
    def execute(
        self,
        func: Callable,
        operation_name: Optional[str] = None,
        fallback: Optional[Callable] = None,
        *args,
        **kwargs
    ) -> Any:
        """执行带韧性保护的操作"""
        orchestrator = self.orchestrator
        
        if orchestrator:
            return orchestrator.execute(
                func,
                operation_name=operation_name,
                fallback=fallback,
                *args,
                **kwargs
            )
        else:
            return func(*args, **kwargs)
    
    def execute_with_checkpoint(
        self,
        func: Callable,
        checkpoint_name: str,
        *args,
        **kwargs
    ) -> Any:
        """执行带检查点的操作"""
        if not self.checkpoint_manager:
            return self.execute(func, checkpoint_name, *args, **kwargs)
        
        from first_principle_agent.layers.atomic_action_executor import AtomicActionPlan
        
        plan = AtomicActionPlan(id=f"checkpoint_{checkpoint_name}")
        
        if self.config.enable_auto_checkpoint:
            self.checkpoint_manager.create_checkpoint(
                plan=plan,
                name=f"{checkpoint_name}_start",
                description="执行前检查点"
            )
        
        try:
            result = self.execute(func, checkpoint_name, *args, **kwargs)
            
            if self.config.enable_auto_checkpoint:
                self.checkpoint_manager.create_checkpoint(
                    plan=plan,
                    name=f"{checkpoint_name}_success",
                    description="成功后检查点"
                )
            
            return result
            
        except Exception as e:
            if self.config.enable_auto_checkpoint:
                try:
                    self.checkpoint_manager.rollback_to_checkpoint(
                        checkpoint_id=f"{checkpoint_name}_start",
                        plan=plan
                    )
                except:
                    pass
            raise
    
    def get_health_status(self) -> SystemHealthStatus:
        """获取系统健康状态"""
        status = SystemHealthStatus(
            overall_health="healthy",
            timestamp=time.time(),
            components={},
            metrics_summary={},
            recommendations=[]
        )
        
        if self.rate_limiter:
            rl_metrics = self.rate_limiter.metrics
            status.components["rate_limiter"] = {
                "enabled": True,
                "rejection_rate": self.rate_limiter.get_rejection_rate(),
                "total_requests": rl_metrics.total_requests
            }
            
            if rl_metrics.rejected_requests > rl_metrics.total_requests * 0.1:
                status.overall_health = "degraded"
                status.recommendations.append("限流器拒绝率较高，考虑增加容量")
        
        if self.circuit_breaker:
            cb_state = self.circuit_breaker.state
            status.components["circuit_breaker"] = {
                "enabled": True,
                "state": cb_state.value,
                "metrics": self.circuit_breaker.metrics.to_dict()
            }
            
            if cb_state == CircuitState.OPEN:
                status.overall_health = "unhealthy"
                status.recommendations.append("熔断器已打开，系统可能存在故障，请检查服务")
            elif cb_state == CircuitState.HALF_OPEN:
                status.overall_health = "degraded"
                status.recommendations.append("熔断器处于半打开状态，正在尝试恢复")
        
        if self.orchestrator:
            orch_metrics = self.orchestrator.metrics
            status.components["orchestrator"] = {
                "enabled": True,
                "total_executions": orch_metrics.total_executions,
                "success_rate": (
                    orch_metrics.successful_executions / orch_metrics.total_executions
                    if orch_metrics.total_executions > 0 else 1.0
                ),
                "strategy_stats": orch_metrics.strategy_stats
            }
            
            status.metrics_summary = orch_metrics.to_dict()
            
            if status.overall_health == "healthy":
                if orch_metrics.failed_executions > orch_metrics.total_executions * 0.05:
                    status.overall_health = "degraded"
                    status.recommendations.append("存在少量失败操作，建议监控")
        
        return status
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """获取所有组件的指标"""
        metrics = {}
        
        if self.rate_limiter:
            metrics["rate_limiter"] = self.rate_limiter.metrics.to_dict()
        
        if self.circuit_breaker:
            metrics["circuit_breaker"] = self.circuit_breaker.metrics.to_dict()
        
        if self.retry_policy:
            metrics["retry_policy"] = self.retry_policy.metrics.to_dict()
        
        if self.timeout_manager:
            metrics["timeout_manager"] = self.timeout_manager.metrics.to_dict()
        
        if self.orchestrator:
            metrics["orchestrator"] = self.orchestrator.metrics.to_dict()
        
        return metrics
    
    def reset_all_metrics(self):
        """重置所有组件的指标"""
        with self._lock:
            if self.rate_limiter:
                self.rate_limiter.reset_metrics()
            # CircuitBreaker没有reset_metrics方法，跳过
            if self.retry_policy:
                self.retry_policy.reset_metrics()
            if self.timeout_manager:
                self.timeout_manager.reset_metrics()
            if self.orchestrator:
                self.orchestrator.reset_metrics()
    
    def __call__(self, func: Callable) -> Callable:
        """支持装饰器用法"""
        def wrapper(*args, **kwargs):
            return self.execute(func, *args, **kwargs)
        return wrapper
    

    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.shutdown()
        return False
    
    def shutdown(self):
        """关闭所有组件"""
        with self._lock:
            if self.timeout_manager:
                self.timeout_manager.shutdown()
            
            self._components.clear()
            self._initialized = False


def create_resilience_manager(
    preset: ResiliencePreset = ResiliencePreset.DEFAULT
) -> ResilienceManager:
    """创建韧性管理器工厂函数"""
    return ResilienceManager(preset=preset)
