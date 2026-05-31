"""
任务执行引擎 - 核心执行组件
"""

from enum import Enum
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import uuid
from typing import Callable, Optional, Any, Dict, List, Set, Union
from dataclasses import dataclass, field
from collections import defaultdict

from first_principle_agent.core.base import JSONSerializable
from first_principle_agent.core.task_tuple import TaskTuple
from first_principle_agent.core.dag_structures import TaskDAG, DAGNode, DAGEdge
from first_principle_agent.core.atomic_action import AtomicAction, AtomicActionStatus, AtomicActionPlan

from first_principle_agent.layers.resilience_manager import (
    ResilienceManager, ResiliencePreset, create_resilience_manager
)
from first_principle_agent.layers.resilience_orchestrator import ExecutionContext
from first_principle_agent.layers.atomic_action_executor import AtomicActionExecutor, ExecutionResult
from first_principle_agent.layers.atomic_action_monitor import AtomicActionMonitor, ActionMetrics


class ExecutionStatus(Enum):
    """执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class ExecutionMode(Enum):
    """执行模式"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    DAG = "dag"
    PIPELINE = "pipeline"


@dataclass
class ExecutionConfig(JSONSerializable):
    """执行配置"""
    mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    enable_parallel: bool = False
    max_parallel_tasks: int = 4
    enable_resilience: bool = True
    resilience_preset: str = "default"
    enable_monitoring: bool = True
    enable_checkpoint: bool = True
    checkpoint_interval: int = 10
    timeout_seconds: float = 300.0
    retry_on_failure: bool = True
    max_retries: int = 3
    log_execution: bool = True
    propagate_exceptions: bool = True

    def to_dict(self) -> Dict:
        return {
            "mode": self.mode.value,
            "enable_parallel": self.enable_parallel,
            "max_parallel_tasks": self.max_parallel_tasks,
            "enable_resilience": self.enable_resilience,
            "resilience_preset": self.resilience_preset,
            "enable_monitoring": self.enable_monitoring,
            "enable_checkpoint": self.enable_checkpoint,
            "checkpoint_interval": self.checkpoint_interval,
            "timeout_seconds": self.timeout_seconds,
            "retry_on_failure": self.retry_on_failure,
            "max_retries": self.max_retries,
            "log_execution": self.log_execution,
            "propagate_exceptions": self.propagate_exceptions
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ExecutionConfig":
        return cls(
            mode=ExecutionMode(data.get("mode", "sequential")),
            enable_parallel=data.get("enable_parallel", False),
            max_parallel_tasks=data.get("max_parallel_tasks", 4),
            enable_resilience=data.get("enable_resilience", True),
            resilience_preset=data.get("resilience_preset", "default"),
            enable_monitoring=data.get("enable_monitoring", True),
            enable_checkpoint=data.get("enable_checkpoint", True),
            checkpoint_interval=data.get("checkpoint_interval", 10),
            timeout_seconds=data.get("timeout_seconds", 300.0),
            retry_on_failure=data.get("retry_on_failure", True),
            max_retries=data.get("max_retries", 3),
            log_execution=data.get("log_execution", True),
            propagate_exceptions=data.get("propagate_exceptions", True)
        )


@dataclass
class TaskExecutionResult(JSONSerializable):
    """任务执行结果"""
    task_id: str
    status: ExecutionStatus
    start_time: float
    end_time: Optional[float] = None
    execution_time: Optional[float] = None
    result: Any = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    retry_count: int = 0
    metrics: Dict[str, Any] = field(default_factory=dict)
    dependencies_results: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "execution_time": self.execution_time,
            "result": str(self.result) if self.result is not None else None,
            "error": self.error,
            "error_type": self.error_type,
            "retry_count": self.retry_count,
            "metrics": self.metrics,
            "dependencies_results": self.dependencies_results
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "TaskExecutionResult":
        return cls(
            task_id=data["task_id"],
            status=ExecutionStatus(data.get("status", "pending")),
            start_time=data.get("start_time", time.time()),
            end_time=data.get("end_time"),
            execution_time=data.get("execution_time"),
            result=data.get("result"),
            error=data.get("error"),
            error_type=data.get("error_type"),
            retry_count=data.get("retry_count", 0),
            metrics=data.get("metrics", {}),
            dependencies_results=data.get("dependencies_results", {})
        )


@dataclass
class ExecutionPlan(JSONSerializable):
    """执行计划"""
    id: str
    config: ExecutionConfig
    tasks: List[TaskTuple] = field(default_factory=list)
    dag: Optional[TaskDAG] = None
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "config": self.config.to_dict(),
            "created_at": self.created_at,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ExecutionPlan":
        return cls(
            id=data["id"],
            config=ExecutionConfig.from_dict(data.get("config", {})),
            created_at=data.get("created_at", time.time()),
            metadata=data.get("metadata", {})
        )


@dataclass
class ExecutionSummary(JSONSerializable):
    """执行摘要"""
    plan_id: str
    status: ExecutionStatus
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    total_time: float
    start_time: float
    end_time: Optional[float] = None
    results: List[TaskExecutionResult] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "plan_id": self.plan_id,
            "status": self.status.value,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "total_time": self.total_time,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "metrics": self.metrics
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ExecutionSummary":
        return cls(
            plan_id=data["plan_id"],
            status=ExecutionStatus(data.get("status", "completed")),
            total_tasks=data.get("total_tasks", 0),
            completed_tasks=data.get("completed_tasks", 0),
            failed_tasks=data.get("failed_tasks", 0),
            total_time=data.get("total_time", 0.0),
            start_time=data.get("start_time", time.time()),
            end_time=data.get("end_time")
        )


class ExecutionEventType(Enum):
    """执行事件类型"""
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    TASK_RETRY = "task_retry"
    PLAN_STARTED = "plan_started"
    PLAN_COMPLETED = "plan_completed"
    PLAN_FAILED = "plan_failed"
    METRICS_UPDATED = "metrics_updated"
    CHECKPOINT_CREATED = "checkpoint_created"


@dataclass
class ExecutionEvent:
    """执行事件"""
    event_type: ExecutionEventType
    timestamp: float
    plan_id: str
    task_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)


