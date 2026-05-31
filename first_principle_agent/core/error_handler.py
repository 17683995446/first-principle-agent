#!/usr/bin/env python3
"""
错误处理与异常管理系统 - 第63阶段
提供完整的异常捕获、处理和恢复机制
"""

import sys
import os
import traceback
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum


class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """错误类别"""
    VALIDATION = "validation"
    EXECUTION = "execution"
    TIMEOUT = "timeout"
    RESOURCE = "resource"
    SYSTEM = "system"
    UNKNOWN = "unknown"


class RecoveryAction(Enum):
    """恢复操作"""
    RETRY = "retry"
    ROLLBACK = "rollback"
    FALLBACK = "fallback"
    SKIP = "skip"
    ABORT = "abort"
    NOTIFY = "notify"


@dataclass
class ErrorInfo:
    """错误信息数据类"""
    error_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    error_type: str = ""
    message: str = ""
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    category: ErrorCategory = ErrorCategory.UNKNOWN
    details: Dict[str, Any] = field(default_factory=dict)
    traceback_str: str = ""
    source: str = ""
    recoverable: bool = True
    recovery_attempts: int = 0
    max_recovery_attempts: int = 3


@dataclass
class RecoveryStrategy:
    """恢复策略"""
    action: RecoveryAction = RecoveryAction.NOTIFY
    max_attempts: int = 3
    backoff_multiplier: float = 2.0
    initial_delay: float = 1.0
    fallback_value: Any = None


class BaseSystemException(Exception):
    """系统基础异常类"""
    
    def __init__(
        self,
        message: str,
        error_type: str = "SystemError",
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.severity = severity
        self.category = category
        self.details = details or {}
        self.error_id = str(uuid.uuid4())
        self.timestamp = datetime.now().isoformat()
    
    def to_error_info(self) -> ErrorInfo:
        """转换为错误信息"""
        return ErrorInfo(
            error_id=self.error_id,
            timestamp=self.timestamp,
            error_type=self.error_type,
            message=self.message,
            severity=self.severity,
            category=self.category,
            details=self.details,
            traceback_str=traceback.format_exc(),
            recoverable=True
        )
    
    def __str__(self):
        return f"[{self.error_type}] {self.message}"


class ValidationError(BaseSystemException):
    """验证错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_type="ValidationError",
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.VALIDATION,
            details=details
        )


class ExecutionError(BaseSystemException):
    """执行错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_type="ExecutionError",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.EXECUTION,
            details=details
        )


