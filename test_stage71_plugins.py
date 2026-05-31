#!/usr/bin/env python3
"""
第71阶段：系统插件和扩展机制测试
"""

import sys
import os
import shutil
from pathlib import Path


def test_data_structures():
    """测试数据结构"""
    print("\n" + "="*80)
    print("📦 测试1: 数据结构")
    print("="*80)
    
    try:
        from first_principle_agent.core.plugin_system import (
            PluginMetadata, PluginType, PluginStatus, ExtensionPoint
        )
        
        print("\n✅ 成功导入数据结构类")
        
        # 测试创建 PluginMetadata
        print("\n📝 创建插件元数据...")
        metadata = PluginMetadata(
            name="Test Plugin",
            version="1.0.0",
            author="Test Author",
            description="A test plugin",
            plugin_type=PluginType.CUSTOM,
            dependencies=["some_dep"],
            tags=["test", "demo"]
        )
        
        assert metadata.name == "Test Plugin"
        assert metadata.version == "1.0.0"
        assert metadata.author == "Test Author"
        assert metadata.description == "A test plugin"
        assert metadata.plugin_type == PluginType.CUSTOM
        print("✅ PluginMetadata 创建成功")
        
        # 测试枚举
        print("\n🔢 测试枚举...")
        assert PluginType.TASK_EXECUTOR != PluginType.CUSTOM
        assert ExtensionPoint.TASK_PRE_PROCESS.value == "task_pre_process"
        print("✅ 枚举测试成功")
        
        print("\n✅ 数据结构测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 数据结构测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_extension_registry():
    """测试扩展注册表"""
    print("\n" + "="*80)
    print("🔗 测试2: 扩展注册表")
    print("="*80)
    
    try:
        from first_principle_agent.core.plugin_system import (
            ExtensionRegistry, ExtensionPoint
        )
        
        print("\n📦 创建扩展注册表...")
        registry = ExtensionRegistry()
        print("✅ ExtensionRegistry 创建成功")
        
        # 测试注册回调
        print("\n🔧 测试注册回调...")
        test_value = []
        def callback1(context):
            test_value.append("callback1")
            return "result1"
        
        def callback2(context):
            test_value.append("callback2")
            return "result2"
        
        registry.register(ExtensionPoint.TASK_PRE_PROCESS, callback1)
        registry.register(ExtensionPoint.TASK_PRE_PROCESS, callback2)
        print("✅ 回调注册成功")
        
        # 测试调用回调
        print("\n🚀 测试调用回调...")
        results = registry.invoke(ExtensionPoint.TASK_PRE_PROCESS, {"key": "value"})
        
        assert test_value == ["callback1", "callback2"]
        assert results == ["result1", "result2"]
        print("✅ 回调调用成功")
        
        # 测试获取扩展
        print("\n📋 测试获取扩展...")
        extensions = registry.get_extensions(ExtensionPoint.TASK_PRE_PROCESS)
        assert len(extensions) == 2
        print("✅ 获取扩展成功")
        
        # 测试注销回调
        print("\n❌ 测试注销回调...")
        registry.unregister(ExtensionPoint.TASK_PRE_PROCESS, callback1)
        extensions = registry.get_extensions(ExtensionPoint.TASK_PRE_PROCESS)
        assert len(extensions) == 1
        print("✅ 回调注销成功")
        
        print("\n✅ 扩展注册表测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 扩展注册表测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_plugin_manager_basic():
    """测试插件管理器基础功能"""
    print("\n" + "="*80)
    print("🔌 测试3: 插件管理器基础")
    print("="*80)
    
    try:
        from first_principle_agent.core.plugin_system import (
            PluginManager, PluginStatus
        )
        
        # 创建临时测试目录
        test_plugin_dir = "test_plugins_temp"
        os.makedirs(test_plugin_dir, exist_ok=True)
        
        print("\n📦 创建插件管理器...")
        manager = PluginManager(plugin_dirs=[test_plugin_dir])
        print("✅ PluginManager 创建成功")
        
        # 测试列出插件
        print("\n📋 测试列出插件...")
        plugins = manager.list_plugins()
        assert isinstance(plugins, list)
        print("✅ 列出插件成功")
        
        # 测试获取不存在的插件
        print("\n🔍 测试获取不存在的插件...")
        plugin = manager.get_plugin("nonexistent")
        assert plugin is None
        print("✅ 获取不存在的插件返回 None")
        
        # 清理
        shutil.rmtree(test_plugin_dir, ignore_errors=True)
        
        print("\n✅ 插件管理器基础测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 插件管理器基础测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_plugin_cli():
    """测试插件CLI"""
    print("\n" + "="*80)
    print("🖥️  测试4: 插件CLI")
    print("="*80)
    
    try:
        from first_principle_agent.core.plugin_system import PluginCLI
        
        print("\n💻 创建PluginCLI...")
        cli = PluginCLI()
        print("✅ PluginCLI 创建成功")
        
        # 测试 help 命令
        print("\n❓ 测试 help 命令...")
        result = cli.run(["help"])
        assert result is True
        print("✅ help 命令成功")
        
        # 测试 test 命令
        print("\n🧪 测试 test 命令...")
        result = cli.run(["test"])
        assert result is True
        print("✅ test 命令成功")
        
        print("\n✅ 插件CLI测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 插件CLI测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_factory_functions():
    """测试工厂函数"""
    print("\n" + "="*80)
    print("🏭 测试5: 工厂函数")
    print("="*80)
    
    try:
        from first_principle_agent.core.plugin_system import (
            create_plugin_manager, create_plugin_cli
        )
        
        print("\n📦 测试 create_plugin_manager...")
        manager = create_plugin_manager(plugin_dirs=["test_dir"])
        print("✅ create_plugin_manager 成功")
        
        print("\n💻 测试 create_plugin_cli...")
        cli = create_plugin_cli()
        print("✅ create_plugin_cli 成功")
        
        print("\n✅ 工厂函数测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 工厂函数测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*80)
    print("🧪 第71阶段：系统插件和扩展机制 - 完整测试套件")
    print("="*80)
    
    tests = [
        ("数据结构测试", test_data_structures),
        ("扩展注册表测试", test_extension_registry),
        ("插件管理器基础测试", test_plugin_manager_basic),
        ("插件CLI测试", test_plugin_cli),
        ("工厂函数测试", test_factory_functions)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} 执行异常: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    print("\n" + "="*80)
    print("📊 测试结果汇总")
    print("="*80)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "="*80)
    if all_passed:
        print("🎉 所有测试通过！第71阶段完成！")
    else:
        print("⚠️  部分测试失败，请检查上述错误")
    print("="*80)
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

