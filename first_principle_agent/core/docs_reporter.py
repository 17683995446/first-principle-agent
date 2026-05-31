#!/usr/bin/env python3
"""
系统文档生成和状态报告 - 第64阶段
提供系统文档生成、状态报告和架构可视化功能
"""

import os
import sys
import json
import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SystemComponent:
    """系统组件信息"""
    name: str
    description: str
    status: str = "ready"
    file_path: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    version: str = "1.0.0"


@dataclass
class SystemStatusReport:
    """系统状态报告"""
    report_id: str
    generated_at: str
    overall_status: str
    components: List[SystemComponent] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class SystemDocumentationGenerator:
    """系统文档生成器"""
    
    def __init__(self, output_dir: str = "docs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.system_components = []
        self._register_core_components()
    
    def _register_core_components(self):
        """注册核心系统组件"""
        components = [
            SystemComponent(
                name="TaskTuple",
                description="任务四元组数据结构，包含目标、条件、边界和终止规则",
                file_path="core/task_tuple.py"
            ),
            SystemComponent(
                name="TaskDAG",
                description="任务依赖图，用于管理任务之间的依赖关系",
                file_path="core/dag_structures.py",
                dependencies=["TaskTuple"]
            ),
            SystemComponent(
                name="TaskExecutionEngine",
                description="任务执行引擎，负责执行原子动作",
                file_path="core/task_execution_engine.py",
                dependencies=["TaskTuple", "AtomicAction"]
            ),
            SystemComponent(
                name="TaskPipeline",
                description="任务管道，用于串联和管理任务执行流程",
                file_path="core/task_pipeline.py",
                dependencies=["TaskExecutionEngine"]
            ),
            SystemComponent(
                name="TaskScheduler",
                description="任务调度器，负责任务的调度和执行",
                file_path="core/task_scheduler.py",
                dependencies=["TaskPipeline"]
            ),
            SystemComponent(
                name="TaskPlanningSystem",
                description="任务规划系统整合层，整合所有核心组件",
                file_path="core/task_planning_system.py",
                dependencies=["TaskExecutionEngine", "TaskPipeline", "TaskScheduler"]
            ),
            SystemComponent(
                name="TaskAnalytics",
                description="任务分析系统，用于分析和报告执行结果",
                file_path="core/task_analytics.py",
                dependencies=["TaskTuple"]
            ),
            SystemComponent(
                name="TaskWorkflowExecutor",
                description="工作流编排器，用于编排复杂的工作流",
                file_path="core/task_workflow_executor.py",
                dependencies=["TaskDAG"]
            ),
            SystemComponent(
                name="TaskOrchestrator",
                description="任务编排器，整合所有核心组件提供端到端解决方案",
                file_path="core/task_orchestrator.py",
                dependencies=["TaskPlanningSystem", "TaskAnalytics", "TaskWorkflowExecutor"]
            ),
            SystemComponent(
                name="SystemConfig",
                description="系统配置管理，提供配置加载和保存功能",
                file_path="core/system_config.py"
            ),
            SystemComponent(
                name="SystemMonitor",
                description="系统监控器，监控系统资源和健康状态",
                file_path="core/system_monitor.py",
                dependencies=["SystemConfig"]
            ),
            SystemComponent(
                name="SystemLogger",
                description="系统日志记录器，提供多级别日志记录功能",
                file_path="core/system_logger.py"
            ),
            SystemComponent(
                name="ErrorHandler",
                description="错误处理器，提供异常捕获和恢复功能",
                file_path="core/error_handler.py"
            )
        ]
        self.system_components.extend(components)
    
    def generate_architecture_document(self, format: str = "markdown") -> str:
        """生成系统架构文档"""
        if format == "markdown":
            return self._generate_markdown_architecture()
        elif format == "json":
            return self._generate_json_architecture()
        else:
            raise ValueError(f"不支持的格式: {format}")
    
    def _generate_markdown_architecture(self) -> str:
        """生成Markdown格式的架构文档"""
        lines = []
        lines.append("# 基于第一性原理的AI Agent任务规划系统 - 系统架构\n")
        lines.append(f"> 生成时间: {datetime.datetime.now().isoformat()}\n")
        
        lines.append("## 目录\n")
        lines.append("1. [系统概述](#系统概述)")
        lines.append("2. [核心组件](#核心组件)")
        lines.append("3. [组件关系](#组件关系)")
        lines.append("4. [使用指南](#使用指南)\n")
        
        lines.append("## 系统概述\n")
        lines.append("本系统是一个基于第一性原理的AI Agent任务规划系统，具有完整的任务建模、拆解、执行和分析功能。\n")
        
        lines.append("## 核心组件\n")
        for component in self.system_components:
            lines.append(f"### {component.name}\n")
            lines.append(f"- **描述**: {component.description}")
            lines.append(f"- **状态**: {component.status}")
            if component.file_path:
                lines.append(f"- **文件路径**: `{component.file_path}`")
            if component.dependencies:
                lines.append(f"- **依赖**: {', '.join(component.dependencies)}")
            lines.append(f"- **版本**: {component.version}\n")
        
        lines.append("## 组件关系\n")
        lines.append("```")
        lines.append("TaskTuple → TaskDAG → TaskWorkflowExecutor")
        lines.append("    ↓")
        lines.append("AtomicAction → TaskExecutionEngine → TaskPipeline → TaskScheduler")
        lines.append("    ↓")
        lines.append("TaskPlanningSystem → TaskOrchestrator")
        lines.append("    ↓")
        lines.append("TaskAnalytics")
        lines.append("```\n")
        
        lines.append("## 使用指南\n")
        lines.append("### 基本使用\n")
        lines.append("```python")
        lines.append("from first_principle_agent.core.task_orchestrator import TaskOrchestrator")
        lines.append("orchestrator = TaskOrchestrator()")
        lines.append("result = orchestrator.orchestrate('我的需求')")
        lines.append("```\n")
        
        lines.append("### CLI使用\n")
        lines.append("```bash")
        lines.append("# 查看帮助")
        lines.append("python -m first_principle_agent help")
        lines.append("")
        lines.append("# 运行演示")
        lines.append("python -m first_principle_agent demo")
        lines.append("```\n")
        
        return "\n".join(lines)
    
    def _generate_json_architecture(self) -> str:
        """生成JSON格式的架构文档"""
        architecture = {
            "system_name": "基于第一性原理的AI Agent任务规划系统",
            "version": "1.0.0",
            "generated_at": datetime.datetime.now().isoformat(),
            "components": [
                {
                    "name": c.name,
                    "description": c.description,
                    "status": c.status,
                    "file_path": c.file_path,
                    "dependencies": c.dependencies,
                    "version": c.version
                }
                for c in self.system_components
            ]
        }
        return json.dumps(architecture, indent=2, ensure_ascii=False)
    
    def save_document(self, content: str, filename: str) -> str:
        """保存文档到文件"""
        file_path = self.output_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return str(file_path)


class SystemStatusReporter:
    """系统状态报告器"""
    
    def __init__(self):
        self.report_id = f"report-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def generate_system_report(self) -> SystemStatusReport:
        """生成系统状态报告"""
        report = SystemStatusReport(
            report_id=self.report_id,
            generated_at=datetime.datetime.now().isoformat(),
            overall_status="healthy"
        )
        
        # 收集核心组件状态
        report.components = self._collect_component_statuses()
        
        # 收集系统指标
        report.metrics = self._collect_system_metrics()
        
        # 检查错误和警告
        report.errors, report.warnings = self._check_system_health()
        
        # 生成建议
        report.recommendations = self._generate_recommendations(report)
        
        return report
    
    def _collect_component_statuses(self) -> List[SystemComponent]:
        """收集组件状态"""
        components = []
        
        try:
            from first_principle_agent.core.task_tuple import TaskTuple
            components.append(SystemComponent(
                name="TaskTuple",
                description="任务四元组数据结构",
                status="ready"
            ))
        except Exception as e:
            components.append(SystemComponent(
                name="TaskTuple",
                description="任务四元组数据结构",
                status="unavailable"
            ))
        
        try:
            from first_principle_agent.core.dag_structures import TaskDAG
            components.append(SystemComponent(
                name="TaskDAG",
                description="任务依赖图",
                status="ready"
            ))
        except Exception as e:
            components.append(SystemComponent(
                name="TaskDAG",
                description="任务依赖图",
                status="unavailable"
            ))
        
        try:
            from first_principle_agent.core.task_orchestrator import TaskOrchestrator
            components.append(SystemComponent(
                name="TaskOrchestrator",
                description="任务编排器",
                status="ready"
            ))
        except Exception as e:
            components.append(SystemComponent(
                name="TaskOrchestrator",
                description="任务编排器",
                status="unavailable"
            ))
        
        try:
            from first_principle_agent.core.system_config import ConfigManager
            components.append(SystemComponent(
                name="ConfigManager",
                description="配置管理器",
                status="ready"
            ))
        except Exception as e:
            components.append(SystemComponent(
                name="ConfigManager",
                description="配置管理器",
                status="unavailable"
            ))
        
        try:
            from first_principle_agent.core.system_monitor import SystemMonitor
            components.append(SystemComponent(
                name="SystemMonitor",
                description="系统监控器",
                status="ready"
            ))
        except Exception as e:
            components.append(SystemComponent(
                name="SystemMonitor",
                description="系统监控器",
                status="unavailable"
            ))
        
        try:
            from first_principle_agent.core.system_logger import SystemLogger
            components.append(SystemComponent(
                name="SystemLogger",
                description="系统日志记录器",
                status="ready"
            ))
        except Exception as e:
            components.append(SystemComponent(
                name="SystemLogger",
                description="系统日志记录器",
                status="unavailable"
            ))
        
        try:
            from first_principle_agent.core.error_handler import ErrorHandler
            components.append(SystemComponent(
                name="ErrorHandler",
                description="错误处理器",
                status="ready"
            ))
        except Exception as e:
            components.append(SystemComponent(
                name="ErrorHandler",
                description="错误处理器",
                status="unavailable"
            ))
        
        return components
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """收集系统指标"""
        metrics = {}
        
        try:
            import psutil
            metrics["cpu_percent"] = psutil.cpu_percent(interval=0.1)
            metrics["memory_percent"] = psutil.virtual_memory().percent
            metrics["disk_percent"] = psutil.disk_usage('/').percent
            metrics["process_count"] = len(psutil.pids())
        except ImportError:
            pass
        
        metrics["python_version"] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        metrics["platform"] = sys.platform
        metrics["timestamp"] = datetime.datetime.now().isoformat()
        
        return metrics
    
    def _check_system_health(self) -> tuple[List[str], List[str]]:
        """检查系统健康状况"""
        errors = []
        warnings = []
        
        # 检查工作目录
        if not os.access('.', os.W_OK):
            warnings.append("工作目录不可写")
        
        # 检查Python版本
        if sys.version_info < (3, 8):
            warnings.append("建议使用Python 3.8或更高版本")
        
        return errors, warnings
    
    def _generate_recommendations(self, report: SystemStatusReport) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 检查组件状态
        unavailable = [c for c in report.components if c.status == "unavailable"]
        if unavailable:
            recommendations.append(f"以下组件不可用，请检查: {', '.join(c.name for c in unavailable)}")
        
        # 检查指标
        if report.metrics.get("cpu_percent", 0) > 80:
            recommendations.append("CPU使用率较高，建议检查系统负载")
        
        if report.metrics.get("memory_percent", 0) > 80:
            recommendations.append("内存使用率较高，建议优化内存使用")
        
        if report.metrics.get("disk_percent", 0) > 90:
            recommendations.append("磁盘空间不足，建议清理磁盘")
        
        if not recommendations:
            recommendations.append("系统运行正常，继续保持")
        
        return recommendations
    
    def render_report(self, report: SystemStatusReport, format: str = "text") -> str:
        """渲染报告"""
        if format == "text":
            return self._render_text_report(report)
        elif format == "markdown":
            return self._render_markdown_report(report)
        elif format == "json":
            return self._render_json_report(report)
        else:
            raise ValueError(f"不支持的格式: {format}")
    
    def _render_text_report(self, report: SystemStatusReport) -> str:
        """渲染文本格式报告"""
        lines = []
        lines.append("=" * 80)
        lines.append("系统状态报告")
        lines.append("=" * 80)
        lines.append(f"报告ID: {report.report_id}")
        lines.append(f"生成时间: {report.generated_at}")
        lines.append(f"整体状态: {report.overall_status}")
        lines.append("")
        
        lines.append("核心组件状态:")
        for component in report.components:
            status_icon = "✅" if component.status == "ready" else "❌"
            lines.append(f"  {status_icon} {component.name}: {component.status}")
        lines.append("")
        
        if report.metrics:
            lines.append("系统指标:")
            for key, value in report.metrics.items():
                lines.append(f"  {key}: {value}")
            lines.append("")
        
        if report.errors:
            lines.append("错误:")
            for error in report.errors:
                lines.append(f"  ❌ {error}")
            lines.append("")
        
        if report.warnings:
            lines.append("警告:")
            for warning in report.warnings:
                lines.append(f"  ⚠️  {warning}")
            lines.append("")
        
        if report.recommendations:
            lines.append("建议:")
            for rec in report.recommendations:
                lines.append(f"  💡 {rec}")
            lines.append("")
        
        lines.append("=" * 80)
        return "\n".join(lines)
    
    def _render_markdown_report(self, report: SystemStatusReport) -> str:
        """渲染Markdown格式报告"""
        lines = []
        lines.append("# 系统状态报告\n")
        lines.append(f"- **报告ID**: {report.report_id}")
        lines.append(f"- **生成时间**: {report.generated_at}")
        lines.append(f"- **整体状态**: {report.overall_status}\n")
        
        lines.append("## 核心组件状态\n")
        for component in report.components:
            status_icon = "✅" if component.status == "ready" else "❌"
            lines.append(f"- {status_icon} **{component.name}**: {component.status}")
        lines.append("")
        
        if report.metrics:
            lines.append("## 系统指标\n")
            for key, value in report.metrics.items():
                lines.append(f"- {key}: {value}")
            lines.append("")
        
        if report.errors:
            lines.append("## 错误\n")
            for error in report.errors:
                lines.append(f"- ❌ {error}")
            lines.append("")
        
        if report.warnings:
            lines.append("## 警告\n")
            for warning in report.warnings:
                lines.append(f"- ⚠️  {warning}")
            lines.append("")
        
        if report.recommendations:
            lines.append("## 建议\n")
            for rec in report.recommendations:
                lines.append(f"- 💡 {rec}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _render_json_report(self, report: SystemStatusReport) -> str:
        """渲染JSON格式报告"""
        report_dict = {
            "report_id": report.report_id,
            "generated_at": report.generated_at,
            "overall_status": report.overall_status,
            "components": [
                {
                    "name": c.name,
                    "description": c.description,
                    "status": c.status
                }
                for c in report.components
            ],
            "metrics": report.metrics,
            "errors": report.errors,
            "warnings": report.warnings,
            "recommendations": report.recommendations
        }
        return json.dumps(report_dict, indent=2, ensure_ascii=False)


class DocsCLI:
    """文档和报告命令行接口"""
    
    def __init__(self):
        self.doc_generator = SystemDocumentationGenerator()
        self.status_reporter = SystemStatusReporter()
    
    def run(self, args: List[str]) -> bool:
        """运行文档和报告命令"""
        if not args:
            return self._show_help()
        
        command = args[0].lower()
        
        if command == "help":
            return self._show_help()
        elif command == "generate":
            return self._generate_docs(args[1:] if len(args) > 1 else [])
        elif command == "status":
            return self._generate_status_report(args[1:] if len(args) > 1 else [])
        elif command == "list":
            return self._list_components()
        elif command == "test":
            return self._test_doc_system()
        else:
            print(f"❌ 未知命令: {command}")
            return False
    
    def _show_help(self) -> bool:
        """显示帮助"""
        help_text = """
📚 文档和报告命令:
  help                - 显示帮助信息
  generate [--format <format>] [--save <file>]
                      - 生成系统架构文档
                      - 格式: markdown, json
  status [--format <format>] [--save <file>]
                      - 生成系统状态报告
                      - 格式: text, markdown, json
  list                - 列出所有核心组件
  test                - 测试文档和报告系统
        """
        print(help_text)
        return True
    
    def _generate_docs(self, args: List[str]) -> bool:
        """生成文档"""
        format = "markdown"
        save_file = None
        
        for i, arg in enumerate(args):
            if arg == "--format" and i + 1 < len(args):
                format = args[i + 1].lower()
            elif arg == "--save" and i + 1 < len(args):
                save_file = args[i + 1]
        
        print(f"\n📚 生成系统架构文档 (格式: {format})")
        print("=" * 80)
        
        try:
            content = self.doc_generator.generate_architecture_document(format=format)
            
            if save_file:
                file_path = self.doc_generator.save_document(content, save_file)
                print(f"\n✅ 文档已保存到: {file_path}")
            else:
                print(f"\n{content}")
            
            return True
        except Exception as e:
            print(f"\n❌ 生成文档失败: {e}")
            return False
    
    def _generate_status_report(self, args: List[str]) -> bool:
        """生成状态报告"""
        format = "text"
        save_file = None
        
        for i, arg in enumerate(args):
            if arg == "--format" and i + 1 < len(args):
                format = args[i + 1].lower()
            elif arg == "--save" and i + 1 < len(args):
                save_file = args[i + 1]
        
        print(f"\n📊 生成系统状态报告 (格式: {format})")
        print("=" * 80)
        
        try:
            report = self.status_reporter.generate_system_report()
            content = self.status_reporter.render_report(report, format=format)
            
            if save_file:
                if not save_file.endswith(('.txt', '.md', '.json')):
                    if format == 'text':
                        save_file += '.txt'
                    elif format == 'markdown':
                        save_file += '.md'
                    elif format == 'json':
                        save_file += '.json'
                
                file_path = self.doc_generator.save_document(content, save_file)
                print(f"\n✅ 报告已保存到: {file_path}")
            else:
                print(f"\n{content}")
            
            return True
        except Exception as e:
            print(f"\n❌ 生成报告失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _list_components(self) -> bool:
        """列出核心组件"""
        print(f"\n📦 核心系统组件 (共 {len(self.doc_generator.system_components)} 个)")
        print("=" * 80)
        
        for i, component in enumerate(self.doc_generator.system_components, 1):
            print(f"\n{i}. {component.name}")
            print(f"   {component.description}")
            if component.dependencies:
                print(f"   依赖: {', '.join(component.dependencies)}")
        
        return True
    
    def _test_doc_system(self) -> bool:
        """测试文档和报告系统"""
        print("\n🧪 测试文档和报告系统")
        print("=" * 80)
        
        print("\n✅ 文档生成器创建成功")
        
        print("\n📚 测试架构文档生成:")
        try:
            markdown_doc = self.doc_generator.generate_architecture_document(format="markdown")
            print(f"   ✅ Markdown格式文档生成成功 ({len(markdown_doc)} 字符)")
            
            json_doc = self.doc_generator.generate_architecture_document(format="json")
            print(f"   ✅ JSON格式文档生成成功 ({len(json_doc)} 字符)")
        except Exception as e:
            print(f"   ❌ 文档生成失败: {e}")
            return False
        
        print("\n📊 测试状态报告生成:")
        try:
            report = self.status_reporter.generate_system_report()
            print(f"   ✅ 状态报告生成成功")
            print(f"   📦 组件数: {len(report.components)}")
            print(f"   💡 建议数: {len(report.recommendations)}")
        except Exception as e:
            print(f"   ❌ 报告生成失败: {e}")
            return False
        
        print("\n🎨 测试报告渲染:")
        try:
            text_report = self.status_reporter.render_report(report, format="text")
            print(f"   ✅ 文本格式报告渲染成功")
            
            markdown_report = self.status_reporter.render_report(report, format="markdown")
            print(f"   ✅ Markdown格式报告渲染成功")
            
            json_report = self.status_reporter.render_report(report, format="json")
            print(f"   ✅ JSON格式报告渲染成功")
        except Exception as e:
            print(f"   ❌ 报告渲染失败: {e}")
            return False
        
        print("\n" + "=" * 80)
        print("🎉 文档和报告系统测试完成！")
        print("=" * 80)
        
        return True


def create_doc_generator(output_dir: str = "docs") -> SystemDocumentationGenerator:
    """创建文档生成器工厂函数"""
    return SystemDocumentationGenerator(output_dir)


def create_status_reporter() -> SystemStatusReporter:
    """创建状态报告器工厂函数"""
    return SystemStatusReporter()
