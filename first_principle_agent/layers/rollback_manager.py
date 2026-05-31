from enum import Enum
import time
from typing import Callable, Optional, Any, Dict, List
from dataclasses import dataclass, field
from first_principle_agent.core.base import JSONSerializable


class RollbackOperationStatus(Enum):
    """回滚操作状态枚举"""
    PENDING = "pending"  # 待执行
    EXECUTED = "executed"  # 已执行
    FAILED = "failed"  # 执行失败
    ROLLED_BACK = "rolled_back"  # 已回滚


@dataclass
class RollbackOperation(JSONSerializable):
    """单个回滚操作"""
    id: str
    name: str
    description: str
    execute_func: Callable
    rollback_func: Callable
    execute_args: tuple = field(default_factory=tuple)
    execute_kwargs: dict = field(default_factory=dict)
    rollback_args: tuple = field(default_factory=tuple)
    rollback_kwargs: dict = field(default_factory=dict)
    status: RollbackOperationStatus = RollbackOperationStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    executed_at: Optional[float] = None
    rolled_back_at: Optional[float] = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "result": str(self.result) if self.result is not None else None,
            "error": self.error,
            "created_at": self.created_at,
            "executed_at": self.executed_at,
            "rolled_back_at": self.rolled_back_at
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "RollbackOperation":
        # 注意：函数无法反序列化，所以这里只反序列化元数据
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            execute_func=lambda: None,
            rollback_func=lambda: None,
            status=RollbackOperationStatus(data["status"]),
            error=data.get("error"),
            created_at=data["created_at"],
            executed_at=data.get("executed_at"),
            rolled_back_at=data.get("rolled_back_at")
        )

    def execute(self) -> Any:
        """执行操作"""
        try:
            self.result = self.execute_func(*self.execute_args, **self.execute_kwargs)
            self.status = RollbackOperationStatus.EXECUTED
            self.executed_at = time.time()
            return self.result
        except Exception as e:
            self.status = RollbackOperationStatus.FAILED
            self.error = str(e)
            raise

    def rollback(self) -> Any:
        """回滚操作"""
        try:
            result = self.rollback_func(*self.rollback_args, **self.rollback_kwargs)
            self.status = RollbackOperationStatus.ROLLED_BACK
            self.rolled_back_at = time.time()
            return result
        except Exception as e:
            self.error = str(e)
            raise


@dataclass
class RollbackTransaction(JSONSerializable):
    """回滚事务（一组操作）"""
    id: str
    name: str
    description: str
    operations: List[RollbackOperation] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    rolled_back_at: Optional[float] = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "operations": [op.to_dict() for op in self.operations],
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "rolled_back_at": self.rolled_back_at
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "RollbackTransaction":
        operations = [RollbackOperation.from_dict(op_data) for op_data in data["operations"]]
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            operations=operations,
            created_at=data["created_at"],
            completed_at=data.get("completed_at"),
            rolled_back_at=data.get("rolled_back_at")
        )


