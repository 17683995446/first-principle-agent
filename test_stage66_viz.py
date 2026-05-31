#!/usr/bin/env python3
"""
第66阶段 - 系统可视化工具测试
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from first_principle_agent.core.visualizer import (
    TextVisualizer,
    SystemDashboard,
    StatsVisualizer,
    VisualizerCLI,
    DataPoint,
    ChartData,
    ChartType,
    ColorCode,
    create_visualizer,
    create_dashboard
)


def test_1_data_structures():
    """测试1: 数据结构"""
    print("\n" + "="*80)
    print("测试1: 数据结构")
    print("="*80)
    
    try:
        # 测试数据点
        dp = DataPoint(label="测试", value=10.5, color=ColorCode.GREEN)
        print("✅ DataPoint 创建成功")
        print(f"  标签: {dp.label}")
        print(f"  值: {dp.value}")
        print(f"  颜色: {dp.color}")
        
        # 测试图表数据
        chart_data = ChartData(
            title="测试图表",
            data_points=[
                DataPoint("A", 10),
                DataPoint("B", 20),
            ]
        )
        print("\n✅ ChartData 创建成功")
        print(f"  标题: {chart_data.title}")
        print(f"  数据点数: {len(chart_data.data_points)}")
        
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_2_text_visualizer():
    """测试2: 文本可视化器"""
    print("\n" + "="*80)
    print("测试2: 文本可视化器")
    print("="*80)
    
    try:
        visualizer = create_visualizer()
        print("✅ TextVisualizer 创建成功")
        
        # 测试条形图
        print("\n📊 测试条形图...")
        bar_data = ChartData(
            title="测试条形图",
            data_points=[
                DataPoint("一月", 15),
                DataPoint("二月", 25),
                DataPoint("三月", 18),
            ]
        )
        bar_chart = visualizer.create_bar_chart(bar_data)
        print("✅ 条形图创建成功")
        
        # 测试饼图
        print("\n🥧 测试饼图...")
        pie_data = ChartData(
            title="测试饼图",
            data_points=[
                DataPoint("类型1", 40),
                DataPoint("类型2", 35),
                DataPoint("类型3", 25),
            ]
        )
        pie_chart = visualizer.create_pie_chart(pie_data)
        print("✅ 饼图创建成功")
        
        # 测试进度条
        print("\n📈 测试进度条...")
        progress = visualizer.create_progress_bar(75, 100, 40, "测试进度")
        print("✅ 进度条创建成功")
        
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_3_system_dashboard():
    """测试3: 系统仪表板"""
    print("\n" + "="*80)
    print("测试3: 系统仪表板")
    print("="*80)
    
    try:
        dashboard = create_dashboard()
        print("✅ SystemDashboard 创建成功")
        
        # 测试系统概览
        print("\n🖥️  测试系统概览...")
        summary = dashboard.generate_system_summary()
        print("✅ 系统概览生成成功")
        
        # 测试模块状态
        print("\n📦 测试模块状态...")
        modules = dashboard.generate_module_status()
        print("✅ 模块状态生成成功")
        
        # 测试性能概览
        print("\n⚡ 测试性能概览...")
        performance = dashboard.generate_performance_summary()
        print("✅ 性能概览生成成功")
        
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_4_stats_visualizer():
    """测试4: 统计可视化器"""
    print("\n" + "="*80)
    print("测试4: 统计可视化器")
    print("="*80)
    
    try:
        # 测试任务指标可视化
        print("\n📈 测试任务指标可视化...")
        metrics = {
            "total_tasks": 200,
            "completed_tasks": 160,
            "failed_tasks": 15,
            "in_progress_tasks": 25,
            "total_duration": 7200.0
        }
        task_viz = StatsVisualizer.visualize_task_metrics(metrics)
        print("✅ 任务指标可视化成功")
        
        # 测试组件健康状态可视化
        print("\n🏥 测试组件健康状态可视化...")
        components = {
            "任务规划器": {"health": 95, "status": "healthy"},
            "执行引擎": {"health": 88, "status": "healthy"},
            "数据库": {"health": 60, "status": "warning"},
        }
        health_viz = StatsVisualizer.visualize_component_health(components)
        print("✅ 组件健康状态可视化成功")
        
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_5_visualizer_cli():
    """测试5: 可视化命令行接口"""
    print("\n" + "="*80)
    print("测试5: 可视化命令行接口")
    print("="*80)
    
    try:
        cli = VisualizerCLI()
        print("✅ VisualizerCLI 创建成功")
        
        # 测试帮助命令
        print("\n❓ 测试help命令...")
        help_success = cli.run(["help"])
        print(f"  help命令: {'成功' if help_success else '失败'}")
        
        # 测试test命令
        print("\n🧪 测试test命令...")
        test_success = cli.run(["test"])
        print(f"  test命令: {'成功' if test_success else '失败'}")
        
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("第66阶段 - 系统可视化工具测试")
    print("="*80)
    
    tests = [
        test_1_data_structures,
        test_2_text_visualizer,
        test_3_system_dashboard,
        test_4_stats_visualizer,
        test_5_visualizer_cli,
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
        print("\n🎉 所有测试通过！第66阶段完成！")
        return 0
    else:
        print("\n❌ 部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
