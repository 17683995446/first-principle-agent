from enum import Enum
import time
import threading
from typing import Callable, Optional, Any, Dict
from dataclasses import dataclass, field
from collections import deque
from first_principle_agent.core.base import JSONSerializable


class RateLimitStrategy(Enum):
    """限流策略枚举"""
    TOKEN_BUCKET = "token_bucket"  # 令牌桶算法
    LEAKY_BUCKET = "leaky_bucket"  # 漏桶算法
    FIXED_WINDOW = "fixed_window"  # 固定窗口算法
    SLIDING_WINDOW = "sliding_window"  # 滑动窗口算法


@dataclass
class RateLimitConfig(JSONSerializable):
    """限流配置"""
    strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET
    max_tokens: int = 100  # 最大令牌数
    refill_rate: float = 10.0  # 每秒补充的令牌数
    capacity: int = 100  # 漏桶容量
    leak_rate: float = 10.0  # 每秒漏水速率
    window_seconds: float = 60.0  # 窗口大小（秒）
    max_requests: int = 100  # 窗口内最大请求数
    burst_limit: int = 10  # 突发请求限制

    def to_dict(self) -> Dict:
        return {
            "strategy": self.strategy.value,
            "max_tokens": self.max_tokens,
            "refill_rate": self.refill_rate,
            "capacity": self.capacity,
            "leak_rate": self.leak_rate,
            "window_seconds": self.window_seconds,
            "max_requests": self.max_requests,
            "burst_limit": self.burst_limit
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "RateLimitConfig":
        return cls(
            strategy=RateLimitStrategy(data.get("strategy", "token_bucket")),
            max_tokens=data.get("max_tokens", 100),
            refill_rate=data.get("refill_rate", 10.0),
            capacity=data.get("capacity", 100),
            leak_rate=data.get("leak_rate", 10.0),
            window_seconds=data.get("window_seconds", 60.0),
            max_requests=data.get("max_requests", 100),
            burst_limit=data.get("burst_limit", 10)
        )


@dataclass
class RateLimitMetrics(JSONSerializable):
    """限流指标"""
    total_requests: int = 0
    allowed_requests: int = 0
    rejected_requests: int = 0
    total_wait_time: float = 0.0
    last_request_time: Optional[float] = None
    rejection_count: int = 0

    def to_dict(self) -> Dict:
        return {
            "total_requests": self.total_requests,
            "allowed_requests": self.allowed_requests,
            "rejected_requests": self.rejected_requests,
            "total_wait_time": self.total_wait_time,
            "last_request_time": self.last_request_time,
            "rejection_count": self.rejection_count
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "RateLimitMetrics":
        return cls(**data)


class RateLimiter:
    """限流器 - 控制系统请求频率"""

    def __init__(
        self,
        config: Optional[RateLimitConfig] = None,
        on_reject: Optional[Callable] = None
    ):
        """
        初始化限流器
        
        Args:
            config: 限流配置
            on_reject: 被限流时的回调函数
        """
        self.config = config or RateLimitConfig()
        self.on_reject = on_reject
        self._metrics = RateLimitMetrics()
        self._lock = threading.RLock()
        
        # 令牌桶状态
        self._tokens = self.config.max_tokens
        self._last_refill_time = time.time()
        
        # 漏桶状态
        self._bucket_queue = deque()
        self._last_leak_time = time.time()
        
        # 固定窗口状态
        self._window_start_time = time.time()
        self._window_request_count = 0
        
        # 滑动窗口状态
        self._request_timestamps = deque()

    @property
    def metrics(self) -> RateLimitMetrics:
        """获取限流指标"""
        return self._metrics

    def _refill_tokens(self):
        """补充令牌（令牌桶算法）"""
        now = time.time()
        elapsed = now - self._last_refill_time
        new_tokens = elapsed * self.config.refill_rate
        self._tokens = min(self._tokens + new_tokens, self.config.max_tokens)
        self._last_refill_time = now

    def _check_token_bucket(self, tokens_needed: int = 1) -> bool:
        """
        使用令牌桶算法检查是否允许请求
        
        Args:
            tokens_needed: 本次请求需要消耗的令牌数
            
        Returns:
            是否允许请求
        """
        with self._lock:
            self._refill_tokens()
            if self._tokens >= tokens_needed:
                self._tokens -= tokens_needed
                return True
            return False

    def _leak_bucket(self):
        """漏水（漏桶算法）"""
        now = time.time()
        elapsed = now - self._last_leak_time
        leaked = elapsed * self.config.leak_rate
        
        # 移除已处理的请求
        while self._bucket_queue and leaked > 0:
            first_request = self._bucket_queue[0]
            if now - first_request >= 1.0 / self.config.leak_rate:
                self._bucket_queue.popleft()
                leaked -= 1.0 / self.config.leak_rate
            else:
                break
        
        self._last_leak_time = now

    def _check_leaky_bucket(self) -> bool:
        """
        使用漏桶算法检查是否允许请求
        
        Returns:
            是否允许请求
        """
        with self._lock:
            self._leak_bucket()
            if len(self._bucket_queue) < self.config.capacity:
                self._bucket_queue.append(time.time())
                return True
            return False

    def _check_fixed_window(self) -> bool:
        """
        使用固定窗口算法检查是否允许请求
        
        Returns:
            是否允许请求
        """
        with self._lock:
            now = time.time()
            
            # 检查是否需要切换到新窗口
            if now - self._window_start_time >= self.config.window_seconds:
                self._window_start_time = now
                self._window_request_count = 0
            
            # 检查是否超过请求限制
            if self._window_request_count < self.config.max_requests:
                self._window_request_count += 1
                return True
            return False

    def _check_sliding_window(self) -> bool:
        """
        使用滑动窗口算法检查是否允许请求
        
        Returns:
            是否允许请求
        """
        with self._lock:
            now = time.time()
            window_start = now - self.config.window_seconds
            
            # 移除窗口外的时间戳
            while self._request_timestamps and self._request_timestamps[0] < window_start:
                self._request_timestamps.popleft()
            
            # 检查是否超过请求限制
            if len(self._request_timestamps) < self.config.max_requests:
                self._request_timestamps.append(now)
                return True
            return False

    def allow(self, tokens_needed: int = 1) -> bool:
        """
        检查是否允许请求
        
        Args:
            tokens_needed: 本次请求需要消耗的令牌数（仅对令牌桶有效）
            
        Returns:
            是否允许请求
        """
        self._metrics.total_requests += 1
        self._metrics.last_request_time = time.time()
        
        strategy = self.config.strategy
        allowed = False
        
        if strategy == RateLimitStrategy.TOKEN_BUCKET:
            allowed = self._check_token_bucket(tokens_needed)
        elif strategy == RateLimitStrategy.LEAKY_BUCKET:
            allowed = self._check_leaky_bucket()
        elif strategy == RateLimitStrategy.FIXED_WINDOW:
            allowed = self._check_fixed_window()
        elif strategy == RateLimitStrategy.SLIDING_WINDOW:
            allowed = self._check_sliding_window()
        
        if allowed:
            self._metrics.allowed_requests += 1
        else:
            self._metrics.rejected_requests += 1
            self._metrics.rejection_count += 1
            if self.on_reject:
                self.on_reject()
        
        return allowed

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        执行受限流保护的函数
        
        Args:
            func: 要执行的函数
            *args: 函数位置参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果，如果被限流则返回None
        """
        start_time = time.time()
        
        if not self.allow():
            return None
        
        wait_time = time.time() - start_time
        self._metrics.total_wait_time += wait_time
        
        return func(*args, **kwargs)

    def __call__(self, func: Callable) -> Callable:
        """支持装饰器用法"""
        def wrapper(*args, **kwargs):
            return self.execute(func, *args, **kwargs)
        return wrapper

    def reset(self):
        """重置限流器状态"""
        with self._lock:
            self._tokens = self.config.max_tokens
            self._last_refill_time = time.time()
            self._bucket_queue.clear()
            self._last_leak_time = time.time()
            self._window_start_time = time.time()
            self._window_request_count = 0
            self._request_timestamps.clear()

    def reset_metrics(self):
        """重置指标"""
        self._metrics = RateLimitMetrics()

    def get_status(self) -> Dict:
        """获取限流器状态"""
        with self._lock:
            status = {
                "strategy": self.config.strategy.value,
                "metrics": self._metrics.to_dict(),
                "token_bucket": {
                    "current_tokens": self._tokens,
                    "max_tokens": self.config.max_tokens,
                    "refill_rate": self.config.refill_rate
                } if self.config.strategy == RateLimitStrategy.TOKEN_BUCKET else None,
                "leaky_bucket": {
                    "current_queue_size": len(self._bucket_queue),
                    "capacity": self.config.capacity,
                    "leak_rate": self.config.leak_rate
                } if self.config.strategy == RateLimitStrategy.LEAKY_BUCKET else None,
                "fixed_window": {
                    "current_requests": self._window_request_count,
                    "max_requests": self.config.max_requests,
                    "window_seconds": self.config.window_seconds
                } if self.config.strategy == RateLimitStrategy.FIXED_WINDOW else None,
                "sliding_window": {
                    "current_requests": len(self._request_timestamps),
                    "max_requests": self.config.max_requests,
                    "window_seconds": self.config.window_seconds
                } if self.config.strategy == RateLimitStrategy.SLIDING_WINDOW else None
            }
            return status

    def get_available_tokens(self) -> float:
        """获取当前可用令牌数（仅对令牌桶有效）"""
        with self._lock:
            self._refill_tokens()
            return self._tokens

    def get_rejection_rate(self) -> float:
        """获取拒绝率"""
        if self._metrics.total_requests == 0:
            return 0.0
        return self._metrics.rejected_requests / self._metrics.total_requests


class DistributedRateLimiter(RateLimiter):
    """分布式限流器 - 基础实现（可扩展为Redis等外部存储）"""

    def __init__(
        self,
        config: Optional[RateLimitConfig] = None,
        on_reject: Optional[Callable] = None,
        storage_backend: Optional[Any] = None
    ):
        """
        初始化分布式限流器
        
        Args:
            config: 限流配置
            on_reject: 被限流时的回调函数
            storage_backend: 存储后端（可用于分布式场景）
        """
        super().__init__(config, on_reject)
        self._storage_backend = storage_backend
        self._instance_id = f"limiter_{id(self)}"

    def allow(self, tokens_needed: int = 1) -> bool:
        """
        分布式限流检查（基础实现，实际项目中可使用Redis等实现）
        
        Args:
            tokens_needed: 本次请求需要消耗的令牌数
            
        Returns:
            是否允许请求
        """
        # 基础实现与单机限流器相同
        # 实际项目中可使用Redis的令牌桶或滑动窗口实现
        return super().allow(tokens_needed)