class TimeoutError(BaseSystemException):
    """超时错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_type="TimeoutError",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.TIMEOUT,
            details=details
        )


class ResourceError(BaseSystemException):
    """资源错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_type="ResourceError",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.RESOURCE,
            details=details
        )


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self):
        self.error_history: List[ErrorInfo] = []
        self.max_history_size = 100
        self.handlers: Dict[str, Callable] = {}
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """设置默认处理器"""
        self.handlers["validation"] = self._handle_validation_error
        self.handlers["execution"] = self._handle_execution_error
        self.handlers["timeout"] = self._handle_timeout_error
        self.handlers["resource"] = self._handle_resource_error
        self.handlers["system"] = self._handle_system_error
    
    def handle_exception(self, exception: Exception, context: Optional[str] = None) -> ErrorInfo:
        """处理异常"""
        error_info = self._create_error_info(exception, context)
        self._add_to_history(error_info)
        
        handler = self.handlers.get(error_info.category.value)
        if handler:
            handler(error_info)
        
        return error_info
    
    def _create_error_info(self, exception: Exception, context: Optional[str]) -> ErrorInfo:
        """创建错误信息"""
        if isinstance(exception, BaseSystemException):
            return exception.to_error_info()
        
        error_type = type(exception).__name__
        severity = ErrorSeverity.MEDIUM
        category = ErrorCategory.UNKNOWN
        
        if isinstance(exception, ValueError):
            category = ErrorCategory.VALIDATION
            severity = ErrorSeverity.LOW
        elif isinstance(exception, TimeoutError):
            category = ErrorCategory.TIMEOUT
            severity = ErrorSeverity.MEDIUM
        elif isinstance(exception, MemoryError):
            category = ErrorCategory.RESOURCE
            severity = ErrorSeverity.CRITICAL
        elif isinstance(exception, OSError):
            category = ErrorCategory.RESOURCE
            severity = ErrorSeverity.HIGH
        
        return ErrorInfo(
            error_type=error_type,
            message=str(exception),
            severity=severity,
            category=category,
            traceback_str=traceback.format_exc(),
            source=context or "unknown",
            recoverable=True
        )
    
    def _add_to_history(self, error_info: ErrorInfo):
        """添加到历史记录"""
        self.error_history.append(error_info)
        if len(self.error_history) > self.max_history_size:
            self.error_history.pop(0)
    
    def _handle_validation_error(self, error_info: ErrorInfo):
        """处理验证错误"""
        print(f"⚠️  验证错误: {error_info.message}")
        if error_info.details:
            print(f"   详情: {error_info.details}")
    
    def _handle_execution_error(self, error_info: ErrorInfo):
        """处理执行错误"""
        print(f"❌ 执行错误: {error_info.message}")
        print(f"   类型: {error_info.error_type}")
        if error_info.details:
            print(f"   详情: {error_info.details}")
    
    def _handle_timeout_error(self, error_info: ErrorInfo):
        """处理超时错误"""
        print(f"⏱️  超时错误: {error_info.message}")
    
    def _handle_resource_error(self, error_info: ErrorInfo):
        """处理资源错误"""
        print(f"💾 资源错误: {error_info.message}")
    
    def _handle_system_error(self, error_info: ErrorInfo):
        """处理系统错误"""
        print(f"🔴 系统错误: {error_info.message}")
    
    def get_error_history(
        self,
        limit: int = 50,
        severity: Optional[ErrorSeverity] = None,
        category: Optional[ErrorCategory] = None
    ) -> List[ErrorInfo]:
        """获取错误历史"""
        errors = self.error_history
        
        if severity:
            errors = [e for e in errors if e.severity == severity]
        if category:
            errors = [e for e in errors if e.category == category]
        
        return errors[-limit:]
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """获取错误统计"""
        if not self.error_history:
            return {"total": 0, "by_severity": {}, "by_category": {}}
        
        by_severity = {}
        by_category = {}
        
        for error in self.error_history:
            sev = error.severity.value
            cat = error.category.value
            by_severity[sev] = by_severity.get(sev, 0) + 1
            by_category[cat] = by_category.get(cat, 0) + 1
        
        return {
            "total": len(self.error_history),
            "by_severity": by_severity,
            "by_category": by_category,
            "recent_count": len(self.error_history[-10:])
        }
    
    def clear_history(self):
        """清除错误历史"""
        self.error_history.clear()
        print("✅ 错误历史已清除")