class RollbackManager:
    """回滚管理器 - 管理操作的执行和回滚"""

    def __init__(self):
        """初始化回滚管理器"""
        self.transactions: Dict[str, RollbackTransaction] = {}
        self.current_transaction: Optional[RollbackTransaction] = None
        self._operation_id_counter: int = 0
        self._transaction_id_counter: int = 0

    def _generate_operation_id(self) -> str:
        """生成操作ID"""
        self._operation_id_counter += 1
        return f"op_{self._operation_id_counter}"

    def _generate_transaction_id(self) -> str:
        """生成事务ID"""
        self._transaction_id_counter += 1
        return f"tx_{self._transaction_id_counter}"

    def begin_transaction(self, name: str, description: str = "") -> RollbackTransaction:
        """
        开始一个新事务
        
        Args:
            name: 事务名称
            description: 事务描述
            
        Returns:
            新创建的事务
        """
        tx_id = self._generate_transaction_id()
        transaction = RollbackTransaction(
            id=tx_id,
            name=name,
            description=description
        )
        self.transactions[tx_id] = transaction
        self.current_transaction = transaction
        return transaction

    def add_operation(
        self,
        name: str,
        description: str,
        execute_func: Callable,
        rollback_func: Callable,
        execute_args: tuple = (),
        execute_kwargs: dict = None,
        rollback_args: tuple = (),
        rollback_kwargs: dict = None,
        transaction_id: Optional[str] = None
    ) -> RollbackOperation:
        """
        添加一个回滚操作到事务
        
        Args:
            name: 操作名称
            description: 操作描述
            execute_func: 执行函数
            rollback_func: 回滚函数
            execute_args: 执行函数位置参数
            execute_kwargs: 执行函数关键字参数
            rollback_args: 回滚函数位置参数
            rollback_kwargs: 回滚函数关键字参数
            transaction_id: 事务ID（如果为None，使用当前事务）
            
        Returns:
            创建的回滚操作
        """
        transaction = self._get_transaction(transaction_id)
        if not transaction:
            raise ValueError("No active transaction. Call begin_transaction first.")
        
        op_id = self._generate_operation_id()
        operation = RollbackOperation(
            id=op_id,
            name=name,
            description=description,
            execute_func=execute_func,
            rollback_func=rollback_func,
            execute_args=execute_args,
            execute_kwargs=execute_kwargs or {},
            rollback_args=rollback_args,
            rollback_kwargs=rollback_kwargs or {}
        )
        transaction.operations.append(operation)
        return operation

    def _get_transaction(self, transaction_id: Optional[str] = None) -> Optional[RollbackTransaction]:
        """获取事务"""
        if transaction_id:
            return self.transactions.get(transaction_id)
        return self.current_transaction

    def execute_transaction(self, transaction_id: Optional[str] = None) -> List[Any]:
        """
        执行事务中的所有操作
        
        Args:
            transaction_id: 事务ID（如果为None，使用当前事务）
            
        Returns:
            所有操作的执行结果列表
        """
        transaction = self._get_transaction(transaction_id)
        if not transaction:
            raise ValueError("No active transaction. Call begin_transaction first.")
        
        results = []
        try:
            for operation in transaction.operations:
                if operation.status == RollbackOperationStatus.PENDING:
                    result = operation.execute()
                    results.append(result)
            transaction.completed_at = time.time()
            return results
        except Exception:
            # 出错时自动回滚已执行的操作
            self.rollback_transaction(transaction.id)
            raise

    def rollback_transaction(self, transaction_id: Optional[str] = None) -> List[Any]:
        """
        回滚事务（从后往前执行回滚操作）
        
        Args:
            transaction_id: 事务ID（如果为None，使用当前事务）
            
        Returns:
            所有回滚操作的结果列表
        """
        transaction = self._get_transaction(transaction_id)
        if not transaction:
            raise ValueError("Transaction not found.")
        
        results = []
        # 从后往前回滚
        for operation in reversed(transaction.operations):
            if operation.status == RollbackOperationStatus.EXECUTED:
                result = operation.rollback()
                results.append(result)
        transaction.rolled_back_at = time.time()
        return results

    def rollback_to_operation(self, operation_id: str, transaction_id: Optional[str] = None) -> List[Any]:
        """
        回滚到指定操作之前
        
        Args:
            operation_id: 回滚到该操作之前
            transaction_id: 事务ID（如果为None，使用当前事务）
            
        Returns:
            回滚操作的结果列表
        """
        transaction = self._get_transaction(transaction_id)
        if not transaction:
            raise ValueError("Transaction not found.")
        
        # 找到目标操作的索引
        target_index = None
        for i, op in enumerate(transaction.operations):
            if op.id == operation_id:
                target_index = i
                break
        
        if target_index is None:
            raise ValueError(f"Operation {operation_id} not found in transaction.")
        
        results = []
        # 回滚目标操作之后的所有操作（包括目标操作）
        for i in reversed(range(target_index, len(transaction.operations))):
            operation = transaction.operations[i]
            if operation.status == RollbackOperationStatus.EXECUTED:
                result = operation.rollback()
                results.append(result)
        
        return results

    def get_transaction(self, transaction_id: str) -> Optional[RollbackTransaction]:
        """获取事务"""
        return self.transactions.get(transaction_id)

    def get_all_transactions(self) -> List[RollbackTransaction]:
        """获取所有事务"""
        return list(self.transactions.values())

    def clear_completed_transactions(self, keep_rolled_back: bool = False) -> int:
        """
        清除已完成的事务
        
        Args:
            keep_rolled_back: 是否保留已回滚的事务
            
        Returns:
            清除的事务数量
        """
        removed = 0
        tx_ids_to_remove = []
        
        for tx_id, tx in self.transactions.items():
            if tx.completed_at is not None:
                if not keep_rolled_back or tx.rolled_back_at is None:
                    tx_ids_to_remove.append(tx_id)
        
        for tx_id in tx_ids_to_remove:
            del self.transactions[tx_id]
            removed += 1
        
        return removed

    def transaction(self, name: str, description: str = ""):
        """
        支持上下文管理器用法
        
        Args:
            name: 事务名称
            description: 事务描述
        """
        return _TransactionContext(self, name, description)


class _TransactionContext:
    """事务上下文管理器"""

    def __init__(self, manager: RollbackManager, name: str, description: str):
        self.manager = manager
        self.name = name
        self.description = description
        self.transaction: Optional[RollbackTransaction] = None

    def __enter__(self):
        self.transaction = self.manager.begin_transaction(self.name, self.description)
        return self.manager

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # 发生异常，回滚事务
            self.manager.rollback_transaction(self.transaction.id)
        return False  # 不抑制异常
