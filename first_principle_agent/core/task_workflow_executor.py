"""
TaskWorkflowExecutor - 第56阶段：任务执行工作流编排器
整合所有核心组件，提供完整的任务执行工作流
"""
import uuid
import time
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict


class WorkflowStatus(Enum):
    """工作流状态"""
    CREATED = "created"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStepType(Enum):
    """工作流步骤类型"""
    TASK = "task"
    PIPELINE = "pipeline"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    SUBWORKFLOW = "subworkflow"
    CHECKPOINT = "checkpoint"
    ROLLBACK = "rollback"


class WorkflowStepStatus(Enum):
    """工作流步骤状态"""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """工作流步骤"""
    step_id: str
    name: str
    step_type: WorkflowStepType
    action: Union[Callable, str, Dict] = None
    dependencies: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    timeout: Optional[float] = None
    status: WorkflowStepStatus = WorkflowStepStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    def can_execute(self) -> bool:
        """检查是否可以执行"""
        return self.status == WorkflowStepStatus.PENDING or self.status == WorkflowStepStatus.READY
    
    def is_completed(self) -> bool:
        """检查是否完成"""
        return self.status in [WorkflowStepStatus.COMPLETED, WorkflowStepStatus.SKIPPED]
    
    def is_failed(self) -> bool:
        """检查是否失败"""
        return self.status == WorkflowStepStatus.FAILED
    
    def execute_time(self) -> float:
        """获取执行时间"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0


@dataclass
class WorkflowContext:
    """工作流上下文"""
    workflow_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    state: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """获取数据"""
        return self.data.get(key, default)
    
    def set_data(self, key: str, value: Any):
        """设置数据"""
        self.data[key] = value
    
    def get_result(self, step_id: str, default: Any = None) -> Any:
        """获取步骤结果"""
        return self.results.get(step_id, default)
    
    def set_result(self, step_id: str, result: Any):
        """设置步骤结果"""
        self.results[step_id] = result


@dataclass
class WorkflowDefinition:
    """工作流定义"""
    workflow_id: str
    name: str
    description: str = ""
    version: str = "1.0"
    steps: List[WorkflowStep] = field(default_factory=list)
    entry_point: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """获取步骤"""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def get_entry_step(self) -> Optional[WorkflowStep]:
        """获取入口步骤"""
        if self.entry_point:
            return self.get_step(self.entry_point)
        return self.steps[0] if self.steps else None
    
    def get_ready_steps(self) -> List[WorkflowStep]:
        """获取就绪的步骤"""
        ready = []
        for step in self.steps:
            if step.can_execute():
                deps_met = all(
                    self.get_step(dep_id) and self.get_step(dep_id).is_completed()
                    for dep_id in step.dependencies
                )
                if deps_met:
                    ready.append(step)
        return ready


@dataclass
class WorkflowExecution:
    """工作流执行"""
    execution_id: str
    workflow_id: str
    workflow_definition: WorkflowDefinition
    context: WorkflowContext
    status: WorkflowStatus = WorkflowStatus.CREATED
    current_steps: List[str] = field(default_factory=list)
    completed_steps: List[str] = field(default_factory=list)
    failed_steps: List[str] = field(default_factory=list)
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error: Optional[str] = None
    
    def execution_time(self) -> float:
        """获取执行时间"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        elif self.start_time:
            return time.time() - self.start_time
        return 0.0
    
    def progress(self) -> float:
        """获取进度"""
        total = len(self.workflow_definition.steps)
        if total == 0:
            return 0.0
        return len(self.completed_steps) / total


@dataclass
class WorkflowMetrics:
    """工作流指标"""
    total_workflows: int = 0
    completed_workflows: int = 0
    failed_workflows: int = 0
    cancelled_workflows: int = 0
    total_execution_time: float = 0.0
    avg_execution_time: float = 0.0
    
    def record_execution(self, execution: WorkflowExecution):
        """记录执行"""
        self.total_workflows += 1
        if execution.status == WorkflowStatus.COMPLETED:
            self.completed_workflows += 1
        elif execution.status == WorkflowStatus.FAILED:
            self.failed_workflows += 1
        elif execution.status == WorkflowStatus.CANCELLED:
            self.cancelled_workflows += 1
        
        if execution.end_time and execution.start_time:
            exec_time = execution.end_time - execution.start_time
            self.total_execution_time += exec_time
            if self.total_workflows > 0:
                self.avg_execution_time = self.total_execution_time / self.total_workflows