class ErrorRecoveryManager:
    """错误恢复管理器"""
    
    def __init__(self):
        self.recovery_strategies: Dict[str, RecoveryStrategy] = {}
        self.failed_recoveries: List[ErrorInfo] = []
        self.successful_recoveries: List[ErrorInfo] = []
        self._setup_default_strategies()
    
    def _setup_default_strategies(self):
        """设置默认恢复策略"""
        self.recovery_strategies["default"] = RecoveryStrategy(
            action=RecoveryAction.RETRY,
            max_attempts=3,
            backoff_multiplier=2.0,
            initial_delay=1.0,
            fallback_value=None
        )
        
        self.recovery_strategies["critical"] = RecoveryStrategy(
            action=RecoveryAction.NOTIFY,
            max_attempts=1,
            fallback_value=None
        )
        
        self.recovery_strategies["timeout"] = RecoveryStrategy(
            action=RecoveryAction.RETRY,
            max_attempts=5,
            backoff_multiplier=1.5,
            initial_delay=0.5,
            fallback_value=None
        )
        
        self.recovery_strategies["safe"] = RecoveryStrategy(
            action=RecoveryAction.RETRY,
            max_attempts=3,
            backoff_multiplier=2.0,
            initial_delay=1.0,
            fallback_value="fallback_value"
        )
    
    def execute_with_recovery(
        self,
        func: Callable,
        *args,
        strategy_name: str = "default",
        **kwargs
    ) -> Any:
        """带恢复的函数执行"""
        strategy = self.recovery_strategies.get(strategy_name, self.recovery_strategies["default"])
        last_error = None
        
        for attempt in range(strategy.max_attempts):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                last_error = e
                if attempt < strategy.max_attempts - 1:
                    delay = strategy.initial_delay * (strategy.backoff_multiplier ** attempt)
                    print(f"⚠️  执行失败 (尝试 {attempt + 1}/{strategy.max_attempts}), {delay:.1f}秒后重试...")
                    import time
                    time.sleep(delay)
        
        # 所有尝试都失败
        print(f"❌ 所有恢复尝试失败: {last_error}")
        
        if strategy.fallback_value is not None:
            print(f"🔄 使用备用值")
            return strategy.fallback_value
        
        raise last_error
    
    def record_recovery_success(self, error_info: ErrorInfo):
        """记录恢复成功"""
        self.successful_recoveries.append(error_info)
        print(f"✅ 错误已恢复: {error_info.error_type} - {error_info.message}")
    
    def record_recovery_failure(self, error_info: ErrorInfo):
        """记录恢复失败"""
        self.failed_recoveries.append(error_info)
        print(f"❌ 错误恢复失败: {error_info.error_type} - {error_info.message}")
    
    def get_recovery_statistics(self) -> Dict[str, Any]:
        """获取恢复统计"""
        total_attempts = len(self.successful_recoveries) + len(self.failed_recoveries)
        success_rate = len(self.successful_recoveries) / total_attempts if total_attempts > 0 else 0
        
        return {
            "total_attempts": total_attempts,
            "successful": len(self.successful_recoveries),
            "failed": len(self.failed_recoveries),
            "success_rate": success_rate * 100
        }


