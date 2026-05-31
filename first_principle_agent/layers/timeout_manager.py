from enum import Enum
import time
import threading
from typing import Callable, Optional, Any, Dict, List
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError, Future
from first_principle_agent.core.base import JSONSerializable


class TimeoutStrategy(Enum):
    """超时策略枚举"""
    FAST_FAIL = "fast_fail"  # 快速失败：超时立即抛出异常
    GRACEFUL = "graceful"  # 优雅降级：超时调用降级函数
    WAIT_COMPLETION = "wait_completion"  # 等待完成：等待任务完成但记录超时
    PARALLEL = "parallel"  # 并行执行：同时执行主任务和超时任务


@dataclass
class TimeoutConfig(JSONSerializable):
    """超时配置"""
    default_timeout_seconds: float = 30.0  # 默认超时时间
    strategy: TimeoutStrategy = TimeoutStrategy.FAST_FAIL
    enable_soft_timeout: bool = False  # 是否启用软超时
    soft_timeout_percentage: float = 0.8  # 软超时时间百分比（相对于硬超时）
    max_workers: int = 10  # 最大工作线程数
    propagate_timeout_exception: bool = True  # 是否传播超时异常

    def to_dict(self) -> Dict:
        return {
            "default_timeout_seconds": self.default_timeout_seconds,
            "strategy": self.strategy.value,
            "enable_soft_timeout": self.enable_soft_timeout,
            "soft_timeout_percentage": self.soft_timeout_percentage,
            "max_workers": self.max_workers,
            "propagate_timeout_exception": self.propagate_timeout_exception
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "TimeoutConfig":
        return cls(
            default_timeout_seconds=data.get("default_timeout_seconds", 30.0),
            strategy=TimeoutStrategy(data.get("strategy", "fast_fail")),
            enable_soft_timeout=data.get("enable_soft_timeout", False),
            soft_timeout_percentage=data.get("soft_timeout_percentage", 0.8),
            max_workers=data.get("max_workers", 10),
            propagate_timeout_exception=data.get("propagate_timeout_exception", True)
        )


@dataclass
class TimeoutMetrics(JSONSerializable):
    """超时指标"""
    total_executions: int = 0
    successful_executions: int = 0
    timeout_executions: int = 0
    soft_timeout_executions: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    longest_execution_time: float = 0.0
    shortest_execution_time: float = float('inf')
    last_execution_time: Optional[float] = None
    last_timeout_time: Optional[float] = None

    def to_dict(self) -> Dict:
        return {
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "timeout_executions": self.timeout_executions,
            "soft_timeout_executions": self.soft_timeout_executions,
            "total_execution_time": self.total_execution_time,
            "average_execution_time": self.average_execution_time,
            "longest_execution_time": self.longest_execution_time,
            "shortest_execution_time": (
                self.shortest_execution_time 
                if self.shortest_execution_time != float('inf') 
                else 0
            ),
            "last_execution_time": self.last_execution_time,
            "last_timeout_time": self.last_timeout_time
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "TimeoutMetrics":
        return cls(**data)


@dataclass
class TimeoutContext:
    """超时上下文"""
    operation_name: str
    start_time: float
    timeout_seconds: float
    is_timed_out: bool = False
    is_soft_timed_out: bool = False
    result: Any = None
    error: Optional[str] = None
    
    def elapsed_time(self) -> float:
        """获取已流逝的时间"""
        return time.time() - self.start_time
    
    def remaining_time(self) -> float:
        """获取剩余时间"""
        return max(0, self.timeout_seconds - self.elapsed_time())
    
    def progress_percentage(self) -> float:
        """获取进度百分比"""
        if self.timeout_seconds == 0:
            return 100.0
        return min(100.0, (self.elapsed_time() / self.timeout_seconds) * 100)


class TimeoutError(Exception):
    """超时错误"""
    pass


class SoftTimeoutError(Exception):
    """软超时错误（警告级别）"""
    pass


class TimeoutManager:
    """超时管理器 - 控制操作执行时间"""

    def __init__(
        self,
        config: Optional[TimeoutConfig] = None,
        on_timeout: Optional[Callable] = None,
        on_soft_timeout: Optional[Callable] = None
    ):
        """
        初始化超时管理器
        
        Args:
            config: 超时配置
            on_timeout: 超时时的回调函数
            on_soft_timeout: 软超时时的回调函数
        """
        self.config = config or TimeoutConfig()
        self.on_timeout = on_timeout
        self.on_soft_timeout = on_soft_timeout
        self._metrics = TimeoutMetrics()
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=self.config.max_workers)

    @property
    def metrics(self) -> TimeoutMetrics:
        """获取超时指标"""
        return self._metrics

    def _record_execution(self, execution_time: float, is_timeout: bool = False, is_soft_timeout: bool = False):
        """记录执行信息"""
        with self._lock:
            self._metrics.total_executions += 1
            self._metrics.total_execution_time += execution_time
            self._metrics.average_execution_time = (
                self._metrics.total_execution_time / self._metrics.total_executions
            )
            self._metrics.last_execution_time = time.time()
            
            if not is_timeout and not is_soft_timeout:
                self._metrics.successful_executions += 1
            
            if is_timeout:
                self._metrics.timeout_executions += 1
                self._metrics.last_timeout_time = time.time()
            
            if is_soft_timeout:
                self._metrics.soft_timeout_executions += 1
            
            self._metrics.longest_execution_time = max(
                self._metrics.longest_execution_time, 
                execution_time
            )
            self._metrics.shortest_execution_time = min(
                self._metrics.shortest_execution_time, 
                execution_time
            )

    def execute(
        self,
        func: Callable,
        *args,
        timeout_seconds: Optional[float] = None,
        fallback: Optional[Callable] = None,
        **kwargs
    ) -> Any:
        """
        执行带超时控制的函数
        
        Args:
            func: 要执行的函数
            *args: 函数位置参数
            timeout_seconds: 超时时间（秒），如果为None则使用默认值
            fallback: 超时时的降级函数
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果
            
        Raises:
            TimeoutError: 当操作超时时
        """
        timeout = timeout_seconds or self.config.default_timeout_seconds
        start_time = time.time()
        context = TimeoutContext(
            operation_name=getattr(func, '__name__', 'unknown'),
            start_time=start_time,
            timeout_seconds=timeout
        )
        
        try:
            if self.config.strategy == TimeoutStrategy.FAST_FAIL:
                result = self._execute_fast_fail(
                    func, timeout, context, *args, **kwargs
                )
            elif self.config.strategy == TimeoutStrategy.GRACEFUL:
                result = self._execute_graceful(
                    func, timeout, fallback, context, *args, **kwargs
                )
            elif self.config.strategy == TimeoutStrategy.WAIT_COMPLETION:
                result = self._execute_wait_completion(
                    func, timeout, context, *args, **kwargs
                )
            elif self.config.strategy == TimeoutStrategy.PARALLEL:
                result = self._execute_parallel(
                    func, timeout, fallback, context, *args, **kwargs
                )
            else:
                raise ValueError(f"Unknown timeout strategy: {self.config.strategy}")
            
            execution_time = time.time() - start_time
            self._record_execution(execution_time, is_timeout=context.is_timed_out)
            context.result = result
            return result
            
        except (TimeoutError, SoftTimeoutError):
            execution_time = time.time() - start_time
            self._record_execution(
                execution_time, 
                is_timeout=context.is_timed_out,
                is_soft_timeout=context.is_soft_timed_out
            )
            raise

    def _execute_fast_fail(
        self,
        func: Callable,
        timeout: float,
        context: TimeoutContext,
        *args,
        **kwargs
    ) -> Any:
        """快速失败策略"""
        future = self._executor.submit(func, *args, **kwargs)
        
        try:
            result = future.result(timeout=timeout)
            return result
        except FutureTimeoutError:
            context.is_timed_out = True
            if self.on_timeout:
                self.on_timeout(context)
            if self.config.propagate_timeout_exception:
                raise TimeoutError(f"Operation timed out after {timeout} seconds")
            return None

    def _execute_graceful(
        self,
        func: Callable,
        timeout: float,
        fallback: Optional[Callable],
        context: TimeoutContext,
        *args,
        **kwargs
    ) -> Any:
        """优雅降级策略"""
        future = self._executor.submit(func, *args, **kwargs)
        
        try:
            result = future.result(timeout=timeout)
            return result
        except FutureTimeoutError:
            context.is_timed_out = True
            if self.on_timeout:
                self.on_timeout(context)
            if fallback:
                return fallback(*args, **kwargs)
            if self.config.propagate_timeout_exception:
                raise TimeoutError(f"Operation timed out after {timeout} seconds")
            return None

    def _execute_wait_completion(
        self,
        func: Callable,
        timeout: float,
        context: TimeoutContext,
        *args,
        **kwargs
    ) -> Any:
        """等待完成策略"""
        future = self._executor.submit(func, *args, **kwargs)
        
        # 检查软超时
        soft_timeout = timeout * self.config.soft_timeout_percentage
        
        # 在单独的线程中监控软超时
        if self.config.enable_soft_timeout and self.on_soft_timeout:
            def check_soft_timeout():
                start = time.time()
                while time.time() - start < soft_timeout:
                    if context.is_timed_out:
                        return
                    time.sleep(0.1)
                if not context.is_timed_out:
                    context.is_soft_timed_out = True
                    self.on_soft_timeout(context)
            
            soft_timeout_thread = threading.Thread(target=check_soft_timeout)
            soft_timeout_thread.daemon = True
            soft_timeout_thread.start()
        
        try:
            result = future.result(timeout=timeout * 2)  # 给予额外时间完成
            return result
        except FutureTimeoutError:
            context.is_timed_out = True
            if self.on_timeout:
                self.on_timeout(context)
            if self.config.propagate_timeout_exception:
                raise TimeoutError(f"Operation timed out after {timeout} seconds")
            return None

    def _execute_parallel(
        self,
        func: Callable,
        timeout: float,
        fallback: Optional[Callable],
        context: TimeoutContext,
        *args,
        **kwargs
    ) -> Any:
        """并行执行策略"""
        future = self._executor.submit(func, *args, **kwargs)
        
        # 启动超时任务
        timeout_future = None
        if fallback:
            timeout_future = self._executor.submit(fallback, *args, **kwargs)
        
        try:
            result = future.result(timeout=timeout)
            return result
        except FutureTimeoutError:
            context.is_timed_out = True
            if self.on_timeout:
                self.on_timeout(context)
            if timeout_future:
                try:
                    return timeout_future.result(timeout=1.0)
                except:
                    pass
            if self.config.propagate_timeout_exception:
                raise TimeoutError(f"Operation timed out after {timeout} seconds")
            return None

    def __call__(self, func: Callable) -> Callable:
        """支持装饰器用法"""
        def wrapper(*args, **kwargs):
            return self.execute(func, *args, **kwargs)
        return wrapper

    def timeout(self, seconds: float):
        """装饰器：指定超时时间"""
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                return self.execute(func, timeout_seconds=seconds, *args, **kwargs)
            return wrapper
        return decorator

    def reset_metrics(self):
        """重置指标"""
        with self._lock:
            self._metrics = TimeoutMetrics()

    def get_metrics_summary(self) -> Dict:
        """获取指标摘要"""
        with self._lock:
            timeout_rate = (
                self._metrics.timeout_executions / self._metrics.total_executions
                if self._metrics.total_executions > 0 
                else 0.0
            )
            return {
                "total_executions": self._metrics.total_executions,
                "successful_executions": self._metrics.successful_executions,
                "timeout_executions": self._metrics.timeout_executions,
                "timeout_rate": timeout_rate,
                "average_execution_time": self._metrics.average_execution_time,
                "longest_execution_time": self._metrics.longest_execution_time
            }

    def shutdown(self, wait: bool = True):
        """关闭线程池"""
        self._executor.shutdown(wait=wait)

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.shutdown()
        return False
