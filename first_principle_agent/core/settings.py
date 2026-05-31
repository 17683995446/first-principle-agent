#!/usr/bin/env python3
"""
系统设置和偏好管理 - 第68阶段
提供系统配置和用户偏好的管理功能
"""

import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class SettingType(Enum):
    """设置类型"""
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    FLOAT = "float"
    LIST = "list"


@dataclass
class SettingDefinition:
    """设置定义"""
    key: str
    name: str
    description: str
    type: SettingType
    default_value: Any
    category: str = "general"
    options: List[Any] = field(default_factory=list)
    validation: Optional[Dict[str, Any]] = None


@dataclass
class SettingValue:
    """设置值"""
    key: str
    value: Any
    modified_at: str
    modified_by: str = "system"


class SettingsManager:
    """设置管理器"""
    
    def __init__(self, settings_dir: str = "settings"):
        self.settings_dir = Path(settings_dir)
        self.settings_dir.mkdir(exist_ok=True)
        self.settings_file = self.settings_dir / "settings.json"
        self.settings: Dict[str, SettingValue] = {}
        self.definitions: Dict[str, SettingDefinition] = {}
        
        # 初始化默认设置定义
        self._initialize_default_definitions()
        self._load_settings()
    
    def _initialize_default_definitions(self):
        """初始化默认设置定义"""
        default_definitions = [
            SettingDefinition(
                key="theme",
                name="主题",
                description="系统界面主题",
                type=SettingType.STRING,
                default_value="light",
                category="ui",
                options=["light", "dark", "blue", "green"]
            ),
            SettingDefinition(
                key="language",
                name="语言",
                description="系统显示语言",
                type=SettingType.STRING,
                default_value="zh-CN",
                category="ui",
                options=["zh-CN", "en-US", "ja-JP"]
            ),
            SettingDefinition(
                key="auto_save",
                name="自动保存",
                description="是否启用自动保存功能",
                type=SettingType.BOOLEAN,
                default_value=True,
                category="behavior"
            ),
            SettingDefinition(
                key="log_level",
                name="日志级别",
                description="系统日志记录级别",
                type=SettingType.STRING,
                default_value="INFO",
                category="system",
                options=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            ),
            SettingDefinition(
                key="max_backups",
                name="最大备份数",
                description="系统保留的最大备份数量",
                type=SettingType.INTEGER,
                default_value=10,
                category="system",
                validation={"min": 1, "max": 100}
            ),
            SettingDefinition(
                key="auto_backup",
                name="自动备份",
                description="是否启用自动备份功能",
                type=SettingType.BOOLEAN,
                default_value=False,
                category="behavior"
            ),
            SettingDefinition(
                key="backup_interval",
                name="备份间隔",
                description="自动备份间隔（小时）",
                type=SettingType.INTEGER,
                default_value=24,
                category="behavior",
                validation={"min": 1, "max": 720}
            ),
            SettingDefinition(
                key="notification_enabled",
                name="启用通知",
                description="是否启用系统通知",
                type=SettingType.BOOLEAN,
                default_value=True,
                category="ui"
            ),
            SettingDefinition(
                key="max_concurrent_tasks",
                name="最大并发任务",
                description="同时执行的最大任务数",
                type=SettingType.INTEGER,
                default_value=5,
                category="system",
                validation={"min": 1, "max": 100}
            ),
            SettingDefinition(
                key="timeout_seconds",
                name="超时时间",
                description="任务执行超时时间（秒）",
                type=SettingType.INTEGER,
                default_value=300,
                category="system",
                validation={"min": 10, "max": 3600}
            )
        ]
        
        for definition in default_definitions:
            self.definitions[definition.key] = definition
    
    def _load_settings(self):
        """加载设置"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value_data in data.items():
                        self.settings[key] = SettingValue(
                            key=key,
                            value=value_data.get("value"),
                            modified_at=value_data.get("modified_at", ""),
                            modified_by=value_data.get("modified_by", "system")
                        )
            except Exception as e:
                print(f"⚠️  加载设置时出错: {e}")
    
    def _save_settings(self):
        """保存设置"""
        try:
            data = {}
            for key, setting_value in self.settings.items():
                data[key] = {
                    "value": setting_value.value,
                    "modified_at": setting_value.modified_at,
                    "modified_by": setting_value.modified_by
                }
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  保存设置时出错: {e}")
    
    def get_setting(self, key: str) -> Any:
        """获取设置值"""
        if key in self.settings:
            return self.settings[key].value
        elif key in self.definitions:
            return self.definitions[key].default_value
        return None
    
    def set_setting(self, key: str, value: Any, modified_by: str = "user") -> bool:
        """设置设置值"""
        if key not in self.definitions:
            print(f"❌ 未知的设置项: {key}")
            return False
        
        definition = self.definitions[key]
        
        # 验证值类型
        try:
            value = self._validate_and_convert_value(value, definition)
        except ValueError as e:
            print(f"❌ {e}")
            return False
        
        # 验证值范围
        if definition.validation:
            if not self._validate_value_range(value, definition.validation):
                print(f"❌ 值超出有效范围: {value}")
                return False
        
        # 验证选项
        if definition.options and value not in definition.options:
            print(f"❌ 值必须是以下之一: {', '.join(str(opt) for opt in definition.options)}")
            return False
        
        from datetime import datetime
        self.settings[key] = SettingValue(
            key=key,
            value=value,
            modified_at=datetime.now().isoformat(),
            modified_by=modified_by
        )
        
        self._save_settings()
        print(f"✅ 设置已更新: {key} = {value}")
        return True
    
    def _validate_and_convert_value(self, value: Any, definition: SettingDefinition) -> Any:
        """验证并转换值类型"""
        try:
            if definition.type == SettingType.BOOLEAN:
                if isinstance(value, str):
                    return value.lower() in ('true', '1', 'yes', 'on')
                return bool(value)
            elif definition.type == SettingType.INTEGER:
                return int(value)
            elif definition.type == SettingType.FLOAT:
                return float(value)
            elif definition.type == SettingType.STRING:
                return str(value)
            elif definition.type == SettingType.LIST:
                if isinstance(value, str):
                    return [item.strip() for item in value.split(',')]
                return list(value)
            return value
        except (ValueError, TypeError) as e:
            raise ValueError(f"类型转换失败: {e}")
    
    def _validate_value_range(self, value: Any, validation: Dict[str, Any]) -> bool:
        """验证值范围"""
        if "min" in validation and value < validation["min"]:
            return False
        if "max" in validation and value > validation["max"]:
            return False
        return True
    
    def reset_setting(self, key: str) -> bool:
        """重置设置为默认值"""
        if key not in self.definitions:
            print(f"❌ 未知的设置项: {key}")
            return False
        
        if key in self.settings:
            del self.settings[key]
            self._save_settings()
            print(f"✅ 设置已重置: {key}")
        else:
            print(f"ℹ️  设置已是默认值: {key}")
        
        return True
    
    def reset_all_settings(self) -> bool:
        """重置所有设置为默认值"""
        self.settings = {}
        self._save_settings()
        print("✅ 所有设置已重置为默认值")
        return True
    
    def list_settings(self, category: Optional[str] = None) -> List[SettingDefinition]:
        """列出所有设置定义"""
        if category:
            return [d for d in self.definitions.values() if d.category == category]
        return list(self.definitions.values())
    
    def get_categories(self) -> List[str]:
        """获取所有设置分类"""
        return list(set(d.category for d in self.definitions.values()))
    
    def export_settings(self, file_path: str) -> bool:
        """导出设置"""
        try:
            export_data = {
                "settings": {},
                "definitions": {},
                "exported_at": ""
            }
            
            from datetime import datetime
            export_data["exported_at"] = datetime.now().isoformat()
            
            for key, definition in self.definitions.items():
                export_data["definitions"][key] = {
                    "name": definition.name,
                    "description": definition.description,
                    "type": definition.type.value,
                    "default_value": definition.default_value,
                    "category": definition.category
                }
                
                value = self.get_setting(key)
                export_data["settings"][key] = value
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 设置已导出到: {file_path}")
            return True
        except Exception as e:
            print(f"❌ 导出设置失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def import_settings(self, file_path: str) -> bool:
        """导入设置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if "settings" not in import_data:
                print("❌ 无效的设置文件格式")
                return False
            
            for key, value in import_data["settings"].items():
                self.set_setting(key, value, "import")
            
            print(f"✅ 设置已从 {file_path} 导入")
            return True
        except Exception as e:
            print(f"❌ 导入设置失败: {e}")
            import traceback
            traceback.print_exc()
            return False


