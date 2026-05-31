"""
任务调度器 - 任务优先级队列和调度策略
"""

from enum import Enum
import time
import threading
import uuid
import heapq
from typing import Callable, Optional, Any, Dict, List, Union, Set
from dataclasses import dataclass, field
from collections import defaultdict
from queue import PriorityQueue, Queue, Empty
from concurrent.futures import ThreadPoolExecutor, Future

from first_principle_agent.core.base import JSONSerializable
from first_principle_agent.core.task_tuple import TaskTuple
from first_principle_agent.core.task_execution_engine import TaskExecutionEngine, ExecutionStatus
from first_principle_agent.core.task_pipeline import TaskPipeline, PipelineResult, PipelineStatus


class SchedulerStatus(Enum):
    """调度器状态"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


class SchedulerStrategy(Enum):
    """调度策略"""
    FIFO = "fifo"  # 先进先出
    LIFO = "lifo"  # 后进先出
    PRIORITY = "priority"  # 优先级调度
    ROUND_ROBIN = "round_robin"  # 轮询调度
    FAIR = "fair"  # 公平调度


class TaskPriority(Enum):
    """任务优先级"""
    CRITICAL = 0  # 最高优先级
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4  # 最低优先级

    def __lt__(self, other):
        """支持优先级比较"""
        if isinstance(other, TaskPriority):
            return self.value < other.value
        return NotImplemented


@dataclass
class ScheduledTask(JSONSerializable):
    """调度任务"""
    task_id: str
    task: Union[TaskTuple, Callable]
    priority: TaskPriority = TaskPriority.NORMAL
    created_at: float = field(default_factory=time.time)
    scheduled_at: Optional[float] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    status: ExecutionStatus = ExecutionStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    dependencies: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "priority": self.priority.value,
            "created_at": self.created_at,
            "scheduled_at": self.scheduled_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "status": self.status.value,
            "error": self.error,
            "dependencies": list(self.dependencies),
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ScheduledTask":
        return cls(
            task_id=data["task_id"],
            task=data.get("task"),
            priority=TaskPriority(data.get("priority", 2)),
            created_at=data.get("created_at", time.time()),
            scheduled_at=data.get("scheduled_at"),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            status=ExecutionStatus(data.get("status", "pending")),
            error=data.get("error"),
            dependencies=set(data.get("dependencies", [])),
            metadata=data.get("metadata", {})
        )

    def __lt__(self, other):
        """用于优先级队列比较"""
        return self.priority.value < other.priority.value


@dataclass
class SchedulerConfig(JSONSerializable):
    """调度器配置"""
    strategy: SchedulerStrategy = SchedulerStrategy.PRIORITY
    max_workers: int = 4
    max_queue_size: int = 1000
    enable_priorities: bool = True
    enable_deduplication: bool = True
    task_timeout_seconds: Optional[float] = None
    enable_monitoring: bool = True
    enable_metrics: bool = True
    checkpoint_interval: int = 10

    def to_dict(self) -> Dict:
        return {
            "strategy": self.strategy.value,
            "max_workers": self.max_workers,
            "max_queue_size": self.max_queue_size,
            "enable_priorities": self.enable_priorities,
            "enable_deduplication": self.enable_deduplication,
            "task_timeout_seconds": self.task_timeout_seconds,
            "enable_monitoring": self.enable_monitoring,
            "enable_metrics": self.enable_metrics,
            "checkpoint_interval": self.checkpoint_interval
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "SchedulerConfig":
        return cls(
            strategy=SchedulerStrategy(data.get("strategy", "priority")),
            max_workers=data.get("max_workers", 4),
            max_queue_size=data.get("max_queue_size", 1000),
            enable_priorities=data.get("enable_priorities", True),
            enable_deduplication=data.get("enable_deduplication", True),
            task_timeout_seconds=data.get("task_timeout_seconds"),
            enable_monitoring=data.get("enable_monitoring", True),
            enable_metrics=data.get("enable_metrics", True),
            checkpoint_interval=data.get("checkpoint_interval", 10)
        )


@dataclass
class SchedulerMetrics:
    """调度器指标"""
    total_tasks: int = 0
    pending_tasks: int = 0
    running_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    cancelled_tasks: int = 0
    total_execution_time: float = 0.0
    average_wait_time: float = 0.0
    throughput: float = 0.0  # 每秒完成的任务数

    def to_dict(self) -> Dict:

        @classmethod
        def from_dict(cls, data: Dict) -> "SchedulerMetrics":
            return cls(
                total_tasks=data.get("total_tasks", 0),
                pending_tasks=data.get("pending_tasks", 0),
                running_tasks=data.get("running_tasks", 0),
                completed_tasks=data.get("completed_tasks", 0),
                failed_tasks=data.get("failed_tasks", 0),
                cancelled_tasks=data.get("cancelled_tasks", 0),
                total_execution_time=data.get("total_execution_time", 0.0),
                average_wait_time=data.get("average_wait_time", 0.0),
                throughput=data.get("throughput", 0.0)
            )
        return {
            "total_tasks": self.total_tasks,
            "pending_tasks": self.pending_tasks,
            "running_tasks": self.running_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "cancelled_tasks": self.cancelled_tasks,
            "total_execution_time": self.total_execution_time,
            "average_wait_time": self.average_wait_time,
            "throughput": self.throughput
        }


class TaskScheduler:
    """任务调度器 - 任务优先级队列和调度策略"""

    def __init__(
        self,
        config: Optional[SchedulerConfig] = None,
        execution_engine: Optional[TaskExecutionEngine] = None
    ):
        """
        初始化任务调度器

        Args:
            config: 调度器配置
            execution_engine: 执行引擎（可选）
        """
        self.id = str(uuid.uuid4())
        self.config = config or SchedulerConfig()
        self.execution_engine = execution_engine
        
        self._lock = threading.RLock()
        self._status = SchedulerStatus.IDLE
        
        # 任务队列
        if self.config.enable_priorities:
            self._task_queue: List[ScheduledTask] = []
        else:
            self._task_queue = Queue(maxsize=self.config.max_queue_size)
        
        # 任务存储
        self._tasks: Dict[str, ScheduledTask] = {}
        self._running_tasks: Dict[str, Future] = {}
        self._completed_tasks: Dict[str, ScheduledTask] = {}
        
        # 依赖关系
        self._dependents: Dict[str, Set[str]] = defaultdict(set)
        self._dependencies: Dict[str, Set[str]] = defaultdict(set)
        
        # 调度器组件
        self._executor: Optional[ThreadPoolExecutor] = None
        self._scheduler_thread: Optional[threading.Thread] = None
        self._running = False
        
        # 指标
        self._metrics = SchedulerMetrics()
        self._start_time: Optional[float] = None
        
        # 回调函数
        self._on_task_complete: Optional[Callable] = None
        self._on_task_fail: Optional[Callable] = None
        self._on_task_submit: Optional[Callable] = None

    @property
    def status(self) -> SchedulerStatus:
        return self._status

    @property
    def metrics(self) -> SchedulerMetrics:
        return self._metrics

    @property
    def queue_size(self) -> int:
        with self._lock:
            return len(self._task_queue)

    def set_callbacks(
        self,
        on_submit: Optional[Callable] = None,
        on_complete: Optional[Callable] = None,
        on_fail: Optional[Callable] = None
    ):
        """设置回调函数"""
        self._on_task_submit = on_submit
        self._on_task_complete = on_complete
        self._on_task_fail = on_fail

    def submit(
        self,
        task: Union[TaskTuple, Callable],
        task_id: Optional[str] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        dependencies: Optional[Set[str]] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        提交任务

        Args:
            task: 任务或函数
            task_id: 任务ID（可选，自动生成）
            priority: 任务优先级
            dependencies: 依赖的任务ID集合
            metadata: 元数据

        Returns:
            任务ID
        """
        with self._lock:
            if self._status == SchedulerStatus.STOPPED:
                raise RuntimeError("Scheduler is stopped")
            
            # 生成任务ID
            tid = task_id or str(uuid.uuid4())
            
            # 检查重复
            if self.config.enable_deduplication and tid in self._tasks:
                raise ValueError(f"Task {tid} already exists")
            
            # 检查依赖
            deps = dependencies or set()
            if deps and not all(dep in self._completed_tasks or dep in self._tasks for dep in deps):
                raise ValueError(f"Dependency task not found")
            
            # 创建调度任务
            scheduled_task = ScheduledTask(
                task_id=tid,
                task=task,
                priority=priority,
                dependencies=deps,
                metadata=metadata or {}
            )
            
            # 添加到任务存储
            self._tasks[tid] = scheduled_task
            
            # 更新依赖关系
            for dep in deps:
                self._dependents[dep].add(tid)
            
            # 更新指标
            self._metrics.total_tasks += 1
            self._metrics.pending_tasks += 1
            
            # 调度任务
            self._schedule_task(scheduled_task)
            
            # 触发回调
            if self._on_task_submit:
                self._on_task_submit(scheduled_task)
            
            return tid

    def submit_batch(
        self,
        tasks: List[Union[TaskTuple, Callable]],
        priorities: Optional[List[TaskPriority]] = None
    ) -> List[str]:
        """
        批量提交任务

        Args:
            tasks: 任务列表
            priorities: 优先级列表（可选）

        Returns:
            任务ID列表
        """
        task_ids = []
        for i, task in enumerate(tasks):
            priority = priorities[i] if priorities and i < len(priorities) else TaskPriority.NORMAL
            tid = self.submit(task, priority=priority)
            task_ids.append(tid)
        return task_ids

    def _schedule_task(self, task: ScheduledTask):
        """调度任务"""
        task.scheduled_at = time.time()
        
        if self.config.enable_priorities:
            heapq.heappush(self._task_queue, task)
        else:
            self._task_queue.put(task)

    def start(self):
        """启动调度器"""
        with self._lock:
            if self._status == SchedulerStatus.RUNNING:
                return
            
            self._running = True
            self._status = SchedulerStatus.RUNNING
            self._start_time = time.time()
            
            # 创建线程池
            self._executor = ThreadPoolExecutor(
                max_workers=self.config.max_workers,
                thread_name_prefix="scheduler_worker_"
            )
            
            # 启动调度线程
            self._scheduler_thread = threading.Thread(
                target=self._scheduler_loop,
                daemon=True,
                name="TaskScheduler"
            )
            self._scheduler_thread.start()

    def _scheduler_loop(self):
        """调度器主循环"""
        while self._running:
            try:
                self._dispatch_tasks()
                time.sleep(0.01)  # 避免CPU过度使用
            except Exception as e:
                print(f"Scheduler error: {e}")

    def _dispatch_tasks(self):
        """分发任务"""
        with self._lock:
            # 检查是否可以分发新任务
            if len(self._running_tasks) >= self.config.max_workers:
                return
            
            # 获取可调度的任务
            available_tasks = self._get_available_tasks()
            
            # 分发任务
            for task in available_tasks[:self.config.max_workers - len(self._running_tasks)]:
                self._execute_task(task)

    def _get_available_tasks(self) -> List[ScheduledTask]:
        """获取可调度的任务"""
        available = []
        
        # 清空队列获取所有待调度的任务
        temp_queue = []
        while self._task_queue:
            if self.config.enable_priorities:
                try:
                    task = heapq.heappop(self._task_queue)
                    temp_queue.append(task)
                except IndexError:
                    break
            else:
                try:
                    task = self._task_queue.get_nowait()
                    temp_queue.append(task)
                except Empty:
                    break
        
        # 放回不满足条件的任务
        for task in temp_queue:
            if self._are_dependencies_met(task):
                available.append(task)
            else:
                # 重新调度
                if self.config.enable_priorities:
                    heapq.heappush(self._task_queue, task)
                else:
                    self._task_queue.put(task)
        
        return available

    def _are_dependencies_met(self, task: ScheduledTask) -> bool:
        """检查依赖是否满足"""
        for dep_id in task.dependencies:
            dep_task = self._tasks.get(dep_id)
            if dep_task and dep_task.status != ExecutionStatus.COMPLETED:
                return False
        return True

    def _execute_task(self, task: ScheduledTask):
        """执行任务"""
        task.started_at = time.time()
        task.status = ExecutionStatus.RUNNING
        
        self._metrics.pending_tasks -= 1
        self._metrics.running_tasks += 1
        
        # 提交到线程池
        future = self._executor.submit(self._execute_task_wrapper, task)
        self._running_tasks[task.task_id] = future

    def _execute_task_wrapper(self, task: ScheduledTask):
        """任务执行包装器"""
        try:
            # 执行任务
            if callable(task.task):
                result = task.task()
            elif isinstance(task.task, TaskTuple):
                result = f"Executed: {task.task.target}"
            else:
                result = None
            
            # 标记完成
            self._complete_task(task, result)
            
        except Exception as e:
            # 标记失败
            self._fail_task(task, str(e))

    def _complete_task(self, task: ScheduledTask, result: Any):
        """完成任务"""
        with self._lock:
            task.completed_at = time.time()
            task.status = ExecutionStatus.COMPLETED
            task.result = result
            
            # 更新指标
            self._metrics.running_tasks -= 1
            self._metrics.completed_tasks += 1
            
            execution_time = task.completed_at - task.started_at
            self._metrics.total_execution_time += execution_time
            
            # 更新指标计算
            if self._metrics.completed_tasks > 0:
                self._metrics.throughput = self._metrics.completed_tasks / (time.time() - self._start_time)
            
            # 移动到完成队列
            if task.task_id in self._running_tasks:
                del self._running_tasks[task.task_id]
            self._completed_tasks[task.task_id] = task
            
            # 触发回调
            if self._on_task_complete:
                self._on_task_complete(task)

    def _fail_task(self, task: ScheduledTask, error: str):
        """任务失败"""
        with self._lock:
            task.completed_at = time.time()
            task.status = ExecutionStatus.FAILED
            task.error = error
            
            # 更新指标
            self._metrics.running_tasks -= 1
            self._metrics.failed_tasks += 1
            
            # 移动到完成队列
            if task.task_id in self._running_tasks:
                del self._running_tasks[task.task_id]
            self._completed_tasks[task.task_id] = task
            
            # 触发回调
            if self._on_task_fail:
                self._on_task_fail(task, error)

    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """获取任务"""
        return self._tasks.get(task_id)

    def get_task_status(self, task_id: str) -> Optional[ExecutionStatus]:
        """获取任务状态"""
        task = self._tasks.get(task_id)
        return task.status if task else None

    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            
            if task.status == ExecutionStatus.RUNNING:
                future = self._running_tasks.get(task_id)
                if future:
                    future.cancel()
                    del self._running_tasks[task_id]
                    self._metrics.running_tasks -= 1
                    self._metrics.cancelled_tasks += 1
                    return True
            elif task.status == ExecutionStatus.PENDING:
                # 从队列中移除
                if self.config.enable_priorities:
                    self._task_queue = [t for t in self._task_queue if t.task_id != task_id]
                    heapq.heapify(self._task_queue)
                else:
                    temp_queue = Queue()
                    while not self._task_queue.empty():
                        try:
                            t = self._task_queue.get_nowait()
                            if t.task_id != task_id:
                                temp_queue.put(t)
                        except Empty:
                            break
                    self._task_queue = temp_queue
                
                self._metrics.pending_tasks -= 1
                self._metrics.cancelled_tasks += 1
                return True
            
            return False

    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """
        等待所有任务完成

        Args:
            timeout: 超时时间（秒）

        Returns:
            是否全部完成
        """
        start_time = time.time()
        
        while True:
            with self._lock:
                if not self._running_tasks and not self._task_queue:
                    return True
            
            if timeout and (time.time() - start_time) > timeout:
                return False
            
            time.sleep(0.1)

    def pause(self):
        """暂停调度器"""
        with self._lock:
            if self._status == SchedulerStatus.RUNNING:
                self._status = SchedulerStatus.PAUSED

    def resume(self):
        """恢复调度器"""
        with self._lock:
            if self._status == SchedulerStatus.PAUSED:
                self._status = SchedulerStatus.RUNNING

    def stop(self):
        """停止调度器"""
        with self._lock:
            self._running = False
            self._status = SchedulerStatus.STOPPED
            
            if self._executor:
                self._executor.shutdown(wait=False)
            
            self._task_queue.clear()
            self._running_tasks.clear()

    def get_metrics(self) -> SchedulerMetrics:
        """获取调度器指标"""
        with self._lock:
            return self._metrics

    def reset_metrics(self):
        """重置指标"""
        with self._lock:
            self._metrics = SchedulerMetrics()


def create_scheduler(
    strategy: SchedulerStrategy = SchedulerStrategy.PRIORITY,
    max_workers: int = 4,
    enable_priorities: bool = True
) -> TaskScheduler:
    """
    创建任务调度器工厂函数

    Args:
        strategy: 调度策略
        max_workers: 最大工作线程数
        enable_priorities: 是否启用优先级

    Returns:
        配置好的任务调度器
    """
    config = SchedulerConfig(
        strategy=strategy,
        max_workers=max_workers,
        enable_priorities=enable_priorities
    )
    
    return TaskScheduler(config=config)
