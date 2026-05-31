from typing import Any, Callable, Dict, List, Optional
from threading import Thread, Lock, Event
from collections import defaultdict
import time
from ..core import AtomicAction, AtomicActionPlan, AtomicActionStatus, ActionType


class ActionMetrics:
    """动作性能指标"""

    def __init__(self, action_id: str):
        self.action_id = action_id
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.duration: Optional[float] = None
        self.attempts = 0
        self.successes = 0
        self.failures = 0
        self.timeouts = 0
        self.status_history: List[Dict[str, Any]] = []

    def record_start(self, timestamp: Optional[float] = None):
        """记录开始"""
        self.start_time = timestamp or time.time()
        self.attempts += 1

    def record_end(self, timestamp: Optional[float] = None, status: Optional[AtomicActionStatus] = None):
        """记录结束"""
        self.end_time = timestamp or time.time()
        if self.start_time:
            self.duration = self.end_time - self.start_time

        if status:
            self._record_status(status)

    def _record_status(self, status: AtomicActionStatus):
        """记录状态变化"""
        self.status_history.append({
            "status": status.value,
            "timestamp": time.time()
        })

        if status == AtomicActionStatus.SUCCESS:
            self.successes += 1
        elif status == AtomicActionStatus.FAILED:
            self.failures += 1
        elif status == AtomicActionStatus.TIMEOUT:
            self.timeouts += 1

    def get_success_rate(self) -> float:
        """获取成功率"""
        if self.attempts == 0:
            return 0.0
        return (self.successes / self.attempts) * 100

    def get_average_duration(self) -> Optional[float]:
        """获取平均执行时长"""
        return self.duration

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "action_id": self.action_id,
            "attempts": self.attempts,
            "successes": self.successes,
            "failures": self.failures,
            "timeouts": self.timeouts,
            "success_rate": self.get_success_rate(),
            "duration": self.duration,
            "status_history": self.status_history
        }


