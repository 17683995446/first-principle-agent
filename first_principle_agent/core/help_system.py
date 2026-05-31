#!/usr/bin/env python3
"""
系统帮助和快速入门向导 - 第69阶段
提供系统帮助信息、交互式教程和快速入门功能
"""

import sys
import os
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


@dataclass
class TutorialStep:
    """教程步骤"""
    step_number: int
    title: str
    description: str
    command: Optional[str] = None
    expected_output: Optional[str] = None
    tips: Optional[str] = None


@dataclass
class CommandHelp:
    """命令帮助信息"""
    command: str
    description: str
    usage: str
    examples: List[str] = field(default_factory=list)
    related_commands: List[str] = field(default_factory=list)


class HelpCategory(Enum):
    """帮助分类"""
    GETTING_STARTED = "getting_started"
    CORE_FUNCTIONS = "core_functions"
    ADVANCED = "advanced"
    TROUBLESHOOTING = "troubleshooting"


class HelpSystem:
    """帮助系统"""
    
    def __init__(self):
        self.command_helps: Dict[str, CommandHelp] = {}
        self.tutorials: Dict[str, List[TutorialStep]] = {}
        self._init_command_helps()
        self._init_tutorials()
    
    def _init_command_helps(self):
        """初始化命令帮助信息"""
        # 基本命令
        self.command_helps["help"] = CommandHelp(
            command="help",
            description="显示系统帮助信息",
            usage="python -m first_principle_agent help [command]",
            examples=[
                "python -m first_principle_agent help",
                "python -m first_principle_agent help run",
            ],
            related_commands=["demo", "status"]
        )
        
        self.command_helps["demo"] = CommandHelp(
            command="demo",
            description="运行系统演示，展示完整功能",
            usage="python -m first_principle_agent demo",
            examples=[
                "python -m first_principle_agent demo",
            ],
            related_commands=["help", "run"]
        )
        
        self.command_helps["status"] = CommandHelp(
            command="status",
            description="显示系统状态和健康信息",
            usage="python -m first_principle_agent status",
            examples=[
                "python -m first_principle_agent status",
            ],
            related_commands=["monitor", "health"]
        )
        
        # 任务相关
        self.command_helps["run"] = CommandHelp(
            command="run",
            description="运行任务规划系统，处理用户需求",
            usage="python -m first_principle_agent run <requirements>",
            examples=[
                'python -m first_principle_agent run "开发一个用户管理系统"',
                'python -m first_principle_agent run "创建一个数据备份系统"',
            ],
            related_commands=["demo", "tutorial"]
        )
        
        # 配置相关
        self.command_helps["config"] = CommandHelp(
            command="config",
            description="管理系统配置",
            usage="python -m first_principle_agent config <subcommand>",
            examples=[
                "python -m first_principle_agent config show",
                "python -m first_principle_agent config set key value",
                "python -m first_principle_agent config reset",
            ],
            related_commands=["settings"]
        )
        
        self.command_helps["settings"] = CommandHelp(
            command="settings",
            description="管理用户偏好和系统设置",
            usage="python -m first_principle_agent settings <subcommand>",
            examples=[
                "python -m first_principle_agent settings list",
                "python -m first_principle_agent settings get theme",
                "python -m first_principle_agent settings set theme dark",
                "python -m first_principle_agent settings export my_settings.json",
                "python -m first_principle_agent settings import my_settings.json",
            ],
            related_commands=["config"]
        )
        
        # 监控相关
        self.command_helps["monitor"] = CommandHelp(
            command="monitor",
            description="系统监控和健康检查",
            usage="python -m first_principle_agent monitor <subcommand>",
            examples=[
                "python -m first_principle_agent monitor status",
                "python -m first_principle_agent monitor health",
                "python -m first_principle_agent monitor metrics",
            ],
            related_commands=["status", "log"]
        )
        
        # 日志相关
        self.command_helps["log"] = CommandHelp(
            command="log",
            description="管理系统日志",
            usage="python -m first_principle_agent log <subcommand>",
            examples=[
                "python -m first_principle_agent log show",
                "python -m first_principle_agent log clear",
                "python -m first_principle_agent log test",
            ],
            related_commands=["monitor", "settings"]
        )
        
        # 错误处理
        self.command_helps["error"] = CommandHelp(
            command="error",
            description="错误处理和恢复管理",
            usage="python -m first_principle_agent error <subcommand>",
            examples=[
                "python -m first_principle_agent error test",
                "python -m first_principle_agent error list",
            ],
            related_commands=["log", "monitor"]
        )
        
        # 文档相关
        self.command_helps["docs"] = CommandHelp(
            command="docs",
            description="文档生成和状态报告",
            usage="python -m first_principle_agent docs <subcommand>",
            examples=[
                "python -m first_principle_agent docs generate",
                "python -m first_principle_agent docs status",
                "python -m first_principle_agent docs list",
            ],
            related_commands=["status", "help"]
        )
        
        # 性能测试
        self.command_helps["perf"] = CommandHelp(
            command="perf",
            description="系统性能基准测试和优化",
            usage="python -m first_principle_agent perf <subcommand>",
            examples=[
                "python -m first_principle_agent perf run",
                "python -m first_principle_agent perf analyze",
                "python -m first_principle_agent perf suggestions",
            ],
            related_commands=["monitor", "test"]
        )
        
        # 可视化
        self.command_helps["viz"] = CommandHelp(
            command="viz",
            description="系统可视化和仪表板",
            usage="python -m first_principle_agent viz <subcommand>",
            examples=[
                "python -m first_principle_agent viz dashboard",
                "python -m first_principle_agent viz demo",
            ],
            related_commands=["status", "monitor"]
        )
        
        # 备份恢复
        self.command_helps["backup"] = CommandHelp(
            command="backup",
            description="系统备份和恢复功能",
            usage="python -m first_principle_agent backup <subcommand>",
            examples=[
                "python -m first_principle_agent backup create",
                "python -m first_principle_agent backup list",
                "python -m first_principle_agent backup restore <id>",
            ],
            related_commands=["settings", "config"]
        )
    
    def _init_tutorials(self):
        """初始化教程"""
        # 快速入门教程
        self.tutorials["quickstart"] = [
            TutorialStep(
                step_number=1,
                title="欢迎使用",
                description="欢迎使用基于第一性原理的AI Agent任务规划系统！这是一个强大的工具，可以帮助您处理复杂任务。",
                tips="让我们从了解系统基本情况开始。"
            ),
            TutorialStep(
                step_number=2,
                title="查看系统状态",
                description="首先让我们查看系统当前的状态和健康情况。",
                command="python -m first_principle_agent status",
                tips="这会显示系统的当前阶段、核心组件状态等信息。"
            ),
            TutorialStep(
                step_number=3,
                title="运行系统演示",
                description="现在让我们运行一个完整的系统演示，看看系统是如何工作的。",
                command="python -m first_principle_agent demo",
                tips="演示会展示系统的主要功能和工作流程。"
            ),
            TutorialStep(
                step_number=4,
                title="运行简单任务",
                description="让我们尝试运行一个简单的任务规划。",
                command='python -m first_principle_agent run "创建一个简单的待办事项系统"',
                tips="您可以用引号包裹任何需求文本。"
            ),
            TutorialStep(
                step_number=5,
                title="探索更多功能",
                description="恭喜！您已完成快速入门。继续探索其他功能吧！",
                tips="尝试运行 help、config、monitor 等命令了解更多功能。"
            )
        ]
        
        # 配置教程
        self.tutorials["config"] = [
            TutorialStep(
                step_number=1,
                title="配置基础",
                description="学习如何管理系统配置。",
            ),
            TutorialStep(
                step_number=2,
                title="查看当前配置",
                description="查看当前系统配置。",
                command="python -m first_principle_agent config show",
            ),
            TutorialStep(
                step_number=3,
                title="修改设置",
                description="尝试修改一些用户设置。",
                command="python -m first_principle_agent settings list",
                tips="使用 settings set 命令修改设置。"
            ),
            TutorialStep(
                step_number=4,
                title="导出和导入",
                description="学习如何导出和导入您的设置。",
                command="python -m first_principle_agent settings export my_config.json",
                tips="这样您可以在不同设备间同步设置。"
            )
        ]
        
        # 完整功能教程
        self.tutorials["complete"] = [
            TutorialStep(
                step_number=1,
                title="系统概览",
                description="了解系统的整体架构和功能模块。",
            ),
            TutorialStep(
                step_number=2,
                title="健康检查",
                description="检查系统健康状态。",
                command="python -m first_principle_agent monitor health",
            ),
            TutorialStep(
                step_number=3,
                title="性能测试",
                description="运行系统性能基准测试。",
                command="python -m first_principle_agent perf test",
            ),
            TutorialStep(
                step_number=4,
                title="创建备份",
                description="创建系统备份以确保数据安全。",
                command="python -m first_principle_agent backup create",
            ),
            TutorialStep(
                step_number=5,
                title="可视化仪表板",
                description="查看系统的可视化仪表板。",
                command="python -m first_principle_agent viz dashboard",
            )
        ]
    
    def get_command_help(self, command: str) -> Optional[CommandHelp]:
        """获取命令帮助信息"""
        return self.command_helps.get(command.lower())
    
    def get_all_commands(self) -> List[str]:
        """获取所有命令列表"""
        return list(self.command_helps.keys())
    
    def get_tutorial(self, tutorial_name: str) -> Optional[List[TutorialStep]]:
        """获取教程"""
        return self.tutorials.get(tutorial_name.lower())
    
    def get_all_tutorials(self) -> List[str]:
        """获取所有教程列表"""
        return list(self.tutorials.keys())


