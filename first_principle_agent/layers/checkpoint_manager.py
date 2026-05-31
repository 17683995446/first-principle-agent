from typing import Any, Dict, List, Optional
from datetime import datetime
import json
import os
from ..core import AtomicAction, AtomicActionPlan, AtomicActionStatus


class Checkpoint:
    """检查点数据结构"""

    def __init__(
        self,
        checkpoint_id: str,
        name: str,
        plan_id: str,
        action_ids: List[str],
        state: Dict[str, Any],
        created_at: Optional[datetime] = None,
        validated: bool = False
    ):
        self.checkpoint_id = checkpoint_id
        self.name = name
        self.plan_id = plan_id
        self.action_ids = action_ids
        self.state = state
        self.created_at = created_at or datetime.now()
        self.validated = validated

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "name": self.name,
            "plan_id": self.plan_id,
            "action_ids": self.action_ids,
            "state": self.state,
            "created_at": self.created_at.isoformat(),
            "validated": self.validated
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Checkpoint':
        return cls(
            checkpoint_id=data["checkpoint_id"],
            name=data["name"],
            plan_id=data["plan_id"],
            action_ids=data["action_ids"],
            state=data["state"],
            created_at=datetime.fromisoformat(data["created_at"]),
            validated=data.get("validated", False)
        )


class CheckpointManager:
    """检查点管理器 - 管理执行检查点，支持状态持久化和回滚"""

    def __init__(self, storage_path: Optional[str] = None):
        self.checkpoints: Dict[str, Checkpoint] = {}
        self.storage_path = storage_path or "./checkpoints"
        self._ensure_storage_path()
        self.checkpoint_counter = 0

    def _ensure_storage_path(self):
        """确保存储路径存在"""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path, exist_ok=True)

    def create_checkpoint(
        self,
        plan: AtomicActionPlan,
        name: str,
        action_ids: Optional[List[str]] = None,
        state: Optional[Dict[str, Any]] = None
    ) -> Checkpoint:
        """
        创建检查点
        
        Args:
            plan: 原子动作计划
            name: 检查点名称
            action_ids: 关联的动作ID列表（默认为所有已完成的动作）
            state: 自定义状态字典
            
        Returns:
            创建的检查点
        """
        self.checkpoint_counter += 1
        checkpoint_id = f"checkpoint_{self.checkpoint_counter:06d}"

        if action_ids is None:
            action_ids = [
                action.action_id for action in plan.actions
                if action.status in [AtomicActionStatus.SUCCESS, AtomicActionStatus.SKIPPED]
            ]

        if state is None:
            state = self._capture_plan_state(plan)

        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            name=name,
            plan_id=plan.plan_id,
            action_ids=action_ids,
            state=state
        )

        self.checkpoints[checkpoint_id] = checkpoint
        self._save_checkpoint(checkpoint)

        return checkpoint

    def _capture_plan_state(self, plan: AtomicActionPlan) -> Dict[str, Any]:
        """捕获计划当前状态"""
        return {
            "progress": plan.get_progress(),
            "actions": [
                {
                    "action_id": action.action_id,
                    "status": action.status.value,
                    "outputs": action.outputs,
                    "start_time": action.start_time,
                    "end_time": action.end_time
                }
                for action in plan.actions
            ]
        }

    def get_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """获取检查点"""
        if checkpoint_id in self.checkpoints:
            return self.checkpoints[checkpoint_id]
        
        return self._load_checkpoint(checkpoint_id)

    def list_checkpoints(self, plan_id: Optional[str] = None) -> List[Checkpoint]:
        """列出检查点"""
        checkpoints = list(self.checkpoints.values())
        
        if plan_id:
            checkpoints = [cp for cp in checkpoints if cp.plan_id == plan_id]
        
        return sorted(checkpoints, key=lambda cp: cp.created_at, reverse=True)

    def validate_checkpoint(self, checkpoint_id: str) -> bool:
        """验证检查点"""
        checkpoint = self.get_checkpoint(checkpoint_id)
        if not checkpoint:
            return False
        
        checkpoint.validated = True
        self._save_checkpoint(checkpoint)
        
        return True

    def rollback_to_checkpoint(
        self,
        checkpoint_id: str,
        plan: AtomicActionPlan
    ) -> bool:
        """
        回滚到指定检查点
        
        Args:
            checkpoint_id: 检查点ID
            plan: 要回滚的计划
            
        Returns:
            是否成功回滚
        """
        checkpoint = self.get_checkpoint(checkpoint_id)
        if not checkpoint:
            return False
        
        action_ids_set = set(checkpoint.action_ids)
        
        for action in plan.actions:
            if action.action_id not in action_ids_set:
                action.reset()
            else:
                if "status" in checkpoint.state:
                    for action_state in checkpoint.state.get("actions", []):
                        if action_state["action_id"] == action.action_id:
                            action.status = AtomicActionStatus(action_state["status"])
        
        return True

    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """删除检查点"""
        if checkpoint_id not in self.checkpoints:
            return False
        
        del self.checkpoints[checkpoint_id]
        
        checkpoint_path = os.path.join(self.storage_path, f"{checkpoint_id}.json")
        if os.path.exists(checkpoint_path):
            os.remove(checkpoint_path)
        
        return True

    def _save_checkpoint(self, checkpoint: Checkpoint):
        """保存检查点到文件"""
        checkpoint_path = os.path.join(self.storage_path, f"{checkpoint.checkpoint_id}.json")
        with open(checkpoint_path, 'w', encoding='utf-8') as f:
            json.dump(checkpoint.to_dict(), f, ensure_ascii=False, indent=2)

    def _load_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """从文件加载检查点"""
        checkpoint_path = os.path.join(self.storage_path, f"{checkpoint_id}.json")
        if not os.path.exists(checkpoint_path):
            return None
        
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            checkpoint = Checkpoint.from_dict(data)
            self.checkpoints[checkpoint_id] = checkpoint
            return checkpoint

    def create_automatic_checkpoints(
        self,
        plan: AtomicActionPlan,
        interval: int = 5,
        prefix: str = "auto"
    ) -> List[Checkpoint]:
        """
        自动创建检查点
        
        Args:
            plan: 原子动作计划
            interval: 每完成N个动作创建一个检查点
            prefix: 检查点名称前缀
            
        Returns:
            创建的检查点列表
        """
        checkpoints = []
        completed_actions = 0
        current_action_ids = []
        
        for i, action in enumerate(plan.actions):
            if action.status in [AtomicActionStatus.SUCCESS, AtomicActionStatus.SKIPPED]:
                completed_actions += 1
                current_action_ids.append(action.action_id)
                
                if completed_actions % interval == 0:
                    checkpoint = self.create_checkpoint(
                        plan=plan,
                        name=f"{prefix}_checkpoint_{len(checkpoints) + 1}",
                        action_ids=current_action_ids.copy()
                    )
                    checkpoints.append(checkpoint)
        
        return checkpoints

    def get_latest_checkpoint(self, plan_id: str) -> Optional[Checkpoint]:
        """获取最新的检查点"""
        checkpoints = self.list_checkpoints(plan_id)
        return checkpoints[0] if checkpoints else None

    def clear_checkpoints(self, plan_id: Optional[str] = None):
        """清除检查点"""
        if plan_id:
            to_delete = [cp_id for cp_id, cp in self.checkpoints.items() if cp.plan_id == plan_id]
            for cp_id in to_delete:
                self.delete_checkpoint(cp_id)
        else:
            for cp_id in list(self.checkpoints.keys()):
                self.delete_checkpoint(cp_id)