class ExecutionEventListener:
    """执行事件监听器"""
    
    def __init__(self, callback: Callable[[ExecutionEvent], None]):
        self.callback = callback
    
    def on_event(self, event: ExecutionEvent):
        """处理事件"""
        self.callback(event)


class TaskExecutionEngine:
    """任务执行引擎 - 核心执行组件"""
    
    def __init__(
        self,
        config: Optional[ExecutionConfig] = None,
        resilience_manager: Optional[ResilienceManager] = None
    ):
        self.config = config or ExecutionConfig()
        self._id = str(uuid.uuid4())
        self._lock = threading.RLock()
        
        if self.config.enable_resilience:
            preset = ResiliencePreset(self.config.resilience_preset)
            self._resilience = resilience_manager or create_resilience_manager(preset)
        else:
            self._resilience = None
        
        self._executor = AtomicActionExecutor()
        self._monitor = AtomicActionMonitor() if self.config.enable_monitoring else None
        
        self._event_listeners: List[ExecutionEventListener] = []
        self._event_queue: List[ExecutionEvent] = []
        self._event_thread: Optional[threading.Thread] = None
        self._running = False
        
        self._status = ExecutionStatus.PENDING
        self._current_plan: Optional[ExecutionPlan] = None
        self._results: Dict[str, TaskExecutionResult] = {}
        self._execution_history: List[ExecutionSummary] = []
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def status(self) -> ExecutionStatus:
        return self._status
    
    @property
    def resilience_manager(self) -> Optional[ResilienceManager]:
        return self._resilience
    
    @property
    def monitor(self) -> Optional[AtomicActionMonitor]:
        return self._monitor
    
    def add_event_listener(self, listener: ExecutionEventListener):
        with self._lock:
            self._event_listeners.append(listener)
    
    def remove_event_listener(self, listener: ExecutionEventListener):
        with self._lock:
            if listener in self._event_listeners:
                self._event_listeners.remove(listener)
    
    def _emit_event(self, event: ExecutionEvent):
        with self._lock:
            self._event_queue.append(event)
    
    def _start_event_processor(self):
        self._running = True
        
        def process_events():
            while self._running:
                if self._event_queue:
                    event = self._event_queue.pop(0)
                    for listener in self._event_listeners:
                        try:
                            listener.on_event(event)
                        except Exception as e:
                            if self.config.log_execution:
                                print(f"Event processing error: {e}")
                time.sleep(0.01)
        
        self._event_thread = threading.Thread(target=process_events, daemon=True)
        self._event_thread.start()
    
    def _stop_event_processor(self):
        self._running = False
        if self._event_thread:
            self._event_thread.join(timeout=1.0)
    
    def _create_execution_result(
        self,
        task_id: str,
        status: ExecutionStatus,
        start_time: float,
        result: Any = None,
        error: Optional[str] = None,
        error_type: Optional[str] = None,
        retry_count: int = 0
    ) -> TaskExecutionResult:
        end_time = time.time()
        return TaskExecutionResult(
            task_id=task_id,
            status=status,
            start_time=start_time,
            end_time=end_time,
            execution_time=end_time - start_time,
            result=result,
            error=error,
            error_type=error_type,
            retry_count=retry_count,
            metrics=self._monitor.metrics if self._monitor else {}
        )
    
    def _execute_single_task(
        self,
        task: TaskTuple,
        dependencies_results: Dict[str, Any] = None
    ) -> TaskExecutionResult:
        start_time = time.time()
        task_id = task.target
        
        self._emit_event(ExecutionEvent(
            event_type=ExecutionEventType.TASK_STARTED,
            timestamp=start_time,
            plan_id=self._current_plan.id if self._current_plan else self._id,
            task_id=task_id
        ))
        
        retry_count = 0
        last_error = None
        
        def execute_task():
            try:
                result = f"Executed: {task.target}"
                
                if self._resilience:
                    def task_func():
                        return result
                    return self._resilience.execute(task_func, operation_name=task.target)
                else:
                    return result
                    
            except Exception as e:
                nonlocal last_error
                last_error = str(e)
                raise
        
        max_retries = self.config.max_retries if self.config.retry_on_failure else 0
        
        for attempt in range(max_retries + 1):
            try:
                result = execute_task()
                
                task_result = self._create_execution_result(
                    task_id=task_id,
                    status=ExecutionStatus.COMPLETED,
                    start_time=start_time,
                    result=result,
                    retry_count=attempt
                )
                
                self._emit_event(ExecutionEvent(
                    event_type=ExecutionEventType.TASK_COMPLETED,
                    timestamp=time.time(),
                    plan_id=self._current_plan.id if self._current_plan else self._id,
                    task_id=task_id,
                    data={"result": result}
                ))
                
                return task_result
                
            except Exception as e:
                retry_count = attempt + 1
                last_error = str(e)
                
                if attempt < max_retries:
                    self._emit_event(ExecutionEvent(
                        event_type=ExecutionEventType.TASK_RETRY,
                        timestamp=time.time(),
                        plan_id=self._current_plan.id if self._current_plan else self._id,
                        task_id=task_id,
                        data={"attempt": attempt + 1, "error": str(e)}
                    ))
        
        task_result = self._create_execution_result(
            task_id=task_id,
            status=ExecutionStatus.FAILED,
            start_time=start_time,
            error=last_error,
            error_type=type(last_error).__name__ if last_error else None,
            retry_count=retry_count
        )
        
        self._emit_event(ExecutionEvent(
            event_type=ExecutionEventType.TASK_FAILED,
            timestamp=time.time(),
            plan_id=self._current_plan.id if self._current_plan else self._id,
            task_id=task_id,
            data={"error": last_error}
        ))
        
        if self.config.propagate_exceptions:
            raise Exception(f"Task {task_id} failed: {last_error}")
        
        return task_result
    
    def execute_plan(self, plan: ExecutionPlan) -> ExecutionSummary:
        start_time = time.time()
        self._current_plan = plan
        self._status = ExecutionStatus.RUNNING
        self._results.clear()
        
        self._start_event_processor()
        
        self._emit_event(ExecutionEvent(
            event_type=ExecutionEventType.PLAN_STARTED,
            timestamp=start_time,
            plan_id=plan.id
        ))
        
        try:
            if plan.config.mode == ExecutionMode.SEQUENTIAL:
                results = self._execute_sequential(plan.tasks)
            elif plan.config.mode == ExecutionMode.PARALLEL:
                results = self._execute_parallel(plan.tasks)
            elif plan.config.mode == ExecutionMode.DAG and plan.dag:
                results = self._execute_dag(plan.tasks, plan.dag)
            else:
                results = self._execute_sequential(plan.tasks)
            
            self._status = ExecutionStatus.COMPLETED
            end_time = time.time()
            
            summary = ExecutionSummary(
                plan_id=plan.id,
                status=self._status,
                total_tasks=len(plan.tasks),
                completed_tasks=len([r for r in results if r.status == ExecutionStatus.COMPLETED]),
                failed_tasks=len([r for r in results if r.status == ExecutionStatus.FAILED]),
                total_time=end_time - start_time,
                start_time=start_time,
                end_time=end_time,
                results=results,
                metrics=self._monitor.metrics if self._monitor else {}
            )
            
            self._emit_event(ExecutionEvent(
                event_type=ExecutionEventType.PLAN_COMPLETED,
                timestamp=end_time,
                plan_id=plan.id,
                data={"summary": summary.to_dict()}
            ))
            
            self._execution_history.append(summary)
            return summary
            
        except Exception as e:
            self._status = ExecutionStatus.FAILED
            end_time = time.time()
            
            summary = ExecutionSummary(
                plan_id=plan.id,
                status=self._status,
                total_tasks=len(plan.tasks),
                completed_tasks=len([r for r in self._results.values() if r.status == ExecutionStatus.COMPLETED]),
                failed_tasks=len([r for r in self._results.values() if r.status == ExecutionStatus.FAILED]),
                total_time=end_time - start_time,
                start_time=start_time,
                end_time=end_time
            )
            
            self._emit_event(ExecutionEvent(
                event_type=ExecutionEventType.PLAN_FAILED,
                timestamp=end_time,
                plan_id=plan.id,
                data={"error": str(e)}
            ))
            
            self._execution_history.append(summary)
            raise
            
        finally:
            self._stop_event_processor()
            self._current_plan = None
    
    def _execute_sequential(self, tasks: List[TaskTuple]) -> List[TaskExecutionResult]:
        results = []
        dependencies_results = {}
        
        for task in tasks:
            result = self._execute_single_task(task, dependencies_results)
            results.append(result)
            self._results[task.target] = result
            
            if result.status == ExecutionStatus.COMPLETED:
                dependencies_results[task.target] = result.result
            elif self.config.propagate_exceptions:
                break
        
        return results
    
    def _execute_parallel(self, tasks: List[TaskTuple]) -> List[TaskExecutionResult]:
        results = []
        max_workers = min(self.config.max_parallel_tasks, len(tasks))
        
        def execute_task_wrapper(task):
            return self._execute_single_task(task)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(execute_task_wrapper, task) for task in tasks]
            results = [future.result() for future in futures]
        
        return results
    
    def _execute_dag(self, tasks: List[TaskTuple], dag: TaskDAG) -> List[TaskExecutionResult]:
        results = []
        dependencies_results = {}
        completed = set()
        
        while len(completed) < len(tasks):
            ready_tasks = []
            for task in tasks:
                if task.target in completed:
                    continue
                
                dependencies = dag.get_node_dependencies(task.target)
                if all(dep in completed for dep in dependencies):
                    ready_tasks.append(task)
            
            if not ready_tasks:
                break
            
            if self.config.enable_parallel:
                with ThreadPoolExecutor(max_workers=len(ready_tasks)) as executor:
                    futures = [executor.submit(self._execute_single_task, task, dependencies_results) 
                              for task in ready_tasks]
                    batch_results = [future.result() for future in futures]
            else:
                batch_results = [self._execute_single_task(task, dependencies_results) 
                                for task in ready_tasks]
            
            for result, task in zip(batch_results, ready_tasks):
                results.append(result)
                self._results[task.target] = result
                
                if result.status == ExecutionStatus.COMPLETED:
                    completed.add(task.target)
                    dependencies_results[task.target] = result.result
                elif self.config.propagate_exceptions:
                    return results
        
        return results
    
    def get_result(self, task_id: str) -> Optional[TaskExecutionResult]:
        return self._results.get(task_id)
    
    def get_execution_history(self) -> List[ExecutionSummary]:
        return self._execution_history
    
    def cancel(self):
        with self._lock:
            if self._status == ExecutionStatus.RUNNING:
                self._status = ExecutionStatus.CANCELLED
                self._stop_event_processor()
    
    def reset(self):
        with self._lock:
            self._status = ExecutionStatus.PENDING
            self._current_plan = None
            self._results.clear()
            # AtomicActionMonitor 没有 reset_metrics 方法，这里跳过
    
    def shutdown(self):
        self._stop_event_processor()
        if self._resilience:
            self._resilience.shutdown()


def create_execution_engine(
    mode: ExecutionMode = ExecutionMode.SEQUENTIAL,
    enable_resilience: bool = True,
    resilience_preset: str = "default"
) -> TaskExecutionEngine:
    """创建执行引擎工厂函数"""
    config = ExecutionConfig(
        mode=mode,
        enable_resilience=enable_resilience,
        resilience_preset=resilience_preset
    )
    
    return TaskExecutionEngine(config=config)
