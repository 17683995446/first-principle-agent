"""
任务管道 - 工作流编排和任务组合
"""

from enum import Enum
import time
import threading
import uuid
from typing import Callable, Optional, Any, Dict, List, Union, Tuple
from dataclasses import dataclass, field
from collections import OrderedDict

from first_principle_agent.core.base import JSONSerializable
from first_principle_agent.core.task_tuple import TaskTuple
from first_principle_agent.core.atomic_action import AtomicActionPlan
from first_principle_agent.core.task_execution_engine import (
    TaskExecutionEngine,
    ExecutionPlan,
    ExecutionSummary,
    TaskExecutionResult,
    ExecutionStatus,
    ExecutionMode,
    ExecutionConfig,
    create_execution_engine
)


class PipelineStatus(Enum):
    """管道状态"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PipelineStageType(Enum):
    """管道阶段类型"""
    TASK = "task"
    TRANSFORM = "transform"
    CONDITIONAL = "conditional"
    PARALLEL = "parallel"
    SEQUENCE = "sequence"


@dataclass
class PipelineStage(JSONSerializable):
    """管道阶段"""
    id: str
    name: str
    stage_type: PipelineStageType
    task: Optional[Union[TaskTuple, Callable]] = None
    transform: Optional[Callable] = None
    condition: Optional[Callable[[Any], bool]] = None
    sub_stages: List['PipelineStage'] = field(default_factory=list)
    enabled: bool = True
    timeout_seconds: Optional[float] = None
    retry_on_failure: bool = False
    max_retries: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "stage_type": self.stage_type.value,
            "enabled": self.enabled,
            "timeout_seconds": self.timeout_seconds,
            "retry_on_failure": self.retry_on_failure,
            "max_retries": self.max_retries,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'PipelineStage':
        return cls(
            id=data["id"],
            name=data.get("name", data["id"]),
            stage_type=PipelineStageType(data.get("stage_type", "task")),
            enabled=data.get("enabled", True),
            timeout_seconds=data.get("timeout_seconds"),
            retry_on_failure=data.get("retry_on_failure", False),
            max_retries=data.get("max_retries", 0),
            metadata=data.get("metadata", {})
        )


@dataclass
class PipelineStageResult(JSONSerializable):
    """管道阶段执行结果"""
    stage_id: str
    stage_name: str
    status: ExecutionStatus
    start_time: float
    end_time: Optional[float] = None
    execution_time: Optional[float] = None
    input_data: Any = None
    output_data: Any = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    retry_count: int = 0
    sub_stage_results: List['PipelineStageResult'] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "stage_id": self.stage_id,
            "stage_name": self.stage_name,
            "status": self.status.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "execution_time": self.execution_time,
            "error": self.error,
            "error_type": self.error_type,
            "retry_count": self.retry_count
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'PipelineStageResult':
        return cls(
            stage_id=data["stage_id"],
            stage_name=data.get("stage_name", data["stage_id"]),
            status=ExecutionStatus(data.get("status", "pending")),
            start_time=data.get("start_time", time.time()),
            end_time=data.get("end_time"),
            execution_time=data.get("execution_time"),
            error=data.get("error"),
            error_type=data.get("error_type"),
            retry_count=data.get("retry_count", 0)
        )


@dataclass
class PipelineResult(JSONSerializable):
    """管道执行结果"""
    pipeline_id: str
    status: PipelineStatus
    start_time: float
    end_time: Optional[float] = None
    total_time: Optional[float] = None
    stage_results: List[PipelineStageResult] = field(default_factory=list)
    final_output: Any = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "pipeline_id": self.pipeline_id,
            "status": self.status.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_time": self.total_time,
            "error": self.error,
            "error_type": self.error_type,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'PipelineResult':
        return cls(
            pipeline_id=data["pipeline_id"],
            status=PipelineStatus(data.get("status", "idle")),
            start_time=data.get("start_time", time.time()),
            end_time=data.get("end_time"),
            total_time=data.get("total_time"),
            error=data.get("error"),
            error_type=data.get("error_type"),
            metadata=data.get("metadata", {})
        )


@dataclass
class PipelineConfig(JSONSerializable):
    """管道配置"""
    stop_on_failure: bool = True
    propagate_exceptions: bool = True
    enable_parallel_stages: bool = False
    max_parallel_stages: int = 4
    enable_checkpoints: bool = False
    checkpoint_interval: int = 5
    timeout_seconds: Optional[float] = None
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL

    def to_dict(self) -> Dict:
        return {
            "stop_on_failure": self.stop_on_failure,
            "propagate_exceptions": self.propagate_exceptions,
            "enable_parallel_stages": self.enable_parallel_stages,
            "max_parallel_stages": self.max_parallel_stages,
            "enable_checkpoints": self.enable_checkpoints,
            "checkpoint_interval": self.checkpoint_interval,
            "timeout_seconds": self.timeout_seconds,
            "execution_mode": self.execution_mode.value
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'PipelineConfig':
        return cls(
            stop_on_failure=data.get("stop_on_failure", True),
            propagate_exceptions=data.get("propagate_exceptions", True),
            enable_parallel_stages=data.get("enable_parallel_stages", False),
            max_parallel_stages=data.get("max_parallel_stages", 4),
            enable_checkpoints=data.get("enable_checkpoints", False),
            checkpoint_interval=data.get("checkpoint_interval", 5),
            timeout_seconds=data.get("timeout_seconds"),
            execution_mode=ExecutionMode(data.get("execution_mode", "sequential"))
        )


class TaskPipeline:
    """任务管道 - 工作流编排"""

    def __init__(
        self,
        name: str,
        config: Optional[PipelineConfig] = None,
        execution_engine: Optional[TaskExecutionEngine] = None
    ):
        """
        初始化任务管道

        Args:
            name: 管道名称
            config: 管道配置
            execution_engine: 执行引擎（可选）
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.config = config or PipelineConfig()
        
        if execution_engine:
            self.execution_engine = execution_engine
        else:
            self.execution_engine = create_execution_engine(
                mode=self.config.execution_mode
            )
        
        self._lock = threading.RLock()
        self._stages: OrderedDict[str, PipelineStage] = OrderedDict()
        self._status = PipelineStatus.IDLE
        self._current_result: Optional[PipelineResult] = None
        self._history: List[PipelineResult] = []
        self._running = False
        self._cancel_flag = False

    @property
    def status(self) -> PipelineStatus:
        return self._status

    @property
    def stages(self) -> List[PipelineStage]:
        return list(self._stages.values())

    def add_stage(
        self,
        name: str,
        task: Optional[Union[TaskTuple, Callable]] = None,
        transform: Optional[Callable] = None,
        condition: Optional[Callable[[Any], bool]] = None,
        stage_type: PipelineStageType = PipelineStageType.TASK,
        timeout_seconds: Optional[float] = None,
        retry_on_failure: bool = False,
        max_retries: int = 0,
        metadata: Optional[Dict] = None
    ) -> 'TaskPipeline':
        """
        添加管道阶段（链式调用）

        Args:
            name: 阶段名称
            task: 任务或函数
            transform: 数据转换函数
            condition: 条件判断函数
            stage_type: 阶段类型
            timeout_seconds: 超时时间
            retry_on_failure: 是否失败重试
            max_retries: 最大重试次数
            metadata: 元数据

        Returns:
            self（支持链式调用）
        """
        with self._lock:
            stage_id = str(uuid.uuid4())
            stage = PipelineStage(
                id=stage_id,
                name=name,
                stage_type=stage_type,
                task=task,
                transform=transform,
                condition=condition,
                enabled=True,
                timeout_seconds=timeout_seconds,
                retry_on_failure=retry_on_failure,
                max_retries=max_retries,
                metadata=metadata or {}
            )
            self._stages[stage_id] = stage
            return self

    def add_parallel_group(
        self,
        name: str,
        stages: List[PipelineStage],
        metadata: Optional[Dict] = None
    ) -> 'TaskPipeline':
        """
        添加并行阶段组

        Args:
            name: 组名称
            stages: 子阶段列表
            metadata: 元数据

        Returns:
            self（支持链式调用）
        """
        with self._lock:
            stage_id = str(uuid.uuid4())
            stage = PipelineStage(
                id=stage_id,
                name=name,
                stage_type=PipelineStageType.PARALLEL,
                sub_stages=stages,
                enabled=True,
                metadata=metadata or {}
            )
            self._stages[stage_id] = stage
            return self

    def add_conditional(
        self,
        name: str,
        condition: Callable[[Any], bool],
        true_stage: Optional[PipelineStage] = None,
        false_stage: Optional[PipelineStage] = None,
        metadata: Optional[Dict] = None
    ) -> 'TaskPipeline':
        """
        添加条件分支

        Args:
            name: 阶段名称
            condition: 条件判断函数
            true_stage: 条件为真时的阶段
            false_stage: 条件为假时的阶段
            metadata: 元数据

        Returns:
            self（支持链式调用）
        """
        with self._lock:
            stage_id = str(uuid.uuid4())
            sub_stages = []
            if true_stage:
                sub_stages.append(true_stage)
            if false_stage:
                sub_stages.append(false_stage)
            
            stage = PipelineStage(
                id=stage_id,
                name=name,
                stage_type=PipelineStageType.CONDITIONAL,
                condition=condition,
                sub_stages=sub_stages,
                enabled=True,
                metadata=metadata or {}
            )
            self._stages[stage_id] = stage
            return self

    def remove_stage(self, stage_id: str) -> bool:
        """移除阶段"""
        with self._lock:
            if stage_id in self._stages:
                del self._stages[stage_id]
                return True
            return False

    def execute(self, initial_input: Any = None) -> PipelineResult:
        """
        执行管道

        Args:
            initial_input: 初始输入数据

        Returns:
            管道执行结果
        """
        with self._lock:
            if self._status == PipelineStatus.RUNNING:
                raise RuntimeError("Pipeline is already running")
            
            self._status = PipelineStatus.RUNNING
            self._cancel_flag = False
        
        start_time = time.time()
        result = PipelineResult(
            pipeline_id=self.id,
            status=PipelineStatus.RUNNING,
            start_time=start_time
        )
        
        current_input = initial_input
        final_output = initial_input
        
        try:
            stage_results = self._execute_stages(current_input, result)
            result.stage_results = stage_results
            
            # 获取最后的输出
            if stage_results:
                for stage_result in reversed(stage_results):
                    if stage_result.status == ExecutionStatus.COMPLETED:
                        final_output = stage_result.output_data
                        break
            
            result.final_output = final_output
            
            # 检查是否有失败的阶段
            has_failed = any(sr.status == ExecutionStatus.FAILED for sr in stage_results)
            if has_failed:
                result.status = PipelineStatus.FAILED
                # 找到第一个失败的阶段
                for sr in stage_results:
                    if sr.status == ExecutionStatus.FAILED:
                        result.error = sr.error
                        result.error_type = sr.error_type
                        break
            else:
                result.status = PipelineStatus.COMPLETED
            
        except Exception as e:
            result.status = PipelineStatus.FAILED
            result.error = str(e)
            result.error_type = type(e).__name__
            
            if self.config.propagate_exceptions:
                raise
        
        finally:
            end_time = time.time()
            result.end_time = end_time
            result.total_time = end_time - start_time
            
            with self._lock:
                self._status = result.status
                self._current_result = result
                self._history.append(result)
        
        return result

    def _execute_stages(
        self,
        initial_input: Any,
        pipeline_result: PipelineResult
    ) -> List[PipelineStageResult]:
        """执行所有阶段"""
        stage_results = []
        current_input = initial_input
        
        for stage_id, stage in self._stages.items():
            if not stage.enabled:
                continue
            
            if self._cancel_flag:
                pipeline_result.status = PipelineStatus.CANCELLED
                break
            
            stage_result = self._execute_single_stage(
                stage,
                current_input
            )
            stage_results.append(stage_result)
            
            if stage_result.status == ExecutionStatus.COMPLETED:
                current_input = stage_result.output_data
            elif stage_result.status == ExecutionStatus.FAILED:
                if self.config.stop_on_failure:
                    break
        
        return stage_results

    def _execute_single_stage(
        self,
        stage: PipelineStage,
        input_data: Any
    ) -> PipelineStageResult:
        """执行单个阶段"""
        start_time = time.time()
        result = PipelineStageResult(
            stage_id=stage.id,
            stage_name=stage.name,
            status=ExecutionStatus.RUNNING,
            start_time=start_time,
            input_data=input_data
        )
        
        retry_count = 0
        max_attempts = 1 + (stage.max_retries if stage.retry_on_failure else 0)
        
        while retry_count < max_attempts:
            try:
                if self._cancel_flag:
                    result.status = ExecutionStatus.CANCELLED
                    break
                
                output = self._execute_stage_by_type(stage, input_data)
                
                result.status = ExecutionStatus.COMPLETED
                result.output_data = output
                break
                
            except Exception as e:
                retry_count += 1
                
                if retry_count < max_attempts:
                    result.retry_count = retry_count
                else:
                    result.status = ExecutionStatus.FAILED
                    result.error = str(e)
                    result.error_type = type(e).__name__
                    break
        
        end_time = time.time()
        result.end_time = end_time
        result.execution_time = end_time - start_time
        
        return result

    def _execute_stage_by_type(
        self,
        stage: PipelineStage,
        input_data: Any
    ) -> Any:
        """根据阶段类型执行"""
        if stage.stage_type == PipelineStageType.TASK:
            return self._execute_task_stage(stage, input_data)
        elif stage.stage_type == PipelineStageType.TRANSFORM:
            return self._execute_transform_stage(stage, input_data)
        elif stage.stage_type == PipelineStageType.CONDITIONAL:
            return self._execute_conditional_stage(stage, input_data)
        elif stage.stage_type == PipelineStageType.PARALLEL:
            return self._execute_parallel_stage(stage, input_data)
        elif stage.stage_type == PipelineStageType.SEQUENCE:
            return self._execute_sequence_stage(stage, input_data)
        else:
            return input_data

    def _execute_task_stage(
        self,
        stage: PipelineStage,
        input_data: Any
    ) -> Any:
        """执行任务阶段"""
        if callable(stage.task):
            return stage.task(input_data)
        elif isinstance(stage.task, TaskTuple):
            return f"Executed task: {stage.task.target}"
        else:
            return input_data

    def _execute_transform_stage(
        self,
        stage: PipelineStage,
        input_data: Any
    ) -> Any:
        """执行转换阶段"""
        if callable(stage.transform):
            return stage.transform(input_data)
        return input_data

    def _execute_conditional_stage(
        self,
        stage: PipelineStage,
        input_data: Any
    ) -> Any:
        """执行条件分支阶段"""
        if stage.condition and callable(stage.condition):
            condition_result = stage.condition(input_data)
            if condition_result and len(stage.sub_stages) > 0:
                return self._execute_single_stage(stage.sub_stages[0], input_data).output_data
            elif not condition_result and len(stage.sub_stages) > 1:
                return self._execute_single_stage(stage.sub_stages[1], input_data).output_data
        return input_data

    def _execute_parallel_stage(
        self,
        stage: PipelineStage,
        input_data: Any
    ) -> List[Any]:
        """执行并行阶段"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = []
        max_workers = min(self.config.max_parallel_stages, len(stage.sub_stages))
        
        def execute_sub_stage(sub_stage):
            sub_result = self._execute_single_stage(sub_stage, input_data)
            return sub_result.output_data if sub_result.status == ExecutionStatus.COMPLETED else None
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(execute_sub_stage, sub_stage) for sub_stage in stage.sub_stages if sub_stage.enabled]
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result is not None:
                        results.append(result)
                except Exception:
                    pass
        
        return results

    def _execute_sequence_stage(
        self,
        stage: PipelineStage,
        input_data: Any
    ) -> Any:
        """执行序列阶段"""
        current_input = input_data
        for sub_stage in stage.sub_stages:
            if not sub_stage.enabled:
                continue
            sub_result = self._execute_single_stage(sub_stage, current_input)
            if sub_result.status == ExecutionStatus.COMPLETED:
                current_input = sub_result.output_data
            elif sub_result.status == ExecutionStatus.FAILED:
                if self.config.stop_on_failure:
                    raise Exception(f"Sub-stage {sub_stage.name} failed")
        return current_input

    def cancel(self):
        """取消执行"""
        with self._lock:
            self._cancel_flag = True
            if self._status == PipelineStatus.RUNNING:
                self._status = PipelineStatus.CANCELLED

    def get_history(self) -> List[PipelineResult]:
        """获取执行历史"""
        with self._lock:
            return list(self._history)

    def get_current_result(self) -> Optional[PipelineResult]:
        """获取当前结果"""
        with self._lock:
            return self._current_result

    def reset(self):
        """重置管道"""
        with self._lock:
            self._status = PipelineStatus.IDLE
            self._current_result = None
            self._cancel_flag = False

    def clear_stages(self):
        """清空所有阶段"""
        with self._lock:
            self._stages.clear()


def create_pipeline(
    name: str,
    config: Optional[PipelineConfig] = None
) -> TaskPipeline:
    """
    创建任务管道工厂函数

    Args:
        name: 管道名称
        config: 管道配置

    Returns:
        配置好的任务管道
    """
    return TaskPipeline(name, config)