class AtomicActionMonitor:
    """原子动作监控器 - 实时监控和收集动作执行指标"""

    def __init__(self, check_interval: float = 1.0):
        self.check_interval = check_interval
        self.metrics: Dict[str, ActionMetrics] = {}
        self.metrics_lock = Lock()
        self.monitoring = False
        self.monitor_thread: Optional[Thread] = None
        self.stop_event = Event()
        self.alerts: List[Dict[str, Any]] = []
        self.callbacks: List[Callable] = []

    def start_monitoring(self, plan: AtomicActionPlan):
        """开始监控"""
        self.monitoring = True
        self.stop_event.clear()

        for action in plan.actions:
            if action.action_id not in self.metrics:
                self.metrics[action.action_id] = ActionMetrics(action.action_id)

        self.monitor_thread = Thread(target=self._monitor_loop, args=(plan,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        self.stop_event.set()

        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
            self.monitor_thread = None

    def _monitor_loop(self, plan: AtomicActionPlan):
        """监控循环"""
        while self.monitoring and not self.stop_event.is_set():
            try:
                self._check_actions(plan)
                self._collect_metrics(plan)
                self._check_alerts(plan)
                self._notify_callbacks(plan)

                time.sleep(self.check_interval)

            except Exception as e:
                print(f"Monitor error: {e}")

    def _check_actions(self, plan: AtomicActionPlan):
        """检查动作状态"""
        for action in plan.actions:
            metrics = self.metrics.get(action.action_id)
            if not metrics:
                continue

            if action.status == AtomicActionStatus.PENDING and not metrics.start_time:
                pass
            elif action.status == AtomicActionStatus.RUNNING and not metrics.start_time:
                metrics.record_start(action.start_time)
            elif action.status in [AtomicActionStatus.SUCCESS, AtomicActionStatus.FAILED, AtomicActionStatus.TIMEOUT]:
                if metrics.start_time and not metrics.end_time:
                    metrics.record_end(action.end_time, action.status)

    def _collect_metrics(self, plan: AtomicActionPlan):
        """收集指标"""
        with self.metrics_lock:
            progress = plan.get_progress()

            if progress["running"] > 0:
                for action in plan.get_actions_by_status(AtomicActionStatus.RUNNING):
                    metrics = self.metrics.get(action.action_id)
                    if metrics and not metrics.start_time:
                        metrics.record_start()

    def _check_alerts(self, plan: AtomicActionPlan):
        """检查告警"""
        for action in plan.actions:
            if action.status == AtomicActionStatus.TIMEOUT:
                self.alerts.append({
                    "type": "timeout",
                    "action_id": action.action_id,
                    "timestamp": time.time(),
                    "message": f"Action {action.action_id} timed out"
                })

            metrics = self.metrics.get(action.action_id)
            if metrics and metrics.attempts > 3:
                if metrics.get_success_rate() < 50:
                    self.alerts.append({
                        "type": "low_success_rate",
                        "action_id": action.action_id,
                        "timestamp": time.time(),
                        "message": f"Action {action.action_id} has low success rate: {metrics.get_success_rate():.2f}%"
                    })

    def _notify_callbacks(self, plan: AtomicActionPlan):
        """通知回调"""
        for callback in self.callbacks:
            try:
                callback(plan, self.get_current_status())
            except Exception as e:
                print(f"Callback error: {e}")

    def get_current_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        with self.metrics_lock:
            total_actions = len(self.metrics)
            running = 0
            completed = 0
            failed = 0

            for metrics in self.metrics.values():
                if metrics.end_time:
                    completed += 1
                    if metrics.failures > 0 or metrics.timeouts > 0:
                        failed += 1
                elif metrics.start_time:
                    running += 1

            return {
                "total_actions": total_actions,
                "running": running,
                "completed": completed,
                "failed": failed,
                "pending": total_actions - running - completed,
                "timestamp": time.time()
            }

    def get_metrics(self, action_id: Optional[str] = None) -> Dict[str, ActionMetrics]:
        """获取指标"""
        with self.metrics_lock:
            if action_id:
                return {action_id: self.metrics.get(action_id)} if action_id in self.metrics else {}
            return self.metrics.copy()

    def get_summary(self) -> Dict[str, Any]:
        """获取监控摘要"""
        with self.metrics_lock:
            total_attempts = sum(m.attempts for m in self.metrics.values())
            total_successes = sum(m.successes for m in self.metrics.values())
            total_failures = sum(m.failures for m in self.metrics.values())
            total_timeouts = sum(m.timeouts for m in self.metrics.values())

            durations = [m.duration for m in self.metrics.values() if m.duration is not None]
            avg_duration = sum(durations) / len(durations) if durations else 0.0
            max_duration = max(durations) if durations else 0.0
            min_duration = min(durations) if durations else 0.0

            by_type: Dict[str, Dict[str, int]] = defaultdict(lambda: {"attempts": 0, "successes": 0, "failures": 0})

            return {
                "total_actions": len(self.metrics),
                "total_attempts": total_attempts,
                "total_successes": total_successes,
                "total_failures": total_failures,
                "total_timeouts": total_timeouts,
                "overall_success_rate": (total_successes / total_attempts * 100) if total_attempts > 0 else 0.0,
                "duration_stats": {
                    "average": avg_duration,
                    "max": max_duration,
                    "min": min_duration,
                    "total": sum(durations)
                },
                "alerts": self.alerts.copy()
            }

    def get_detailed_report(self) -> str:
        """获取详细报告"""
        lines = []
        lines.append("=" * 60)
        lines.append("原子动作监控报告")
        lines.append("=" * 60)
        lines.append("")

        summary = self.get_summary()

        lines.append("总体统计:")
        lines.append(f"  总动作数: {summary['total_actions']}")
        lines.append(f"  总尝试次数: {summary['total_attempts']}")
        lines.append(f"  成功次数: {summary['total_successes']}")
        lines.append(f"  失败次数: {summary['total_failures']}")
        lines.append(f"  超时次数: {summary['total_timeouts']}")
        lines.append(f"  成功率: {summary['overall_success_rate']:.2f}%")
        lines.append("")

        lines.append("执行时长统计:")
        duration_stats = summary['duration_stats']
        lines.append(f"  平均: {duration_stats['average']:.3f}秒")
        lines.append(f"  最大: {duration_stats['max']:.3f}秒")
        lines.append(f"  最小: {duration_stats['min']:.3f}秒")
        lines.append(f"  总计: {duration_stats['total']:.3f}秒")
        lines.append("")

        if summary['alerts']:
            lines.append(f"告警 ({len(summary['alerts'])}):")
            for alert in summary['alerts']:
                lines.append(f"  [{alert['type']}] {alert['message']}")
            lines.append("")

        lines.append("详细指标:")
        with self.metrics_lock:
            for action_id, metrics in self.metrics.items():
                lines.append(f"  {action_id}:")
                lines.append(f"    尝试: {metrics.attempts}, 成功: {metrics.successes}, 失败: {metrics.failures}")
                lines.append(f"    成功率: {metrics.get_success_rate():.2f}%")
                if metrics.duration:
                    lines.append(f"    时长: {metrics.duration:.3f}秒")

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)

    def register_callback(self, callback: Callable):
        """注册回调"""
        if callback not in self.callbacks:
            self.callbacks.append(callback)

    def unregister_callback(self, callback: Callable):
        """注销回调"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def clear_alerts(self):
        """清除告警"""
        self.alerts.clear()

    def reset(self):
        """重置监控器"""
        self.stop_monitoring()
        with self.metrics_lock:
            self.metrics.clear()
        self.alerts.clear()
        self.callbacks.clear()
