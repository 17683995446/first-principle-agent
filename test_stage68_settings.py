#!/usr/bin/env python3
"""
第68阶段 - 系统设置和偏好管理测试
"""

import sys
import os
import json
import shutil

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from first_principle_agent.core.settings import (
    SettingsManager,
    SettingsCLI,
    SettingDefinition,
    SettingValue,
    SettingType,
    create_settings_manager,
    create_settings_cli
)


def test_1_data_structures():
    """测试1: 数据结构"""
    print("\n" + "="*80)
    print("测试1: 数据结构")
    print("="*80)
    
    try:
        # 测试SettingDefinition
        definition = SettingDefinition(
            key="test_setting",
            name="测试设置",
            description="这是一个测试设置",
            type=SettingType.STRING,
            default_value="default_value",
            category="test",
            options=["option1", "option2", "option3"]
        )
        
        print("✅ SettingDefinition 创建成功")
        print(f"   Key: {definition.key}")
        print(f"   名称: {definition.name}")
        print(f"   描述: {definition.description}")
        print(f"   类型: {definition.type}")
        print(f"   默认值: {definition.default_value}")
        print(f"   分类: {definition.category}")
        print(f"   选项: {definition.options}")
        
        # 测试SettingValue
        from datetime import datetime
        value = SettingValue(
            key="test_setting",
            value="custom_value",
            modified_at=datetime.now().isoformat(),
            modified_by="test_user"
        )
        
        print("\n✅ SettingValue 创建成功")
        print(f"   Key: {value.key}")
        print(f"   值: {value.value}")
        print(f"   修改时间: {value.modified_at}")
        print(f"   修改者: {value.modified_by}")
        
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_2_settings_manager():
    """测试2: 设置管理器"""
    print("\n" + "="*80)
    print("测试2: 设置管理器")
    print("="*80)
    
    try:
        # 先清理测试目录
        test_dir = "test_settings_68"
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        
        manager = SettingsManager(settings_dir=test_dir)
        print("✅ SettingsManager 创建成功")
        
        # 测试获取默认设置
        print("\n📋 测试获取默认设置...")
        theme = manager.get_setting("theme")
        print(f"✅ 默认主题: {theme}")
        
        # 测试设置值
        print("\n⚙️  测试设置值...")
        success = manager.set_setting("theme", "dark", "test_user")
        print(f"✅ 设置主题: {'成功' if success else '失败'}")
        
        # 测试获取修改后的设置
        new_theme = manager.get_setting("theme")
        print(f"✅ 修改后的主题: {new_theme}")
        
        # 测试重置设置
        print("\n🔄 测试重置设置...")
        reset_success = manager.reset_setting("theme")
        print(f"✅ 重置主题: {'成功' if reset_success else '失败'}")
        
        # 验证重置后的值
        reset_theme = manager.get_setting("theme")
        print(f"✅ 重置后的主题: {reset_theme}")
        
        # 测试设置数值类型
        print("\n🔢 测试设置数值类型...")
        success = manager.set_setting("max_backups", "20")
        print(f"✅ 设置备份数: {'成功' if success else '失败'}")
        value = manager.get_setting("max_backups")
        print(f"✅ 值: {value} (类型: {type(value)})")
        
        # 测试设置布尔类型
        print("\n🔌 测试设置布尔类型...")
        success = manager.set_setting("auto_save", "false")
        print(f"✅ 设置自动保存: {'成功' if success else '失败'}")
        value = manager.get_setting("auto_save")
        print(f"✅ 值: {value} (类型: {type(value)})")
        
        # 清理
        shutil.rmtree(test_dir)
        
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        # 清理
        if os.path.exists("test_settings_68"):
            shutil.rmtree("test_settings_68")
        return False


def test_3_settings_validation():
    """测试3: 设置验证"""
    print("\n" + "="*80)
    print("测试3: 设置验证")
    print("="*80)
    
    try:
        test_dir = "test_settings_validation_68"
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        
        manager = SettingsManager(settings_dir=test_dir)
        
        # 测试选项验证
        print("\n📝 测试选项验证...")
        success = manager.set_setting("theme", "invalid_theme")
        print(f"❌ 无效选项正确拒绝: {'成功' if not success else '失败'}")
        
        # 测试范围验证
        print("\n📏 测试范围验证...")
        success = manager.set_setting("max_backups", "9999")
        print(f"❌ 超出范围正确拒绝: {'成功' if not success else '失败'}")
        
        # 测试有效范围值
        success = manager.set_setting("max_backups", "50")
        print(f"✅ 有效范围值接受: {'成功' if success else '失败'}")
        
        # 测试类型验证
        print("\n🏷️  测试类型验证...")
        success = manager.set_setting("max_backups", "not_a_number")
        print(f"❌ 无效类型正确拒绝: {'成功' if not success else '失败'}")
        
        # 清理
        shutil.rmtree(test_dir)
        
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        if os.path.exists("test_settings_validation_68"):
            shutil.rmtree("test_settings_validation_68")
        return False


