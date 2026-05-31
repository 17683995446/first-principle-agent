"""
TaskOrchestrator - 任务编排器
基于第一性原理AI Agent任务规划系统 - 第57阶段
整合所有核心组件，提供端到端的任务规划和执行解决方案
"""

import uuid
import time
import logging
from typing import Dict, Any, List, Optional, Callable, Union
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict

from .task_tuple import TaskTuple
from .dag_structures import TaskDAG, DAGNode, DAGEdge
from .task_planning_system import TaskPlanningSystem
from .task_execution_engine import TaskExecutionEngine
from .task_pipeline import TaskPipeline
from .task_scheduler import TaskScheduler, TaskPriority, SchedulerStrategy
from .task_analytics import TaskAnalytics, ReportFormat, TaskReportGenerator
from .task_workflow_executor import (
    TaskWorkflowExecutor,
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowStatus,
    WorkflowStepType
)


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrchestrationPhase(Enum):
    """编排阶段枚举"""
    INITIALIZING = "initializing"
    ANALYZING = "analyzing"
    PLANNING = "planning"
    EXECUTING = "executing"
    MONITORING = "monitoring"
    ANALYZING_RESULTS = "analyzing_results"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OrchestrationStrategy(Enum):
    """编排策略枚举"""
    SEQUENTIAL = "sequential"  # 顺序执行
    PARALLEL = "parallel"      # 并行执行
    WORKFLOW = "workflow"      # 工作流模式
    PIPELINE = "pipeline"      # 管道模式
    ADAPTIVE = "adaptive"      # 自适应模式


@dataclass
class OrchestrationConfig:
    """编排配置"""
    strategy: OrchestrationStrategy = OrchestrationStrategy.ADAPTIVE
    enable_analytics: bool = True
    enable_checkpoints: bool = True
    auto_retry: bool = True
    max_retries: int = 3
    timeout_seconds: Optional[float] = None
    callback_on_progress: Optional[Callable] = None
    callback_on_complete: Optional[Callable] = None
    callback_on_failure: Optional[Callable] = None


@dataclass
class OrchestrationMetrics:
    """编排指标"""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    pending_tasks: int = 0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    total_duration: Optional[float] = None
    phase_durations: Dict[str, float] = field(default_factory=dict)
    task_durations: Dict[str, float] = field(default_factory=dict)


@dataclass
class OrchestrationResult:
    """编排结果"""
    orchestration_id: str
    status: OrchestrationPhase
    metrics: OrchestrationMetrics
    task_results: Dict[str, Any]
    analytics_report: Optional[str] = None
    error_message: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)


