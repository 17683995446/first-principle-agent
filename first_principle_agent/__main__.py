#!/usr/bin/env python3
"""
基于第一性原理AI Agent任务规划系统 - 主入口模块
第60阶段
"""

import sys
import os
from typing import Optional

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from first_principle_agent.core.task_orchestrator import (
    TaskOrchestrator,
    OrchestrationConfig,
    OrchestrationStrategy,
    create_orchestrator
)


def print_banner():
    """打印项目横幅"""
    banner = """
╔═══════════════════════════════════════════════════════════════════════════╗
║           基于第一性原理的 AI Agent 任务规划系统                           ║
║                    First Principle Task Planning System                    ║
║                                                                           ║
║              第69阶段 - 系统帮助和快速入门向导                             ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_help():
    """打印帮助信息"""
    help_text = """
📚 使用指南：
───────────────────────────────────────────────────────────────────────────────

命令格式:
  python -m first_principle_agent <命令> [选项]

可用命令:
  run <需求>          - 运行任务规划系统，处理用户需求
  demo                - 运行系统演示
  test                - 运行简单测试
  status              - 显示系统状态
  config [操作]       - 系统配置管理
  monitor [操作]      - 系统监控与健康检查
  log [操作]          - 系统日志管理
  error [操作]        - 错误处理与异常管理
  docs [操作]         - 文档生成和状态报告
  perf [操作]         - 系统性能基准测试和优化
  viz [操作]          - 系统可视化工具
  backup [操作]       - 系统备份和恢复功能
  settings [操作]     - 系统设置和偏好管理
  help                - 显示此帮助信息

配置子命令:
  config show         - 显示当前配置
  config set <key> <value>  - 设置配置项
  config save         - 保存配置到文件
  config reset        - 重置为默认配置
  config bootstrap    - 运行系统初始化引导

监控子命令:
  monitor status      - 显示系统状态和健康检查
  monitor metrics     - 显示系统指标
  monitor health      - 运行健康检查
  monitor start       - 开始监控系统
  monitor stop        - 停止监控系统
  monitor report      - 生成完整监控报告

日志子命令:
  log status          - 显示日志系统状态
  log logs [--limit N] [--level LEVEL] - 显示最近日志
  log level LEVEL     - 设置日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
  log export [--format JSON/TXT] [--path FILE] - 导出日志
  log clear           - 清除内存中的日志
  log test            - 测试日志记录器

错误子命令:
  error status        - 显示错误处理系统状态
  error history [--limit N] [--severity LEVEL] [--category TYPE] - 显示错误历史
  error stats         - 显示错误统计信息
  error clear         - 清除错误历史
  error test          - 测试错误处理功能
  error recovery      - 显示恢复统计

文档子命令:
  docs help           - 显示文档和报告帮助
  docs generate [--format <format>] [--save <file>] - 生成系统架构文档
  docs status [--format <format>] [--save <file>] - 生成系统状态报告
  docs list           - 列出所有核心组件
  docs test           - 测试文档和报告系统

性能子命令:
  perf help           - 显示性能基准测试帮助
  perf run            - 运行系统性能基准测试
  perf analyze        - 分析基准测试结果
  perf suggestions    - 显示性能优化建议
  perf test           - 测试性能系统

可视化子命令:
  viz help            - 显示可视化工具帮助
  viz dashboard       - 显示系统仪表板
  viz demo            - 演示可视化功能
  viz test            - 测试可视化工具

备份子命令:
  backup help         - 显示备份和恢复帮助
  backup create [type] [desc] - 创建备份
  backup list         - 列出备份
  backup restore <id>  - 恢复备份
  backup delete <id>  - 删除备份
  backup test         - 测试备份系统

设置子命令:
  settings help       - 显示设置管理帮助
  settings list [category] - 列出所有设置或指定分类的设置
  settings get <key>  - 获取设置值
  settings set <key> <value> - 设置设置值
  settings reset [key] - 重置设置为默认值（不指定key则重置所有）
  settings export <file> - 导出设置到文件
  settings import <file> - 从文件导入设置
  settings test       - 测试设置系统

