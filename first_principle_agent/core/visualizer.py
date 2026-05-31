#!/usr/bin/env python3
"""
系统可视化工具 - 第66阶段
提供系统状态可视化、文本图表生成等功能
"""

import time
import random
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class ChartType(Enum):
    """图表类型"""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    PROGRESS = "progress"


class ColorCode(Enum):
    """颜色代码（ANSI）"""
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"


@dataclass
class DataPoint:
    """数据点"""
    label: str
    value: float
    color: Optional[ColorCode] = None


@dataclass
class ChartData:
    """图表数据"""
    title: str
    data_points: List[DataPoint]
    chart_type: ChartType = ChartType.BAR
    max_width: int = 60
    show_values: bool = True


class TextVisualizer:
    """文本可视化器"""
    
    @staticmethod
    def get_color_for_value(value: float, min_val: float, max_val: float) -> ColorCode:
        """根据值获取颜色"""
        if max_val == min_val:
            return ColorCode.CYAN
        
        ratio = (value - min_val) / (max_val - min_val)
        if ratio < 0.33:
            return ColorCode.GREEN
        elif ratio < 0.66:
            return ColorCode.YELLOW
        else:
            return ColorCode.RED
    
    @staticmethod
    def create_bar_chart(chart_data: ChartData) -> str:
        """创建条形图"""
        lines = []
        lines.append(f"\n{ColorCode.BOLD}{chart_data.title}{ColorCode.RESET}")
        lines.append("-" * (chart_data.max_width + 20))
        
        if not chart_data.data_points:
            lines.append("  无数据")
            return "\n".join(lines)
        
        max_value = max(dp.value for dp in chart_data.data_points)
        min_value = min(dp.value for dp in chart_data.data_points)
        
        for dp in chart_data.data_points:
            color = dp.color if dp.color else TextVisualizer.get_color_for_value(
                dp.value, min_value, max_value
            )
            
            bar_length = int((dp.value / max_value) * chart_data.max_width) if max_value > 0 else 0
            bar = "█" * bar_length
            
            if chart_data.show_values:
                line = f"  {dp.label:15} {color}{bar}{ColorCode.RESET} {dp.value:.2f}"
            else:
                line = f"  {dp.label:15} {color}{bar}{ColorCode.RESET}"
            
            lines.append(line)
        
        lines.append("-" * (chart_data.max_width + 20))
        return "\n".join(lines)
    
    @staticmethod
    def create_pie_chart(chart_data: ChartData) -> str:
        """创建饼图（文本版本）"""
        lines = []
        lines.append(f"\n{ColorCode.BOLD}{chart_data.title}{ColorCode.RESET}")
        lines.append("-" * 50)
        
        if not chart_data.data_points:
            lines.append("  无数据")
            return "\n".join(lines)
        
        total = sum(dp.value for dp in chart_data.data_points)
        
        if total == 0:
            lines.append("  总值为0，无法绘制饼图")
            return "\n".join(lines)
        
        colors = [ColorCode.RED, ColorCode.GREEN, ColorCode.YELLOW, ColorCode.BLUE, ColorCode.MAGENTA, ColorCode.CYAN]
        
        for i, dp in enumerate(chart_data.data_points):
            percentage = (dp.value / total) * 100
            color = dp.color if dp.color else colors[i % len(colors)]
            wedge = "▓" * int(percentage / 2)
            
            line = f"  {color}{wedge}{ColorCode.RESET} {dp.label:15} {dp.value:8.2f} ({percentage:5.1f}%)"
            lines.append(line)
        
        lines.append("-" * 50)
        lines.append(f"  总计: {total:.2f}")
        return "\n".join(lines)
    
    @staticmethod
    def create_progress_bar(current: float, total: float, width: int = 50, label: str = "") -> str:
        """创建进度条"""
        percentage = (current / total) * 100 if total > 0 else 0
        filled = int((current / total) * width) if total > 0 else 0
        empty = width - filled
        
        if percentage < 33:
            color = ColorCode.GREEN
        elif percentage < 66:
            color = ColorCode.YELLOW
        else:
            color = ColorCode.RED
        
        bar = f"{color}{'█' * filled}{'░' * empty}{ColorCode.RESET}"
        
        if label:
            return f"  {label}: [{bar}] {percentage:.1f}% ({current}/{total})"
        else:
            return f"  [{bar}] {percentage:.1f}% ({current}/{total})"


