#!/usr/bin/env python3
"""
系统配置管理与初始化 - 第60阶段
提供系统级配置管理和初始化引导
"""

import os
import json
import uuid
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from enum import Enum


class Environment(Enum):
    """运行环境枚举"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(Enum):
    """日志级别枚举"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class SystemConfig:
    """系统配置数据类"""
    version: str = "1.0.0"
    environment: Environment = Environment.DEVELOPMENT
    log_level: LogLevel = LogLevel.INFO
    log_file: Optional[str] = None
    max_workers: int = 4
    timeout_seconds: int = 3600
    retry_attempts: int = 3
    enable_analytics: bool = True
    enable_metrics: bool = True
    enable_caching: bool = True
    cache_ttl: int = 300
    enable_persistence: bool = False
    persistence_path: Optional[str] = None
    custom_settings: Dict[str, Any] = field(default_factory=dict)


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化配置管理器"""
        self.config_path = config_path or self._get_default_config_path()
        self.config = SystemConfig()
        self._loaded = False
    
    def _get_default_config_path(self) -> str:
        """获取默认配置路径"""
        home_dir = os.path.expanduser("~")
        config_dir = os.path.join(home_dir, ".first_principle_agent")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "config.json")
    
    def load(self) -> SystemConfig:
        """加载配置"""
        if self._loaded:
            return self.config
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._apply_config_data(data)
                    print(f"✅ 配置已从 {self.config_path} 加载")
            except Exception as e:
                print(f"⚠️  加载配置失败，使用默认配置: {e}")
                self._use_default_config()
        else:
            print(f"ℹ️  配置文件不存在，使用默认配置")
            self._use_default_config()
        
        self._loaded = True
        return self.config
    
    def _apply_config_data(self, data: Dict[str, Any]):
        """应用配置数据"""
        if 'environment' in data:
            data['environment'] = Environment(data['environment'])
        if 'log_level' in data:
            data['log_level'] = LogLevel(data['log_level'])
        
        for key, value in data.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
    
    def _use_default_config(self):
        """使用默认配置"""
        self.config = SystemConfig()
    
    def save(self) -> bool:
        """保存配置"""
        try:
            config_dict = asdict(self.config)
            config_dict['environment'] = self.config.environment.value
            config_dict['log_level'] = self.config.log_level.value
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 配置已保存到 {self.config_path}")
            return True
        except Exception as e:
            print(f"❌ 保存配置失败: {e}")
            return False
    
    def update(self, **kwargs) -> SystemConfig:
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                print(f"✅ 配置更新: {key} = {value}")
            else:
                print(f"⚠️  未知配置项: {key}")
        
        return self.config
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return getattr(self.config, key, default)
    
    def reset(self):
        """重置为默认配置"""
        self._use_default_config()
        print("✅ 配置已重置为默认配置")


class SystemBootstrap:
    """系统引导类"""
    
    def __init__(self, config: Optional[SystemConfig] = None):
        """初始化系统引导"""
        self.config = config or SystemConfig()
        self.boot_id = str(uuid.uuid4())
        self.boot_time = time.time()
        self.components_initialized: List[str] = []
        self.errors: List[str] = []
    
    def bootstrap(self) -> bool:
        """执行系统引导"""
        print("\n" + "=" * 80)
        print("🚀 系统初始化引导")
        print("=" * 80)
        
        try:
            print(f"\n📋 引导ID: {self.boot_id}")
            print(f"📋 配置环境: {self.config.environment.value}")
            print(f"📋 日志级别: {self.config.log_level.value}")
            
            print("\n📦 初始化组件:")
            
            # 初始化核心组件
            self._init_core_components()
            
            # 初始化执行引擎
            self._init_execution_engine()
            
            # 初始化编排器
            self._init_orchestrator()
            
            # 初始化分析器
            self._init_analytics()
            
            # 完成引导
            boot_duration = time.time() - self.boot_time
            print(f"\n✅ 系统引导完成！")
            print(f"   初始化组件: {len(self.components_initialized)} 个")
            print(f"   初始化耗时: {boot_duration:.3f} 秒")
            
            if self.errors:
                print(f"\n⚠️  引导过程中的问题:")
                for error in self.errors:
                    print(f"   - {error}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ 系统引导失败: {e}")
            self.errors.append(str(e))
            return False
    
    def _init_core_components(self):
        """初始化核心组件"""
        try:
            from first_principle_agent.core.task_tuple import TaskTuple
            from first_principle_agent.core.dag_structures import TaskDAG
            self.components_initialized.append("CoreComponents")
            print("   ✅ 核心组件 - TaskTuple, TaskDAG")
        except Exception as e:
            self.errors.append(f"核心组件初始化失败: {e}")
            print(f"   ❌ 核心组件初始化失败: {e}")
    
    def _init_execution_engine(self):
        """初始化执行引擎"""
        try:
            from first_principle_agent.core.task_execution_engine import TaskExecutionEngine
            engine = TaskExecutionEngine()
            self.components_initialized.append("TaskExecutionEngine")
            print("   ✅ 任务执行引擎 - TaskExecutionEngine")
        except Exception as e:
            self.errors.append(f"执行引擎初始化失败: {e}")
            print(f"   ❌ 执行引擎初始化失败: {e}")
    
    def _init_orchestrator(self):
        """初始化编排器"""
        try:
            from first_principle_agent.core.task_orchestrator import TaskOrchestrator
            orchestrator = TaskOrchestrator()
            self.components_initialized.append("TaskOrchestrator")
            print("   ✅ 任务编排器 - TaskOrchestrator")
        except Exception as e:
            self.errors.append(f"编排器初始化失败: {e}")
            print(f"   ❌ 编排器初始化失败: {e}")
    
    def _init_analytics(self):
        """初始化分析器"""
        try:
            from first_principle_agent.core.task_analytics import TaskAnalytics
            analytics = TaskAnalytics()
            self.components_initialized.append("TaskAnalytics")
            print("   ✅ 任务分析器 - TaskAnalytics")
        except Exception as e:
            self.errors.append(f"分析器初始化失败: {e}")
            print(f"   ❌ 分析器初始化失败: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取引导状态"""
        return {
            "boot_id": self.boot_id,
            "boot_time": self.boot_time,
            "components_initialized": len(self.components_initialized),
            "errors": len(self.errors),
            "config": asdict(self.config)
        }