class ErrorCLI:
    """错误处理命令行接口"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.recovery_manager = ErrorRecoveryManager()
    
    def run(self, args: List[str]) -> bool:
        """运行错误处理命令"""
        if not args:
            return self._show_status()
        
        command = args[0].lower()
        
        if command == "status":
            return self._show_status()
        elif command == "history":
            return self._show_history(args[1:] if len(args) > 1 else [])
        elif command == "stats":
            return self._show_statistics()
        elif command == "clear":
            return self._clear_history()
        elif command == "test":
            return self._test_error_handling()
        elif command == "recovery":
            return self._show_recovery_stats()
        else:
            print(f"❌ 未知命令: {command}")
            return False
    
    def _show_status(self) -> bool:
        """显示错误处理系统状态"""
        print("\n🔧 错误处理系统状态")
        print("=" * 80)
        
        stats = self.error_handler.get_error_statistics()
        recovery_stats = self.recovery_manager.get_recovery_statistics()
        
        print(f"\n📊 错误统计:")
        print(f"   总错误数: {stats['total']}")
        
        if stats['by_severity']:
            print(f"   按严重程度:")
            for severity, count in stats['by_severity'].items():
                icon = "🔴" if severity == "critical" else "🟠" if severity == "high" else "🟡" if severity == "medium" else "🟢"
                print(f"     {icon} {severity}: {count}")
        
        if stats['by_category']:
            print(f"   按类别:")
            for category, count in stats['by_category'].items():
                print(f"     - {category}: {count}")
        
        print(f"\n🔄 恢复统计:")
        print(f"   总尝试次数: {recovery_stats['total_attempts']}")
        print(f"   成功: {recovery_stats['successful']}")
        print(f"   失败: {recovery_stats['failed']}")
        print(f"   成功率: {recovery_stats['success_rate']:.1f}%")
        
        return True
    
    def _show_history(self, args: List[str]) -> bool:
        """显示错误历史"""
        limit = 20
        severity = None
        category = None
        
        for i, arg in enumerate(args):
            if arg == "--limit" and i + 1 < len(args):
                try:
                    limit = int(args[i + 1])
                except ValueError:
                    pass
            elif arg == "--severity" and i + 1 < len(args):
                try:
                    severity = ErrorSeverity(args[i + 1].lower())
                except ValueError:
                    pass
            elif arg == "--category" and i + 1 < len(args):
                try:
                    category = ErrorCategory(args[i + 1].lower())
                except ValueError:
                    pass
        
        errors = self.error_handler.get_error_history(limit, severity, category)
        
        print(f"\n📋 错误历史 (限制: {limit})")
        print("=" * 80)
        
        if not errors:
            print("   暂无错误记录")
            return True
        
        for error in reversed(errors):
            icon = "🔴" if error.severity == ErrorSeverity.CRITICAL else "❌" if error.severity == ErrorSeverity.HIGH else "⚠️" if error.severity == ErrorSeverity.MEDIUM else "ℹ️"
            print(f"\n{icon} [{error.severity.value.upper()}] {error.category.value.upper()}")
            print(f"   ID: {error.error_id}")
            print(f"   时间: {error.timestamp}")
            print(f"   类型: {error.error_type}")
            print(f"   消息: {error.message}")
            if error.details:
                print(f"   详情: {error.details}")
        
        return True
    
    def _show_statistics(self) -> bool:
        """显示详细统计"""
        return self._show_status()
    
    def _clear_history(self) -> bool:
        """清除错误历史"""
        self.error_handler.clear_history()
        print("✅ 错误历史已清除")
        return True
    
    def _test_error_handling(self) -> bool:
        """测试错误处理"""
        print("\n🧪 测试错误处理")
        print("=" * 80)
        
        test_errors = [
            ("验证错误", ValidationError("测试验证错误", {"field": "username", "reason": "格式不正确"})),
            ("执行错误", ExecutionError("测试执行错误", {"task": "task_123", "step": 2})),
            ("超时错误", TimeoutError("测试超时错误", {"timeout": 30, "actual": 35})),
            ("资源错误", ResourceError("测试资源错误", {"resource": "memory", "available": "0MB"})),
            ("系统错误", Exception("测试系统错误"))
        ]
        
        for name, error in test_errors:
            print(f"\n📌 测试 {name}:")
            error_info = self.error_handler.handle_exception(error, context="test")
            print(f"   错误ID: {error_info.error_id}")
            print(f"   状态: 已处理")
        
        print(f"\n✅ 错误处理测试完成！")
        print(f"   共处理 {len(test_errors)} 个测试错误")
        print(f"   当前错误历史: {len(self.error_handler.error_history)} 条")
        
        return True
    
    def _show_recovery_stats(self) -> bool:
        """显示恢复统计"""
        stats = self.recovery_manager.get_recovery_statistics()
        
        print(f"\n🔄 恢复统计")
        print("=" * 80)
        print(f"   总尝试次数: {stats['total_attempts']}")
        print(f"   成功: {stats['successful']}")
        print(f"   失败: {stats['failed']}")
        print(f"   成功率: {stats['success_rate']:.1f}%")
        
        return True


def create_error_handler() -> ErrorHandler:
    """创建错误处理器工厂函数"""
    return ErrorHandler()


def create_recovery_manager() -> ErrorRecoveryManager:
    """创建恢复管理器工厂函数"""
    return ErrorRecoveryManager()


def handle_error(error: Exception, context: Optional[str] = None) -> ErrorInfo:
    """快速错误处理函数"""
    handler = ErrorHandler()
    return handler.handle_exception(error, context)
