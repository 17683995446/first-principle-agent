"""
TaskPlanningSystem - 第54阶段：任务规划系统整合层
将所有核心组件有机整合，提供从自然语言需求到任务执行的完整流程
"""
import uuid
import time
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum
from dataclasses import dataclass, field
from collections import OrderedDict

from .base import JSONSerializable, TaskPlanningError, ErrorCode
from .task_tuple import TaskTuple
from .dag_structures import TaskDAG
from .atomic_action import AtomicActionPlan
from .task_execution_engine import (
    TaskExecutionEngine,
    ExecutionConfig,
    ExecutionMode,
    ExecutionSummary,
    create_execution_engine
)
from .task_pipeline import TaskPipeline, create_pipeline
from .task_scheduler import TaskScheduler, TaskPriority, create_scheduler

from ..layers import (
    TaskNormalizer,
    TaskPlanner,
    AtomicActionSplitter,
    AtomicActionValidator,
    AtomicActionExecutor,
    AtomicActionMonitor,
    ResilienceManager,
    ResiliencePreset,
    create_resilience_manager
)


class SystemStatus(Enum):
    """系统状态枚举"""
    IDLE = "idle"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    SHUTDOWN = "shutdown"


@dataclass
class SystemConfig:
    """系统配置"""
    name: str = "TaskPlanningSystem"
    auto_start_scheduler: bool = True
    use_resilience: bool = True
    resilience_preset: ResiliencePreset = ResiliencePreset.DEFAULT
    execution_mode: ExecutionMode = ExecutionMode.DAG
    enable_monitoring: bool = True
    enable_checkpoints: bool = True


@dataclass
class TaskRequest:
    """任务请求"""
    request_id: str
    requirement: str
    priority: TaskPriority = TaskPriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


@dataclass
class TaskResult:
    """任务结果"""
    request_id: str
    success: bool
    task_tuple: Optional[TaskTuple] = None
    task_dag: Optional[TaskDAG] = None
    atomic_plan: Optional[AtomicActionPlan] = None
    execution_summary: Optional[ExecutionSummary] = None
    error_message: Optional[str] = None
    start_time: float = 0.0
    end_time: float = 0.0
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time