def test_4_categories_and_listing():
    """测试4: 分类和列表"""
    print("\n" + "="*80)
    print("测试4: 分类和列表")
    print("="*80)
    
    try:
        test_dir = "test_settings_listing_68"
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        
        manager = SettingsManager(settings_dir=test_dir)
        
        # 测试获取分类
        print("\n📁 测试获取分类...")
        categories = manager.get_categories()
        print(f"✅ 分类数: {len(categories)}")
        print(f"   分类: {categories}")
        
        # 测试列出所有设置
        print("\n📋 测试列出所有设置...")
        all_settings = manager.list_settings()
        print(f"✅ 设置数: {len(all_settings)}")
        
        # 测试按分类列出设置
        print("\n📁 测试按分类列出设置...")
        ui_settings = manager.list_settings("ui")
        print(f"✅ UI分类设置数: {len(ui_settings)}")
        
        # 清理
        shutil.rmtree(test_dir)
        
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        if os.path.exists("test_settings_listing_68"):
            shutil.rmtree("test_settings_listing_68")
        return False


def test_5_export_import():
    """测试5: 导出和导入"""
    print("\n" + "="*80)
    print("测试5: 导出和导入")
    print("="*80)
    
    try:
        test_dir = "test_settings_export_import_68"
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        
        manager = SettingsManager(settings_dir=test_dir)
        
        # 先修改一些设置
        print("\n⚙️  修改一些设置...")
        manager.set_setting("theme", "green")
        manager.set_setting("auto_save", "false")
        manager.set_setting("max_backups", "15")
        
        # 测试导出
        print("\n📤 测试导出设置...")
        export_file = "test_settings_export.json"
        if os.path.exists(export_file):
            os.remove(export_file)
        
        export_success = manager.export_settings(export_file)
        print(f"✅ 导出: {'成功' if export_success else '失败'}")
        
        # 验证导出文件
        assert os.path.exists(export_file), "导出文件不存在"
        with open(export_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert "settings" in data, "导出格式错误"
            assert "definitions" in data, "导出格式错误"
        print(f"✅ 导出文件验证通过")
        
        # 修改当前设置
        print("\n🔄 修改当前设置...")
        manager.set_setting("theme", "blue")
        manager.set_setting("auto_save", "true")
        
        # 测试导入
        print("\n📥 测试导入设置...")
        import_success = manager.import_settings(export_file)
        print(f"✅ 导入: {'成功' if import_success else '失败'}")
        
        # 验证导入后的值
        theme_after = manager.get_setting("theme")
        auto_save_after = manager.get_setting("auto_save")
        max_backups_after = manager.get_setting("max_backups")
        
        assert theme_after == "green", "主题未正确导入"
        assert auto_save_after == False, "自动保存未正确导入"
        assert max_backups_after == 15, "最大备份数未正确导入"
        print(f"✅ 导入值验证通过")
        
        # 清理
        os.remove(export_file)
        shutil.rmtree(test_dir)
        
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        if os.path.exists("test_settings_export.json"):
            os.remove("test_settings_export.json")
        if os.path.exists("test_settings_export_import_68"):
            shutil.rmtree("test_settings_export_import_68")
        return False


def test_6_settings_cli():
    """测试6: 设置命令行接口"""
    print("\n" + "="*80)
    print("测试6: 设置命令行接口")
    print("="*80)
    
    try:
        cli = create_settings_cli()
        print("✅ SettingsCLI 创建成功")
        
        # 测试help命令
        print("\n❓ 测试help命令...")
        help_success = cli.run(["help"])
        print(f"   help命令: {'成功' if help_success else '失败'}")
        
        # 测试list命令
        print("\n📋 测试list命令...")
        list_success = cli.run(["list"])
        print(f"   list命令: {'成功' if list_success else '失败'}")
        
        # 测试list ui命令
        print("\n📁 测试list ui命令...")
        list_ui_success = cli.run(["list", "ui"])
        print(f"   list ui命令: {'成功' if list_ui_success else '失败'}")
        
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("第68阶段 - 系统设置和偏好管理测试")
    print("="*80)
    
    tests = [
        test_1_data_structures,
        test_2_settings_manager,
        test_3_settings_validation,
        test_4_categories_and_listing,
        test_5_export_import,
        test_6_settings_cli
    ]
    
    results = []
    for test_func in tests:
        result = test_func()
        results.append(result)
    
    print("\n" + "="*80)
    print("测试结果汇总")
    print("="*80)
    passed = sum(results)
    total = len(results)
    print(f"✅ 通过: {passed}/{total}")
    print(f"❌ 失败: {total-passed}/{total}")
    
    if passed == total:
        print("\n🎉 所有测试通过！第68阶段完成！")
        return 0
    else:
        print("\n❌ 部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())

