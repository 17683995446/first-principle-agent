#!/usr/bin/env python3
"""
系统插件和扩展机制 - 第71阶段
提供完整的插件管理系统，支持插件发现、加载、卸载和扩展点
"""

import importlib
import inspect
import json
import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Type, Callable, Any, Set


class PluginType(Enum):
    """插件类型"""
    TASK_EXECUTOR = auto()  # 任务执行器插件
    WORKFLOW_STEP = auto()  # 工作流步骤插件
    ANALYTICS = auto()       # 分析插件
    REPORTING = auto()       # 报告插件
    STORAGE = auto()         # 存储插件
    NOTIFICATION = auto()    # 通知插件
    CUSTOM = auto()          # 自定义插件


class PluginStatus(Enum):
    """插件状态"""
    DISCOVERED = auto()     # 已发现
    LOADED = auto()         # 已加载
    ACTIVE = auto()         # 活动中
    ERROR = auto()          # 错误
    UNLOADED = auto()       # 已卸载


class ExtensionPoint(Enum):
    """扩展点枚举"""
    TASK_PRE_PROCESS = "task_pre_process"
    TASK_POST_PROCESS = "task_post_process"
    TASK_ERROR_HANDLER = "task_error_handler"
    WORKFLOW_START = "workflow_start"
    WORKFLOW_COMPLETE = "workflow_complete"
    REPORT_GENERATION = "report_generation"
    METRIC_COLLECTION = "metric_collection"


@dataclass
class PluginMetadata:
    """插件元数据"""
    name: str
    version: str
    author: str
    description: str
    plugin_type: PluginType
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    entry_point: str = ""
    enabled: bool = True
    config_schema: Dict = field(default_factory=dict)


@dataclass
class PluginInstance:
    """插件实例"""
    metadata: PluginMetadata
    instance: Any
    status: PluginStatus
    loaded_at: str = ""
    error_message: str = ""


class BasePlugin(ABC):
    """插件基类"""
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """获取插件元数据"""
        pass
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        pass
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Any:
        """执行插件功能"""
        pass
    
    @abstractmethod
    def shutdown(self) -> bool:
        """关闭插件"""
        pass


class ExtensionRegistry:
    """扩展点注册表"""
    
    def __init__(self):
        self.extensions: Dict[ExtensionPoint, List[Callable]] = {}
        for point in ExtensionPoint:
            self.extensions[point] = []
    
    def register(self, point: ExtensionPoint, callback: Callable) -> bool:
        """注册扩展回调"""
        if point not in self.extensions:
            self.extensions[point] = []
        self.extensions[point].append(callback)
        return True
    
    def unregister(self, point: ExtensionPoint, callback: Callable) -> bool:
        """注销扩展回调"""
        if point in self.extensions and callback in self.extensions[point]:
            self.extensions[point].remove(callback)
            return True
        return False
    
    def invoke(self, point: ExtensionPoint, context: Dict[str, Any]) -> List[Any]:
        """调用扩展点的所有回调"""
        results = []
        if point in self.extensions:
            for callback in self.extensions[point]:
                try:
                    result = callback(context)
                    results.append(result)
                except Exception as e:
                    print(f"⚠️ 扩展点 {point} 回调执行失败: {e}")
        return results
    
    def get_extensions(self, point: ExtensionPoint) -> List[Callable]:
        """获取指定扩展点的所有回调"""
        return self.extensions.get(point, [])


