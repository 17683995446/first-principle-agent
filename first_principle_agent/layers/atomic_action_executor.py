from typing import Any, Callable, Dict, List, Optional
from threading import Thread, Lock, Event
from concurrent.futures import ThreadPoolExecutor, Future
import time
from ..core import AtomicAction, AtomicActionPlan, AtomicActionStatus, ActionType


class ExecutionResult:
    """执行结果"""

    def __init__(self, success: bool, output: Any = None, error: Optional[str] = None):
        self.success = success
        self.output = output
        self.error = error
        self.timestamp = time.time()


class AtomicActionExecutor:
    """原子动作执行器 - 执行原子动作计划"""

    def __init__(self, max_workers: int = 4, enable_parallel: bool = True):
        self.max_workers = max_workers
        self.enable_parallel = enable_parallel
        self.executor: Optional[ThreadPoolExecutor] = None
        self.running_actions: Dict[str, Future] = {}
        self.action_handlers: Dict[ActionType, Callable] = {}
        self.execution_lock = Lock()
        self.stop_event = Event()

        self._register_default_handlers()

    def _register_default_handlers(self):
        """注册默认的动作处理器"""

        def handle_init(action: AtomicAction) -> ExecutionResult:
            time.sleep(0.1)
            return ExecutionResult(True, {"initialized": True})

        def handle_compute(action: AtomicAction) -> ExecutionResult:
            time.sleep(0.2)
            return ExecutionResult(True, {"computed": True})

        def handle_read(action: AtomicAction) -> ExecutionResult:
            time.sleep(0.15)
            return ExecutionResult(True, {"data": "sample_data"})

        def handle_write(action: AtomicAction) -> ExecutionResult:
            time.sleep(0.15)
            return ExecutionResult(True, {"written": True})

        def handle_validate(action: AtomicAction) -> ExecutionResult:
            time.sleep(0.1)
            return ExecutionResult(True, {"valid": True})

        def handle_transform(action: AtomicAction) -> ExecutionResult:
            time.sleep(0.2)
            return ExecutionResult(True, {"transformed": True})

        def handle_send(action: AtomicAction) -> ExecutionResult:
            time.sleep(0.2)
            return ExecutionResult(True, {"sent": True})

        def handle_receive(action: AtomicAction) -> ExecutionResult:
            time.sleep(0.2)
            return ExecutionResult(True, {"received": True})

        def handle_cleanup(action: AtomicAction) -> ExecutionResult:
            time.sleep(0.1)
            return ExecutionResult(True, {"cleaned": True})

        self.action_handlers = {
            ActionType.INIT: handle_init,
            ActionType.COMPUTE: handle_compute,
            ActionType.READ: handle_read,
            ActionType.WRITE: handle_write,
            ActionType.VALIDATE: handle_validate,
            ActionType.TRANSFORM: handle_transform,
            ActionType.SEND: handle_send,
            ActionType.RECEIVE: handle_receive,
            ActionType.CLEANUP: handle_cleanup,
        }

    def register_handler(self, action_type: ActionType, handler: Callable[[AtomicAction], ExecutionResult]):
        """注册动作处理器"""
        self.action_handlers[action_type] = handler

    def execute_plan(self, plan: AtomicActionPlan, callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        执行动作计划

        Args:
            plan: 原子动作计划
            callback: 执行进度回调函数

        Returns:
            执行结果
        """
        if self.enable_parallel:
            return self._execute_parallel(plan, callback)
        else:
            return self._execute_sequential(plan, callback)

    def _execute_sequential(self, plan: AtomicActionPlan, callback: Optional[Callable]) -> Dict[str, Any]:
        """顺序执行"""
        plan.mark_started()
        results = {}
        start_time = time.time()

        completed_ids = set()
        failed = False

        while not plan.is_complete() and not failed:
            ready_actions = plan.get_ready_actions()

            if not ready_actions:
                if not failed:
                    failed = True
                break

            for action in ready_actions:
                result = self._execute_single_action(action, plan)

                if result.success:
                    completed_ids.add(action.action_id)
                    results[action.action_id] = result
                else:
                    failed = True
                    results[action.action_id] = result

                if callback:
                    progress = plan.get_progress()
                    callback(action, result, progress)

        end_time = time.time()

        if not failed:
            plan.mark_completed()

        return {
            "success": not failed,
            "results": results,
            "duration": end_time - start_time,
            "completed_count": len(completed_ids),
            "total_count": len(plan.actions)
        }

    def _execute_parallel(self, plan: AtomicActionPlan, callback: Optional[Callable]) -> Dict[str, Any]:
        """并发执行"""
        plan.mark_started()
        results = {}
        start_time = time.time()

        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self.stop_event.clear()

        completed_ids = set()
        failed = False

        try:
            while not plan.is_complete() and not failed and not self.stop_event.is_set():
                ready_actions = plan.get_ready_actions()

                if not ready_actions:
                    time.sleep(0.1)
                    continue

                for action in ready_actions:
                    if action.action_id in self.running_actions:
                        continue

                    if not self._can_execute(action, completed_ids):
                        continue

                    future = self.executor.submit(self._execute_action_thread, action, plan)
                    self.running_actions[action.action_id] = future

                done_futures = [f for f in self.running_actions.values() if f.done()]
                for future in done_futures:
                    for action_id, f in list(self.running_actions.items()):
                        if f == future:
                            try:
                                result = f.result()
                                if result.success:
                                    completed_ids.add(action_id)
                                    results[action_id] = result
                                    plan.get_action(action_id).mark_success()
                                else:
                                    results[action_id] = result
                                    plan.get_action(action_id).mark_failed(error=result.error)
                                    failed = True

                                if callback:
                                    progress = plan.get_progress()
                                    callback(plan.get_action(action_id), result, progress)

                            except Exception as e:
                                results[action_id] = ExecutionResult(False, error=str(e))
                                plan.get_action(action_id).mark_failed(error=str(e))
                                failed = True

                            del self.running_actions[action_id]
                            break

                time.sleep(0.05)

        finally:
            # 等待所有正在运行的动作完成
            for action_id, future in list(self.running_actions.items()):
                try:
                    result = future.result(timeout=30)
                    if result.success:
                        completed_ids.add(action_id)
                        results[action_id] = result
                        plan.get_action(action_id).mark_success()
                    else:
                        results[action_id] = result
                        plan.get_action(action_id).mark_failed(error=result.error)
                        failed = True

                    if callback:
                        progress = plan.get_progress()
                        callback(plan.get_action(action_id), result, progress)

                except Exception as e:
                    results[action_id] = ExecutionResult(False, error=str(e))
                    plan.get_action(action_id).mark_failed(error=str(e))
                    failed = True

            if self.executor:
                self.executor.shutdown(wait=True)
                self.executor = None

        end_time = time.time()

        if not failed:
            plan.mark_completed()

        return {
            "success": not failed,
            "results": results,
            "duration": end_time - start_time,
            "completed_count": len(completed_ids),
            "total_count": len(plan.actions)
        }

    def _can_execute(self, action: AtomicAction, completed_ids: set) -> bool:
        """检查动作是否可以执行"""
        return all(dep in completed_ids for dep in action.dependencies)

    def _execute_single_action(self, action: AtomicAction, plan: AtomicActionPlan) -> ExecutionResult:
        """执行单个动作"""
        try:
            handler = self.action_handlers.get(action.action_type)
            if not handler:
                return ExecutionResult(False, error=f"No handler for action type {action.action_type}")

            action.mark_running()

            result = handler(action)

            if result.success:
                action.mark_success(outputs=result.output if result.output else {})
            else:
                action.mark_failed(error=result.error)

            return result

        except Exception as e:
            action.mark_failed(error=str(e))
            return ExecutionResult(False, error=str(e))

    def _execute_action_thread(self, action: AtomicAction, plan: AtomicActionPlan) -> ExecutionResult:
        """在线程中执行动作"""
        with self.execution_lock:
            return self._execute_single_action(action, plan)

    def stop(self):
        """停止执行"""
        self.stop_event.set()
        if self.executor:
            self.executor.shutdown(wait=False)

    def get_execution_stats(self, plan: AtomicActionPlan) -> Dict[str, Any]:
        """获取执行统计信息"""
        stats = {
            "total": len(plan.actions),
            "by_status": {},
            "by_type": {},
            "total_duration": 0.0
        }

        for action in plan.actions:
            status_name = action.status.value
            stats["by_status"][status_name] = stats["by_status"].get(status_name, 0) + 1

            type_name = action.action_type.value
            stats["by_type"][type_name] = stats["by_type"].get(type_name, 0) + 1

            duration = action.get_duration()
            if duration:
                stats["total_duration"] += duration

        return stats

    def validate_before_execution(self, plan: AtomicActionPlan) -> Dict[str, Any]:
        """执行前验证"""
        errors = []
        warnings = []

        if not plan.actions:
            errors.append("Plan has no actions")

        for action in plan.actions:
            if action.action_type not in self.action_handlers:
                warnings.append(f"Action {action.action_id} has no registered handler")

            for dep_id in action.dependencies:
                if not plan.get_action(dep_id):
                    errors.append(f"Action {action.action_id} depends on non-existent action {dep_id}")

        return {
            "ready": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