class TaskOrchestrator:
    """
    任务编排器
    整合所有核心组件，提供端到端的任务规划和执行解决方案
    """
    
    def __init__(self, config: Optional[OrchestrationConfig] = None):
        """
        初始化任务编排器
        
        Args:
            config: 编排配置
        """
        self.orchestrator_id = str(uuid.uuid4())
        self.config = config or OrchestrationConfig()
        
        # 初始化所有核心组件
        self.planning_system = TaskPlanningSystem()
        self.execution_engine = TaskExecutionEngine()
        self.pipeline = TaskPipeline(name="Orchestrator Pipeline")
        self.scheduler = TaskScheduler()
        self.analytics = TaskAnalytics()
        self.workflow_executor = TaskWorkflowExecutor()
        
        # 内部状态
        self.orchestrations: Dict[str, OrchestrationResult] = {}
        self.metrics = OrchestrationMetrics()
        self._callbacks: Dict[str, List[Callable]] = defaultdict(list)
        
        logger.info(f"TaskOrchestrator initialized with ID: {self.orchestrator_id}")
    
    def register_callback(self, event: str, callback: Callable) -> None:
        """
        注册回调函数
        
        Args:
            event: 事件名称
            callback: 回调函数
        """
        self._callbacks[event].append(callback)
        logger.debug(f"Callback registered for event: {event}")
    
    def _emit_event(self, event: str, *args, **kwargs) -> None:
        """
        触发事件
        
        Args:
            event: 事件名称
            *args: 位置参数
            **kwargs: 关键字参数
        """
        for callback in self._callbacks.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Callback error for event {event}: {e}")
    
    def orchestrate(
        self,
        requirement: str,
        config: Optional[OrchestrationConfig] = None
    ) -> OrchestrationResult:
        """
        执行完整的任务编排流程
        
        Args:
            requirement: 用户需求（自然语言）
            config: 可选的编排配置
            
        Returns:
            编排结果
        """
        orchestration_id = str(uuid.uuid4())
        current_config = config or self.config
        
        logger.info(f"Starting orchestration {orchestration_id} for requirement: {requirement[:50]}...")
        
        # 初始化结果
        result = OrchestrationResult(
            orchestration_id=orchestration_id,
            status=OrchestrationPhase.INITIALIZING,
            metrics=OrchestrationMetrics(),
            task_results={}
        )
        
        self.orchestrations[orchestration_id] = result
        result.metrics.start_time = time.time()
        phase_start_time = time.time()
        
        try:
            # 阶段1: 需求分析
            result.status = OrchestrationPhase.ANALYZING
            logger.info(f"Phase: {result.status.value}")
            task_tuple = self._analyze_requirement(requirement, result)
            result.metrics.phase_durations["analyzing"] = time.time() - phase_start_time
            
            # 阶段2: 任务规划
            phase_start_time = time.time()
            result.status = OrchestrationPhase.PLANNING
            logger.info(f"Phase: {result.status.value}")
            task_dag = self._plan_tasks(task_tuple, result)
            result.metrics.phase_durations["planning"] = time.time() - phase_start_time
            
            # 阶段3: 任务执行
            phase_start_time = time.time()
            result.status = OrchestrationPhase.EXECUTING
            logger.info(f"Phase: {result.status.value}")
            task_results = self._execute_tasks(task_dag, current_config, result)
            result.metrics.phase_durations["executing"] = time.time() - phase_start_time
            
            # 阶段4: 结果分析
            phase_start_time = time.time()
            result.status = OrchestrationPhase.ANALYZING_RESULTS
            logger.info(f"Phase: {result.status.value}")
            analytics_report = self._analyze_results(task_results, result)
            result.metrics.phase_durations["analyzing_results"] = time.time() - phase_start_time
            
            # 完成
            result.status = OrchestrationPhase.COMPLETED
            result.task_results = task_results
            result.analytics_report = analytics_report
            
            # 计算总时长
            result.metrics.end_time = time.time()
            result.metrics.total_duration = result.metrics.end_time - result.metrics.start_time
            
            # 也更新全局指标
            self.metrics = result.metrics
            
            logger.info(f"Orchestration {orchestration_id} completed successfully")
            
            # 触发完成回调
            if current_config.callback_on_complete:
                current_config.callback_on_complete(result)
            
            self._emit_event("orchestration_complete", result)
            
        except Exception as e:
            result.status = OrchestrationPhase.FAILED
            result.error_message = str(e)
            logger.error(f"Orchestration {orchestration_id} failed: {e}")
            
            # 触发失败回调
            if current_config.callback_on_failure:
                current_config.callback_on_failure(result)
            
            self._emit_event("orchestration_failed", result)
        
        return result
    
    def _analyze_requirement(
        self,
        requirement: str,
        result: OrchestrationResult
    ) -> TaskTuple:
        """
        分析用户需求
        
        Args:
            requirement: 用户需求
            result: 编排结果对象
            
        Returns:
            任务四元组
        """
        # 创建一个简单的 TaskTuple 用于演示
        task_tuple = TaskTuple(
            target=requirement,
            condition=["Basic requirement analysis"],
            boundary={"include": [], "exclude": [], "constraints": {}},
            end_rule={
                "success_criteria": ["Task completed"],
                "failure_criteria": ["Task failed"],
                "timeout": 3600,
                "max_attempts": 3
            }
        )
        
        logger.info(f"Requirement analyzed, created TaskTuple: {task_tuple.target[:50]}...")
        
        # 更新指标（这只是占位，实际任务数在规划阶段确定）
        return task_tuple
    
    def _plan_tasks(
        self,
        task_tuple: TaskTuple,
        result: OrchestrationResult
    ) -> TaskDAG:
        """
        规划任务拓扑
        
        Args:
            task_tuple: 任务四元组
            result: 编排结果对象
            
        Returns:
            任务DAG
        """
        # 创建一个简单的 DAG 用于演示
        node1 = DAGNode(
            node_id="task-1",
            name="Step 1: Analyze requirement",
            node_type="analysis"
        )
        node2 = DAGNode(
            node_id="task-2",
            name="Step 2: Develop plan",
            node_type="planning"
        )
        node3 = DAGNode(
            node_id="task-3",
            name="Step 3: Execute plan",
            node_type="execution"
        )
        
        edge1 = DAGEdge(
            edge_id="edge-1",
            from_node="task-1",
            to_node="task-2",
            edge_type="requires"
        )
        edge2 = DAGEdge(
            edge_id="edge-2",
            from_node="task-2",
            to_node="task-3",
            edge_type="requires"
        )
        
        task_dag = TaskDAG(
            dag_id="task-dag-1",
            nodes=[node1, node2, node3],
            edges=[edge1, edge2]
        )
        
        logger.info(f"Tasks planned, created DAG with {len(task_dag.nodes)} nodes")
        
        # 更新指标
        result.metrics.total_tasks = len(task_dag.nodes)
        result.metrics.pending_tasks = len(task_dag.nodes)
        
        return task_dag
    
    def _execute_tasks(
        self,
        task_dag: TaskDAG,
        config: OrchestrationConfig,
        result: OrchestrationResult
    ) -> Dict[str, Any]:
        """
        执行任务
        
        Args:
            task_dag: 任务DAG
            config: 编排配置
            result: 编排结果对象
            
        Returns:
            任务执行结果
        """
        task_results = {}
        
        # 根据策略选择执行方式
        if config.strategy == OrchestrationStrategy.SEQUENTIAL:
            task_results = self._execute_sequential(task_dag, config, result)
        elif config.strategy == OrchestrationStrategy.PARALLEL:
            task_results = self._execute_parallel(task_dag, config, result)
        elif config.strategy == OrchestrationStrategy.WORKFLOW:
            task_results = self._execute_workflow(task_dag, config, result)
        elif config.strategy == OrchestrationStrategy.PIPELINE:
            task_results = self._execute_pipeline(task_dag, config, result)
        else:  # ADAPTIVE
            task_results = self._execute_adaptive(task_dag, config, result)
        
        return task_results
    
    def _execute_sequential(
        self,
        task_dag: TaskDAG,
        config: OrchestrationConfig,
        result: OrchestrationResult
    ) -> Dict[str, Any]:
        """顺序执行模式"""
        task_results = {}
        
        for node in task_dag.nodes:
            node_id = node.id
            logger.info(f"Executing task: {node.name} ({node_id})")
            
            start_time = time.time()
            
            try:
                # 模拟任务执行
                execution_result = self._simulate_task_execution(node)
                task_results[node_id] = execution_result
                
                # 更新指标
                result.metrics.completed_tasks += 1
                result.metrics.pending_tasks -= 1
                result.metrics.task_durations[node_id] = time.time() - start_time
                
                logger.info(f"Task {node.name} completed successfully")
                
            except Exception as e:
                result.metrics.failed_tasks += 1
                logger.error(f"Task {node.name} failed: {e}")
                
                if config.auto_retry and result.metrics.failed_tasks <= config.max_retries:
                    logger.info(f"Retrying task {node.name}...")
                    continue
                else:
                    raise
        
        return task_results
    
    def _execute_parallel(
        self,
        task_dag: TaskDAG,
        config: OrchestrationConfig,
        result: OrchestrationResult
    ) -> Dict[str, Any]:
        """并行执行模式（简化版本）"""
        # 简单版本：顺序执行但标记为并行策略
        return self._execute_sequential(task_dag, config, result)
    
    def _execute_workflow(
        self,
        task_dag: TaskDAG,
        config: OrchestrationConfig,
        result: OrchestrationResult
    ) -> Dict[str, Any]:
        """工作流模式（简化版本）"""
        return self._execute_sequential(task_dag, config, result)
    
    def _execute_pipeline(
        self,
        task_dag: TaskDAG,
        config: OrchestrationConfig,
        result: OrchestrationResult
    ) -> Dict[str, Any]:
        """管道模式（简化版本）"""
        return self._execute_sequential(task_dag, config, result)
    
    def _execute_adaptive(
        self,
        task_dag: TaskDAG,
        config: OrchestrationConfig,
        result: OrchestrationResult
    ) -> Dict[str, Any]:
        """自适应执行模式"""
        # 简单版本：直接使用顺序执行
        return self._execute_sequential(task_dag, config, result)
    
    def _simulate_task_execution(self, node: DAGNode) -> Dict[str, Any]:
        """模拟任务执行"""
        # 简单的模拟执行
        time.sleep(0.01)  # 模拟执行时间
        return {
            "success": True,
            "node_id": node.id,
            "node_name": node.name,
            "output": f"Result of {node.name}",
            "timestamp": time.time()
        }
    
    def _analyze_results(
        self,
        task_results: Dict[str, Any],
        result: OrchestrationResult
    ) -> str:
        """
        分析执行结果
        
        Args:
            task_results: 任务执行结果
            result: 编排结果对象
            
        Returns:
            分析报告
        """
        if not self.config.enable_analytics:
            return "Analytics disabled"
        
        # 使用 TaskAnalytics 的实际 API
        success_count = sum(1 for r in task_results.values() if r.get("success", False))
        total_count = len(task_results)
        failed_count = total_count - success_count
        
        # 进行成功率分析
        if total_count > 0:
            self.analytics.analyze_success_rate(
                total_tasks=total_count,
                successful_tasks=success_count,
                failed_tasks=failed_count
            )
        
        # 进行执行时间分析
        execution_times = list(result.metrics.task_durations.values())
        if execution_times:
            self.analytics.analyze_execution_time(execution_times)
        
        # 生成报告
        report_generator = TaskReportGenerator(self.analytics)
        report = report_generator.generate_summary_report()
        report_text = report.to_text()
        
        # 生成建议
        result.recommendations = self._generate_recommendations(task_results)
        
        return report
    
    def _generate_recommendations(self, task_results: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        success_count = sum(1 for r in task_results.values() if r.get("success", False))
        total_count = len(task_results)
        
        if success_count < total_count:
            recommendations.append(
                f"Some tasks failed ({total_count - success_count}/{total_count}), "
                f"consider reviewing task configurations"
            )
        
        if total_count > 10:
            recommendations.append(
                "Large number of tasks detected, consider breaking down into smaller workflows"
            )
        
        return recommendations
    
    def get_orchestration(self, orchestration_id: str) -> Optional[OrchestrationResult]:
        """
        获取编排结果
        
        Args:
            orchestration_id: 编排ID
            
        Returns:
            编排结果
        """
        return self.orchestrations.get(orchestration_id)
    
    def get_all_orchestrations(self) -> List[OrchestrationResult]:
        """
        获取所有编排结果
        
        Returns:
            编排结果列表
        """
        return list(self.orchestrations.values())
    
    def cancel_orchestration(self, orchestration_id: str) -> bool:
        """
        取消编排
        
        Args:
            orchestration_id: 编排ID
            
        Returns:
            是否成功取消
        """
        result = self.orchestrations.get(orchestration_id)
        if result and result.status in [
            OrchestrationPhase.INITIALIZING,
            OrchestrationPhase.ANALYZING,
            OrchestrationPhase.PLANNING,
            OrchestrationPhase.EXECUTING
        ]:
            result.status = OrchestrationPhase.CANCELLED
            logger.info(f"Orchestration {orchestration_id} cancelled")
            return True
        return False
    
    def reset(self) -> None:
        """重置编排器状态"""
        self.orchestrations.clear()
        self.metrics = OrchestrationMetrics()
        logger.info("TaskOrchestrator reset")


def create_orchestrator(
    strategy: OrchestrationStrategy = OrchestrationStrategy.ADAPTIVE,
    enable_analytics: bool = True
) -> TaskOrchestrator:
    """
    创建任务编排器的工厂函数
    
    Args:
        strategy: 编排策略
        enable_analytics: 是否启用分析
        
    Returns:
        任务编排器实例
    """
    config = OrchestrationConfig(
        strategy=strategy,
        enable_analytics=enable_analytics
    )
    return TaskOrchestrator(config=config)
