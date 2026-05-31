from typing import Any, Dict, List, Optional
from enum import Enum
from .base import JSONSerializable


class ActionType(Enum):
    """动作类型枚举"""
    READ = "read"  # 读操作
    WRITE = "write"  # 写操作
    COMPUTE = "compute"  # 计算操作
    CALL = "call"  # 调用操作
    TRANSFORM = "transform"  # 转换操作
    VALIDATE = "validate"  # 验证操作
    SEND = "send"  # 发送操作
    RECEIVE = "receive"  # 接收操作
    INIT = "init"  # 初始化操作
    CLEANUP = "cleanup"  # 清理操作


class AtomicActionStatus(Enum):
    """原子动作状态枚举"""
    PENDING = "pending"  # 待执行
    RUNNING = "running"  # 执行中
    SUCCESS = "success"  # 成功
    FAILED = "failed"  # 失败
    SKIPPED = "skipped"  # 跳过
    TIMEOUT = "timeout"  # 超时


class AtomicAction(JSONSerializable):
    """原子动作 - 不可再分的最小执行单元"""

    def __init__(
        self,
        action_id: str,
        action_type: ActionType,
        name: str,
        description: str = "",
        inputs: Optional[Dict[str, Any]] = None,
        outputs: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        timeout: float = 300.0,
        retries: int = 0
    ):
        self.action_id = action_id
        self.action_type = action_type
        self.name = name
        self.description = description
        self.inputs = inputs or {}
        self.outputs = outputs or {}
        self.metadata = metadata or {}
        self.status = AtomicActionStatus.PENDING
        self.timeout = timeout
        self.retries = retries
        self.current_retry = 0
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.error: Optional[str] = None
        self.dependencies: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "action_type": self.action_type.value,
            "name": self.name,
            "description": self.description,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "metadata": self.metadata,
            "status": self.status.value,
            "timeout": self.timeout,
            "retries": self.retries,
            "current_retry": self.current_retry,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "error": self.error,
            "dependencies": self.dependencies
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AtomicAction':
        action = cls(
            action_id=data["action_id"],
            action_type=ActionType(data["action_type"]),
            name=data["name"],
            description=data.get("description", ""),
            inputs=data.get("inputs"),
            outputs=data.get("outputs"),
            metadata=data.get("metadata"),
            timeout=data.get("timeout", 300.0),
            retries=data.get("retries", 0)
        )
        action.status = AtomicActionStatus(data.get("status", "pending"))
        action.current_retry = data.get("current_retry", 0)
        action.start_time = data.get("start_time")
        action.end_time = data.get("end_time")
        action.error = data.get("error")
        action.dependencies = data.get("dependencies", [])
        return action

    def add_dependency(self, action_id: str) -> None:
        """添加依赖"""
        if action_id not in self.dependencies:
            self.dependencies.append(action_id)

    def remove_dependency(self, action_id: str) -> None:
        """移除依赖"""
        if action_id in self.dependencies:
            self.dependencies.remove(action_id)

    def can_execute(self, completed_actions: List[str]) -> bool:
        """检查是否可以执行（所有依赖都已完成）"""
        return all(dep in completed_actions for dep in self.dependencies)

    def mark_running(self, start_time: Optional[float] = None) -> None:
        """标记为运行中"""
        import time
        self.status = AtomicActionStatus.RUNNING
        self.start_time = start_time or time.time()

    def mark_success(self, end_time: Optional[float] = None, outputs: Optional[Dict[str, Any]] = None) -> None:
        """标记为成功"""
        import time
        self.status = AtomicActionStatus.SUCCESS
        self.end_time = end_time or time.time()
        if outputs:
            self.outputs = outputs

    def mark_failed(self, end_time: Optional[float] = None, error: Optional[str] = None) -> None:
        """标记为失败"""
        import time
        self.status = AtomicActionStatus.FAILED
        self.end_time = end_time or time.time()
        if error:
            self.error = error

    def mark_skipped(self, end_time: Optional[float] = None) -> None:
        """标记为跳过"""
        import time
        self.status = AtomicActionStatus.SKIPPED
        self.end_time = end_time or time.time()

    def mark_timeout(self, end_time: Optional[float] = None) -> None:
        """标记为超时"""
        import time
        self.status = AtomicActionStatus.TIMEOUT
        self.end_time = end_time or time.time()
        self.error = "Action timed out"

    def get_duration(self) -> Optional[float]:
        """获取执行时长"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

    def reset(self) -> None:
        """重置动作状态"""
        self.status = AtomicActionStatus.PENDING
        self.start_time = None
        self.end_time = None
        self.error = None
        self.current_retry = 0


class AtomicActionPlan(JSONSerializable):
    """原子动作计划 - 包含一组原子动作的执行计划"""

    def __init__(
        self,
        plan_id: str,
        name: str = "",
        actions: Optional[List[AtomicAction]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.plan_id = plan_id
        self.name = name
        self.actions = actions or []
        self.metadata = metadata or {}
        self.created_at: Optional[float] = None
        self.started_at: Optional[float] = None
        self.completed_at: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "name": self.name,
            "actions": [action.to_dict() for action in self.actions],
            "metadata": self.metadata,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AtomicActionPlan':
        plan = cls(
            plan_id=data["plan_id"],
            name=data.get("name", ""),
            metadata=data.get("metadata")
        )
        plan.actions = [AtomicAction.from_dict(action_data) for action_data in data.get("actions", [])]
        plan.created_at = data.get("created_at")
        plan.started_at = data.get("started_at")
        plan.completed_at = data.get("completed_at")
        return plan

    def add_action(self, action: AtomicAction) -> None:
        """添加原子动作"""
        self.actions.append(action)

    def remove_action(self, action_id: str) -> bool:
        """移除原子动作"""
        for i, action in enumerate(self.actions):
            if action.action_id == action_id:
                self.actions.pop(i)
                return True
        return False

    def get_action(self, action_id: str) -> Optional[AtomicAction]:
        """获取原子动作"""
        for action in self.actions:
            if action.action_id == action_id:
                return action
        return None

    def get_actions_by_type(self, action_type: ActionType) -> List[AtomicAction]:
        """根据类型获取动作"""
        return [action for action in self.actions if action.action_type == action_type]

    def get_actions_by_status(self, status: AtomicActionStatus) -> List[AtomicAction]:
        """根据状态获取动作"""
        return [action for action in self.actions if action.status == status]

    def get_action_ids(self) -> List[str]:
        """获取所有动作ID"""
        return [action.action_id for action in self.actions]

    def get_completed_action_ids(self) -> List[str]:
        """获取已完成的动作ID"""
        return [
            action.action_id for action in self.actions
            if action.status in [AtomicActionStatus.SUCCESS, AtomicActionStatus.SKIPPED]
        ]

    def get_ready_actions(self) -> List[AtomicAction]:
        """获取可以执行的动作"""
        completed = self.get_completed_action_ids()
        return [
            action for action in self.actions
            if action.status == AtomicActionStatus.PENDING
            and action.can_execute(completed)
        ]

    def get_progress(self) -> Dict[str, Any]:
        """获取进度信息"""
        total = len(self.actions)
        completed = len(self.get_actions_by_status(AtomicActionStatus.SUCCESS))
        failed = len(self.get_actions_by_status(AtomicActionStatus.FAILED))
        skipped = len(self.get_actions_by_status(AtomicActionStatus.SKIPPED))
        running = len(self.get_actions_by_status(AtomicActionStatus.RUNNING))
        pending = len(self.get_actions_by_status(AtomicActionStatus.PENDING))
        timeout = len(self.get_actions_by_status(AtomicActionStatus.TIMEOUT))

        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "skipped": skipped,
            "running": running,
            "pending": pending,
            "timeout": timeout,
            "percentage": (completed + skipped) / total * 100 if total > 0 else 0.0
        }

    def is_complete(self) -> bool:
        """检查是否所有动作都已完成"""
        pending_or_running = len(self.get_actions_by_status(AtomicActionStatus.PENDING)) + \
                            len(self.get_actions_by_status(AtomicActionStatus.RUNNING))
        return pending_or_running == 0

    def mark_started(self, start_time: Optional[float] = None) -> None:
        """标记为已开始"""
        import time
        if not self.created_at:
            self.created_at = start_time or time.time()
        self.started_at = start_time or time.time()

    def mark_completed(self, completed_at: Optional[float] = None) -> None:
        """标记为已完成"""
        import time
        self.completed_at = completed_at or time.time()

    def reset(self) -> None:
        """重置所有动作"""
        for action in self.actions:
            action.reset()
        self.started_at = None
        self.completed_at = None
