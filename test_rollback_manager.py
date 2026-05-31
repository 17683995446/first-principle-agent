import unittest
from first_principle_agent.layers.rollback_manager import (
    RollbackManager,
    RollbackTransaction,
    RollbackOperation,
    RollbackOperationStatus
)


class TestRollbackManager(unittest.TestCase):
    """测试回滚管理器"""

    def setUp(self):
        """测试前准备"""
        self.manager = RollbackManager()
        self.test_data = []

    def _add_item(self, item):
        """添加数据"""
        self.test_data.append(item)
        return f"Added: {item}"

    def _remove_item(self, item):
        """删除数据"""
        if item in self.test_data:
            self.test_data.remove(item)
            return f"Removed: {item}"
        return f"Not found: {item}"

    def test_begin_transaction(self):
        """测试开始事务"""
        transaction = self.manager.begin_transaction("test_tx", "Test transaction")
        self.assertEqual(transaction.name, "test_tx")
        self.assertEqual(transaction.description, "Test transaction")
        self.assertIsNotNone(transaction.id)
        self.assertEqual(len(transaction.operations), 0)

    def test_add_operation(self):
        """测试添加操作"""
        self.manager.begin_transaction("test_tx")
        
        op = self.manager.add_operation(
            name="add_a",
            description="Add item A",
            execute_func=self._add_item,
            rollback_func=self._remove_item,
            execute_args=("A",),
            rollback_args=("A",)
        )
        
        self.assertEqual(op.name, "add_a")
        self.assertEqual(op.status, RollbackOperationStatus.PENDING)

    def test_execute_transaction(self):
        """测试执行事务"""
        self.manager.begin_transaction("test_tx")
        
        self.manager.add_operation(
            name="add_a",
            description="Add item A",
            execute_func=self._add_item,
            rollback_func=self._remove_item,
            execute_args=("A",),
            rollback_args=("A",)
        )
        
        self.manager.add_operation(
            name="add_b",
            description="Add item B",
            execute_func=self._add_item,
            rollback_func=self._remove_item,
            execute_args=("B",),
            rollback_args=("B",)
        )
        
        results = self.manager.execute_transaction()
        
        self.assertEqual(len(results), 2)
        self.assertEqual(self.test_data, ["A", "B"])

    def test_rollback_transaction(self):
        """测试回滚事务"""
        self.manager.begin_transaction("test_tx")
        
        self.manager.add_operation(
            name="add_a",
            description="Add item A",
            execute_func=self._add_item,
            rollback_func=self._remove_item,
            execute_args=("A",),
            rollback_args=("A",)
        )
        
        self.manager.add_operation(
            name="add_b",
            description="Add item B",
            execute_func=self._add_item,
            rollback_func=self._remove_item,
            execute_args=("B",),
            rollback_args=("B",)
        )
        
        self.manager.execute_transaction()
        self.assertEqual(self.test_data, ["A", "B"])
        
        # 回滚
        rollback_results = self.manager.rollback_transaction()
        self.assertEqual(len(rollback_results), 2)
        self.assertEqual(self.test_data, [])

    def test_auto_rollback_on_error(self):
        """测试出错时自动回滚"""
        self.manager.begin_transaction("test_tx")
        
        self.manager.add_operation(
            name="add_a",
            description="Add item A",
            execute_func=self._add_item,
            rollback_func=self._remove_item,
            execute_args=("A",),
            rollback_args=("A",)
        )
        
        # 会失败的操作
        def failing_func():
            raise ValueError("Intentional failure")
        
        self.manager.add_operation(
            name="fail_op",
            description="Failing operation",
            execute_func=failing_func,
            rollback_func=lambda: None
        )
        
        with self.assertRaises(ValueError):
            self.manager.execute_transaction()
        
        # 应该自动回滚，A被移除
        self.assertEqual(self.test_data, [])

    def test_rollback_to_operation(self):
        """测试回滚到指定操作"""
        self.manager.begin_transaction("test_tx")
        
        # 添加三个操作
        op1 = self.manager.add_operation(
            name="add_a",
            description="Add item A",
            execute_func=self._add_item,
            rollback_func=self._remove_item,
            execute_args=("A",),
            rollback_args=("A",)
        )
        
        op2 = self.manager.add_operation(
            name="add_b",
            description="Add item B",
            execute_func=self._add_item,
            rollback_func=self._remove_item,
            execute_args=("B",),
            rollback_args=("B",)
        )
        
        op3 = self.manager.add_operation(
            name="add_c",
            description="Add item C",
            execute_func=self._add_item,
            rollback_func=self._remove_item,
            execute_args=("C",),
            rollback_args=("C",)
        )
        
        self.manager.execute_transaction()
        self.assertEqual(self.test_data, ["A", "B", "C"])
        
        # 回滚到op2（即回滚op2和op3）
        self.manager.rollback_to_operation(op2.id)
        self.assertEqual(self.test_data, ["A"])

    def test_context_manager(self):
        """测试上下文管理器用法"""
        with self.manager.transaction("context_tx", "Test context") as mgr:
            mgr.add_operation(
                name="add_a",
                description="Add item A",
                execute_func=self._add_item,
                rollback_func=self._remove_item,
                execute_args=("A",),
                rollback_args=("A",)
            )
            mgr.execute_transaction()
        
        self.assertEqual(self.test_data, ["A"])

    def test_context_manager_auto_rollback(self):
        """测试上下文管理器异常时自动回滚"""
        with self.assertRaises(ValueError):
            with self.manager.transaction("error_tx", "Error test") as mgr:
                mgr.add_operation(
                    name="add_a",
                    description="Add item A",
                    execute_func=self._add_item,
                    rollback_func=self._remove_item,
                    execute_args=("A",),
                    rollback_args=("A",)
                )
                mgr.execute_transaction()
                raise ValueError("Intentional error")
        
        # 应该自动回滚
        self.assertEqual(self.test_data, [])

    def test_get_all_transactions(self):
        """测试获取所有事务"""
        self.manager.begin_transaction("tx1")
        self.manager.begin_transaction("tx2")
        
        transactions = self.manager.get_all_transactions()
        self.assertEqual(len(transactions), 2)

    def test_clear_completed_transactions(self):
        """测试清除已完成事务"""
        # 创建并执行一个事务
        tx1 = self.manager.begin_transaction("tx1")
        self.manager.add_operation(
            name="noop",
            description="No-op",
            execute_func=lambda: None,
            rollback_func=lambda: None
        )
        self.manager.execute_transaction()
        
        # 创建另一个事务不执行
        self.manager.begin_transaction("tx2")
        
        # 清除已完成的
        removed = self.manager.clear_completed_transactions()
        self.assertEqual(removed, 1)
        
        transactions = self.manager.get_all_transactions()
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0].name, "tx2")

    def test_operation_status_transitions(self):
        """测试操作状态转换"""
        self.manager.begin_transaction("test_tx")
        
        op = self.manager.add_operation(
            name="test_op",
            description="Test operation",
            execute_func=lambda: "ok",
            rollback_func=lambda: "rolled back"
        )
        
        self.assertEqual(op.status, RollbackOperationStatus.PENDING)
        
        self.manager.execute_transaction()
        self.assertEqual(op.status, RollbackOperationStatus.EXECUTED)
        
        self.manager.rollback_transaction()
        self.assertEqual(op.status, RollbackOperationStatus.ROLLED_BACK)

    def test_transaction_serialization(self):
        """测试事务序列化"""
        self.manager.begin_transaction("test_tx")
        self.manager.add_operation(
            name="test_op",
            description="Test op",
            execute_func=lambda: None,
            rollback_func=lambda: None
        )
        self.manager.execute_transaction()
        
        tx = self.manager.get_transaction(self.manager.current_transaction.id)
        data = tx.to_dict()
        
        self.assertIn("id", data)
        self.assertIn("operations", data)
        self.assertIn("created_at", data)
        
        # 反序列化
        restored = RollbackTransaction.from_dict(data)
        self.assertEqual(restored.id, tx.id)
        self.assertEqual(restored.name, tx.name)


if __name__ == "__main__":
    unittest.main()