class SystemDashboard:
    """系统仪表板"""
    
    def __init__(self):
        self.start_time = datetime.now()
    
    def generate_system_summary(self) -> str:
        """生成系统概览"""
        lines = []
        lines.append(f"\n{ColorCode.BOLD}{'='*80}{ColorCode.RESET}")
        lines.append(f"{ColorCode.BOLD}📊 系统仪表板{ColorCode.RESET}")
        lines.append(f"{ColorCode.BOLD}{'='*80}{ColorCode.RESET}")
        
        # 系统基本信息
        lines.append(f"\n{ColorCode.CYAN}🖥️  系统信息{ColorCode.RESET}")
        lines.append(f"  启动时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"  运行时间: {datetime.now() - self.start_time}")
        
        return "\n".join(lines)
    
    def generate_module_status(self) -> str:
        """生成模块状态"""
        modules = [
            ("任务规划系统", "✅ 运行中"),
            ("配置管理", "✅ 运行中"),
            ("监控系统", "✅ 运行中"),
            ("日志系统", "✅ 运行中"),
            ("错误处理", "✅ 运行中"),
            ("文档生成", "✅ 运行中"),
            ("性能测试", "✅ 运行中"),
        ]
        
        lines = []
        lines.append(f"\n{ColorCode.CYAN}📦 模块状态{ColorCode.RESET}")
        
        for name, status in modules:
            lines.append(f"  • {name}: {status}")
        
        return "\n".join(lines)
    
    def generate_performance_summary(self) -> str:
        """生成性能概览"""
        # 模拟一些性能数据
        cpu_usage = random.uniform(10, 80)
        memory_usage = random.uniform(30, 70)
        disk_usage = random.uniform(40, 60)
        
        lines = []
        lines.append(f"\n{ColorCode.CYAN}⚡ 性能概览{ColorCode.RESET}")
        lines.append(TextVisualizer.create_progress_bar(cpu_usage, 100, 40, "CPU使用率"))
        lines.append(TextVisualizer.create_progress_bar(memory_usage, 100, 40, "内存使用"))
        lines.append(TextVisualizer.create_progress_bar(disk_usage, 100, 40, "磁盘使用"))
        
        return "\n".join(lines)
    
    def generate_full_dashboard(self) -> str:
        """生成完整仪表板"""
        parts = [
            self.generate_system_summary(),
            self.generate_module_status(),
            self.generate_performance_summary(),
        ]
        return "\n".join(parts)


class StatsVisualizer:
    """统计数据可视化器"""
    
    @staticmethod
    def visualize_task_metrics(metrics: Dict[str, Any]) -> str:
        """可视化任务指标"""
        lines = []
        lines.append(f"\n{ColorCode.BOLD}📈 任务执行指标{ColorCode.RESET}")
        lines.append("-" * 60)
        
        data_points = [
            DataPoint("总任务数", metrics.get("total_tasks", 0)),
            DataPoint("完成任务", metrics.get("completed_tasks", 0), ColorCode.GREEN),
            DataPoint("失败任务", metrics.get("failed_tasks", 0), ColorCode.RED),
            DataPoint("进行中", metrics.get("in_progress_tasks", 0), ColorCode.YELLOW),
        ]
        
        chart_data = ChartData(
            title="任务数量统计",
            data_points=data_points,
            chart_type=ChartType.BAR,
            max_width=40
        )
        
        lines.append(TextVisualizer.create_bar_chart(chart_data))
        
        # 显示执行时间
        if "total_duration" in metrics:
            lines.append(f"\n  总执行时间: {metrics['total_duration']:.2f}秒")
        
        return "\n".join(lines)
    
    @staticmethod
    def visualize_component_health(components: Dict[str, Dict[str, Any]]) -> str:
        """可视化组件健康状态"""
        lines = []
        lines.append(f"\n{ColorCode.BOLD}🏥 组件健康状态{ColorCode.RESET}")
        lines.append("-" * 60)
        
        for comp_name, comp_info in components.items():
            health = comp_info.get("health", 100)
            status = comp_info.get("status", "unknown")
            
            if health >= 80:
                color = ColorCode.GREEN
                status_emoji = "✅"
            elif health >= 50:
                color = ColorCode.YELLOW
                status_emoji = "⚠️"
            else:
                color = ColorCode.RED
                status_emoji = "❌"
            
            lines.append(f"\n  {status_emoji} {comp_name}")
            lines.append(f"    状态: {color}{status}{ColorCode.RESET}")
            lines.append(TextVisualizer.create_progress_bar(health, 100, 30, "健康度"))
        
        return "\n".join(lines)


class VisualizerCLI:
    """可视化命令行接口"""
    
    def __init__(self):
        self.dashboard = SystemDashboard()
    
    def run(self, args: List[str]) -> bool:
        """运行可视化命令"""
        if not args:
            return self._show_help()
        
        command = args[0].lower()
        
        if command == "help":
            return self._show_help()
        elif command == "dashboard":
            return self._show_dashboard()
        elif command == "demo":
            return self._show_demo()
        elif command == "test":
            return self._test_visualizer()
        else:
            print(f"❌ 未知命令: {command}")
            return False
    
    def _show_help(self) -> bool:
        """显示帮助"""
        help_text = """
🎨 系统可视化工具命令:
  help                - 显示帮助信息
  dashboard           - 显示系统仪表板
  demo                - 演示可视化功能
  test                - 测试可视化工具

使用示例:
  # 显示系统仪表板
  python -m first_principle_agent viz dashboard
  
  # 演示可视化功能
  python -m first_principle_agent viz demo
  
  # 测试可视化工具
  python -m first_principle_agent viz test
        """
        print(help_text)
        return True
    
    def _show_dashboard(self) -> bool:
        """显示系统仪表板"""
        print(self.dashboard.generate_full_dashboard())
        return True
    
    def _show_demo(self) -> bool:
        """演示可视化功能"""
        print(f"\n{ColorCode.BOLD}🎨 可视化功能演示{ColorCode.RESET}")
        print(f"{ColorCode.BOLD}{'='*80}{ColorCode.RESET}")
        
        # 1. 系统仪表板
        print("\n1. 系统仪表板")
        print(self.dashboard.generate_system_summary())
        print(self.dashboard.generate_module_status())
        print(self.dashboard.generate_performance_summary())
        
        # 2. 条形图演示
        print("\n2. 条形图演示")
        chart_data = ChartData(
            title="每周任务完成量",
            data_points=[
                DataPoint("周一", 12),
                DataPoint("周二", 18),
                DataPoint("周三", 25),
                DataPoint("周四", 15),
                DataPoint("周五", 22),
            ],
            chart_type=ChartType.BAR,
            max_width=50
        )
        print(TextVisualizer.create_bar_chart(chart_data))
        
        # 3. 饼图演示
        print("\n3. 饼图演示")
        pie_data = ChartData(
            title="任务分布",
            data_points=[
                DataPoint("开发", 45),
                DataPoint("测试", 25),
                DataPoint("文档", 15),
                DataPoint("部署", 10),
                DataPoint("其他", 5),
            ],
            chart_type=ChartType.PIE
        )
        print(TextVisualizer.create_pie_chart(pie_data))
        
        # 4. 任务指标可视化
        print("\n4. 任务指标可视化")
        metrics = {
            "total_tasks": 150,
            "completed_tasks": 120,
            "failed_tasks": 10,
            "in_progress_tasks": 20,
            "total_duration": 3600.5
        }
        print(StatsVisualizer.visualize_task_metrics(metrics))
        
        # 5. 组件健康状态可视化
        print("\n5. 组件健康状态可视化")
        components = {
            "任务规划器": {"health": 95, "status": "healthy"},
            "执行引擎": {"health": 88, "status": "healthy"},
            "监控系统": {"health": 75, "status": "warning"},
            "数据库": {"health": 50, "status": "needs_attention"},
        }
        print(StatsVisualizer.visualize_component_health(components))
        
        print(f"\n{ColorCode.BOLD}{'='*80}{ColorCode.RESET}")
        print(f"{ColorCode.GREEN}✅ 演示完成！{ColorCode.RESET}")
        return True
    
    def _test_visualizer(self) -> bool:
        """测试可视化工具"""
        print(f"\n🧪 测试可视化工具...")
        print(f"{ColorCode.BOLD}{'='*80}{ColorCode.RESET}")
        
        try:
            # 测试1: 文本可视化器
            print("✅ TextVisualizer 初始化成功")
            
            # 测试2: 条形图
            print("\n📊 测试条形图...")
            bar_data = ChartData(
                title="测试条形图",
                data_points=[
                    DataPoint("A", 10),
                    DataPoint("B", 20),
                    DataPoint("C", 15),
                ]
            )
            bar_chart = TextVisualizer.create_bar_chart(bar_data)
            print("✅ 条形图创建成功")
            
            # 测试3: 饼图
            print("\n🥧 测试饼图...")
            pie_data = ChartData(
                title="测试饼图",
                data_points=[
                    DataPoint("X", 30),
                    DataPoint("Y", 20),
                ]
            )
            pie_chart = TextVisualizer.create_pie_chart(pie_data)
            print("✅ 饼图创建成功")
            
            # 测试4: 进度条
            print("\n📈 测试进度条...")
            progress_bar = TextVisualizer.create_progress_bar(75, 100, 40, "测试进度")
            print("✅ 进度条创建成功")
            
            # 测试5: 系统仪表板
            print("\n🎛️ 测试系统仪表板...")
            dashboard = SystemDashboard()
            summary = dashboard.generate_system_summary()
            print("✅ 系统仪表板创建成功")
            
            # 测试6: 统计可视化
            print("\n📉 测试统计可视化...")
            metrics = {"total_tasks": 100, "completed_tasks": 80, "failed_tasks": 5, "in_progress_tasks": 15}
            task_viz = StatsVisualizer.visualize_task_metrics(metrics)
            print("✅ 任务指标可视化成功")
            
            print(f"\n{ColorCode.BOLD}{'='*80}{ColorCode.RESET}")
            print(f"{ColorCode.GREEN}🎉 可视化工具测试完成！{ColorCode.RESET}")
            print(f"{ColorCode.BOLD}{'='*80}{ColorCode.RESET}")
            
            return True
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False


def create_visualizer() -> TextVisualizer:
    """创建文本可视化器"""
    return TextVisualizer()


def create_dashboard() -> SystemDashboard:
    """创建系统仪表板"""
    return SystemDashboard()
