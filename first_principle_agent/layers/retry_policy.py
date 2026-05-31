from enum import Enum
import time
import random
from typing import Callable, Optional, Any, Dict, List, Type, Tuple
from dataclasses import dataclass, field
from first_principle_agent.core.base import JSONSerializable


class BackoffStrategy(Enum):
    """退避策略枚举"""
    FIXED = "fixed"  # 固定间隔
    LINEAR = "linear"  # 线性递增
    EXPONENTIAL = "exponential"  # 指数退避
    FIBONACCI = "fibonacci"  # 斐波那契退避
    EXPONENTIAL_WITH_JITTER = "exponential_with_jitter"  # 带抖动的指数退避


@dataclass
class RetryPolicyConfig(JSONSerializable):
    """重试策略配置"""
    max_attempts: int = 3  # 最大尝试次数
    max_delay_seconds: float = 60.0  # 最大延迟时间
    base_delay_seconds: float = 1.0  # 基础延迟时间
    timeout_seconds: Optional[float] = None  # 总超时时间
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    retryable_exceptions: Tuple[Type[Exception], ...] = field(
        default_factory=lambda: (Exception,)
    )  # 可重试的异常类型
    jitter_factor: float = 0.1  # 抖动因子（0-1之间）

    def to_dict(self) -> Dict:
        return {
            "max_attempts": self.max_attempts,
            "max_delay_seconds": self.max_delay_seconds,
            "base_delay_seconds": self.base_delay_seconds,
            "timeout_seconds": self.timeout_seconds,
            "backoff_strategy": self.backoff_strategy.value,
            "retryable_exceptions": [e.__name__ for e in self.retryable_exceptions],
            "jitter_factor": self.jitter_factor
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "RetryPolicyConfig":
        # 异常类型无法从字符串完全恢复，这里只恢复可重试的异常类型
        retryable_exceptions = tuple(data.get("retryable_exceptions", [Exception]))
        return cls(
            max_attempts=data.get("max_attempts", 3),
            max_delay_seconds=data.get("max_delay_seconds", 60.0),
            base_delay_seconds=data.get("base_delay_seconds", 1.0),
            timeout_seconds=data.get("timeout_seconds"),
            backoff_strategy=BackoffStrategy(data.get("backoff_strategy", "exponential")),
            retryable_exceptions=retryable_exceptions,
            jitter_factor=data.get("jitter_factor", 0.1)
        )


@dataclass
class RetryMetrics(JSONSerializable):
    """重试指标"""
    total_attempts: int = 0
    total_successes: int = 0
    total_failures: int = 0
    total_retries: int = 0
    total_time_seconds: float = 0.0
    last_attempt_time: Optional[float] = None
    last_success_time: Optional[float] = None
    last_failure_time: Optional[float] = None
    last_error: Optional[str] = None
    retry_history: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "total_attempts": self.total_attempts,
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
            "total_retries": self.total_retries,
            "total_time_seconds": self.total_time_seconds,
            "last_attempt_time": self.last_attempt_time,
            "last_success_time": self.last_success_time,
            "last_failure_time": self.last_failure_time,
            "last_error": self.last_error,
            "retry_history": self.retry_history
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "RetryMetrics":
        return cls(**data)


class RetryPolicy:
    """重试策略 - 智能重试机制"""

    def __init__(
        self,
        config: Optional[RetryPolicyConfig] = None,
        on_retry: Optional[Callable] = None
    ):
        """
        初始化重试策略
        
        Args:
            config: 重试策略配置
            on_retry: 每次重试前的回调函数，参数为(attempt, exception)
        """
        self.config = config or RetryPolicyConfig()
        self.on_retry = on_retry
        self._metrics = RetryMetrics()
        self._fibonacci_cache = {0: 0, 1: 1}

    @property
    def metrics(self) -> RetryMetrics:
        """获取重试指标"""
        return self._metrics

    def _calculate_delay(self, attempt: int) -> float:
        """计算延迟时间"""
        base_delay = self.config.base_delay_seconds
        max_delay = self.config.max_delay_seconds
        strategy = self.config.backoff_strategy
        
        if strategy == BackoffStrategy.FIXED:
            delay = base_delay
        elif strategy == BackoffStrategy.LINEAR:
            delay = base_delay * attempt
        elif strategy == BackoffStrategy.EXPONENTIAL:
            delay = base_delay * (2 ** (attempt - 1))
        elif strategy == BackoffStrategy.FIBONACCI:
            delay = base_delay * self._fibonacci(attempt)
        elif strategy == BackoffStrategy.EXPONENTIAL_WITH_JITTER:
            delay = base_delay * (2 ** (attempt - 1))
        else:
            delay = base_delay
        
        # 添加抖动
        if strategy == BackoffStrategy.EXPONENTIAL_WITH_JITTER:
            jitter = delay * self.config.jitter_factor * random.uniform(-1, 1)
            delay = delay + jitter
        
        # 确保不超过最大延迟
        return min(delay, max_delay)

    def _fibonacci(self, n: int) -> int:
        """计算斐波那契数（带缓存）"""
        if n in self._fibonacci_cache:
            return self._fibonacci_cache[n]
        
        result = self._fibonacci(n - 1) + self._fibonacci(n - 2)
        self._fibonacci_cache[n] = result
        return result

    def _should_retry(self, exception: Exception, attempt: int) -> bool:
        """判断是否应该重试"""
        # 检查是否为可重试的异常类型
        if not isinstance(exception, self.config.retryable_exceptions):
            return False
        
        # 检查是否超过最大尝试次数
        # 当attempt达到max_attempts时，不应该再重试
        # 这是因为attempt已经等于允许的最大尝试次数
        if attempt >= self.config.max_attempts:
            return False
        
        return True

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        执行带重试的函数
        
        Args:
            func: 要执行的函数
            *args: 函数位置参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果
            
        Raises:
            Exception: 当所有重试都失败后抛出最后一次异常
        """
        start_time = time.time()
        attempt = 0
        last_exception = None
        
        while True:
            attempt += 1
            self._metrics.total_attempts += 1
            self._metrics.last_attempt_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                # 成功
                duration = time.time() - start_time
                self._metrics.total_time_seconds += duration
                self._metrics.total_successes += 1
                self._metrics.last_success_time = time.time()
                
                return result
                
            except Exception as e:
                last_exception = e
                self._metrics.last_error = str(e)
                
                # 记录重试历史
                self._metrics.retry_history.append({
                    "attempt": attempt,
                    "error": str(e),
                    "timestamp": time.time()
                })
                
                # 检查是否应该重试
                if not self._should_retry(e, attempt):
                    self._metrics.total_failures += 1
                    self._metrics.last_failure_time = time.time()
                    raise
                
                # 检查是否超时
                if self.config.timeout_seconds:
                    elapsed = time.time() - start_time
                    if elapsed >= self.config.timeout_seconds:
                        self._metrics.total_failures += 1
                        self._metrics.last_failure_time = time.time()
                        raise
                
                # 计算延迟并等待
                delay = self._calculate_delay(attempt)
                self._metrics.total_retries += 1
                
                # 调用重试回调
                if self.on_retry:
                    self.on_retry(attempt, e)
                
                time.sleep(delay)

    def __call__(self, func: Callable) -> Callable:
        """支持装饰器用法"""
        def wrapper(*args, **kwargs):
            return self.execute(func, *args, **kwargs)
        return wrapper

    def reset_metrics(self):
        """重置指标"""
        self._metrics = RetryMetrics()

    def get_metrics_summary(self) -> Dict:
        """获取指标摘要"""
        return {
            "total_attempts": self._metrics.total_attempts,
            "total_successes": self._metrics.total_successes,
            "total_failures": self._metrics.total_failures,
            "total_retries": self._metrics.total_retries,
            "success_rate": (
                self._metrics.total_successes / self._metrics.total_attempts
                if self._metrics.total_attempts > 0 else 0
            ),
            "average_time_per_attempt": (
                self._metrics.total_time_seconds / self._metrics.total_attempts
                if self._metrics.total_attempts > 0 else 0
            )
        }


class RetryContext:
    """重试上下文（用于在重试之间传递状态）"""

    def __init__(self, max_attempts: int = 3):
        self.max_attempts = max_attempts
        self.current_attempt = 0
        self.data: Dict[str, Any] = {}
        self.errors: List[str] = []

    def increment_attempt(self):
        """增加尝试次数"""
        self.current_attempt += 1

    def add_error(self, error: str):
        """添加错误信息"""
        self.errors.append(error)

    def is_last_attempt(self) -> bool:
        """是否是最后一次尝试"""
        return self.current_attempt >= self.max_attempts

    def get_remaining_attempts(self) -> int:
        """获取剩余尝试次数"""
        return max(0, self.max_attempts - self.current_attempt)


class RetryPolicyWithContext(RetryPolicy):
    """支持上下文的重试策略"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._context: Optional[RetryContext] = None

    def execute_with_context(
        self,
        func: Callable,
        context_factory: Callable[[], RetryContext],
        *args,
        **kwargs
    ) -> Any:
        """
        执行带上下文的重试函数
        
        Args:
            func: 要执行的函数，签名必须是 (context, *args, **kwargs)
            context_factory: 上下文工厂函数
            *args: 函数位置参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果
        """
        self._context = context_factory()
        start_time = time.time()
        last_exception = None
        
        while True:
            self._context.increment_attempt()
            self._metrics.total_attempts += 1
            self._metrics.last_attempt_time = time.time()
            
            try:
                result = func(self._context, *args, **kwargs)
                
                duration = time.time() - start_time
                self._metrics.total_time_seconds += duration
                self._metrics.total_successes += 1
                self._metrics.last_success_time = time.time()
                
                return result
                
            except Exception as e:
                last_exception = e
                self._context.add_error(str(e))
                self._metrics.last_error = str(e)
                
                self._metrics.retry_history.append({
                    "attempt": self._context.current_attempt,
                    "error": str(e),
                    "timestamp": time.time()
                })
                
                if not self._should_retry(e, self._context.current_attempt):
                    self._metrics.total_failures += 1
                    self._metrics.last_failure_time = time.time()
                    raise
                
                if self.config.timeout_seconds:
                    elapsed = time.time() - start_time
                    if elapsed >= self.config.timeout_seconds:
                        self._metrics.total_failures += 1
                        self._metrics.last_failure_time = time.time()
                        raise
                
                delay = self._calculate_delay(self._context.current_attempt)
                self._metrics.total_retries += 1
                
                if self.on_retry:
                    self.on_retry(self._context.current_attempt, e)
                
                time.sleep(delay)
