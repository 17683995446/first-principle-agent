#!/usr/bin/env python3
"""
第64阶段：文档生成和状态报告系统测试
"""

import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("🧪 第64阶段：文档生成和状态报告系统测试")
print("=" * 80)
print()


def test_system_component():
    """测试系统组件数据类"""
    print("\n📦 测试 1: 系统组件数据类")
    print("=" * 80)
    
    try:
        from first_principle_agent.core.docs_reporter import SystemComponent
        
        component = SystemComponent(
            name="TestComponent",
            description="测试组件",
            status="ready",
            file_path="test/file.py",
            dependencies=["Dep1", "Dep2"]
        )
        
        assert component.name == "TestComponent"
        assert component.description == "测试组件"
        assert component.status == "ready"
        assert component.file_path == "test/file.py"
        assert component.dependencies == ["Dep1", "Dep2"]
        
        print("✅ 系统组件数据类测试通过")
        return True
    except Exception as e:
        print(f"❌ 系统组件数据类测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_doc_generator():
    """测试文档生成器"""
    print("\n📚 测试 2: 文档生成器")
    print("=" * 80)
    
    try:
        from first_principle_agent.core.docs_reporter import SystemDocumentationGenerator
        
        # 创建文档生成器
        doc_gen = SystemDocumentationGenerator(output_dir="/tmp/test_docs")
        print("✅ 文档生成器创建成功")
        print(f"   📦 已注册组件数: {len(doc_gen.system_components)}")
        
        # 测试Markdown文档生成
        markdown_doc = doc_gen.generate_architecture_document(format="markdown")
        assert "# 基于第一性原理的AI Agent任务规划系统" in markdown_doc
        assert "## 核心组件" in markdown_doc
        print(f"✅ Markdown文档生成成功 ({len(markdown_doc)} 字符)")
        
        # 测试JSON文档生成
        json_doc = doc_gen.generate_architecture_document(format="json")
        assert "system_name" in json_doc
        assert "components" in json_doc
        print(f"✅ JSON文档生成成功 ({len(json_doc)} 字符)")
        
        # 测试文档保存
        test_file = "test_architecture.md"
        saved_path = doc_gen.save_document(markdown_doc, test_file)
        assert os.path.exists(saved_path)
        print(f"✅ 文档保存成功: {saved_path}")
        
        return True
    except Exception as e:
        print(f"❌ 文档生成器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_status_report():
    """测试状态报告"""
    print("\n📊 测试 3: 状态报告")
    print("=" * 80)
    
    try:
        from first_principle_agent.core.docs_reporter import SystemStatusReporter, SystemStatusReport
        
        # 创建状态报告器
        reporter = SystemStatusReporter()
        print("✅ 状态报告器创建成功")
        
        # 测试报告生成
        report = reporter.generate_system_report()
        assert isinstance(report, SystemStatusReport)
        assert report.report_id is not None
        assert report.generated_at is not None
        print(f"✅ 系统状态报告生成成功")
        print(f"   📋 报告ID: {report.report_id}")
        print(f"   📦 组件数: {len(report.components)}")
        print(f"   💡 建议数: {len(report.recommendations)}")
        
        # 测试文本格式渲染
        text_report = reporter.render_report(report, format="text")
        assert "系统状态报告" in text_report
        assert "核心组件状态" in text_report
        print(f"✅ 文本格式报告渲染成功 ({len(text_report)} 字符)")
        
        # 测试Markdown格式渲染
        markdown_report = reporter.render_report(report, format="markdown")
        assert "# 系统状态报告" in markdown_report
        assert "## 核心组件状态" in markdown_report
        print(f"✅ Markdown格式报告渲染成功 ({len(markdown_report)} 字符)")
        
        # 测试JSON格式渲染
        json_report = reporter.render_report(report, format="json")
        assert "report_id" in json_report
        assert "components" in json_report
        print(f"✅ JSON格式报告渲染成功 ({len(json_report)} 字符)")
        
        return True
    except Exception as e:
        print(f"❌ 状态报告测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_docs_cli():
    """测试文档命令行接口"""
    print("\n💻 测试 4: 文档命令行接口")
    print("=" * 80)
    
    try:
        from first_principle_agent.core.docs_reporter import DocsCLI
        
        # 创建CLI
        cli = DocsCLI()
        print("✅ DocsCLI创建成功")
        
        # 测试help命令
        print("\n📌 测试 docs help:")
        success = cli.run(["help"])
        assert success
        print("✅ help命令执行成功")
        
        # 测试list命令
        print("\n📌 测试 docs list:")
        success = cli.run(["list"])
        assert success
        print("✅ list命令执行成功")
        
        # 测试test命令
        print("\n📌 测试 docs test:")
        success = cli.run(["test"])
        assert success
        print("✅ test命令执行成功")
        
        # 测试generate命令
        print("\n📌 测试 docs generate:")
        success = cli.run(["generate"])
        assert success
        print("✅ generate命令执行成功")
        
        # 测试status命令
        print("\n📌 测试 docs status:")
        success = cli.run(["status"])
        assert success
        print("✅ status命令执行成功")
        
        return True
    except Exception as e:
        print(f"❌ 文档CLI测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_factory_functions():
    """测试工厂函数"""
    print("\n🏭 测试 5: 工厂函数")
    print("=" * 80)
    
    try:
        from first_principle_agent.core.docs_reporter import (
            create_doc_generator, create_status_reporter
        )
        
        # 测试文档生成器工厂
        doc_gen = create_doc_generator(output_dir="/tmp/factory_docs")
        assert doc_gen is not None
        print("✅ create_doc_generator工厂函数工作正常")
        
        # 测试状态报告器工厂
        reporter = create_status_reporter()
        assert reporter is not None
        print("✅ create_status_reporter工厂函数工作正常")
        
        return True
    except Exception as e:
        print(f"❌ 工厂函数测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    results = []
    
    # 运行测试
    results.append(("系统组件数据类", test_system_component()))
    results.append(("文档生成器", test_doc_generator()))
    results.append(("状态报告", test_status_report()))
    results.append(("文档命令行接口", test_docs_cli()))
    results.append(("工厂函数", test_factory_functions()))
    
    # 打印汇总
    print("\n" + "=" * 80)
    print("📊 测试结果汇总")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n总计: {passed}/{len(results)} 通过, {failed}/{len(results)} 失败")
    
    if failed == 0:
        print("\n🎉 所有测试通过！第64阶段完成！")
        print(f"📈 项目进度: 64/100 阶段完成")
        return 0
    else:
        print(f"\n⚠️  部分测试失败，请检查！")
        return 1


if __name__ == "__main__":
    sys.exit(main())