class TaskWorkflowExecutor:
    """
    任务工作流编排器
    整合所有核心组件，提供完整的任务执行工作流
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化工作流编排器
        
        Args:
            config: 配置字典
        """
        self.id = str(uuid.uuid4())
        self.config = config or {}
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.metrics = WorkflowMetrics()
        self._step_handlers: Dict[WorkflowStepType, Callable] = {}
        self._callbacks: Dict[str, List[Callable]] = defaultdict(list)
        
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """注册默认处理器"""
        self._step_handlers[WorkflowStepType.TASK] = self._handle_task_step
        self._step_handlers[WorkflowStepType.PIPELINE] = self._handle_pipeline_step
        self._step_handlers[WorkflowStepType.PARALLEL] = self._handle_parallel_step
        self._step_handlers[WorkflowStepType.CONDITIONAL] = self._handle_conditional_step
        self._step_handlers[WorkflowStepType.LOOP] = self._handle_loop_step
        self._step_handlers[WorkflowStepType.SUBWORKFLOW] = self._handle_subworkflow_step
        self._step_handlers[WorkflowStepType.CHECKPOINT] = self._handle_checkpoint_step
        self._step_handlers[WorkflowStepType.ROLLBACK] = self._handle_rollback_step
    
    def register_handler(self, step_type: WorkflowStepType, handler: Callable):
        """注册步骤处理器"""
        self._step_handlers[step_type] = handler
    
    def register_callback(self, event: str, callback: Callable):
        """注册回调"""
        self._callbacks[event].append(callback)
    
    def _emit_event(self, event: str, data: Any):
        """触发事件"""
        for callback in self._callbacks.get(event, []):
            try:
                callback(data)
            except Exception as e:
                print(f"Error in callback for event {event}: {e}")
    
    def create_workflow(
        self,
        name: str,
        description: str = "",
        config: Optional[Dict[str, Any]] = None
    ) -> WorkflowDefinition:
        """
        创建工作流
        
        Args:
            name: 工作流名称
            description: 工作流描述
            config: 配置
        
        Returns:
            WorkflowDefinition: 工作流定义
        """
        workflow_id = str(uuid.uuid4())
        workflow = WorkflowDefinition(
            workflow_id=workflow_id,
            name=name,
            description=description,
            config=config or {}
        )
        self.workflows[workflow_id] = workflow
        return workflow
    
    def add_step(
        self,
        workflow: WorkflowDefinition,
        name: str,
        step_type: WorkflowStepType,
        action: Union[Callable, str, Dict] = None,
        dependencies: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> WorkflowStep:
        """
        添加步骤
        
        Args:
            workflow: 工作流定义
            name: 步骤名称
            step_type: 步骤类型
            action: 步骤动作
            dependencies: 依赖的步骤ID列表
            config: 步骤配置
        
        Returns:
            WorkflowStep: 工作流步骤
        """
        step_id = str(uuid.uuid4())
        step = WorkflowStep(
            step_id=step_id,
            name=name,
            step_type=step_type,
            action=action,
            dependencies=dependencies or [],
            config=config or {}
        )
        workflow.steps.append(step)
        return step
    
    def execute_workflow(
        self,
        workflow_id: str,
        initial_data: Optional[Dict[str, Any]] = None
    ) -> WorkflowExecution:
        """
        执行工作流
        
        Args:
            workflow_id: 工作流ID
            initial_data: 初始数据
        
        Returns:
            WorkflowExecution: 工作流执行对象
        """
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        execution_id = str(uuid.uuid4())
        context = WorkflowContext(
            workflow_id=workflow_id,
            data=initial_data or {}
        )
        
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            workflow_definition=workflow,
            context=context
        )
        
        self.executions[execution_id] = execution
        
        self._emit_event("workflow_started", execution)
        
        return self._execute_workflow(execution)
    
    def _execute_workflow(self, execution: WorkflowExecution) -> WorkflowExecution:
        """执行工作流"""
        execution.status = WorkflowStatus.RUNNING
        execution.start_time = time.time()
        
        try:
            ready_steps = execution.workflow_definition.get_ready_steps()
            
            while ready_steps and execution.status == WorkflowStatus.RUNNING:
                for step in ready_steps[:1]:
                    result = self._execute_step(execution, step)
                    if result:
                        execution.completed_steps.append(step.step_id)
                    else:
                        execution.failed_steps.append(step.step_id)
                        if step.retry_count < step.max_retries:
                            step.retry_count += 1
                            step.status = WorkflowStepStatus.READY
                        else:
                            execution.status = WorkflowStatus.FAILED
                            execution.error = f"Step {step.name} failed"
                            break
                
                ready_steps = execution.workflow_definition.get_ready_steps()
                
                if not ready_steps:
                    break
            
            if execution.status == WorkflowStatus.RUNNING:
                if len(execution.completed_steps) == len(execution.workflow_definition.steps):
                    execution.status = WorkflowStatus.COMPLETED
                else:
                    execution.status = WorkflowStatus.FAILED
                    execution.error = "Workflow incomplete: some steps not executed"
        
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error = str(e)
        
        finally:
            execution.end_time = time.time()
            self.metrics.record_execution(execution)
            self._emit_event("workflow_completed", execution)
        
        return execution
    
    def _execute_step(self, execution: WorkflowExecution, step: WorkflowStep) -> bool:
        """执行步骤"""
        step.status = WorkflowStepStatus.RUNNING
        step.start_time = time.time()
        
        self._emit_event("step_started", (execution, step))
        
        try:
            handler = self._step_handlers.get(step.step_type)
            if handler:
                result = handler(execution, step)
                step.result = result
                step.status = WorkflowStepStatus.COMPLETED
                execution.context.set_result(step.step_id, result)
                self._emit_event("step_completed", (execution, step, result))
                return True
            else:
                step.error = f"No handler for step type {step.step_type}"
                step.status = WorkflowStepStatus.FAILED
                return False
        
        except Exception as e:
            step.error = str(e)
            step.status = WorkflowStepStatus.FAILED
            self._emit_event("step_failed", (execution, step, e))
            return False
        
        finally:
            step.end_time = time.time()
    
    def _handle_task_step(self, execution: WorkflowExecution, step: WorkflowStep) -> Any:
        """处理任务步骤"""
        if callable(step.action):
            return step.action(execution.context)
        return f"Task executed: {step.name}"
    
    def _handle_pipeline_step(self, execution: WorkflowExecution, step: WorkflowStep) -> Any:
        """处理管道步骤"""
        return f"Pipeline executed: {step.name}"
    
    def _handle_parallel_step(self, execution: WorkflowExecution, step: WorkflowStep) -> Any:
        """处理并行步骤"""
        return f"Parallel steps executed: {step.name}"
    
    def _handle_conditional_step(self, execution: WorkflowExecution, step: WorkflowStep) -> Any:
        """处理条件步骤"""
        condition = step.conditions.get("condition", True)
        if callable(condition):
            condition = condition(execution.context)
        return f"Conditional result: {condition}"
    
    def _handle_loop_step(self, execution: WorkflowExecution, step: WorkflowStep) -> Any:
        """处理循环步骤"""
        iterations = step.config.get("iterations", 1)
        results = []
        for i in range(iterations):
            results.append(f"Iteration {i+1}")
        return results
    
    def _handle_subworkflow_step(self, execution: WorkflowExecution, step: WorkflowStep) -> Any:
        """处理子工作流步骤"""
        subworkflow_id = step.config.get("subworkflow_id")
        if subworkflow_id and subworkflow_id in self.workflows:
            sub_execution = self.execute_workflow(subworkflow_id)
            return sub_execution.results
        return f"Subworkflow executed: {step.name}"
    
    def _handle_checkpoint_step(self, execution: WorkflowExecution, step: WorkflowStep) -> Any:
        """处理检查点步骤"""
        checkpoint_data = {
            "execution_id": execution.execution_id,
            "completed_steps": execution.completed_steps.copy(),
            "context_data": execution.context.data.copy(),
            "timestamp": time.time()
        }
        return checkpoint_data
    
    def _handle_rollback_step(self, execution: WorkflowExecution, step: WorkflowStep) -> Any:
        """处理回滚步骤"""
        rollback_data = step.config.get("rollback_data", {})
        return f"Rollback executed: {rollback_data}"
    
    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """获取执行"""
        return self.executions.get(execution_id)
    
    def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """获取工作流"""
        return self.workflows.get(workflow_id)
    
    def cancel_execution(self, execution_id: str) -> bool:
        """取消执行"""
        execution = self.executions.get(execution_id)
        if execution and execution.status == WorkflowStatus.RUNNING:
            execution.status = WorkflowStatus.CANCELLED
            execution.end_time = time.time()
            self.metrics.record_execution(execution)
            self._emit_event("workflow_cancelled", execution)
            return True
        return False
    
    def get_metrics(self) -> WorkflowMetrics:
        """获取指标"""
        return self.metrics
    
    def get_all_executions(self) -> List[WorkflowExecution]:
        """获取所有执行"""
        return list(self.executions.values())
    
    def get_executions_by_status(self, status: WorkflowStatus) -> List[WorkflowExecution]:
        """按状态获取执行"""
        return [e for e in self.executions.values() if e.status == status]


def create_workflow_executor(config: Optional[Dict[str, Any]] = None) -> TaskWorkflowExecutor:
    """
    创建工作流编排器工厂函数
    
    Args:
        config: 配置字典
    
    Returns:
        TaskWorkflowExecutor: 工作流编排器实例
    """
    return TaskWorkflowExecutor(config=config)
