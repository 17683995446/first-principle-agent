from enum import Enum
import time
from typing import Callable, Optional, Any, Dict
from dataclasses import dataclass, field
from datetime import datetime
from first_principle_agent.core.base import JSONSerializable


class CircuitState(Enum):
    """熔断器状态枚举"""
    CLOSED = "closed"  # 闭合状态：正常工作，请求可以通过
    OPEN = "open"  # 打开状态：熔断器已打开，请求直接失败
    HALF_OPEN = "half_open"  # 半打开状态：尝试少量请求，判断系统是否恢复


@dataclass
class CircuitBreakerConfig:
    """熔断器配置"""
    failure_threshold: int = 5  # 失败阈值，超过该值熔断器打开
    success_threshold: int = 3  # 成功阈值，半打开状态下连续成功该次数后关闭
    timeout_seconds: float = 30.0  # 超时时间，打开状态保持多久后进入半打开
    expected_exception_types: tuple = field(default_factory=lambda: (Exception,))  # 需要计数的异常类型
    slow_call_duration_seconds: float = 5.0  # 慢调用判定时间
    slow_call_count_threshold: int = 3  # 慢调用计数阈值


@dataclass
class CircuitMetrics(JSONSerializable):
    """熔断器指标"""
    total_requests: int = 0
    success_count: int = 0
    failure_count: int = 0
    slow_call_count: int = 0
    timeout_count: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    state_transitions: int = 0
    consecutive_successes: int = 0
    consecutive_failures: int = 0

    def to_dict(self) -> Dict:
        return {
            "total_requests": self.total_requests,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "slow_call_count": self.slow_call_count,
            "timeout_count": self.timeout_count,
            "last_failure_time": self.last_failure_time,
            "last_success_time": self.last_success_time,
            "state_transitions": self.state_transitions,
            "consecutive_successes": self.consecutive_successes,
            "consecutive_failures": self.consecutive_failures
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CircuitMetrics":
        return cls(**data)


class CircuitBreaker:
    """熔断器 - 防止系统雪崩的保护机制"""

    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
        fallback: Optional[Callable] = None
    ):
        """
        初始化熔断器
        
        Args:
            name: 熔断器名称
            config: 熔断器配置
            fallback: 降级函数，当熔断器打开时调用
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.fallback = fallback
        self._state = CircuitState.CLOSED
        self._metrics = CircuitMetrics()
        self._open_time: Optional[float] = None
        self._lock = False

    @property
    def state(self) -> CircuitState:
        """获取当前状态"""
        self._check_and_transition_state()
        return self._state

    @property
    def metrics(self) -> CircuitMetrics:
        """获取指标"""
        return self._metrics

    def _check_and_transition_state(self):
        """检查并转换状态"""
        if self._state == CircuitState.OPEN:
            # 检查是否超时，超时则进入半打开状态
            if self._open_time and time.time() - self._open_time >= self.config.timeout_seconds:
                self._transition_to(CircuitState.HALF_OPEN)

    def _transition_to(self, new_state: CircuitState):
        """转换到新状态"""
        if self._state != new_state:
            old_state = self._state
            self._state = new_state
            self._metrics.state_transitions += 1
            
            if new_state == CircuitState.OPEN:
                self._open_time = time.time()
            elif new_state == CircuitState.CLOSED:
                self._open_time = None
                self._metrics.consecutive_failures = 0

    def _record_success(self, duration: float):
        """记录成功请求"""
        self._metrics.total_requests += 1
        self._metrics.success_count += 1
        self._metrics.last_success_time = time.time()
        self._metrics.consecutive_successes += 1
        self._metrics.consecutive_failures = 0
        
        # 检查是否为慢调用
        if duration > self.config.slow_call_duration_seconds:
            self._metrics.slow_call_count += 1

    def _record_failure(self, exception: Optional[Exception] = None):
        """记录失败请求"""
        self._metrics.total_requests += 1
        self._metrics.failure_count += 1
        self._metrics.last_failure_time = time.time()
        self._metrics.consecutive_failures += 1
        self._metrics.consecutive_successes = 0

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        执行受保护的函数
        
        Args:
            func: 要执行的函数
            *args: 函数位置参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果
            
        Raises:
            Exception: 当熔断器打开或函数执行失败时
        """
        # 检查并转换状态
        self._check_and_transition_state()
        
        # 如果熔断器打开，直接失败或调用降级函数
        if self._state == CircuitState.OPEN:
            if self.fallback:
                return self.fallback(*args, **kwargs)
            raise CircuitBreakerOpenError(f"Circuit breaker '{self.name}' is OPEN")
        
        # 执行函数
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            self._on_success(duration)
            return result
        except Exception as e:
            duration = time.time() - start_time
            self._on_failure(e, duration)
            if self.fallback:
                return self.fallback(*args, **kwargs)
            raise

    def _on_success(self, duration: float):
        """处理成功情况"""
        self._record_success(duration)
        
        if self._state == CircuitState.HALF_OPEN:
            # 半打开状态下，连续成功次数达到阈值则关闭
            if self._metrics.consecutive_successes >= self.config.success_threshold:
                self._transition_to(CircuitState.CLOSED)

    def _on_failure(self, exception: Exception, duration: float):
        """处理失败情况"""
        # 检查是否为需要计数的异常类型
        if isinstance(exception, self.config.expected_exception_types):
            self._record_failure(exception)
            
            if self._state == CircuitState.CLOSED:
                # 闭合状态下，检查是否达到失败阈值
                if self._metrics.consecutive_failures >= self.config.failure_threshold:
                    self._transition_to(CircuitState.OPEN)
            elif self._state == CircuitState.HALF_OPEN:
                # 半打开状态下，一次失败就重新打开
                self._transition_to(CircuitState.OPEN)

    def force_open(self):
        """强制打开熔断器"""
        self._transition_to(CircuitState.OPEN)

    def force_close(self):
        """强制关闭熔断器"""
        self._transition_to(CircuitState.CLOSED)
        self._metrics.consecutive_failures = 0
        self._metrics.consecutive_successes = 0

    def reset(self):
        """重置熔断器"""
        self._state = CircuitState.CLOSED
        self._metrics = CircuitMetrics()
        self._open_time = None

    def get_state_info(self) -> Dict:
        """获取完整状态信息"""
        return {
            "name": self.name,
            "state": self._state.value,
            "metrics": self._metrics.to_dict(),
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "success_threshold": self.config.success_threshold,
                "timeout_seconds": self.config.timeout_seconds,
                "slow_call_duration_seconds": self.config.slow_call_duration_seconds,
                "slow_call_count_threshold": self.config.slow_call_count_threshold
            },
            "open_time": self._open_time,
            "open_duration": time.time() - self._open_time if self._open_time else 0
        }

    def __call__(self, func: Callable) -> Callable:
        """支持装饰器用法"""
        def wrapper(*args, **kwargs):
            return self.execute(func, *args, **kwargs)
        return wrapper


class CircuitBreakerOpenError(Exception):
    """熔断器打开错误"""
    pass