class ConfigCLI:
    """配置命令行接口"""
    
    def __init__(self):
        """初始化配置CLI"""
        self.config_manager = ConfigManager()
    
    def run(self, args: List[str]) -> bool:
        """运行配置命令"""
        if not args:
            return self._show_current_config()
        
        command = args[0].lower()
        
        if command == "show":
            return self._show_current_config()
        elif command == "set":
            return self._set_config(args[1:])
        elif command == "save":
            return self._save_config()
        elif command == "reset":
            return self._reset_config()
        elif command == "bootstrap":
            return self._run_bootstrap()
        else:
            print(f"❌ 未知命令: {command}")
            return False
    
    def _show_current_config(self) -> bool:
        """显示当前配置"""
        config = self.config_manager.load()
        
        print("\n📋 当前系统配置:")
        print("=" * 80)
        for key, value in asdict(config).items():
            if key not in ['custom_settings']:
                print(f"   {key}: {value}")
        print("=" * 80)
        
        return True
    
    def _set_config(self, args: List[str]) -> bool:
        """设置配置"""
        if len(args) < 2:
            print("❌ 用法: config set <key> <value>")
            return False
        
        key = args[0]
        value = args[1]
        
        # 类型转换
        if key == 'max_workers' or key == 'timeout_seconds' or key == 'retry_attempts' or key == 'cache_ttl':
            value = int(value)
        elif key == 'enable_analytics' or key == 'enable_metrics' or key == 'enable_caching' or key == 'enable_persistence':
            value = value.lower() in ['true', '1', 'yes', 'on']
        elif key == 'environment':
            value = Environment(value)
        elif key == 'log_level':
            value = LogLevel(value)
        
        self.config_manager.update(**{key: value})
        return True
    
    def _save_config(self) -> bool:
        """保存配置"""
        return self.config_manager.save()
    
    def _reset_config(self) -> bool:
        """重置配置"""
        self.config_manager.reset()
        return True
    
    def _run_bootstrap(self) -> bool:
        """运行系统引导"""
        config = self.config_manager.load()
        bootstrap = SystemBootstrap(config)
        return bootstrap.bootstrap()


def create_config_manager() -> ConfigManager:
    """创建配置管理器工厂函数"""
    return ConfigManager()


def create_bootstrap(config: Optional[SystemConfig] = None) -> SystemBootstrap:
    """创建系统引导工厂函数"""
    return SystemBootstrap(config)


def initialize_system() -> bool:
    """初始化系统"""
    config_manager = create_config_manager()
    config = config_manager.load()
    bootstrap = create_bootstrap(config)
    return bootstrap.bootstrap()
