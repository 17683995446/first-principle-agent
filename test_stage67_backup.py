#!/usr/bin/env python3
"""
第67阶段 - 系统备份和恢复功能测试
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from first_principle_agent.core.backup import (
    BackupManager,
    BackupCLI,
    BackupMetadata,
    BackupRecord,
    BackupType,
    create_backup_manager,
    create_backup_cli
)


def test_1_data_structures():
    """测试1: 数据结构"""
    print("\n" + "="*80)
    print("测试1: 数据结构")
    print("="*80)
    
    try:
        # 测试BackupMetadata
        metadata = BackupMetadata(
            backup_id="test_backup_001",
            backup_type=BackupType.FULL,
            created_at="2026-05-29 12:00:00",
            description="测试备份",
            version="1.0",
            file_size=1024
        )
        print("✅ BackupMetadata 创建成功")
        print(f"   ID: {metadata.backup_id}")
        print(f"   类型: {metadata.backup_type.value}")
        print(f"   创建时间: {metadata.created_at}")
        
        # 测试BackupRecord
        record = BackupRecord(
            metadata=metadata,
            file_path="backups/test_backup_001.zip"
        )
        print("\n✅ BackupRecord 创建成功")
        print(f"   文件路径: {record.file_path}")
        
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_2_backup_manager():
    """测试2: 备份管理器"""
    print("\n" + "="*80)
    print("测试2: 备份管理器")
    print("="*80)
    
    try:
        manager = create_backup_manager()
        print("✅ BackupManager 创建成功")
        
        # 测试创建备份
        print("\n💾 测试创建备份...")
        record = manager.create_backup(BackupType.FULL, "自动化测试备份")
        if not record:
            print("❌ 创建备份失败")
            return False
        print("✅ 创建备份成功")
        print(f"   备份ID: {record.metadata.backup_id}")
        
        # 测试列出备份
        print("\n📋 测试列出备份...")
        backups = manager.list_backups()
        if len(backups) == 0:
            print("❌ 没有找到备份")
            return False
        print(f"✅ 找到 {len(backups)} 个备份")
        
        # 测试删除备份
        print("\n🗑️  测试删除备份...")
        delete_success = manager.delete_backup(record.metadata.backup_id)
        if not delete_success:
            print("❌ 删除备份失败")
            return False
        print("✅ 删除备份成功")
        
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_3_backup_types():
    """测试3: 备份类型"""
    print("\n" + "="*80)
    print("测试3: 备份类型")
    print("="*80)
    
    try:
        manager = create_backup_manager()
        
        # 测试配置备份
        print("\n⚙️  测试配置备份...")
        config_record = manager.create_backup(BackupType.CONFIG, "配置测试备份")
        if not config_record:
            print("❌ 创建配置备份失败")
            return False
        print("✅ 配置备份创建成功")
        
        # 测试数据备份
        print("\n📊 测试数据备份...")
        data_record = manager.create_backup(BackupType.DATA, "数据测试备份")
        if not data_record:
            print("❌ 创建数据备份失败")
            return False
        print("✅ 数据备份创建成功")
        
        # 清理测试备份
        print("\n🧹 清理测试备份...")
        manager.delete_backup(config_record.metadata.backup_id)
        manager.delete_backup(data_record.metadata.backup_id)
        
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_4_backup_cli():
    """测试4: 备份命令行接口"""
    print("\n" + "="*80)
    print("测试4: 备份命令行接口")
    print("="*80)
    
    try:
        cli = create_backup_cli()
        print("✅ BackupCLI 创建成功")
        
        # 测试help命令
        print("\n❓ 测试help命令...")
        help_success = cli.run(["help"])
        print(f"   help命令: {'成功' if help_success else '失败'}")
        
        # 测试list命令
        print("\n📋 测试list命令...")
        list_success = cli.run(["list"])
        print(f"   list命令: {'成功' if list_success else '失败'}")
        
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_5_integration_test():
    """测试5: 集成测试"""
    print("\n" + "="*80)
    print("测试5: 集成测试")
    print("="*80)
    
    try:
        cli = create_backup_cli()
        
        print("\n🧪 运行test命令...")
        test_success = cli.run(["test"])
        
        print(f"\n📋 集成测试: {'成功' if test_success else '失败'}")
        return test_success
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("第67阶段 - 系统备份和恢复功能测试")
    print("="*80)
    
    tests = [
        test_1_data_structures,
        test_2_backup_manager,
        test_3_backup_types,
        test_4_backup_cli,
        test_5_integration_test
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
        print("\n🎉 所有测试通过！第67阶段完成！")
        return 0
    else:
        print("\n❌ 部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())

