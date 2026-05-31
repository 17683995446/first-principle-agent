#!/usr/bin/env python3
"""
第70阶段: 系统任务模板库测试
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime


def test_data_structures():
    """测试模板数据结构"""
    print("\n" + "="*80)
    print("📋 测试1: 模板数据结构")
    print("="*80)
    
    try:
        from first_principle_agent.core.task_templates import (
            TaskTemplate, TemplateCategory
        )
        
        print("\n✅ 成功导入模板数据结构类")
        
        # 测试创建模板
        print("\n📝 创建测试模板...")
        template = TaskTemplate(
            template_id="test_template",
            name="测试模板",
            description="这是一个测试模板",
            category=TemplateCategory.CUSTOM,
            tags=["test", "demo"],
            requirements=["准备环境"],
            steps=["步骤1", "步骤2"],
            estimated_time="1小时",
            difficulty="easy",
            version="1.0",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            is_preset=False
        )
        print(f"✅ TaskTemplate 创建成功")
        print(f"   - ID: {template.template_id}")
        print(f"   - 名称: {template.name}")
        print(f"   - 分类: {template.category.value}")
        
        print("\n✅ 数据结构测试通过！")
        return True
    except Exception as e:
        print(f"\n❌ 数据结构测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_template_library():
    """测试模板库"""
    print("\n" + "="*80)
    print("📚 测试2: 模板库功能")
    print("="*80)
    
    try:
        from first_principle_agent.core.task_templates import (
            TaskTemplateLibrary, TemplateCategory
        )
        
        print("\n📦 创建模板库实例...")
        library = TaskTemplateLibrary(library_dir="test_task_templates")
        print("✅ TaskTemplateLibrary 创建成功")
        
        # 测试列出模板
        print("\n📋 列出所有模板...")
        templates = library.list_templates()
        print(f"✅ 列出 {len(templates)} 个模板")
        for i, template in enumerate(templates[:3], 1):
            print(f"   {i}. {template.name} ({template.category.value})")
        
        # 测试获取单个模板
        if templates:
            print(f"\n🔍 获取第一个模板...")
            first_template = library.get_template(templates[0].template_id)
            print(f"✅ 获取模板成功: {first_template.name}")
        
        # 测试分类过滤
        print(f"\n🏷️ 按分类过滤 (Web开发)...")
        web_templates = library.list_templates(category=TemplateCategory.WEB_DEVELOPMENT)
        print(f"✅ Web开发模板: {len(web_templates)} 个")
        
        # 测试创建自定义模板
        print(f"\n✏️ 创建自定义模板...")
        new_template = library.create_template(
            name="我的自定义模板",
            description="测试创建自定义模板",
            category=TemplateCategory.CUSTOM,
            tags=["custom", "test"],
            requirements=["准备材料"],
            steps=["开始", "中间", "结束"],
            estimated_time="10分钟",
            difficulty="easy"
        )
        print(f"✅ 创建自定义模板成功: {new_template.name}")
        
        # 测试更新模板
        print(f"\n📝 更新模板...")
        update_success = library.update_template(
            new_template.template_id,
            description="更新后的描述"
        )
        print(f"✅ 更新模板: {'成功' if update_success else '失败'}")
        
        # 测试使用模板
        print(f"\n📖 使用模板...")
        use_success = library.use_template(new_template.template_id)
        print(f"✅ 使用模板: {'成功' if use_success else '失败'}")
        
        # 测试获取热门模板
        print(f"\n🔥 获取热门模板...")
        popular = library.get_popular_templates(limit=3)
        print(f"✅ 热门模板: {len(popular)} 个")
        
        # 测试导出模板
        print(f"\n📤 导出模板...")
        export_file = "test_exported_template.json"
        export_success = library.export_template(
            templates[0].template_id,
            export_file
        )
        if export_success:
            print(f"✅ 模板导出成功: {export_file}")
            
            # 测试导入模板
            print(f"\n📥 导入模板...")
            imported = library.import_template(export_file)
            print(f"✅ 模板导入成功: {imported.name}")
            
            # 清理导出文件
            os.remove(export_file)
        
        # 测试删除模板
        print(f"\n🗑️ 删除自定义模板...")
        delete_success = library.delete_template(new_template.template_id)
        print(f"✅ 删除模板: {'成功' if delete_success else '失败'}")
        
        print("\n✅ 模板库功能测试通过！")
        
        # 清理测试目录
        import shutil
        test_dir = Path("test_task_templates")
        if test_dir.exists():
            shutil.rmtree(test_dir)
        
        return True
    except Exception as e:
        print(f"\n❌ 模板库功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        
        # 清理测试目录
        test_dir = Path("test_task_templates")
        if test_dir.exists():
            import shutil
            shutil.rmtree(test_dir)
        
        return False


def test_template_cli():
    """测试模板CLI"""
    print("\n" + "="*80)
    print("🖥️ 测试3: 模板CLI")
    print("="*80)
    
    try:
        from first_principle_agent.core.task_templates import TemplateCLI
        
        print("\n💻 创建TemplateCLI实例...")
        cli = TemplateCLI()
        print("✅ TemplateCLI 创建成功")
        
        # 测试 help 命令
        print("\n❓ 测试 help 命令...")
        result = cli.run(["help"])
        print(f"✅ help 命令: {'成功' if result else '失败'}")
        
        # 测试 list 命令
        print("\n📋 测试 list 命令...")
        result = cli.run(["list"])
        print(f"✅ list 命令: {'成功' if result else '失败'}")
        
        # 测试 test 命令
        print("\n🧪 测试 test 命令...")
        result = cli.run(["test"])
        print(f"✅ test 命令: {'成功' if result else '失败'}")
        
        print("\n✅ 模板CLI测试通过！")
        return True
    except Exception as e:
        print(f"\n❌ 模板CLI测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_preset_templates():
    """测试预设模板"""
    print("\n" + "="*80)
    print("✨ 测试4: 预设模板")
    print("="*80)
    
    try:
        from first_principle_agent.core.task_templates import (
            TaskTemplateLibrary, TemplateCategory
        )
        
        library = TaskTemplateLibrary(library_dir="test_task_templates")
        
        print("\n📋 检查预设模板...")
        templates = library.list_templates()
        print(f"✅ 预设模板总数: {len(templates)}")
        
        # 检查各分类模板
        print("\n🏷️ 按分类检查模板:")
        categories = [
            (TemplateCategory.WEB_DEVELOPMENT, "Web开发"),
            (TemplateCategory.DATA_PROCESSING, "数据处理"),
            (TemplateCategory.SYSTEM_ADMIN, "系统管理"),
            (TemplateCategory.MACHINE_LEARNING, "机器学习"),
            (TemplateCategory.DOCUMENTATION, "文档"),
            (TemplateCategory.TESTING, "测试"),
            (TemplateCategory.DEVOPS, "DevOps"),
        ]
        
        for category, name in categories:
            category_templates = library.list_templates(category=category)
            print(f"   {name}: {len(category_templates)} 个模板")
        
        print("\n📝 检查单个模板详情...")
        web_templates = library.list_templates(category=TemplateCategory.WEB_DEVELOPMENT)
        if web_templates:
            template = web_templates[0]
            print(f"✅ 模板 '{template.name}' 详情:")
            print(f"   - 描述: {template.description}")
            print(f"   - 难度: {template.difficulty}")
            print(f"   - 预估时间: {template.estimated_time}")
            print(f"   - 需求数: {len(template.requirements)}")
            print(f"   - 步骤数: {len(template.steps)}")
        
        print("\n✅ 预设模板测试通过！")
        
        # 清理测试目录
        import shutil
        test_dir = Path("test_task_templates")
        if test_dir.exists():
            shutil.rmtree(test_dir)
        
        return True
    except Exception as e:
        print(f"\n❌ 预设模板测试失败: {e}")
        import traceback
        traceback.print_exc()
        
        test_dir = Path("test_task_templates")
        if test_dir.exists():
            import shutil
            shutil.rmtree(test_dir)
        
        return False


def test_factory_functions():
    """测试工厂函数"""
    print("\n" + "="*80)
    print("🏭 测试5: 工厂函数")
    print("="*80)
    
    try:
        from first_principle_agent.core.task_templates import (
            create_template_library, create_template_cli
        )
        
        print("\n📦 测试 create_template_library...")
        library = create_template_library()
        print("✅ create_template_library() 成功")
        
        print("\n💻 测试 create_template_cli...")
        cli = create_template_cli()
        print("✅ create_template_cli() 成功")
        
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
    print("🧪 第70阶段: 系统任务模板库 - 完整测试套件")
    print("="*80)
    
    tests = [
        ("数据结构测试", test_data_structures),
        ("模板库功能测试", test_template_library),
        ("模板CLI测试", test_template_cli),
        ("预设模板测试", test_preset_templates),
        ("工厂函数测试", test_factory_functions),
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
        print("🎉 所有测试通过！第70阶段完成！")
    else:
        print("⚠️  部分测试失败，请检查上述错误")
    print("="*80)
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