class PluginManager:
    """插件管理器"""
    
    def __init__(self, plugin_dirs: Optional[List[str]] = None):
        self.plugin_dirs = plugin_dirs or ["plugins"]
        self.plugins: Dict[str, PluginInstance] = {}
        self.extension_registry = ExtensionRegistry()
        self._ensure_plugin_dirs()
    
    def _ensure_plugin_dirs(self):
        """确保插件目录存在"""
        for dir_path in self.plugin_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def discover_plugins(self) -> List[str]:
        """发现插件目录中的所有插件"""
        discovered = []
        
        for plugin_dir in self.plugin_dirs:
            dir_path = Path(plugin_dir)
            if not dir_path.exists():
                continue
            
            # 查找子目录作为插件
            for item in dir_path.iterdir():
                if item.is_dir() and (item / "__init__.py").exists():
                    plugin_id = item.name
                    if plugin_id not in self.plugins:
                        try:
                            metadata = self._load_plugin_metadata(item)
                            if metadata:
                                self.plugins[plugin_id] = PluginInstance(
                                    metadata=metadata,
                                    instance=None,
                                    status=PluginStatus.DISCOVERED
                                )
                                discovered.append(plugin_id)
                        except Exception as e:
                            print(f"⚠️ 发现插件 {plugin_id} 失败: {e}")
        
        return discovered
    
    def _load_plugin_metadata(self, plugin_path: Path) -> Optional[PluginMetadata]:
        """加载插件元数据"""
        # 先尝试从 plugin.json 加载
        metadata_file = plugin_path / "plugin.json"
        if metadata_file.exists():
            with open(metadata_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return PluginMetadata(
                    name=data.get("name", plugin_path.name),
                    version=data.get("version", "1.0.0"),
                    author=data.get("author", ""),
                    description=data.get("description", ""),
                    plugin_type=PluginType[data.get("type", "CUSTOM")],
                    dependencies=data.get("dependencies", []),
                    tags=data.get("tags", []),
                    entry_point=data.get("entry_point", "Plugin"),
                    enabled=data.get("enabled", True),
                    config_schema=data.get("config_schema", {})
                )
        
        # 否则创建默认元数据
        return PluginMetadata(
            name=plugin_path.name,
            version="1.0.0",
            author="",
            description=f"{plugin_path.name} 插件",
            plugin_type=PluginType.CUSTOM,
            entry_point="Plugin"
        )
    
    def load_plugin(self, plugin_id: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """加载插件"""
        if plugin_id not in self.plugins:
            print(f"❌ 插件 {plugin_id} 未发现")
            return False
        
        plugin_instance = self.plugins[plugin_id]
        
        if plugin_instance.status == PluginStatus.LOADED:
            print(f"ℹ️  插件 {plugin_id} 已加载")
            return True
        
        metadata = plugin_instance.metadata
        
        if not metadata.enabled:
            print(f"ℹ️  插件 {plugin_id} 已禁用")
            return False
        
        try:
            # 添加插件目录到 Python 路径
            plugin_dir = None
            for dir_path in self.plugin_dirs:
                if Path(dir_path, plugin_id).exists():
                    plugin_dir = Path(dir_path).parent
                    break
            
            if plugin_dir and str(plugin_dir) not in sys.path:
                sys.path.insert(0, str(plugin_dir))
            
            # 导入插件模块
            module_name = f"{self.plugin_dirs[0]}.{plugin_id}"
            module = importlib.import_module(module_name)
            
            # 获取插件类
            plugin_class = getattr(module, metadata.entry_point, None)
            if not plugin_class:
                raise ImportError(f"插件 {plugin_id} 缺少入口点 {metadata.entry_point}")
            
            # 创建插件实例
            plugin_obj = plugin_class()
            
            # 初始化插件
            init_config = config or {}
            if not plugin_obj.initialize(init_config):
                raise RuntimeError(f"插件 {plugin_id} 初始化失败")
            
            # 更新插件状态
            plugin_instance.instance = plugin_obj
            plugin_instance.status = PluginStatus.LOADED
            plugin_instance.loaded_at = str(Path.cwd())
            
            print(f"✅ 插件 {plugin_id} 加载成功")
            return True
            
        except Exception as e:
            plugin_instance.status = PluginStatus.ERROR
            plugin_instance.error_message = str(e)
            print(f"❌ 加载插件 {plugin_id} 失败: {e}")
            return False
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """卸载插件"""
        if plugin_id not in self.plugins:
            print(f"❌ 插件 {plugin_id} 不存在")
            return False
        
        plugin_instance = self.plugins[plugin_id]
        
        if plugin_instance.status == PluginStatus.UNLOADED:
            print(f"ℹ️  插件 {plugin_id} 已卸载")
            return True
        
        try:
            # 调用插件关闭方法
            if plugin_instance.instance:
                plugin_instance.instance.shutdown()
            
            # 更新插件状态
            plugin_instance.status = PluginStatus.UNLOADED
            plugin_instance.instance = None
            
            print(f"✅ 插件 {plugin_id} 卸载成功")
            return True
            
        except Exception as e:
            print(f"❌ 卸载插件 {plugin_id} 失败: {e}")
            return False
    
    def activate_plugin(self, plugin_id: str) -> bool:
        """激活插件"""
        if plugin_id not in self.plugins:
            print(f"❌ 插件 {plugin_id} 不存在")
            return False
        
        plugin_instance = self.plugins[plugin_id]
        
        if plugin_instance.status != PluginStatus.LOADED:
            print(f"❌ 插件 {plugin_id} 未加载，无法激活")
            return False
        
        plugin_instance.status = PluginStatus.ACTIVE
        
        # 注册插件的扩展点
        if hasattr(plugin_instance.instance, "register_extensions"):
            try:
                plugin_instance.instance.register_extensions(self.extension_registry)
            except Exception as e:
                print(f"⚠️  插件 {plugin_id} 注册扩展点失败: {e}")
        
        print(f"✅ 插件 {plugin_id} 激活成功")
        return True
    
    def deactivate_plugin(self, plugin_id: str) -> bool:
        """停用插件"""
        if plugin_id not in self.plugins:
            print(f"❌ 插件 {plugin_id} 不存在")
            return False
        
        plugin_instance = self.plugins[plugin_id]
        
        if plugin_instance.status != PluginStatus.ACTIVE:
            print(f"ℹ️  插件 {plugin_id} 未激活")
            return True
        
        # 注销插件的扩展点
        if hasattr(plugin_instance.instance, "unregister_extensions"):
            try:
                plugin_instance.instance.unregister_extensions(self.extension_registry)
            except Exception as e:
                print(f"⚠️  插件 {plugin_id} 注销扩展点失败: {e}")
        
        plugin_instance.status = PluginStatus.LOADED
        
        print(f"✅ 插件 {plugin_id} 停用成功")
        return True
    
    def get_plugin(self, plugin_id: str) -> Optional[PluginInstance]:
        """获取插件"""
        return self.plugins.get(plugin_id)
    
    def list_plugins(self, status: Optional[PluginStatus] = None,
                    plugin_type: Optional[PluginType] = None) -> List[PluginInstance]:
        """列出插件"""
        result = list(self.plugins.values())
        
        if status:
            result = [p for p in result if p.status == status]
        
        if plugin_type:
            result = [p for p in result if p.metadata.plugin_type == plugin_type]
        
        return result
    
    def execute_plugin(self, plugin_id: str, context: Dict[str, Any]) -> Any:
        """执行插件"""
        if plugin_id not in self.plugins:
            print(f"❌ 插件 {plugin_id} 不存在")
            return None
        
        plugin_instance = self.plugins[plugin_id]
        
        if plugin_instance.status not in [PluginStatus.LOADED, PluginStatus.ACTIVE]:
            print(f"❌ 插件 {plugin_id} 未加载")
            return None
        
        try:
            return plugin_instance.instance.execute(context)
        except Exception as e:
            print(f"❌ 插件 {plugin_id} 执行失败: {e}")
            return None


class PluginCLI:
    """插件管理命令行接口"""
    
    def __init__(self):
        self.manager = PluginManager()
    
    def run(self, args: List[str]) -> bool:
        """运行插件命令"""
        if not args:
            return self._show_help()
        
        command = args[0].lower()
        
        if command == "help":
            return self._show_help()
        elif command == "discover":
            return self._discover_plugins(args[1:])
        elif command == "list":
            return self._list_plugins(args[1:])
        elif command == "load":
            return self._load_plugin(args[1:])
        elif command == "unload":
            return self._unload_plugin(args[1:])
        elif command == "activate":
            return self._activate_plugin(args[1:])
        elif command == "deactivate":
            return self._deactivate_plugin(args[1:])
        elif command == "info":
            return self._show_plugin_info(args[1:])
        elif command == "test":
            return self._test_plugin_system()
        else:
            print(f"❌ 未知命令: {command}")
            return False
    
    def _show_help(self) -> bool:
        """显示帮助"""
        help_text = """
🔌 系统插件管理命令:
  help                       - 显示帮助信息
  discover                   - 发现可用插件
  list [status] [type]       - 列出插件，可选按状态或类型过滤
  info <plugin_id>           - 显示插件详情
  load <plugin_id> [config]  - 加载插件
  unload <plugin_id>         - 卸载插件
  activate <plugin_id>       - 激活插件
  deactivate <plugin_id>     - 停用插件
  test                       - 测试插件系统

使用示例:
  # 发现插件
  python -m first_principle_agent plugin discover
  
  # 列出所有插件
  python -m first_principle_agent plugin list
  
  # 加载插件
  python -m first_principle_agent plugin load my_plugin
  
  # 激活插件
  python -m first_principle_agent plugin activate my_plugin
  
  # 测试插件系统
  python -m first_principle_agent plugin test
"""
        print(help_text)
        return True
    
    def _discover_plugins(self, args: List[str]) -> bool:
        """发现插件"""
        print("🔍 正在发现插件...")
        discovered = self.manager.discover_plugins()
        
        if discovered:
            print(f"✅ 发现 {len(discovered)} 个插件:")
            for plugin_id in discovered:
                plugin = self.manager.get_plugin(plugin_id)
                print(f"   - {plugin.metadata.name} ({plugin_id})")
        else:
            print("ℹ️  未发现新插件")
        
        return True
    
    def _list_plugins(self, args: List[str]) -> bool:
        """列出插件"""
        status = None
        plugin_type = None
        
        if len(args) > 0 and args[0]:
            try:
                status = PluginStatus[args[0].upper()]
            except KeyError:
                pass
        
        if len(args) > 1 and args[1]:
            try:
                plugin_type = PluginType[args[1].upper()]
            except KeyError:
                pass
        
        plugins = self.manager.list_plugins(status=status, plugin_type=plugin_type)
        
        print(f"\n🔌 插件列表 ({len(plugins)} 个):")
        print("=" * 80)
        
        for plugin in plugins:
            status_icon = {
                PluginStatus.DISCOVERED: "📦",
                PluginStatus.LOADED: "✅",
                PluginStatus.ACTIVE: "🚀",
                PluginStatus.ERROR: "❌",
                PluginStatus.UNLOADED: "📦"
            }.get(plugin.status, "📦")
            
            print(f"\n{status_icon} {plugin.metadata.name}")
            print(f"   ID: {plugin.metadata.plugin_type}")
            print(f"   版本: {plugin.metadata.version}")
            print(f"   状态: {plugin.status.name}")
            print(f"   描述: {plugin.metadata.description}")
        
        print("\n" + "=" * 80)
        return True
    
    def _show_plugin_info(self, args: List[str]) -> bool:
        """显示插件信息"""
        if not args:
            print("❌ 请指定插件ID")
            return False
        
        plugin_id = args[0]
        plugin = self.manager.get_plugin(plugin_id)
        
        if not plugin:
            print(f"❌ 插件 {plugin_id} 不存在")
            return False
        
        print(f"\n📦 插件详情: {plugin.metadata.name}")
        print("=" * 80)
        print(f"ID: {plugin_id}")
        print(f"名称: {plugin.metadata.name}")
        print(f"版本: {plugin.metadata.version}")
        print(f"作者: {plugin.metadata.author}")
        print(f"类型: {plugin.metadata.plugin_type.name}")
        print(f"状态: {plugin.status.name}")
        print(f"\n📄 描述:")
        print(f"   {plugin.metadata.description}")
        
        if plugin.metadata.tags:
            print(f"\n🏷️ 标签: {', '.join(plugin.metadata.tags)}")
        
        if plugin.metadata.dependencies:
            print(f"\n🔗 依赖: {', '.join(plugin.metadata.dependencies)}")
        
        if plugin.error_message:
            print(f"\n❌ 错误: {plugin.error_message}")
        
        print("\n" + "=" * 80)
        return True
    
    def _load_plugin(self, args: List[str]) -> bool:
        """加载插件"""
        if not args:
            print("❌ 请指定插件ID")
            return False
        
        plugin_id = args[0]
        config = {}
        
        # 尝试解析配置参数
        if len(args) > 1:
            try:
                config = json.loads(args[1])
            except:
                pass
        
        return self.manager.load_plugin(plugin_id, config)
    
    def _unload_plugin(self, args: List[str]) -> bool:
        """卸载插件"""
        if not args:
            print("❌ 请指定插件ID")
            return False
        
        plugin_id = args[0]
        return self.manager.unload_plugin(plugin_id)
    
    def _activate_plugin(self, args: List[str]) -> bool:
        """激活插件"""
        if not args:
            print("❌ 请指定插件ID")
            return False
        
        plugin_id = args[0]
        return self.manager.activate_plugin(plugin_id)
    
    def _deactivate_plugin(self, args: List[str]) -> bool:
        """停用插件"""
        if not args:
            print("❌ 请指定插件ID")
            return False
        
        plugin_id = args[0]
        return self.manager.deactivate_plugin(plugin_id)
    
    def _test_plugin_system(self) -> bool:
        """测试插件系统"""
        print("\n🧪 测试插件系统...")
        print("=" * 80)
        
        try:
            # 测试插件管理器创建
            print("\n📦 测试插件管理器创建...")
            test_manager = PluginManager(plugin_dirs=["test_plugins"])
            print("✅ 插件管理器创建成功")
            
            # 测试扩展注册表
            print("\n🔗 测试扩展注册表...")
            registry = ExtensionRegistry()
            
            test_callback_called = False
            def test_callback(context):
                nonlocal test_callback_called
                test_callback_called = True
                return "test_result"
            
            registry.register(ExtensionPoint.TASK_PRE_PROCESS, test_callback)
            results = registry.invoke(ExtensionPoint.TASK_PRE_PROCESS, {})
            
            assert test_callback_called, "扩展回调未被调用"
            assert results == ["test_result"], f"预期结果 'test_result'，实际 {results}"
            print("✅ 扩展注册表测试成功")
            
            print("\n" + "=" * 80)
            print("🎉 插件系统测试完成！")
            print("=" * 80)
            
            return True
            
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False


def create_plugin_manager(plugin_dirs: Optional[List[str]] = None) -> PluginManager:
    """创建插件管理器工厂函数"""
    return PluginManager(plugin_dirs=plugin_dirs)


def create_plugin_cli() -> PluginCLI:
    """创建插件CLI工厂函数"""
    return PluginCLI()

