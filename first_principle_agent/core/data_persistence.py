#!/usr/bin/env python3
"""
数据持久化和缓存管理 - 第73阶段
提供完整的数据持久化和缓存管理系统
"""

import json
import time
import hashlib
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timedelta


class CacheType(Enum):
    """缓存类型"""
    MEMORY = "memory"
    DISK = "disk"
    DISTRIBUTED = "distributed"


class PersistenceFormat(Enum):
    """持久化格式"""
    JSON = "json"
    PICKLE = "pickle"
    YAML = "yaml"
    CSV = "csv"


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    created_at: str
    expires_at: Optional[str] = None
    hit_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if not self.expires_at:
            return False
        expires = datetime.fromisoformat(self.expires_at)
        return datetime.now() > expires


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_type: CacheType = CacheType.MEMORY, ttl: int = 3600):
        self.cache_type = cache_type
        self.ttl = ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.hits = 0
        self.misses = 0
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存"""
        try:
            expires_at = None
            if ttl or self.ttl:
                expires = datetime.now() + timedelta(seconds=ttl or self.ttl)
                expires_at = expires.isoformat()
            
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now().isoformat(),
                expires_at=expires_at
            )
            
            self.cache[key] = entry
            return True
        except Exception as e:
            print(f"❌ 设置缓存失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取缓存"""
        if key not in self.cache:
            self.misses += 1
            return default
        
        entry = self.cache[key]
        
        if entry.is_expired():
            del self.cache[key]
            self.misses += 1
            return default
        
        entry.hit_count += 1
        self.hits += 1
        return entry.value
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self) -> bool:
        """清空缓存"""
        self.cache.clear()
        return True
    
    def has(self, key: str) -> bool:
        """检查键是否存在"""
        if key not in self.cache:
            return False
        entry = self.cache[key]
        if entry.is_expired():
            del self.cache[key]
            return False
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "total_entries": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.2f}%",
            "cache_type": self.cache_type.value
        }


class DataPersistenceManager:
    """数据持久化管理器"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
    
    def save(self, key: str, data: Any, format: PersistenceFormat = PersistenceFormat.JSON) -> bool:
        """保存数据"""
        try:
            file_path = self.data_dir / f"{key}.{format.value}"
            
            if format == PersistenceFormat.JSON:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            elif format == PersistenceFormat.PICKLE:
                import pickle
                with open(file_path, 'wb') as f:
                    pickle.dump(data, f)
            
            return True
        except Exception as e:
            print(f"❌ 保存数据失败: {e}")
            return False
    
    def load(self, key: str, format: PersistenceFormat = PersistenceFormat.JSON) -> Optional[Any]:
        """加载数据"""
        try:
            file_path = self.data_dir / f"{key}.{format.value}"
            
            if not file_path.exists():
                return None
            
            if format == PersistenceFormat.JSON:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif format == PersistenceFormat.PICKLE:
                import pickle
                with open(file_path, 'rb') as f:
                    return pickle.load(f)
            
            return None
        except Exception as e:
            print(f"❌ 加载数据失败: {e}")
            return None
    
    def delete(self, key: str, format: PersistenceFormat = PersistenceFormat.JSON) -> bool:
        """删除数据"""
        try:
            file_path = self.data_dir / f"{key}.{format.value}"
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"❌ 删除数据失败: {e}")
            return False
    
    def list_keys(self, format: Optional[PersistenceFormat] = None) -> List[str]:
        """列出所有键"""
        try:
            if format:
                pattern = f"*.{format.value}"
            else:
                pattern = "*"
            
            files = self.data_dir.glob(pattern)
            keys = [f.stem for f in files]
            return keys
        except Exception as e:
            print(f"❌ 列出键失败: {e}")
            return []


class PersistenceCLI:
    """持久化管理CLI"""
    
    def __init__(self):
        self.cache = CacheManager()
        self.persistence = DataPersistenceManager()
    
    def run(self, args: List[str]) -> bool:
        """运行命令"""
        if not args:
            return self._show_help()
        
        command = args[0].lower()
        
        if command == "help":
            return self._show_help()
        elif command == "cache":
            return self._manage_cache(args[1:])
        elif command == "persist":
            return self._manage_persistence(args[1:])
        elif command == "stats":
            return self._show_statistics()
        elif command == "test":
            return self._test_system()
        else:
            print(f"❌ 未知命令: {command}")
            return False
    
    def _show_help(self) -> bool:
        """显示帮助"""
        help_text = """
