#!/usr/bin/env python3
"""
日志系统和记录器 - 第62阶段
提供完整的系统日志记录和管理功能
"""

import os
import sys
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class LogLevel(Enum):
    """日志级别枚举"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


@dataclass
class LogConfig:
    """日志配置数据类"""
    level: LogLevel = LogLevel.INFO
    log_to_file: bool = True
    log_file_path: str = "logs/system.log"
    max_file_size: int = 10 * 1024 * 1024  # 10 MB
    backup_count: int = 5
    log_to_console: bool = True
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"


@dataclass
class LogEntry:
    """日志条目数据类"""
    timestamp: str
    level: str
    logger_name: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


class SystemLogger:
    """系统日志记录器"""
    
    _instances = {}  # 单例模式
    
    def __new__(cls, name: str = "system", config: Optional[LogConfig] = None):
        if name not in cls._instances:
            instance = super().__new__(cls)
            instance._initialized = False
            cls._instances[name] = instance
        return cls._instances[name]
    
    def __init__(self, name: str = "system", config: Optional[LogConfig] = None):
        if self._initialized:
            return
            
        self.name = name
        self.config = config or LogConfig()
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.config.level.value)
        self.log_entries: List[LogEntry] = []
        self._setup_handlers()
        self._initialized = True
    
    def _setup_handlers(self):
        """设置日志处理器"""
        # 移除现有的处理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 创建格式化器
        formatter = logging.Formatter(
            self.config.log_format,
            datefmt=self.config.date_format
        )
        
        # 控制台处理器
        if self.config.log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.config.level.value)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        # 文件处理器
        if self.config.log_to_file:
            self._ensure_log_directory()
            try:
                from logging.handlers import RotatingFileHandler
                file_handler = RotatingFileHandler(
                    self.config.log_file_path,
                    maxBytes=self.config.max_file_size,
                    backupCount=self.config.backup_count,
                    encoding='utf-8'
                )
                file_handler.setLevel(self.config.level.value)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            except Exception as e:
                print(f"⚠️ 无法设置文件日志处理器: {e}")
    
    def _ensure_log_directory(self):
        """确保日志目录存在"""
        log_dir = Path(self.config.log_file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)
    
    def debug(self, message: str, **details):
        """记录DEBUG级别日志"""
        self.logger.debug(message)
        self._add_log_entry("DEBUG", message, details)
    
    def info(self, message: str, **details):
        """记录INFO级别日志"""
        self.logger.info(message)
        self._add_log_entry("INFO", message, details)
    
    def warning(self, message: str, **details):
        """记录WARNING级别日志"""
        self.logger.warning(message)
        self._add_log_entry("WARNING", message, details)
    
    def error(self, message: str, **details):
        """记录ERROR级别日志"""
        self.logger.error(message)
        self._add_log_entry("ERROR", message, details)
    
    def critical(self, message: str, **details):
        """记录CRITICAL级别日志"""
        self.logger.critical(message)
        self._add_log_entry("CRITICAL", message, details)
    
    def _add_log_entry(self, level: str, message: str, details: Dict[str, Any]):
        """添加日志条目"""
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=level,
            logger_name=self.name,
            message=message,
            details=details
        )
        self.log_entries.append(entry)
        
        # 限制内存中的日志条目数量
        if len(self.log_entries) > 1000:
            self.log_entries = self.log_entries[-1000:]
    
    def set_level(self, level: LogLevel):
        """设置日志级别"""
        self.config.level = level
        self.logger.setLevel(level.value)
        for handler in self.logger.handlers:
            handler.setLevel(level.value)
        self.info(f"日志级别已设置为: {level.value}")
    
    def get_recent_logs(self, limit: int = 50, level: Optional[str] = None) -> List[LogEntry]:
        """获取最近的日志"""
        logs = reversed(self.log_entries)
        if level:
            logs = (log for log in logs if log.level == level.upper())
        return list(logs)[:limit]
    
    def export_logs(self, file_path: str, format: str = "json"):
        """导出日志"""
        if format == "json":
            log_data = [
                {
                    "timestamp": log.timestamp,
                    "level": log.level,
                    "logger": log.logger_name,
                    "message": log.message,
                    "details": log.details
                }
                for log in self.log_entries
            ]
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                for log in self.log_entries:
                    f.write(f"{log.timestamp} - {log.level} - {log.message}\n")
        
        self.info(f"日志已导出到: {file_path}")
    
    def clear_logs(self):
        """清除内存中的日志"""
        self.log_entries.clear()
        self.info("内存中的日志已清除")


class LoggerManager:
    """日志管理器"""
    
    def __init__(self):
        self.loggers: Dict[str, SystemLogger] = {}
    
    def get_logger(self, name: str, config: Optional[LogConfig] = None) -> SystemLogger:
        """获取或创建日志记录器"""
        if name not in self.loggers:
            self.loggers[name] = SystemLogger(name, config)
        return self.loggers[name]
    
    def get_all_loggers(self) -> Dict[str, SystemLogger]:
        """获取所有日志记录器"""
        return self.loggers
    
    def set_global_level(self, level: LogLevel):
        """设置全局日志级别"""
        for logger in self.loggers.values():
            logger.set_level(level)
    
    def get_all_logs(self) -> Dict[str, List[LogEntry]]:
        """获取所有日志"""
        return {
            name: logger.log_entries
            for name, logger in self.loggers.items()
        }


class LoggerCLI:
    """日志命令行接口"""
    
    def __init__(self):
        self.logger_manager = LoggerManager()
        self.system_logger = self.logger_manager.get_logger("system")
    
    def run(self, args: List[str]) -> bool:
        """运行日志命令"""
        if not args:
            return self._show_status()
        
        command = args[0].lower()
        
        if command == "status":
            return self._show_status()
        elif command == "logs":
            return self._show_logs(args[1:] if len(args) > 1 else [])
        elif command == "level":
            return self._set_level(args[1:] if len(args) > 1 else [])
        elif command == "export":
            return self._export_logs(args[1:] if len(args) > 1 else [])
        elif command == "clear":
            return self._clear_logs()
        elif command == "test":
            return self._test_logger()
        else:
            print(f"❌ 未知命令: {command}")
            return False
    
    def _show_status(self) -> bool:
        """显示日志系统状态"""
        print("\n📝 日志系统状态")
        print("=" * 80)
        
        print(f"\n系统日志器:")
        log_config = self.system_logger.config
        print(f"   当前级别: {log_config.level.value}")
        print(f"   日志文件: {log_config.log_file_path}")
        print(f"   文件大小: {log_config.max_file_size / 1024 / 1024:.1f} MB")
        print(f"   备份数量: {log_config.backup_count}")
        print(f"   日志条目: {len(self.system_logger.log_entries)}")
        
        print(f"\n所有日志器:")
        for name in self.logger_manager.loggers.keys():
            print(f"   - {name}")
        
        return True
    
    def _show_logs(self, args: List[str]) -> bool:
        """显示日志"""
        limit = 20
        level = None
        
        for i, arg in enumerate(args):
            if arg == "--limit" and i + 1 < len(args):
                try:
                    limit = int(args[i + 1])
                except ValueError:
                    pass
            elif arg == "--level" and i + 1 < len(args):
                level = args[i + 1].upper()
        
        logs = self.system_logger.get_recent_logs(limit, level)
        
        print(f"\n📋 最近日志 (限制: {limit})")
        print("=" * 80)
        
        if not logs:
            print("   暂无日志")
            return True
        
        for log in logs:
            status_icon = "📌" if log.level == "INFO" else "⚠️" if log.level == "WARNING" else "❌" if log.level in ["ERROR", "CRITICAL"] else "🔍"
            print(f"\n{status_icon} {log.timestamp} - {log.level}")
            print(f"   {log.message}")
            if log.details:
                print(f"   详情: {log.details}")
        
        return True
    
    def _set_level(self, args: List[str]) -> bool:
        """设置日志级别"""
        if not args:
            print(f"\n❌ 请指定日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL")
            return False
        
        level_str = args[0].upper()
        try:
            level = LogLevel[level_str]
            self.logger_manager.set_global_level(level)
            print(f"\n✅ 日志级别已设置为: {level.value}")
            return True
        except KeyError:
            print(f"\n❌ 无效的日志级别: {level_str}")
            return False
    
    def _export_logs(self, args: List[str]) -> bool:
        """导出日志"""
        file_path = args[0] if args else f"logs/export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        format = "json"
        
        for i, arg in enumerate(args):
            if arg == "--format" and i + 1 < len(args):
                format = args[i + 1]
        
        self.system_logger.export_logs(file_path, format)
        print(f"\n✅ 日志已导出到: {file_path}")
        return True
    
    def _clear_logs(self) -> bool:
        """清除内存中的日志"""
        self.system_logger.clear_logs()
        print(f"\n✅ 内存中的日志已清除")
        return True
    
    def _test_logger(self) -> bool:
        """测试日志记录器"""
        print("\n🧪 测试日志记录器")
        print("=" * 80)
        
        test_logger = self.logger_manager.get_logger("test")
        
        test_logger.debug("这是DEBUG级别的测试日志", test=True, module="LoggerCLI")
        test_logger.info("这是INFO级别的测试日志", user="system", action="test")
        test_logger.warning("这是WARNING级别的测试日志", warning="low")
        test_logger.error("这是ERROR级别的测试日志", error="test_error")
        test_logger.critical("这是CRITICAL级别的测试日志", critical=True)
        
        print(f"\n✅ 日志测试完成！共记录 {len(test_logger.log_entries)} 条日志")
        
        # 显示最近3条日志
        recent_logs = test_logger.get_recent_logs(3)
        for log in recent_logs:
            print(f"   {log.level}: {log.message}")
        
        return True


def create_logger(name: str = "system", config: Optional[LogConfig] = None) -> SystemLogger:
    """创建日志记录器工厂函数"""
    return SystemLogger(name, config)


def get_logger_manager() -> LoggerManager:
    """获取日志管理器"""
    return LoggerManager()


def quick_log(level: str, message: str, **details):
    """快速记录日志"""
    logger = SystemLogger("quick")
    
    log_funcs = {
        "debug": logger.debug,
        "info": logger.info,
        "warning": logger.warning,
        "error": logger.error,
        "critical": logger.critical
    }
    
    func = log_funcs.get(level.lower(), logger.info)
    func(message, **details)