class QuickStartWizard:
    """快速入门向导"""
    
    def __init__(self):
        self.help_system = HelpSystem()
    
    def show_welcome(self):
        """显示欢迎信息"""
        welcome = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    🎉 欢迎使用任务规划系统 🎉                                ║
╚═══════════════════════════════════════════════════════════════════════════════╝

📚 可用命令：
  help [command]    - 显示帮助信息
  demo              - 运行系统演示
  tutorial [name]   - 运行教程 (quickstart, config, complete)
  status            - 显示系统状态
  run <requirement> - 运行任务规划
  config            - 管理系统配置
  settings          - 管理用户设置
  monitor           - 系统监控
  log               - 日志管理
  error             - 错误处理
  docs              - 文档生成
  perf              - 性能测试
  viz               - 可视化
  backup            - 备份恢复

💡 开始使用：
  1. 运行 'demo' 查看系统演示
  2. 运行 'tutorial quickstart' 完成快速入门
  3. 运行 'status' 查看系统状态
  4. 运行 'help' 了解更多信息
        """
        print(welcome)
    
    def show_command_summary(self):
        """显示命令摘要"""
        summary = """
📋 命令分类：

🚀 基础命令：
  help      - 显示帮助
  demo      - 运行演示
  status    - 查看状态
  run       - 运行任务

