#!/usr/bin/env python3
"""
系统任务模板库 - 第70阶段
提供常用任务模板库，支持快速创建和管理任务模板
"""

import json
import os
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from datetime import datetime


class TemplateCategory(Enum):
    """模板分类"""
    WEB_DEVELOPMENT = "web_development"
    DATA_PROCESSING = "data_processing"
    SYSTEM_ADMIN = "system_admin"
    MACHINE_LEARNING = "machine_learning"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    DEVOPS = "devops"
    CUSTOM = "custom"


@dataclass
class TaskTemplate:
    """任务模板"""
    template_id: str
    name: str
    description: str
    category: TemplateCategory
    tags: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    steps: List[str] = field(default_factory=list)
    estimated_time: str = ""
    difficulty: str = "medium"
    version: str = "1.0"
    created_at: str = ""
    updated_at: str = ""
    is_preset: bool = False


@dataclass
class TemplateUsage:
    """模板使用记录"""
    usage_id: str
    template_id: str
    used_at: str
    success: bool
    notes: str = ""


class TaskTemplateLibrary:
    """任务模板库"""
    
    def __init__(self, library_dir: str = "task_templates"):
        self.library_dir = Path(library_dir)
        self.library_dir.mkdir(exist_ok=True)
        self.templates: Dict[str, TaskTemplate] = {}
        self.usage_history: List[TemplateUsage] = []
        self._init_preset_templates()
        self._load_templates()
        self._load_usage_history()
    
    def _init_preset_templates(self):
        """初始化预设模板"""
        preset_templates = [
            TaskTemplate(
                template_id="web_app_from_scratch",
                name="从零构建Web应用",
                description="从零开始构建一个完整的Web应用程序",
                category=TemplateCategory.WEB_DEVELOPMENT,
                tags=["web", "fullstack", "beginner"],
                requirements=[
                    "选择技术栈（前端/后端框架）",
                    "确定应用功能需求",
                    "设计数据库结构"
                ],
                steps=[
                    "创建项目结构",
                    "设计数据库模型",
                    "实现后端API",
                    "开发前端界面",
                    "集成前后端",
                    "编写测试",
                    "部署上线"
                ],
                estimated_time="3-7天",
                difficulty="medium",
                is_preset=True
            ),
            TaskTemplate(
                template_id="data_cleaning_pipeline",
                name="数据清洗流水线",
                description="构建完整的数据清洗和预处理流水线",
                category=TemplateCategory.DATA_PROCESSING,
                tags=["data", "cleaning", "pipeline"],
                requirements=[
                    "确定数据源",
                    "定义数据质量标准",
                    "选择处理工具"
                ],
                steps=[
                    "数据采集",
                    "数据探索分析",
                    "缺失值处理",
                    "异常值检测",
                    "数据类型转换",
                    "数据标准化",
                    "数据验证"
                ],
                estimated_time="2-3天",
                difficulty="medium",
                is_preset=True
            ),
            TaskTemplate(
                template_id="system_backup_strategy",
                name="系统备份策略",
                description="设计和实施完整的系统备份策略",
                category=TemplateCategory.SYSTEM_ADMIN,
                tags=["backup", "system", "security"],
                requirements=[
                    "确定备份内容",
                    "选择备份工具",
                    "规划备份存储"
                ],
                steps=[
                    "分析备份需求",
                    "选择备份方案",
                    "配置备份工具",
                    "设置备份周期",
                    "测试备份恢复",
                    "监控备份状态"
                ],
                estimated_time="1-2天",
                difficulty="easy",
                is_preset=True
            ),
            TaskTemplate(
                template_id="ml_model_training",
                name="机器学习模型训练",
                description="完整的机器学习模型训练流程",
                category=TemplateCategory.MACHINE_LEARNING,
                tags=["ml", "training", "model"],
                requirements=[
                    "准备训练数据",
                    "选择模型架构",
                    "确定评估指标"
                ],
                steps=[
                    "数据准备",
                    "数据预处理",
                    "数据集划分",
                    "模型选择",
                    "模型训练",
                    "模型评估",
                    "模型优化",
                    "模型部署"
                ],
                estimated_time="5-10天",
                difficulty="hard",
                is_preset=True
            ),
            TaskTemplate(
                template_id="api_documentation",
                name="API文档编写",
                description="完整的API文档编写和发布流程",
                category=TemplateCategory.DOCUMENTATION,
                tags=["docs", "api", "documentation"],
                requirements=[
                    "API接口列表",
                    "文档风格指南",
                    "示例数据"
                ],
                steps=[
                    "收集API信息",
                    "编写接口文档",
                    "添加使用示例",
                    "编写错误说明",
                    "生成文档站点",
                    "发布和维护"
                ],
                estimated_time="1-3天",
                difficulty="easy",
                is_preset=True
            ),
            TaskTemplate(
                template_id="test_suite_build",
                name="测试套件构建",
                description="构建完整的测试套件",
                category=TemplateCategory.TESTING,
                tags=["test", "testing", "quality"],
                requirements=[
                    "确定测试范围",
                    "选择测试框架",
                    "制定测试策略"
                ],
                steps=[
                    "测试规划",
                    "单元测试开发",
                    "集成测试开发",
                    "端到端测试",
                    "性能测试",
                    "CI集成",
                    "测试报告生成"
                ],
                estimated_time="3-5天",
                difficulty="medium",
                is_preset=True
            ),
            TaskTemplate(
                template_id="cicd_pipeline",
                name="CI/CD流水线搭建",
                description="搭建持续集成和持续部署流水线",
                category=TemplateCategory.DEVOPS,
                tags=["ci", "cd", "devops", "automation"],
                requirements=[
                    "代码仓库",
                    "部署环境",
                    "CI工具选择"
                ],
                steps=[
                    "环境准备",
                    "配置CI流程",
                    "配置CD流程",
                    "编写部署脚本",
                    "设置监控告警",
                    "集成测试"
                ],
                estimated_time="2-4天",
                difficulty="hard",
                is_preset=True
            )
        ]
        
        for template in preset_templates:
            template.created_at = datetime.now().isoformat()
            template.updated_at = datetime.now().isoformat()
            self.templates[template.template_id] = template
    
    def _load_templates(self):
        """加载模板"""
        templates_file = self.library_dir / "templates.json"
        if templates_file.exists():
            try:
                with open(templates_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for template_data in data:
                        category = TemplateCategory(template_data.get('category', 'custom'))
                        template = TaskTemplate(
                            template_id=template_data['template_id'],
                            name=template_data['name'],
                            description=template_data['description'],
                            category=category,
                            tags=template_data.get('tags', []),
                            requirements=template_data.get('requirements', []),
                            steps=template_data.get('steps', []),
                            estimated_time=template_data.get('estimated_time', ''),
                            difficulty=template_data.get('difficulty', 'medium'),
                            version=template_data.get('version', '1.0'),
                            created_at=template_data.get('created_at', ''),
                            updated_at=template_data.get('updated_at', ''),
                            is_preset=template_data.get('is_preset', False)
                        )
                        self.templates[template.template_id] = template
            except Exception as e:
                print(f"⚠️ 加载模板时出错: {e}")
    
    def _save_templates(self):
        """保存模板"""
        templates_file = self.library_dir / "templates.json"
        try:
            data = []
            for template in self.templates.values():
                data.append({
                    'template_id': template.template_id,
                    'name': template.name,
                    'description': template.description,
                    'category': template.category.value,
                    'tags': template.tags,
                    'requirements': template.requirements,
                    'steps': template.steps,
                    'estimated_time': template.estimated_time,
                    'difficulty': template.difficulty,
                    'version': template.version,
                    'created_at': template.created_at,
                    'updated_at': template.updated_at,
                    'is_preset': template.is_preset
                })
            
            with open(templates_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ 保存模板时出错: {e}")
    
    def _load_usage_history(self):
        """加载使用历史"""
        history_file = self.library_dir / "usage_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for usage_data in data:
                        usage = TemplateUsage(
                            usage_id=usage_data['usage_id'],
                            template_id=usage_data['template_id'],
                            used_at=usage_data['used_at'],
                            success=usage_data['success'],
                            notes=usage_data.get('notes', '')
                        )
                        self.usage_history.append(usage)
            except Exception as e:
                print(f"⚠️ 加载使用历史时出错: {e}")
    
    def _save_usage_history(self):
        """保存使用历史"""
        history_file = self.library_dir / "usage_history.json"
        try:
            data = []
            for usage in self.usage_history:
                data.append({
                    'usage_id': usage.usage_id,
                    'template_id': usage.template_id,
                    'used_at': usage.used_at,
                    'success': usage.success,
                    'notes': usage.notes
                })
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ 保存使用历史时出错: {e}")
    
    def get_template(self, template_id: str) -> Optional[TaskTemplate]:
        """获取模板"""
        return self.templates.get(template_id)
    
    def list_templates(self, category: Optional[TemplateCategory] = None, 
                      tags: Optional[List[str]] = None) -> List[TaskTemplate]:
        """列出模板"""
        templates = list(self.templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
        
        if tags:
            templates = [t for t in templates if any(tag in t.tags for tag in tags)]
        
        return templates
    
    def create_template(self, name: str, description: str, 
                       category: TemplateCategory = TemplateCategory.CUSTOM,
                       tags: Optional[List[str]] = None,
                       requirements: Optional[List[str]] = None,
                       steps: Optional[List[str]] = None,
                       estimated_time: str = "",
                       difficulty: str = "medium") -> Optional[TaskTemplate]:
        """创建自定义模板"""
        template_id = f"custom_{name.lower().replace(' ', '_')}_{int(datetime.now().timestamp())}"
        
        template = TaskTemplate(
            template_id=template_id,
            name=name,
            description=description,
            category=category,
            tags=tags or [],
            requirements=requirements or [],
            steps=steps or [],
            estimated_time=estimated_time,
            difficulty=difficulty,
            version="1.0",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            is_preset=False
        )
        
        self.templates[template_id] = template
        self._save_templates()
        
        print(f"✅ 模板创建成功: {name}")
        return template
    
    def update_template(self, template_id: str, **kwargs) -> bool:
        """更新模板"""
        if template_id not in self.templates:
            print(f"❌ 模板不存在: {template_id}")
            return False
        
        template = self.templates[template_id]
        
        if template.is_preset:
            print("⚠️ 预设模板不能修改")
            return False
        
        for key, value in kwargs.items():
            if hasattr(template, key):
                setattr(template, key, value)
        
        template.updated_at = datetime.now().isoformat()
        self._save_templates()
        
        print(f"✅ 模板更新成功: {template.name}")
        return True
    
    def delete_template(self, template_id: str) -> bool:
        """删除模板"""
        if template_id not in self.templates:
            print(f"❌ 模板不存在: {template_id}")
            return False
        
        template = self.templates[template_id]
        if template.is_preset:
            print("⚠️ 预设模板不能删除")
            return False
        
        del self.templates[template_id]
        self._save_templates()
        
        print(f"✅ 模板删除成功: {template.name}")
        return True
    
    def use_template(self, template_id: str, success: bool = True, notes: str = "") -> bool:
        """使用模板"""
        if template_id not in self.templates:
            print(f"❌ 模板不存在: {template_id}")
            return False
        
        usage = TemplateUsage(
            usage_id=f"usage_{int(datetime.now().timestamp())}",
            template_id=template_id,
            used_at=datetime.now().isoformat(),
            success=success,
            notes=notes
        )
        
        self.usage_history.append(usage)
        self._save_usage_history()
        
        print(f"✅ 模板使用记录已保存: {self.templates[template_id].name}")
        return True
    
    def get_popular_templates(self, limit: int = 5) -> List[TaskTemplate]:
        """获取最受欢迎的模板"""
        usage_count = {}
        for usage in self.usage_history:
            if usage.template_id not in usage_count:
                usage_count[usage.template_id] = 0
            usage_count[usage.template_id] += 1
        
        sorted_templates = sorted(
            self.templates.values(),
            key=lambda t: usage_count.get(t.template_id, 0),
            reverse=True
        )
        
        return sorted_templates[:limit]
    
    def export_template(self, template_id: str, output_file: str) -> bool:
        """导出模板"""
        template = self.get_template(template_id)
        if not template:
            print(f"❌ 模板不存在: {template_id}")
            return False
        
        try:
            data = {
                'template_id': template.template_id,
                'name': template.name,
                'description': template.description,
                'category': template.category.value,
                'tags': template.tags,
                'requirements': template.requirements,
                'steps': template.steps,
                'estimated_time': template.estimated_time,
                'difficulty': template.difficulty,
                'version': template.version,
                'created_at': template.created_at,
                'updated_at': template.updated_at,
                'is_preset': template.is_preset
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 模板导出成功: {output_file}")
            return True
        except Exception as e:
            print(f"❌ 导出模板失败: {e}")
            return False
    
    def import_template(self, input_file: str) -> Optional[TaskTemplate]:
        """导入模板"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            category = TemplateCategory(data.get('category', 'custom'))
            template = TaskTemplate(
                template_id=data.get('template_id', f"imported_{int(datetime.now().timestamp())}"),
                name=data['name'],
                description=data['description'],
                category=category,
                tags=data.get('tags', []),
                requirements=data.get('requirements', []),
                steps=data.get('steps', []),
                estimated_time=data.get('estimated_time', ''),
                difficulty=data.get('difficulty', 'medium'),
                version=data.get('version', '1.0'),
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                is_preset=False
            )
            
            self.templates[template.template_id] = template
            self._save_templates()
            
            print(f"✅ 模板导入成功: {template.name}")
            return template
        except Exception as e:
            print(f"❌ 导入模板失败: {e}")
            import traceback
            traceback.print_exc()
            return None


class TemplateCLI:
    """模板管理命令行接口"""
    
    def __init__(self):
        self.library = TaskTemplateLibrary()
    
    def run(self, args: List[str]) -> bool:
        """运行模板命令"""
        if not args:
            return self._show_help()
        
        command = args[0].lower()
        
        if command == "help":
            return self._show_help()
        elif command == "list":
            return self._list_templates(args[1:])
        elif command == "show":
            return self._show_template(args[1:])
        elif command == "create":
            return self._create_template(args[1:])
        elif command == "delete":
            return self._delete_template(args[1:])
        elif command == "use":
            return self._use_template(args[1:])
        elif command == "popular":
            return self._show_popular(args[1:])
        elif command == "export":
            return self._export_template(args[1:])
        elif command == "import":
            return self._import_template(args[1:])
        elif command == "test":
            return self._test_template_library()
        else:
            print(f"❌ 未知命令: {command}")
            return False
    
    def _show_help(self) -> bool:
        """显示帮助"""
        help_text = """
📋 系统任务模板库命令:
  help                       - 显示帮助信息
  list [category] [tags]     - 列出模板，可选按分类或标签过滤
  show <template_id>         - 显示模板详情
  create <name> [desc]       - 创建自定义模板
  delete <template_id>       - 删除模板
  use <template_id>          - 使用模板并记录
  popular [limit]            - 显示最受欢迎的模板
  export <template_id> <file> - 导出模板
  import <file>              - 导入模板
  test                       - 测试模板库

使用示例:
  # 列出所有模板
  python -m first_principle_agent template list
  
  # 列出Web开发相关模板
  python -m first_principle_agent template list web_development
  
  # 显示模板详情
  python -m first_principle_agent template show web_app_from_scratch
  
  # 使用模板
  python -m first_principle_agent template use web_app_from_scratch
  
  # 导出模板
  python -m first_principle_agent template export web_app_from_scratch my_template.json
        """
        print(help_text)
        return True
    
    def _list_templates(self, args: List[str]) -> bool:
        """列出模板"""
        category = None
        tags = None
        
        if len(args) > 0:
            try:
                category = TemplateCategory(args[0])
            except ValueError:
                pass
        
        if len(args) > 1:
            tags = args[1].split(',')
        
        templates = self.library.list_templates(category=category, tags=tags)
        
        print(f"\n📋 任务模板 ({len(templates)}个):")
        print("=" * 80)
        
        for i, template in enumerate(templates, 1):
            print(f"\n{i}. 📝 {template.name}")
            print(f"   ID: {template.template_id}")
            print(f"   分类: {template.category.value}")
            print(f"   难度: {template.difficulty}")
            print(f"   预估时间: {template.estimated_time}")
            print(f"   描述: {template.description[:60]}..." if len(template.description) > 60 else f"   描述: {template.description}")
            if template.tags:
                print(f"   标签: {', '.join(template.tags)}")
        
        print("\n" + "=" * 80)
        return True
    
    def _show_template(self, args: List[str]) -> bool:
        """显示模板详情"""
        if not args:
            print("❌ 请指定模板ID")
            return False
        
        template_id = args[0]
        template = self.library.get_template(template_id)
        
        if not template:
            print(f"❌ 模板不存在: {template_id}")
            return False
        
        print(f"\n📝 模板详情: {template.name}")
        print("=" * 80)
        print(f"ID: {template.template_id}")
        print(f"名称: {template.name}")
        print(f"分类: {template.category.value}")
        print(f"难度: {template.difficulty}")
        print(f"预估时间: {template.estimated_time}")
        print(f"版本: {template.version}")
        print(f"预设: {'是' if template.is_preset else '否'}")
        print(f"\n📄 描述:")
        print(f"   {template.description}")
        
        if template.tags:
            print(f"\n🏷️ 标签: {', '.join(template.tags)}")
        
        if template.requirements:
            print(f"\n📋 前置需求:")
            for i, req in enumerate(template.requirements, 1):
                print(f"   {i}. {req}")
        
        if template.steps:
            print(f"\n🔄 执行步骤:")
            for i, step in enumerate(template.steps, 1):
                print(f"   {i}. {step}")
        
        print("\n" + "=" * 80)
        return True
    
    def _create_template(self, args: List[str]) -> bool:
        """创建模板"""
        if not args:
            print("❌ 请指定模板名称")
            return False
        
        name = args[0]
        description = " ".join(args[1:]) if len(args) > 1 else "自定义模板"
        
        template = self.library.create_template(
            name=name,
            description=description
        )
        
        return template is not None
    
    def _delete_template(self, args: List[str]) -> bool:
        """删除模板"""
        if not args:
            print("❌ 请指定模板ID")
            return False
        
        template_id = args[0]
        return self.library.delete_template(template_id)
    
    def _use_template(self, args: List[str]) -> bool:
        """使用模板"""
        if not args:
            print("❌ 请指定模板ID")
            return False
        
        template_id = args[0]
        success = self.library.use_template(template_id)
        return success
    
    def _show_popular(self, args: List[str]) -> bool:
        """显示热门模板"""
        limit = 5
        if len(args) > 0:
            try:
                limit = int(args[0])
            except ValueError:
                pass
        
        templates = self.library.get_popular_templates(limit=limit)
        
        print(f"\n🔥 最受欢迎的模板 ({len(templates)}个):")
        print("=" * 80)
        
        for i, template in enumerate(templates, 1):
            print(f"\n{i}. 📝 {template.name}")
            print(f"   ID: {template.template_id}")
            print(f"   分类: {template.category.value}")
            print(f"   描述: {template.description[:60]}...")
        
        print("\n" + "=" * 80)
        return True
    
    def _export_template(self, args: List[str]) -> bool:
        """导出模板"""
        if len(args) < 2:
            print("❌ 请指定模板ID和输出文件")
            return False
        
        template_id = args[0]
        output_file = args[1]
        
        return self.library.export_template(template_id, output_file)
    
    def _import_template(self, args: List[str]) -> bool:
        """导入模板"""
        if not args:
            print("❌ 请指定输入文件")
            return False
        
        input_file = args[0]
        
        template = self.library.import_template(input_file)
        return template is not None
    
    def _test_template_library(self) -> bool:
        """测试模板库"""
        print("\n🧪 测试任务模板库...")
        print("=" * 80)
        
        try:
            # 测试列出模板
            print("\n📋 测试列出模板...")
            templates = self.library.list_templates()
            print(f"✅ 模板数量: {len(templates)}")
            
            # 测试获取模板
            print("\n📝 测试获取模板...")
            template = self.library.get_template(templates[0].template_id)
            if template:
                print(f"✅ 获取模板成功: {template.name}")
            
            # 测试分类过滤
            print("\n🏷️ 测试分类过滤...")
            web_templates = self.library.list_templates(category=TemplateCategory.WEB_DEVELOPMENT)
            print(f"✅ Web开发模板: {len(web_templates)}")
            
            # 测试创建模板
            print("\n✏️ 测试创建模板...")
            new_template = self.library.create_template(
                name="测试模板",
                description="这是一个测试模板",
                category=TemplateCategory.CUSTOM
            )
            if new_template:
                print(f"✅ 创建模板成功: {new_template.name}")
                
                # 测试删除模板
                print("\n🗑️ 测试删除模板...")
                delete_success = self.library.delete_template(new_template.template_id)
                print(f"✅ 删除模板: {'成功' if delete_success else '失败'}")
            
            print("\n" + "=" * 80)
            print("🎉 模板库测试完成！")
            print("=" * 80)
            
            return True
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False


def create_template_library() -> TaskTemplateLibrary:
    """创建模板库工厂函数"""
    return TaskTemplateLibrary()


def create_template_cli() -> TemplateCLI:
    """创建模板CLI工厂函数"""
    return TemplateCLI()