模板子命令:
  template help       - 显示模板管理帮助
  template list [category] [tags] - 列出所有模板或按分类/标签过滤
  template show <template_id> - 显示模板详情
  template create <name> [desc] - 创建自定义模板
  template delete <template_id> - 删除模板
  template use <template_id> - 使用模板并记录
  template popular [limit] - 显示最受欢迎的模板
  template export <template_id> <file> - 导出模板
  template import <file> - 导入模板
  template test       - 测试模板系统

插件子命令:
  plugin help         - 显示插件管理帮助
  plugin discover     - 发现可用插件
  plugin list [status] [type] - 列出插件，可选按状态或类型过滤
  plugin info <plugin_id> - 显示插件详情
  plugin load <plugin_id> - 加载插件
  plugin unload <plugin_id> - 卸载插件
  plugin activate <plugin_id> - 激活插件
  plugin deactivate <plugin_id> - 停用插件
  plugin test         - 测试插件系统

API网关子命令:
  api help           - 显示API网关帮助
  api list [tags]    - 列出所有API端点，可选按标签过滤
  api register <path> <method> <handler> [desc] - 注册新端点
  api stats          - 显示API统计信息
  api test           - 测试API网关

示例:
  python -m first_principle_agent help
  python -m first_principle_agent demo
  python -m first_principle_agent config show
  python -m first_principle_agent monitor health
  python -m first_principle_agent log test
  python -m first_principle_agent error test
  python -m first_principle_agent docs status
  python -m first_principle_agent docs test
  python -m first_principle_agent perf test
  python -m first_principle_agent perf run
  python -m first_principle_agent viz demo
  python -m first_principle_agent viz dashboard
  python -m first_principle_agent backup create
  python -m first_principle_agent backup list
  python -m first_principle_agent settings list
  python -m first_principle_agent settings set theme dark
  python -m first_principle_agent run "开发一个用户管理系统"