class SettingsCLI:
    """设置命令行接口"""
    
    def __init__(self):
        self.manager = SettingsManager()
    
    def run(self, args: List[str]) -> bool:
        """运行设置命令"""
        if not args:
            return self._show_help()
        
        command = args[0].lower()
        
        if command == "help":
            return self._show_help()
        elif command == "list":
            return self._list_settings(args[1:])
        elif command == "get":
            return self._get_setting(args[1:])
        elif command == "set":
            return self._set_setting(args[1:])
        elif command == "reset":
            return self._reset_setting(args[1:])
        elif command == "export":
            return self._export_settings(args[1:])
        elif command == "import":
            return self._import_settings(args[1:])
        elif command == "test":
            return self._test_settings_system()
        else:
            print(f"❌ 未知命令: {command}")
            return False
    
    def _show_help(self) -> bool:
        """显示帮助"""
        help_text = """
⚙️  系统设置命令:
  help                - 显示帮助信息
  list [category]     - 列出所有设置或指定分类的设置
  get <key>           - 获取设置值
  set <key> <value>   - 设置设置值
  reset [key]         - 重置设置为默认值（不指定key则重置所有）
  export <file>       - 导出设置到文件
  import <file>       - 从文件导入设置
  test                - 测试设置系统

使用示例:
  # 列出所有设置
  python -m first_principle_agent settings list
  
  # 列出UI分类的设置
  python -m first_principle_agent settings list ui
  
  # 获取设置值
  python -m first_principle_agent settings get theme
  
  # 设置设置值
  python -m first_principle_agent settings set theme dark
  
  # 重置设置
  python -m first_principle_agent settings reset theme
  
  # 导出设置
  python -m first_principle_agent settings export my_settings.json
  
  # 导入设置
  python -m first_principle_agent settings import my_settings.json
        """
        print(help_text)
        return True
    
    def _list_settings(self, args: List[str]) -> bool:
        """列出设置"""
        category = args[0] if len(args) > 0 else None
        
        print("\n📋 系统设置:")
        print("=" * 80)
        
        categories = self.manager.get_categories()
        if category and category not in categories:
            print(f"❌ 未知的分类: {category}")
            print(f"可用分类: {', '.join(categories)}")
            return False
        
        if category:
            categories = [category]
        
        for cat in categories:
            definitions = self.manager.list_settings(cat)
            if not definitions:
                continue
            
            print(f"\n📁 {cat.upper()}:")
            for definition in definitions:
                current_value = self.manager.get_setting(definition.key)
                is_default = definition.key not in self.manager.settings
                
                default_str = " (默认)" if is_default else ""
                
                if definition.options:
                    options_str = f" [选项: {', '.join(str(opt) for opt in definition.options)}]"
                else:
                    options_str = ""
                
                print(f"  • {definition.key}")
                print(f"    名称: {definition.name}")
                print(f"    描述: {definition.description}")
                print(f"    类型: {definition.type.value}")
                print(f"    当前值: {current_value}{default_str}")
                print(f"    默认值: {definition.default_value}")
                if options_str:
                    print(f"    {options_str}")
                print()
        
        return True
    
    def _get_setting(self, args: List[str]) -> bool:
        """获取设置"""
        if not args:
            print("\n❌ 请指定要获取的设置项")
            return False
        
        key = args[0]
        value = self.manager.get_setting(key)
        
        if value is None and key not in self.manager.definitions:
            print(f"\n❌ 未知的设置项: {key}")
            return False
        
        definition = self.manager.definitions.get(key)
        if definition:
            is_default = key not in self.manager.settings
            default_str = " (默认)" if is_default else ""
            
            print(f"\n📋 {definition.name}:")
            print(f"   描述: {definition.description}")
            print(f"   当前值: {value}{default_str}")
            print(f"   类型: {definition.type.value}")
            if definition.options:
                print(f"   选项: {', '.join(str(opt) for opt in definition.options)}")
        
        return True
    
    def _set_setting(self, args: List[str]) -> bool:
        """设置设置"""
        if len(args) < 2:
            print("\n❌ 请指定要设置的项和值")
            return False
        
        key = args[0]
        value = args[1]
        
        return self.manager.set_setting(key, value)
    
    def _reset_setting(self, args: List[str]) -> bool:
        """重置设置"""
        if len(args) > 0:
            key = args[0]
            return self.manager.reset_setting(key)
        else:
            confirm = input("⚠️  确定要重置所有设置吗？ (yes/no): ")
            if confirm.lower() != "yes":
                print("❌ 已取消重置")
                return False
            
            return self.manager.reset_all_settings()
    
    def _export_settings(self, args: List[str]) -> bool:
        """导出设置"""
        if not args:
            print("\n❌ 请指定导出文件路径")
            return False
        
        file_path = args[0]
        return self.manager.export_settings(file_path)
    
    def _import_settings(self, args: List[str]) -> bool:
        """导入设置"""
        if not args:
            print("\n❌ 请指定导入文件路径")
            return False
        
        file_path = args[0]
        if not os.path.exists(file_path):
            print(f"\n❌ 文件不存在: {file_path}")
            return False
        
        confirm = input("⚠️  导入设置将覆盖当前设置。确定继续吗？ (yes/no): ")
        if confirm.lower() != "yes":
            print("❌ 已取消导入")
            return False
        
        return self.manager.import_settings(file_path)
    
    def _test_settings_system(self) -> bool:
        """测试设置系统"""
        print("\n🧪 测试设置系统...")
        print("=" * 80)
        
        try:
            # 测试获取默认设置
            print("\n📋 测试获取默认设置...")
            theme_value = self.manager.get_setting("theme")
            print(f"✅ 默认主题: {theme_value}")
            
            # 测试设置值
            print("\n⚙️  测试设置值...")
            set_success = self.manager.set_setting("theme", "dark")
            print(f"✅ 设置主题: {'成功' if set_success else '失败'}")
            
            # 测试获取修改后的设置
            new_theme = self.manager.get_setting("theme")
            print(f"✅ 修改后的主题: {new_theme}")
            
            # 测试重置设置
            print("\n🔄 测试重置设置...")
            reset_success = self.manager.reset_setting("theme")
            print(f"✅ 重置主题: {'成功' if reset_success else '失败'}")
            
            # 测试列出设置
            print("\n📁 测试列出分类...")
            categories = self.manager.get_categories()
            print(f"✅ 分类数量: {len(categories)}")
            
            # 测试列出所有设置
            print("\n📋 测试列出所有设置...")
            all_settings = self.manager.list_settings()
            print(f"✅ 设置数量: {len(all_settings)}")
            
            print("\n" + "=" * 80)
            print("🎉 设置系统测试完成！")
            print("=" * 80)
            
            return True
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False


def create_settings_manager() -> SettingsManager:
    """创建设置管理器工厂函数"""
    return SettingsManager()


def create_settings_cli() -> SettingsCLI:
    """创建设置CLI工厂函数"""
    return SettingsCLI()