@dataclass
class SystemMetrics:
    """系统指标"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_execution_time: float = 0.0
    avg_execution_time: float = 0.0
    requests_per_minute: float = 0.0
    status_counts: Dict[SystemStatus, int] = field(default_factory=dict)
    
    def record_request(self, success: bool, execution_time: float):
        """记录请求"""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        self.total_execution_time += execution_time
        if self.total_requests > 0:
            self.avg_execution_time = self.total_execution_time / self.total_requests


class TaskPlanningSystem:
    """
    任务规划系统整合类
    提供从自然语言需求到任务执行的完整流程
    """
    
    def __init__(self, config: Optional[SystemConfig] = None):
        """
        初始化任务规划系统
        
        Args:
            config: 系统配置
        """
        self.id = str(uuid.uuid4())
        self.config = config or SystemConfig()
        self.status = SystemStatus.INITIALIZING
        
        # 核心组件
        self.task_normalizer: Optional[TaskNormalizer] = None
        self.task_planner: Optional[TaskPlanner] = None
        self.atomic_splitter: Optional[AtomicActionSplitter] = None
        self.atomic_validator: Optional[AtomicActionValidator] = None
        self.atomic_executor: Optional[AtomicActionExecutor] = None
        self.atomic_monitor: Optional[AtomicActionMonitor] = None
        self.resilience_manager: Optional[ResilienceManager] = None
        self.execution_engine: Optional[TaskExecutionEngine] = None
        self.task_scheduler: Optional[TaskScheduler] = None
        
        # 任务管理
        self._pending_requests: OrderedDict[str, TaskRequest] = OrderedDict()
        self._active_tasks: Dict[str, TaskRequest] = {}
        self._completed_tasks: Dict[str, TaskResult] = {}
        
        # 指标统计
        self.metrics = SystemMetrics()
        self._start_time = time.time()
        
        # 回调函数
        self._on_task_start: Optional[Callable[[TaskRequest], None]] = None
        self._on_task_complete: Optional[Callable[[TaskResult], None]] = None
        self._on_task_failed: Optional[Callable[[TaskRequest, str], None]] = None
        
        # 初始化组件
        self._initialize_components()
        self.status = SystemStatus.READY
    
    def _initialize_components(self):
        """初始化所有核心组件"""
        # 任务归一建模层
        self.task_normalizer = TaskNormalizer()
        
        # 拓扑依赖拆解层
        self.task_planner = TaskPlanner()
        
        # 原子动作收敛层
        self.atomic_splitter = AtomicActionSplitter()
        self.atomic_validator = AtomicActionValidator()
        self.atomic_executor = AtomicActionExecutor()
        
        if self.config.enable_monitoring:
            self.atomic_monitor = AtomicActionMonitor()
        
        # 分段校验收敛层
        if self.config.use_resilience:
            self.resilience_manager = create_resilience_manager(
                preset=self.config.resilience_preset
            )
        
        # 核心执行层
        self.execution_engine = create_execution_engine(
            mode=self.config.execution_mode,
            enable_resilience=self.config.use_resilience,
            resilience_preset=self.config.resilience_preset.value
        )
        
        self.task_scheduler = create_scheduler()
        
        if self.config.auto_start_scheduler:
            self.task_scheduler.start()
    
    def set_callbacks(
        self,
        on_task_start: Optional[Callable[[TaskRequest], None]] = None,
        on_task_complete: Optional[Callable[[TaskResult], None]] = None,
        on_task_failed: Optional[Callable[[TaskRequest, str], None]] = None
    ):
        """
        设置回调函数
        
        Args:
            on_task_start: 任务开始回调
            on_task_complete: 任务完成回调
            on_task_failed: 任务失败回调
        """
        self._on_task_start = on_task_start
        self._on_task_complete = on_task_complete
        self._on_task_failed = on_task_failed
    
    def submit_requirement(
        self,
        requirement: str,
        priority: TaskPriority = TaskPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        提交需求
        
        Args:
            requirement: 自然语言需求
            priority: 任务优先级
            metadata: 额外元数据
        
        Returns:
            request_id: 请求ID
        """
        request_id = str(uuid.uuid4())
        request = TaskRequest(
            request_id=request_id,
            requirement=requirement,
            priority=priority,
            metadata=metadata or {}
        )
        
        self._pending_requests[request_id] = request
        
        # 通过调度器提交
        def task_func():
            return self._process_request(request_id)
        
        self.task_scheduler.submit(
            task_func,
            task_id=request_id,
            priority=priority
        )
        
        return request_id
    
    def _process_request(self, request_id: str) -> TaskResult:
        """
        处理单个请求
        
        Args:
            request_id: 请求ID
        
        Returns:
            TaskResult: 任务结果
        """
        start_time = time.time()
        request = self._pending_requests.pop(request_id, None)
        
        if not request:
            return TaskResult(
                request_id=request_id,
                success=False,
                error_message=f"Request {request_id} not found",
                start_time=start_time,
                end_time=time.time()
            )
        
        self._active_tasks[request_id] = request
        
        if self._on_task_start:
            self._on_task_start(request)
        
        result = TaskResult(
            request_id=request_id,
            success=False,
            start_time=start_time
        )
        
        try:
            # 步骤1: 需求归一化
            task_tuple = self.task_normalizer.normalize(request.requirement)
            result.task_tuple = task_tuple
            
            # 步骤2: 生成DAG
            plan_result = self.task_planner.plan(task_tuple)
            result.task_dag = plan_result.optimized_dag
            
            # 步骤3: 拆分为原子动作
            atomic_plan = self.atomic_splitter.split(plan_result.optimized_dag)
            result.atomic_plan = atomic_plan
            
            # 步骤4: 验证原子动作计划
            validation_result = self.atomic_validator.validate(atomic_plan)
            if not validation_result.is_valid:
                raise TaskPlanningError(
                    code=ErrorCode.VALIDATION_ERROR,
                    message=f"Atomic plan validation failed: {validation_result.errors}"
                )
            
            # 步骤5: 执行原子动作
            if self.atomic_monitor:
                self.atomic_monitor.start_monitoring(atomic_plan)
            
            execution_result = self.atomic_executor.execute(atomic_plan)
            
            if self.atomic_monitor:
                self.atomic_monitor.stop_monitoring()
            
            # 生成执行摘要
            summary = ExecutionSummary(
                success=execution_result.success,
                total_actions=len(atomic_plan.actions),
                completed_actions=len([a for a in atomic_plan.actions if a.status.is_completed]),
                failed_actions=len([a for a in atomic_plan.actions if a.status.is_failed]),
                execution_time=execution_result.execution_time,
                results=execution_result.results
            )
            result.execution_summary = summary
            result.success = summary.success
            
        except Exception as e:
            result.error_message = str(e)
            result.success = False
            
            if self._on_task_failed:
                self._on_task_failed(request, str(e))
        
        finally:
            self._active_tasks.pop(request_id, None)
            result.end_time = time.time()
            self._completed_tasks[request_id] = result
            
            self.metrics.record_request(
                success=result.success,
                execution_time=result.duration
            )
            
            if self._on_task_complete:
                self._on_task_complete(result)
        
        return result
    
    def execute_requirement(
        self,
        requirement: str,
        priority: TaskPriority = TaskPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None
    ) -> TaskResult:
        """
        同步执行需求
        
        Args:
            requirement: 自然语言需求
            priority: 任务优先级
            metadata: 额外元数据
            timeout: 超时时间(秒)
        
        Returns:
            TaskResult: 任务结果
        """
        request_id = self.submit_requirement(requirement, priority, metadata)
        return self.wait_for_result(request_id, timeout=timeout)
    
    def wait_for_result(
        self,
        request_id: str,
        timeout: Optional[float] = None,
        poll_interval: float = 0.1
    ) -> TaskResult:
        """
        等待任务结果
        
        Args:
            request_id: 请求ID
            timeout: 超时时间(秒)
            poll_interval: 轮询间隔(秒)
        
        Returns:
            TaskResult: 任务结果
        """
        start_time = time.time()
        
        while True:
            if request_id in self._completed_tasks:
                return self._completed_tasks[request_id]
            
            if timeout and (time.time() - start_time) > timeout:
                return TaskResult(
                    request_id=request_id,
                    success=False,
                    error_message=f"Task {request_id} timed out after {timeout}s",
                    start_time=start_time,
                    end_time=time.time()
                )
            
            time.sleep(poll_interval)
    
    def get_request_status(self, request_id: str) -> Optional[str]:
        """
        获取请求状态
        
        Args:
            request_id: 请求ID
        
        Returns:
            状态字符串
        """
        if request_id in self._pending_requests:
            return "pending"
        if request_id in self._active_tasks:
            return "active"
        if request_id in self._completed_tasks:
            task = self._completed_tasks[request_id]
            return "completed" if task.success else "failed"
        return None
    
    def get_result(self, request_id: str) -> Optional[TaskResult]:
        """
        获取任务结果
        
        Args:
            request_id: 请求ID
        
        Returns:
            TaskResult: 任务结果
        """
        return self._completed_tasks.get(request_id)
    
    def get_all_pending_requests(self) -> List[TaskRequest]:
        """获取所有待处理请求"""
        return list(self._pending_requests.values())
    
    def get_all_active_tasks(self) -> List[TaskRequest]:
        """获取所有活跃任务"""
        return list(self._active_tasks.values())
    
    def get_all_completed_tasks(self, limit: int = 100) -> List[TaskResult]:
        """
        获取所有已完成任务
        
        Args:
            limit: 限制返回数量
        
        Returns:
            TaskResult列表
        """
        tasks = list(self._completed_tasks.values())
        return tasks[-limit:]
    
    def pause(self):
        """暂停系统"""
        if self.status == SystemStatus.RUNNING:
            self.status = SystemStatus.PAUSED
            if self.task_scheduler:
                self.task_scheduler.pause()
    
    def resume(self):
        """恢复系统"""
        if self.status == SystemStatus.PAUSED:
            self.status = SystemStatus.READY
            if self.task_scheduler:
                self.task_scheduler.resume()
    
    def shutdown(self, wait: bool = True, timeout: float = 30.0):
        """
        关闭系统

        Args:
            wait: 是否等待任务完成
            timeout: 等待超时时间
        """
        self.status = SystemStatus.SHUTDOWN
        
        if self.task_scheduler:
            if wait:
                self.task_scheduler.wait_for_completion(timeout=timeout)
            self.task_scheduler.stop()
        
        if self.atomic_monitor:
            self.atomic_monitor.stop_monitoring()
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        获取系统信息
        
        Returns:
            系统信息字典
        """
        return {
            "system_id": self.id,
            "system_name": self.config.name,
            "status": self.status.value,
            "uptime": time.time() - self._start_time,
            "metrics": {
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "avg_execution_time": self.metrics.avg_execution_time,
                "success_rate": (
                    self.metrics.successful_requests / self.metrics.total_requests * 100
                    if self.metrics.total_requests > 0 else 0
                )
            },
            "pending_count": len(self._pending_requests),
            "active_count": len(self._active_tasks),
            "completed_count": len(self._completed_tasks)
        }


def create_planning_system(
    name: str = "TaskPlanningSystem",
    auto_start: bool = True,
    use_resilience: bool = True,
    resilience_preset: ResiliencePreset = ResiliencePreset.DEFAULT
) -> TaskPlanningSystem:
    """
    创建任务规划系统的工厂函数
    
    Args:
        name: 系统名称
        auto_start: 是否自动启动调度器
        use_resilience: 是否使用韧性管理
        resilience_preset: 韧性预设
    
    Returns:
        TaskPlanningSystem实例
    """
    config = SystemConfig(
        name=name,
        auto_start_scheduler=auto_start,
        use_resilience=use_resilience,
        resilience_preset=resilience_preset
    )
    return TaskPlanningSystem(config=config)