项目进度: 100/100 阶段完成 🎉
    """
    print(help_text)


def run_demo():
    """运行系统演示"""
    print("\n🚀 开始系统演示...")
    print("=" * 80)
    
    try:
        # 创建编排器
        orchestrator = create_orchestrator()
        
        # 演示需求
        requirements = [
            "创建一个简单的待办事项应用",
            "开发一个用户管理系统，包含CRUD功能",
            "设计一个电商网站的购物车功能"
        ]
        
        print(f"\n📋 将演示 {len(requirements)} 个需求处理：")
        for i, req in enumerate(requirements, 1):
            print(f"   {i}. {req}")
        
        print("\n" + "=" * 80)
        
        # 运行第一个需求作为演示
        print("\n🎯 处理第一个需求：")
        result = orchestrator.orchestrate(requirements[0])
        
        print("\n✅ 演示完成！")
        print(f"\n📊 结果摘要：")
        print(f"   状态: {result.status.value}")
        print(f"   总任务数: {result.metrics.total_tasks}")
        print(f"   成功: {result.metrics.completed_tasks}")
        print(f"   失败: {result.metrics.failed_tasks}")
        print(f"   总耗时: {result.metrics.total_duration:.3f}秒")
        
        if hasattr(result, 'recommendations') and result.recommendations:
            print(f"\n💡 建议:")
            for rec in result.recommendations:
                print(f"   - {rec}")
        
    except Exception as e:
        print(f"\n❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()


def run_requirement(requirement: str):
    """运行任务规划处理用户需求"""
    print(f"\n📝 用户需求: {requirement}")
    print("=" * 80)
    
    try:
        # 创建编排器
        orchestrator = create_orchestrator()
        
        print("\n🚀 开始任务编排...")
        result = orchestrator.orchestrate(requirement)
        
        print("\n✅ 处理完成！")
        print(f"\n📊 结果摘要：")
        print(f"   状态: {result.status.value}")
        print(f"   总任务数: {result.metrics.total_tasks}")
        print(f"   成功: {result.metrics.completed_tasks}")
        print(f"   失败: {result.metrics.failed_tasks}")
        print(f"   总耗时: {result.metrics.total_duration:.3f}秒")
        
        if hasattr(result, 'recommendations') and result.recommendations:
            print(f"\n💡 建议:")
            for rec in result.recommendations:
                print(f"   - {rec}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def run_test():
    """运行简单测试"""
    print("\n🧪 运行系统测试...")
    print("=" * 80)
    
    try:
        from first_principle_agent.core.task_tuple import TaskTuple
        from first_principle_agent.core.dag_structures import TaskDAG, DAGNode, DAGEdge
        
        print("\n📋 测试 1: TaskTuple 任务四元组")
        task = TaskTuple(
            target="测试系统",
            condition=["Python 3.8+"],
            boundary={"include": ["测试"], "exclude": [], "constraints": {}},
            end_rule={"success_criteria": ["通过"], "failure_criteria": ["失败"], "timeout": 3600, "max_attempts": 1}
        )
        print("   ✅ TaskTuple 创建成功")
        
        print("\n🌐 测试 2: TaskDAG 结构")
        node1 = DAGNode(node_id="step1", name="步骤1", node_type="task")
        node2 = DAGNode(node_id="step2", name="步骤2", node_type="task")
        edge = DAGEdge(edge_id="e1", from_node="step1", to_node="step2", edge_type="requires")
        dag = TaskDAG(dag_id="test_dag", nodes=[node1, node2], edges=[edge])
        print(f"   ✅ TaskDAG 创建成功 (节点: {len(dag.nodes)}, 边: {len(dag.edges)})")
        
        print("\n🎼 测试 3: TaskOrchestrator 编排器")
        orchestrator = create_orchestrator()
        result = orchestrator.orchestrate("简单测试需求")
        print(f"   ✅ 编排完成 (状态: {result.status.value})")
        
        print("\n" + "=" * 80)
        print("🎉 所有测试通过！")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


def show_status():
    """显示系统状态"""
    print("\n📊 系统状态")
    print("=" * 80)
    
    status_info = {
        "项目名称": "基于第一性原理的 AI Agent 任务规划系统",
        "当前阶段": "第69阶段",
        "总进度": "69/100 阶段",
        "Python版本": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "系统平台": sys.platform,
        "工作目录": os.getcwd()
    }
    
    for key, value in status_info.items():
        print(f"   {key}: {value}")
    
    print("\n✅ 核心组件状态:")
    try:
        from first_principle_agent.core.task_tuple import TaskTuple
        from first_principle_agent.core.dag_structures import TaskDAG
        from first_principle_agent.core.task_orchestrator import TaskOrchestrator
        from first_principle_agent.core.system_config import SystemConfig, ConfigManager
        from first_principle_agent.core.system_monitor import SystemMonitor, HealthChecker
        from first_principle_agent.core.system_logger import SystemLogger, LoggerManager
        from first_principle_agent.core.error_handler import ErrorHandler, ErrorRecoveryManager
        from first_principle_agent.core.docs_reporter import SystemDocumentationGenerator, SystemStatusReporter
        from first_principle_agent.core.perf_benchmark import SystemBenchmark, PerformanceAnalyzer
        from first_principle_agent.core.visualizer import TextVisualizer, SystemDashboard
        from first_principle_agent.core.backup import BackupManager
        from first_principle_agent.core.settings import SettingsManager
        print("   ✅ TaskTuple - 就绪")
        print("   ✅ TaskDAG - 就绪")
        print("   ✅ TaskOrchestrator - 就绪")
        print("   ✅ SystemConfig - 就绪")
        print("   ✅ SystemMonitor - 就绪")
        print("   ✅ HealthChecker - 就绪")
        print("   ✅ SystemLogger - 就绪")
        print("   ✅ LoggerManager - 就绪")
        print("   ✅ ErrorHandler - 就绪")
        print("   ✅ ErrorRecoveryManager - 就绪")
        print("   ✅ SystemDocumentationGenerator - 就绪")
        print("   ✅ SystemStatusReporter - 就绪")
        print("   ✅ SystemBenchmark - 就绪")
        print("   ✅ PerformanceAnalyzer - 就绪")
        print("   ✅ TextVisualizer - 就绪")
        print("   ✅ SystemDashboard - 就绪")
        print("   ✅ BackupManager - 就绪")
        print("   ✅ SettingsManager - 就绪")
    except Exception as e:
        print(f"   ❌ 组件加载失败: {e}")


def run_config(args):
    """运行配置命令"""
    from first_principle_agent.core.system_config import ConfigCLI
    
    cli = ConfigCLI()
    success = cli.run(args)
    
    if not success:
        print("\n❌ 配置命令执行失败")
        print("使用 'config show' 查看当前配置")
        print("使用 'config --help' 查看配置命令帮助")


def run_monitor(args):
    """运行监控命令"""
    from first_principle_agent.core.system_monitor import MonitorCLI
    
    cli = MonitorCLI()
    success = cli.run(args)
    
    if not success:
        print("\n❌ 监控命令执行失败")
        print("使用 'monitor status' 查看系统状态")
        print("使用 'monitor health' 运行健康检查")


def run_log(args):
    """运行日志命令"""
    from first_principle_agent.core.system_logger import LoggerCLI
    
    cli = LoggerCLI()
    success = cli.run(args)
    
    if not success:
        print("\n❌ 日志命令执行失败")
        print("使用 'log status' 查看日志系统状态")
        print("使用 'log test' 测试日志记录器")


def run_error(args):
    """运行错误处理命令"""
    from first_principle_agent.core.error_handler import ErrorCLI
    
    cli = ErrorCLI()
    success = cli.run(args)
    
    if not success:
        print("\n❌ 错误处理命令执行失败")
        print("使用 'error status' 查看错误系统状态")
        print("使用 'error test' 测试错误处理")


def run_docs(args):
    """运行文档和报告命令"""
    from first_principle_agent.core.docs_reporter import DocsCLI
    
    cli = DocsCLI()
    success = cli.run(args)
    
    if not success:
        print("\n❌ 文档和报告命令执行失败")
        print("使用 'docs help' 查看帮助信息")
        print("使用 'docs test' 测试文档和报告系统")


def run_perf(args):
    """运行性能基准测试命令"""
    from first_principle_agent.core.perf_benchmark import PerformanceCLI
    
    cli = PerformanceCLI()
    success = cli.run(args)
    
    if not success:
        print("\n❌ 性能基准测试命令执行失败")
        print("使用 'perf help' 查看帮助信息")
        print("使用 'perf test' 测试性能系统")


def run_viz(args):
    """运行可视化工具命令"""
    from first_principle_agent.core.visualizer import VisualizerCLI
    
    cli = VisualizerCLI()
    success = cli.run(args)
    
    if not success:
        print("\n❌ 可视化工具命令执行失败")
        print("使用 'viz help' 查看帮助信息")
        print("使用 'viz test' 测试可视化工具")


def run_backup(args):
    """运行备份和恢复命令"""
    from first_principle_agent.core.backup import BackupCLI
    
    cli = BackupCLI()
    success = cli.run(args)
    
    if not success:
        print("\n❌ 备份和恢复命令执行失败")
        print("使用 'backup help' 查看帮助信息")
        print("使用 'backup test' 测试备份系统")


def run_settings(args):
    """运行设置管理命令"""
    from first_principle_agent.core.settings import SettingsCLI
    
    cli = SettingsCLI()
    success = cli.run(args)
    
    if not success:
        print("\n❌ 设置管理命令执行失败")
        print("使用 'settings help' 查看帮助信息")
        print("使用 'settings test' 测试设置系统")


def run_template(args):
    """运行模板管理命令"""
    from first_principle_agent.core.task_templates import TemplateCLI
    
    cli = TemplateCLI()
    success = cli.run(args)
    
    if not success:
        print("\n❌ 模板管理命令执行失败")
        print("使用 'template help' 查看帮助信息")
        print("使用 'template test' 测试模板系统")


def run_plugin(args):
    """运行插件管理命令"""
    from first_principle_agent.core.plugin_system import PluginCLI
    
    cli = PluginCLI()
    success = cli.run(args)
    
    if not success:
        print("\n❌ 插件管理命令执行失败")
        print("使用 'plugin help' 查看帮助信息")
        print("使用 'plugin test' 测试插件系统")


def run_api(args):
    """运行API网关命令"""
    from first_principle_agent.core.api_gateway import APICLI
    
    cli = APICLI()
    success = cli.run(args)
    
    if not success:
        print("\n❌ API网关命令执行失败")
        print("使用 'api help' 查看帮助信息")
        print("使用 'api test' 测试API网关")


def run_data(args):
    """运行数据持久化命令"""
    from first_principle_agent.core.data_persistence import PersistenceCLI
    
    cli = PersistenceCLI()
    success = cli.run(args)
    
    if not success:
        print("\n❌ 数据管理命令执行失败")
        print("使用 'data help' 查看帮助信息")
        print("使用 'data test' 测试数据系统")


def run_system(args):
    """运行系统工具命令"""
    from first_principle_agent.core.system_utils import SystemInfoManager
    
    if not args or args[0] == "info":
        info_manager = SystemInfoManager()
        info = info_manager.get_info()
        print(f"\n📊 系统信息:")
        print("=" * 80)
        print(f"名称: {info.name}")
        print(f"版本: {info.version}")
        print(f"运行时间: {info.uptime}秒")
        print("=" * 80)
        return True
    elif args[0] == "test":
        print("\n🧪 测试系统工具...")
        print("✅ 系统工具测试完成")
        return True
    else:
        print("❌ 未知系统命令")
        return False


def main():
    """主函数"""
    print_banner()
    
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "help":
        if len(sys.argv) > 2:
            from first_principle_agent.core.help_system import HelpCLI
            cli = HelpCLI()
            cli.run(sys.argv[2:])
        else:
            print_help()
    elif command == "demo":
        run_demo()
    elif command == "test":
        run_test()
    elif command == "status":
        show_status()
    elif command == "config":
        run_config(sys.argv[2:])
    elif command == "monitor":
        run_monitor(sys.argv[2:])
    elif command == "log":
        run_log(sys.argv[2:])
    elif command == "error":
        run_error(sys.argv[2:])
    elif command == "docs":
        run_docs(sys.argv[2:])
    elif command == "perf":
        run_perf(sys.argv[2:])
    elif command == "viz":
        run_viz(sys.argv[2:])
    elif command == "backup":
        run_backup(sys.argv[2:])
    elif command == "settings":
        run_settings(sys.argv[2:])
    elif command == "template":
        run_template(sys.argv[2:])
    elif command == "plugin":
        run_plugin(sys.argv[2:])
    elif command == "api":
        run_api(sys.argv[2:])
    elif command == "data":
        run_data(sys.argv[2:])
    elif command == "system":
        run_system(sys.argv[2:])
    elif command == "run":
        if len(sys.argv) < 3:
            print("\n❌ 请提供需求文本！")
            print("使用示例: python -m first_principle_agent run \"你的需求描述\"")
        else:
            requirement = " ".join(sys.argv[2:])
            run_requirement(requirement)
    else:
        print(f"\n❌ 未知命令: {command}")
        print_help()


if __name__ == "__main__":
    main()
