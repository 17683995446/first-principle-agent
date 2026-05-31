#!/usr/bin/env python3
"""
系统监控与健康检查 - 第61阶段
提供系统级监控和健康检查功能
"""

import os
import sys
import time
import psutil
import json
import uuid
import threading
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class HealthStatus(Enum):
    """健康状态枚举"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class MetricType(Enum):
    """指标类型枚举"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    CUSTOM = "custom"


@dataclass
class SystemMetrics:
    """系统指标数据类"""
    timestamp: float = field(default_factory=time.time)
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used_mb: float = 0.0
    memory_total_mb: float = 0.0
    disk_percent: float = 0.0
    disk_used_gb: float = 0.0
    disk_total_gb: float = 0.0
    network_sent_mb: float = 0.0
    network_recv_mb: float = 0.0
    process_count: int = 0
    thread_count: int = 0
    uptime_seconds: float = 0.0


@dataclass
class HealthCheckResult:
    """健康检查结果"""
    component: str
    status: HealthStatus
    message: str
    timestamp: float = field(default_factory=time.time)
    details: Dict[str, Any] = field(default_factory=dict)
    response_time_ms: float = 0.0


@dataclass
class MonitorSnapshot:
    """监控快照"""
    snapshot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    metrics: Optional[SystemMetrics] = None
    health_checks: List[HealthCheckResult] = field(default_factory=list)
    overall_status: HealthStatus = HealthStatus.UNKNOWN
    metadata: Dict[str, Any] = field(default_factory=dict)


