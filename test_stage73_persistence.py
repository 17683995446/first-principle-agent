#!/usr/bin/env python3
"""
第73阶段：数据持久化和缓存管理测试
"""

import sys
import shutil
from pathlib import Path


def test_data_structures():
    """测试数据结构"""
    print("\n" + "="*80)
    print("📦 测试1: 数据结构")
    print("="*80)
    
    try:
        from first_principle_agent.core.data_persistence import (
            CacheType, PersistenceFormat, CacheEntry
        )
        
        print("\n✅ 成功导入数据结构类")
        
        # 测试 CacheEntry
        entry = CacheEntry(
            key="test",
            value="value",
            created_at="2024-01-01T00:00:00"
        )
        assert entry.key == "test"
        assert not entry.is_expired()
        print("✅ CacheEntry 测试成功")
        
        print("\n✅ 数据结构测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 数据结构测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cache_manager():
    """测试缓存管理器"""
    print("\n" + "="*80)
    print("💾 测试2: 缓存管理器")
    print("="*80)
    
    try:
        from first_principle_agent.core.data_persistence import CacheManager
        
        print("\n📦 创建缓存管理器...")
        cache = CacheManager(ttl=3600)
        print("✅ CacheManager 创建成功")
        
        # 测试 set/get
        print("\n💾 测试 set/get...")
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        print("✅ set/get 测试成功")
        
        # 测试 has/delete
        print("\n❌ 测试 has/delete...")
        assert cache.has("key1")
        cache.delete("key1")
        assert not cache.has("key1")
        print("✅ has/delete 测试成功")
        
        # 测试统计
        print("\n📊 测试统计...")
        cache.set("key1", "value1")
        cache.get("key1")
        stats = cache.get_statistics()
        assert stats['hits'] >= 1
        print("✅ 统计测试成功")
        
        print("\n✅ 缓存管理器测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 缓存管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_persistence_manager():
    """测试持久化管理器"""
    print("\n" + "="*80)
    print("💾 测试3: 持久化管理器")
    print("="*80)
    
    try:
        from first_principle_agent.core.data_persistence import DataPersistenceManager
        
        # 创建测试目录
        test_dir = Path("test_data")
        test_dir.mkdir(exist_ok=True)
        
        print("\n📦 创建持久化管理器...")
        manager = DataPersistenceManager(data_dir=str(test_dir))
        print("✅ DataPersistenceManager 创建成功")
        
        # 测试 save/load
        print("\n💾 测试 save/load...")
        manager.save("test_key", {"data": "value"})
        data = manager.load("test_key")
        assert data is not None
        assert data["data"] == "value"
        print("✅ save/load 测试成功")
        
        # 测试 list/delete
        print("\n📋 测试 list/delete...")
        keys = manager.list_keys()
        assert "test_key" in keys
        manager.delete("test_key")
        keys = manager.list_keys()
        assert "test_key" not in keys
        print("✅ list/delete 测试成功")
        
        # 清理
        shutil.rmtree(test_dir, ignore_errors=True)
        
        print("\n✅ 持久化管理器测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 持久化管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*80)
    print("🧪 第73阶段：数据持久化和缓存管理 - 完整测试套件")
    print("="*80)
    
    tests = [
        ("数据结构测试", test_data_structures),
        ("缓存管理器测试", test_cache_manager),
        ("持久化管理器测试", test_persistence_manager)
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
        print("🎉 所有测试通过！第73阶段完成！")
    else:
        print("⚠️  部分测试失败，请检查上述错误")
    print("="*80)
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