⚙️  配置管理：
  config    - 系统配置
  settings  - 用户设置

🔍 监控分析：
  monitor   - 系统监控
  log       - 日志管理
  perf      - 性能测试

📄 文档备份：
  docs      - 文档生成
  backup    - 备份恢复

🎨 可视化：
  viz       - 系统可视化
        """
        print(summary)


class HelpCLI:
    """帮助命令行接口"""
    
    def __init__(self):
        self.help_system = HelpSystem()
        self.wizard = QuickStartWizard()
    
    def run(self, args: List[str]) -> bool:
        """运行帮助命令"""
        if not args:
            self.wizard.show_welcome()
            return True
        
        command = args[0].lower()
        
        if command == "help":
            if len(args) > 1:
                return self._show_command_help(args[1])
            else:
                self.wizard.show_welcome()
                return True
        elif command == "commands":
            return self._list_commands()
        elif command == "tutorial":
            if len(args) > 1:
                return self._run_tutorial(args[1])
            else:
                return self._list_tutorials()
        elif command == "welcome":
            self.wizard.show_welcome()
            return True
        elif command == "summary":
            self.wizard.show_command_summary()
            return True
        elif command == "test":
            return self._test_help_system()
        else:
            # 尝试作为命令帮助显示
            return self._show_command_help(command)
    
    def _show_command_help(self, command_name: str) -> bool:
        """显示命令帮助"""
        help_info = self.help_system.get_command_help(command_name)
        
        if not help_info:
            print(f"\n❌ 未找到命令 '{command_name}' 的帮助信息")
            print(f"可用命令: {', '.join(self.help_system.get_all_commands())}")
            return False
        
        print(f"\n📚 {help_info.command.upper()} 命令帮助")
        print("=" * 80)
        print(f"\n📝 描述: {help_info.description}")
        print(f"\n💡 用法: {help_info.usage}")
        
        if help_info.examples:
            print(f"\n📋 示例:")
            for example in help_info.examples:
                print(f"  {example}")
        
        if help_info.related_commands:
            print(f"\n🔗 相关命令: {', '.join(help_info.related_commands)}")
        
        print("\n" + "=" * 80)
        return True
    
    def _list_commands(self) -> bool:
        """列出所有命令"""
        commands = self.help_system.get_all_commands()
        
        print("\n📋 所有可用命令：")
        print("=" * 80)
        
        for cmd in sorted(commands):
            help_info = self.help_system.get_command_help(cmd)
            if help_info:
                print(f"  • {cmd:12} - {help_info.description}")
        
        print("\n" + "=" * 80)
        print(f"共 {len(commands)} 个命令")
        return True
    
    def _list_tutorials(self) -> bool:
        """列出所有教程"""
        tutorials = self.help_system.get_all_tutorials()
        
        print("\n📖 可用教程：")
        print("=" * 80)
        
        tutorial_desc = {
            "quickstart": "快速入门 - 了解系统基本使用",
            "config": "配置教程 - 学习配置管理",
            "complete": "完整功能 - 探索所有功能",
        }
        
        for tutorial in tutorials:
            desc = tutorial_desc.get(tutorial, "教程")
            print(f"  • {tutorial:12} - {desc}")
        
        print("\n" + "=" * 80)
        print("使用 'help tutorial <name>' 运行教程")
        return True
    
    def _run_tutorial(self, tutorial_name: str) -> bool:
        """运行教程"""
        steps = self.help_system.get_tutorial(tutorial_name)
        
        if not steps:
            print(f"\n❌ 未找到教程 '{tutorial_name}'")
            print("可用教程:", ", ".join(self.help_system.get_all_tutorials()))
            return False
        
        print(f"\n📖 教程: {tutorial_name.upper()}")
        print("=" * 80)
        
        for step in steps:
            print(f"\nStep {step.step_number}: {step.title}")
            print("-" * 40)
            print(f"\n{step.description}")
            
            if step.command:
                print(f"\n💻 尝试运行:")
                print(f"   {step.command}")
            
            if step.tips:
                print(f"\n💡 提示: {step.tips}")
        
        print("\n" + "=" * 80)
        print("🎉 教程完成！继续探索其他功能吧！")
        return True
    
    def _test_help_system(self) -> bool:
        """测试帮助系统"""
        print("\n🧪 测试帮助系统...")
        print("=" * 80)
        
        try:
            # 测试帮助系统初始化
            print("\n✅ HelpSystem 创建成功")
            
            # 测试获取命令帮助
            print("\n📚 测试获取命令帮助...")
            help_info = self.help_system.get_command_help("run")
            if help_info:
                print(f"✅ 获取命令帮助成功: {help_info.command}")
                print(f"   描述: {help_info.description}")
            else:
                print("❌ 获取命令帮助失败")
                return False
            
            # 测试获取所有命令
            print("\n📋 测试获取所有命令...")
            all_commands = self.help_system.get_all_commands()
            print(f"✅ 获取 {len(all_commands)} 个命令")
            
            # 测试获取教程
            print("\n📖 测试获取教程...")
            tutorial = self.help_system.get_tutorial("quickstart")
            if tutorial:
                print(f"✅ 获取教程成功: {len(tutorial)} 个步骤")
            else:
                print("❌ 获取教程失败")
                return False
            
            # 测试获取所有教程
            print("\n📖 测试获取所有教程...")
            all_tutorials = self.help_system.get_all_tutorials()
            print(f"✅ 获取 {len(all_tutorials)} 个教程")
            
            print("\n" + "=" * 80)
            print("🎉 帮助系统测试完成！")
            print("=" * 80)
            
            return True
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False


def create_help_system() -> HelpSystem:
    """创建帮助系统工厂函数"""
    return HelpSystem()


def create_help_cli() -> HelpCLI:
    """创建帮助CLI工厂函数"""
    return HelpCLI()


def create_wizard() -> QuickStartWizard:
    """创建快速入门向导工厂函数"""
    return QuickStartWizard()