💾 数据持久化和缓存管理命令:
  help                 - 显示帮助信息
  cache set <key> <value> [ttl] - 设置缓存
  cache get <key>      - 获取缓存
  cache delete <key>   - 删除缓存
  cache clear          - 清空缓存
  persist save <key> <value> - 保存数据
  persist load <key>   - 加载数据
  persist delete <key> - 删除数据
  persist list         - 列出所有数据
  stats                - 显示统计信息
  test                 - 测试系统

使用示例:
  # 设置缓存
  python -m first_principle_agent data cache set mykey myvalue 3600
  
  # 获取缓存
  python -m first_principle_agent data cache get mykey
  
  # 保存数据
  python -m first_principle_agent data persist save mydata '{"name": "test"}'
"""
        print(help_text)
        return True
    
    def _manage_cache(self, args: List[str]) -> bool:
        """管理缓存"""
        if not args:
            print("❌ 请指定缓存操作")
            return False
        
        action = args[0].lower()
        
        if action == "set" and len(args) >= 3:
            key = args[1]
            value = args[2]
            ttl = int(args[3]) if len(args) > 3 else self.cache.ttl
            result = self.cache.set(key, value, ttl)
            print(f"✅ 缓存设置{'成功' if result else '失败'}")
            return result
        elif action == "get" and len(args) >= 2:
            key = args[1]
            value = self.cache.get(key)
            if value is not None:
                print(f"✅ 获取缓存: {value}")
            else:
                print(f"❌ 缓存不存在: {key}")
            return True
        elif action == "delete" and len(args) >= 2:
            key = args[1]
            result = self.cache.delete(key)
            print(f"✅ 缓存删除{'成功' if result else '失败'}")
            return result
        elif action == "clear":
            result = self.cache.clear()
            print(f"✅ 缓存清空{'成功' if result else '失败'}")
            return result
        else:
            print("❌ 无效的缓存操作")
            return False
    
    def _manage_persistence(self, args: List[str]) -> bool:
        """管理持久化"""
        if not args:
            print("❌ 请指定持久化操作")
            return False
        
        action = args[0].lower()
        
        if action == "save" and len(args) >= 3:
            key = args[1]
            value_str = args[2]
            try:
                value = json.loads(value_str)
            except:
                value = value_str
            result = self.persistence.save(key, value)
            print(f"✅ 数据保存{'成功' if result else '失败'}")
            return result
        elif action == "load" and len(args) >= 2:
            key = args[1]
            value = self.persistence.load(key)
            if value is not None:
                print(f"✅ 加载数据: {value}")
            else:
                print(f"❌ 数据不存在: {key}")
            return True
        elif action == "delete" and len(args) >= 2:
            key = args[1]
            result = self.persistence.delete(key)
            print(f"✅ 数据删除{'成功' if result else '失败'}")
            return result
        elif action == "list":
            keys = self.persistence.list_keys()
            print(f"\n💾 已保存的数据 ({len(keys)} 个):")
            for key in keys:
                print(f"   - {key}")
            return True
        else:
            print("❌ 无效的持久化操作")
            return False
    
    def _show_statistics(self) -> bool:
        """显示统计信息"""
        stats = self.cache.get_statistics()
        print(f"\n📊 缓存统计信息:")
        print("=" * 80)
        print(f"总条目数: {stats['total_entries']}")
        print(f"命中次数: {stats['hits']}")
        print(f"未命中次数: {stats['misses']}")
        print(f"命中率: {stats['hit_rate']}")
        print(f"缓存类型: {stats['cache_type']}")
        print("\n" + "=" * 80)
        return True
    
    def _test_system(self) -> bool:
        """测试系统"""
        print("\n🧪 测试数据持久化和缓存系统...")
        print("=" * 80)
        
        try:
            # 测试缓存
            print("\n💾 测试缓存...")
            assert self.cache.set("test_key", "test_value")
            assert self.cache.get("test_key") == "test_value"
            assert self.cache.has("test_key")
            assert self.cache.delete("test_key")
            print("✅ 缓存测试成功")
            
            # 测试持久化
            print("\n💾 测试持久化...")
            assert self.persistence.save("test_data", {"test": "value"})
            data = self.persistence.load("test_data")
            assert data is not None
            assert self.persistence.delete("test_data")
            print("✅ 持久化测试成功")
            
            print("\n" + "=" * 80)
            print("🎉 数据持久化和缓存系统测试完成！")
            print("=" * 80)
            return True
            
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False


def create_cache_manager() -> CacheManager:
    """创建缓存管理器"""
    return CacheManager()


def create_persistence_manager() -> DataPersistenceManager:
    """创建持久化管理器"""
    return DataPersistenceManager()


def create_persistence_cli() -> PersistenceCLI:
    """创建持久化CLI"""
    return PersistenceCLI()

