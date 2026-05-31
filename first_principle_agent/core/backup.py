#!/usr/bin/env python3
"""
系统备份和恢复功能 - 第67阶段
提供系统配置、任务数据等的备份和恢复功能
"""

import json
import os
import datetime
import shutil
import zipfile
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path


class BackupType(Enum):
    """备份类型"""
    FULL = "full"
    CONFIG = "config"
    DATA = "data"


@dataclass
class BackupMetadata:
    """备份元数据"""
    backup_id: str
    backup_type: BackupType
    created_at: str
    description: str = ""
    version: str = "1.0"
    file_size: int = 0


@dataclass
class BackupRecord:
    """备份记录"""
    metadata: BackupMetadata
    file_path: str


class BackupManager:
    """备份管理器"""
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.backup_records: List[BackupRecord] = []
        self._load_records()
    
    def _load_records(self):
        """加载备份记录"""
        record_file = self.backup_dir / "backup_records.json"
        if record_file.exists():
            try:
                with open(record_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        metadata = BackupMetadata(
                            backup_id=item["metadata"]["backup_id"],
                            backup_type=BackupType(item["metadata"]["backup_type"]),
                            created_at=item["metadata"]["created_at"],
                            description=item["metadata"].get("description", ""),
                            version=item["metadata"].get("version", "1.0"),
                            file_size=item["metadata"].get("file_size", 0)
                        )
                        self.backup_records.append(BackupRecord(
                            metadata=metadata,
                            file_path=item["file_path"]
                        ))
            except Exception as e:
                print(f"⚠️  加载备份记录时出错: {e}")
    
    def _save_records(self):
        """保存备份记录"""
        record_file = self.backup_dir / "backup_records.json"
        data = []
        for record in self.backup_records:
            data.append({
                "metadata": {
                    "backup_id": record.metadata.backup_id,
                    "backup_type": record.metadata.backup_type.value,
                    "created_at": record.metadata.created_at,
                    "description": record.metadata.description,
                    "version": record.metadata.version,
                    "file_size": record.metadata.file_size
                },
                "file_path": record.file_path
            })
        
        try:
            with open(record_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  保存备份记录时出错: {e}")
    
    def _generate_backup_id(self) -> str:
        """生成备份ID"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"backup_{timestamp}"
    
    def create_backup(
        self,
        backup_type: BackupType = BackupType.FULL,
        description: str = ""
    ) -> Optional[BackupRecord]:
        """创建备份"""
        backup_id = self._generate_backup_id()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        metadata = BackupMetadata(
            backup_id=backup_id,
            backup_type=backup_type,
            created_at=timestamp,
            description=description
        )
        
        backup_filename = f"{backup_id}.zip"
        backup_path = self.backup_dir / backup_filename
        
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if backup_type in [BackupType.FULL, BackupType.CONFIG]:
                    self._add_config_files(zipf)
                
                if backup_type in [BackupType.FULL, BackupType.DATA]:
                    self._add_data_files(zipf)
            
            file_size = backup_path.stat().st_size
            metadata.file_size = file_size
            
            record = BackupRecord(
                metadata=metadata,
                file_path=str(backup_path)
            )
            
            self.backup_records.append(record)
            self._save_records()
            
            print(f"✅ 备份成功: {backup_id}")
            return record
        except Exception as e:
            print(f"❌ 创建备份失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _add_config_files(self, zipf):
        """添加配置文件到备份"""
        config_dir = Path("config")
        if config_dir.exists() and config_dir.is_dir():
            for file in config_dir.rglob("*"):
                if file.is_file():
                    arcname = f"config/{file.relative_to(config_dir)}"
                    zipf.write(file, arcname=arcname)
    
    def _add_data_files(self, zipf):
        """添加数据文件到备份"""
        data_dir = Path("data")
        if data_dir.exists() and data_dir.is_dir():
            for file in data_dir.rglob("*"):
                if file.is_file():
                    arcname = f"data/{file.relative_to(data_dir)}"
                    zipf.write(file, arcname=arcname)
    
    def list_backups(self) -> List[BackupRecord]:
        """列出所有备份"""
        return self.backup_records
    
    def restore_backup(self, backup_id: str) -> bool:
        """恢复备份"""
        record = self._find_backup(backup_id)
        if not record:
            print(f"❌ 找不到备份: {backup_id}")
            return False
        
        try:
            backup_path = Path(record.file_path)
            if not backup_path.exists():
                print(f"❌ 备份文件不存在: {backup_path}")
                return False
            
            print(f"🔄 正在恢复备份: {backup_id}")
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall()
            
            print("✅ 备份恢复成功")
            return True
        except Exception as e:
            print(f"❌ 恢复备份失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def delete_backup(self, backup_id: str) -> bool:
        """删除备份"""
        record = self._find_backup(backup_id)
        if not record:
            print(f"❌ 找不到备份: {backup_id}")
            return False
        
        try:
            backup_path = Path(record.file_path)
            if backup_path.exists():
                os.remove(backup_path)
            
            self.backup_records.remove(record)
            self._save_records()
            
            print(f"✅ 备份已删除: {backup_id}")
            return True
        except Exception as e:
            print(f"❌ 删除备份失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _find_backup(self, backup_id: str) -> Optional[BackupRecord]:
        """查找备份"""
        for record in self.backup_records:
            if record.metadata.backup_id == backup_id:
                return record
        return None


class BackupCLI:
    """备份命令行接口"""
    
    def __init__(self):
        self.backup_manager = BackupManager()
    
    def run(self, args: List[str]) -> bool:
        """运行备份命令"""
        if not args:
            return self._show_help()
        
        command = args[0].lower()
        
        if command == "help":
            return self._show_help()
        elif command == "create":
            return self._create_backup(args[1:])
        elif command == "list":
            return self._list_backups()
        elif command == "restore":
            return self._restore_backup(args[1:])
        elif command == "delete":
            return self._delete_backup(args[1:])
        elif command == "test":
            return self._test_backup_system()
        else:
            print(f"❌ 未知命令: {command}")
            return False
    
    def _show_help(self) -> bool:
        """显示帮助"""
        help_text = """
💾 系统备份和恢复命令:
  help                - 显示帮助信息
  create [type] [desc] - 创建备份
  list                - 列出备份
  restore <backup_id>   - 恢复备份
  delete <backup_id>  - 删除备份
  test                - 测试备份系统

备份类型:
  full                - 完整备份（默认）
  config              - 仅配置备份
  data                - 仅数据备份

使用示例:
  # 创建完整备份
  python -m first_principle_agent backup create

  # 创建配置备份
  python -m first_principle_agent backup create config "我的配置备份"

  # 列出备份
  python -m first_principle_agent backup list

  # 恢复备份
  python -m first_principle_agent backup restore backup_20260529_120000
        """
        print(help_text)
        return True
    
    def _create_backup(self, args: List[str]) -> bool:
        """创建备份"""
        backup_type = BackupType.FULL
        description = ""
        
        if len(args) > 0:
            type_str = args[0].lower()
            if type_str == "config":
                backup_type = BackupType.CONFIG
            elif type_str == "data":
                backup_type = BackupType.DATA
        
        if len(args) > 1:
            description = " ".join(args[1:])
        
        print(f"\n💾 创建{backup_type.value}备份...")
        record = self.backup_manager.create_backup(backup_type, description)
        return record is not None
    
    def _list_backups(self) -> bool:
        """列出备份"""
        backups = self.backup_manager.list_backups()
        
        print(f"\n📋 备份列表:")
        print("=" * 80)
        
        if not backups:
            print("  暂无备份")
            return True
        
        for idx, record in enumerate(backups, 1):
            meta = record.metadata
            print(f"\n  {idx}. {meta.backup_id}")
            print(f"     类型: {meta.backup_type.value}")
            print(f"     创建时间: {meta.created_at}")
            print(f"     大小: {meta.file_size} 字节")
            if meta.description:
                print(f"     描述: {meta.description}")
        
        print("\n" + "=" * 80)
        print(f"共 {len(backups)} 个备份")
        return True
    
    def _restore_backup(self, args: List[str]) -> bool:
        """恢复备份"""
        if not args:
            print("\n❌ 请指定要恢复的备份ID")
            return False
        
        backup_id = args[0]
        print(f"\n🔄 正在恢复备份: {backup_id}")
        print("⚠️  警告: 这将覆盖当前数据！")
        confirm = input("确认恢复? (yes/no): ")
        
        if confirm.lower() != "yes":
            print("❌ 已取消恢复")
            return False
        
        return self.backup_manager.restore_backup(backup_id)
    
    def _delete_backup(self, args: List[str]) -> bool:
        """删除备份"""
        if not args:
            print("\n❌ 请指定要删除的备份ID")
            return False
        
        backup_id = args[0]
        confirm = input(f"确认删除备份 {backup_id}? (yes/no): ")
        
        if confirm.lower() != "yes":
            print("❌ 已取消删除")
            return False
        
        return self.backup_manager.delete_backup(backup_id)
    
    def _test_backup_system(self) -> bool:
        """测试备份系统"""
        print("\n🧪 测试备份和恢复系统...")
        print("=" * 80)
        
        try:
            # 测试1: 创建测试备份
            print("\n💾 测试创建备份...")
            record = self.backup_manager.create_backup(BackupType.FULL, "测试备份")
            if not record:
                print("❌ 创建备份失败")
                return False
            print("✅ 创建备份成功")
            
            # 测试2: 列出备份
            print("\n📋 测试列出备份...")
            backups = self.backup_manager.list_backups()
            if len(backups) == 0:
                print("❌ 没有找到备份")
                return False
            print(f"✅ 找到 {len(backups)} 个备份")
            
            # 测试3: 删除测试备份
            print("\n🗑️  测试删除备份...")
            delete_success = self.backup_manager.delete_backup(record.metadata.backup_id)
            if not delete_success:
                print("❌ 删除备份失败")
                return False
            print("✅ 删除备份成功")
            
            print("\n" + "=" * 80)
            print("🎉 备份和恢复系统测试完成！")
            print("=" * 80)
            return True
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False


def create_backup_manager() -> BackupManager:
    """创建备份管理器工厂函数"""
    return BackupManager()


def create_backup_cli() -> BackupCLI:
    """创建备份CLI工厂函数"""
    return BackupCLI()