class SystemMonitor:
    """系统监控器"""
    
    def __init__(self, collection_interval: int = 5):
        """初始化系统监控器"""
        self.monitor_id = str(uuid.uuid4())
        self.collection_interval = collection_interval
        self.metrics_history: List[SystemMetrics] = []
        self.max_history_size = 100
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._callbacks: List[Callable] = []
    
    def start_monitoring(self):
        """开始监控"""
        if self._monitoring:
            print("⚠️  监控已经在运行中")
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        print(f"✅ 系统监控已启动 (ID: {self.monitor_id})")
    
    def stop_monitoring(self):
        """停止监控"""
        if not self._monitoring:
            print("⚠️  监控未运行")
            return
        
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)
        print("✅ 系统监控已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self._monitoring:
            try:
                metrics = self.collect_metrics()
                self.add_metrics(metrics)
                
                # 调用回调
                for callback in self._callbacks:
                    try:
                        callback(metrics)
                    except Exception as e:
                        print(f"⚠️  监控回调执行失败: {e}")
                
                time.sleep(self.collection_interval)
            except Exception as e:
                print(f"⚠️  监控循环出错: {e}")
    
    def collect_metrics(self) -> SystemMetrics:
        """收集系统指标"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # 内存
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            memory_total_mb = memory.total / (1024 * 1024)
            
            # 磁盘
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used_gb = disk.used / (1024 * 1024 * 1024)
            disk_total_gb = disk.total / (1024 * 1024 * 1024)
            
            # 网络
            net_io = psutil.net_io_counters()
            network_sent_mb = net_io.bytes_sent / (1024 * 1024)
            network_recv_mb = net_io.bytes_recv / (1024 * 1024)
            
            # 进程和线程
            process = psutil.Process()
            process_count = len(psutil.pids())
            thread_count = process.num_threads()
            
            # 运行时间
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            
            return SystemMetrics(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                memory_total_mb=memory_total_mb,
                disk_percent=disk_percent,
                disk_used_gb=disk_used_gb,
                disk_total_gb=disk_total_gb,
                network_sent_mb=network_sent_mb,
                network_recv_mb=network_recv_mb,
                process_count=process_count,
                thread_count=thread_count,
                uptime_seconds=uptime_seconds
            )
        except Exception as e:
            print(f"⚠️  收集系统指标失败: {e}")
            return SystemMetrics()
    
    def add_metrics(self, metrics: SystemMetrics):
        """添加指标到历史记录"""
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history.pop(0)
    
    def get_latest_metrics(self) -> Optional[SystemMetrics]:
        """获取最新指标"""
        return self.metrics_history[-1] if self.metrics_history else None
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        if not self.metrics_history:
            return {"status": "no_data"}
        
        latest = self.metrics_history[-1]
        cpu_values = [m.cpu_percent for m in self.metrics_history]
        mem_values = [m.memory_percent for m in self.metrics_history]
        
        return {
            "latest": {
                "cpu_percent": latest.cpu_percent,
                "memory_percent": latest.memory_percent,
                "disk_percent": latest.disk_percent
            },
            "average": {
                "cpu_percent": sum(cpu_values) / len(cpu_values),
                "memory_percent": sum(mem_values) / len(mem_values)
            },
            "max": {
                "cpu_percent": max(cpu_values),
                "memory_percent": max(mem_values)
            },
            "history_size": len(self.metrics_history)
        }
    
    def add_callback(self, callback: Callable):
        """添加监控回调"""
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable):
        """移除监控回调"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)


class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        """初始化健康检查器"""
        self.checker_id = str(uuid.uuid4())
        self.check_results: Dict[str, HealthCheckResult] = {}
    
    def check_all(self) -> List[HealthCheckResult]:
        """执行所有健康检查"""
        results = []
        
        results.append(self.check_system_resources())
        results.append(self.check_components())
        results.append(self.check_dependencies())
        results.append(self.check_permissions())
        
        for result in results:
            self.check_results[result.component] = result
        
        return results
    
    def check_system_resources(self) -> HealthCheckResult:
        """检查系统资源"""
        start_time = time.time()
        
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent
            disk_percent = psutil.disk_usage('/').percent
            
            # 判断健康状态
            if cpu_percent > 90 or memory_percent > 90 or disk_percent > 95:
                status = HealthStatus.UNHEALTHY
                message = "系统资源使用率过高"
            elif cpu_percent > 70 or memory_percent > 70 or disk_percent > 80:
                status = HealthStatus.DEGRADED
                message = "系统资源使用率较高"
            else:
                status = HealthStatus.HEALTHY
                message = "系统资源使用正常"
            
            return HealthCheckResult(
                component="SystemResources",
                status=status,
                message=message,
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent,
                    "disk_percent": disk_percent
                },
                response_time_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
            return HealthCheckResult(
                component="SystemResources",
                status=HealthStatus.UNHEALTHY,
                message=f"健康检查失败: {e}",
                response_time_ms=(time.time() - start_time) * 1000
            )
    
    def check_components(self) -> HealthCheckResult:
        """检查核心组件"""
        start_time = time.time()
        
        try:
            # 检查核心组件是否可以导入
            components = [
                ("TaskTuple", "first_principle_agent.core.task_tuple"),
                ("TaskDAG", "first_principle_agent.core.dag_structures"),
                ("TaskOrchestrator", "first_principle_agent.core.task_orchestrator"),
                ("TaskExecutionEngine", "first_principle_agent.core.task_execution_engine")
            ]
            
            available = []
            unavailable = []
            
            for name, module_path in components:
                try:
                    __import__(module_path)
                    available.append(name)
                except Exception:
                    unavailable.append(name)
            
            if unavailable:
                status = HealthStatus.DEGRADED
                message = f"部分组件不可用: {', '.join(unavailable)}"
            else:
                status = HealthStatus.HEALTHY
                message = f"所有 {len(available)} 个核心组件正常"
            
            return HealthCheckResult(
                component="CoreComponents",
                status=status,
                message=message,
                details={
                    "available": available,
                    "unavailable": unavailable,
                    "total": len(components)
                },
                response_time_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
            return HealthCheckResult(
                component="CoreComponents",
                status=HealthStatus.UNHEALTHY,
                message=f"组件检查失败: {e}",
                response_time_ms=(time.time() - start_time) * 1000
            )
    
    def check_dependencies(self) -> HealthCheckResult:
        """检查依赖项"""
        start_time = time.time()
        
        try:
            dependencies = ["psutil", "json", "threading", "uuid", "time"]
            available = []
            unavailable = []
            
            for dep in dependencies:
                try:
                    __import__(dep)
                    available.append(dep)
                except Exception:
                    unavailable.append(dep)
            
            if unavailable:
                status = HealthStatus.UNHEALTHY
                message = f"缺少依赖: {', '.join(unavailable)}"
            else:
                status = HealthStatus.HEALTHY
                message = "所有依赖项正常"
            
            return HealthCheckResult(
                component="Dependencies",
                status=status,
                message=message,
                details={
                    "available": available,
                    "unavailable": unavailable
                },
                response_time_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
            return HealthCheckResult(
                component="Dependencies",
                status=HealthStatus.UNHEALTHY,
                message=f"依赖检查失败: {e}",
                response_time_ms=(time.time() - start_time) * 1000
            )
    
    def check_permissions(self) -> HealthCheckResult:
        """检查权限"""
        start_time = time.time()
        
        try:
            # 检查读写权限
            can_read = os.access('.', os.R_OK)
            can_write = os.access('.', os.W_OK)
            can_execute = os.access('.', os.X_OK)
            
            if not can_write:
                status = HealthStatus.DEGRADED
                message = "当前目录不可写"
            elif not can_read:
                status = HealthStatus.UNHEALTHY
                message = "当前目录不可读"
            else:
                status = HealthStatus.HEALTHY
                message = "权限检查正常"
            
            return HealthCheckResult(
                component="Permissions",
                status=status,
                message=message,
                details={
                    "can_read": can_read,
                    "can_write": can_write,
                    "can_execute": can_execute
                },
                response_time_ms=(time.time() - start_time) * 1000
            )
        except Exception as e:
            return HealthCheckResult(
                component="Permissions",
                status=HealthStatus.UNHEALTHY,
                message=f"权限检查失败: {e}",
                response_time_ms=(time.time() - start_time) * 1000
            )
    
    def get_overall_status(self) -> HealthStatus:
        """获取整体健康状态"""
        if not self.check_results:
            return HealthStatus.UNKNOWN
        
        statuses = [result.status for result in self.check_results.values()]
        
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        elif all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN
    
    def generate_report(self) -> Dict[str, Any]:
        """生成健康检查报告"""
        results = self.check_all()
        overall = self.get_overall_status()
        
        return {
            "checker_id": self.checker_id,
            "timestamp": datetime.now().isoformat(),
            "overall_status": overall.value,
            "checks": [
                {
                    "component": r.component,
                    "status": r.status.value,
                    "message": r.message,
                    "details": r.details,
                    "response_time_ms": r.response_time_ms
                }
                for r in results
            ]
        }


class MonitorCLI:
    """监控命令行接口"""
    
    def __init__(self):
        """初始化监控CLI"""
        self.monitor = SystemMonitor()
        self.health_checker = HealthChecker()
    
    def run(self, args: List[str]) -> bool:
        """运行监控命令"""
        if not args:
            return self._show_status()
        
        command = args[0].lower()
        
        if command == "status":
            return self._show_status()
        elif command == "metrics":
            return self._show_metrics()
        elif command == "health":
            return self._run_health_check()
        elif command == "start":
            return self._start_monitoring()
        elif command == "stop":
            return self._stop_monitoring()
        elif command == "report":
            return self._generate_report()
        else:
            print(f"❌ 未知命令: {command}")
            return False
    
    def _show_status(self) -> bool:
        """显示系统状态"""
        print("\n📊 系统状态")
        print("=" * 80)
        
        # 显示最新指标
        metrics = self.monitor.get_latest_metrics()
        if metrics:
            print(f"\n💻 系统资源:")
            print(f"   CPU: {metrics.cpu_percent:.1f}%")
            print(f"   内存: {metrics.memory_percent:.1f}% ({metrics.memory_used_mb:.0f} MB / {metrics.memory_total_mb:.0f} MB)")
            print(f"   磁盘: {metrics.disk_percent:.1f}% ({metrics.disk_used_gb:.1f} GB / {metrics.disk_total_gb:.1f} GB)")
            print(f"   进程数: {metrics.process_count}")
            print(f"   线程数: {metrics.thread_count}")
        else:
            print("\n⚠️  暂无系统指标数据")
        
        # 显示健康检查结果
        print(f"\n🏥 健康检查:")
        results = self.health_checker.check_all()
        overall = self.health_checker.get_overall_status()
        
        status_icon = "✅" if overall == HealthStatus.HEALTHY else "⚠️" if overall == HealthStatus.DEGRADED else "❌"
        print(f"   整体状态: {status_icon} {overall.value}")
        
        for result in results:
            status_icon = "✅" if result.status == HealthStatus.HEALTHY else "⚠️" if result.status == HealthStatus.DEGRADED else "❌"
            print(f"   {result.component}: {status_icon} {result.message}")
        
        print("=" * 80)
        return True
    
    def _show_metrics(self) -> bool:
        """显示指标"""
        print("\n📈 系统指标")
        print("=" * 80)
        
        summary = self.monitor.get_metrics_summary()
        
        if "status" in summary:
            print("\n⚠️  暂无指标数据")
            print("使用 'monitor start' 开始收集指标")
            return True
        
        print("\n💻 最新指标:")
        latest = summary["latest"]
        print(f"   CPU: {latest['cpu_percent']:.1f}%")
        print(f"   内存: {latest['memory_percent']:.1f}%")
        print(f"   磁盘: {latest['disk_percent']:.1f}%")
        
        print("\n📊 平均指标:")
        avg = summary["average"]
        print(f"   CPU: {avg['cpu_percent']:.1f}%")
        print(f"   内存: {avg['memory_percent']:.1f}%")
        
        print("\n📈 历史峰值:")
        max_vals = summary["max"]
        print(f"   CPU: {max_vals['cpu_percent']:.1f}%")
        print(f"   内存: {max_vals['memory_percent']:.1f}%")
        
        print(f"\n📦 历史记录: {summary['history_size']} 条")
        print("=" * 80)
        return True
    
    def _run_health_check(self) -> bool:
        """运行健康检查"""
        print("\n🏥 运行健康检查...")
        print("=" * 80)
        
        report = self.health_checker.generate_report()
        
        print(f"\n整体状态: {report['overall_status']}")
        print(f"检查时间: {report['timestamp']}")
        
        for check in report['checks']:
            status_icon = "✅" if check['status'] == 'healthy' else "⚠️" if check['status'] == 'degraded' else "❌"
            print(f"\n{status_icon} {check['component']}: {check['message']}")
            print(f"   响应时间: {check['response_time_ms']:.2f} ms")
        
        print("=" * 80)
        return True
    
    def _start_monitoring(self) -> bool:
        """开始监控"""
        self.monitor.start_monitoring()
        return True
    
    def _stop_monitoring(self) -> bool:
        """停止监控"""
        self.monitor.stop_monitoring()
        return True
    
    def _generate_report(self) -> bool:
        """生成完整报告"""
        print("\n📋 生成完整监控报告...")
        print("=" * 80)
        
        # 健康检查
        health_report = self.health_checker.generate_report()
        
        # 指标摘要
        metrics_summary = self.monitor.get_metrics_summary()
        
        print("\n🏥 健康检查报告:")
        print(json.dumps(health_report, indent=2, ensure_ascii=False))
        
        print("\n📈 指标摘要:")
        print(json.dumps(metrics_summary, indent=2, ensure_ascii=False))
        
        print("=" * 80)
        return True


def create_monitor() -> SystemMonitor:
    """创建系统监控器工厂函数"""
    return SystemMonitor()


def create_health_checker() -> HealthChecker:
    """创建健康检查器工厂函数"""
    return HealthChecker()


def quick_health_check() -> HealthStatus:
    """快速健康检查"""
    checker = HealthChecker()
    results = checker.check_all()
    return checker.get_overall_status()
