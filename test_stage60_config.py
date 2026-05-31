#!/usr/bin/env python3
"""
第60阶段：系统配置管理测试
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("🧪 第60阶段：系统配置管理测试")
print("=" * 80)
print()


def test_config_manager():
    """测试配置管理器"""
    print("\n📋 测试 1: 配置管理器")
    print("=" * 80)
    
    try:
        from first_principle_agent.core.system_config import (
            ConfigManager, SystemConfig, Environment, LogLevel
        )
        
        # 创建配置管理器
        manager = ConfigManager()
        print("✅ ConfigManager 创建成功")
        
        # 加载配置
        config = manager.load()
        print(f"✅ 配置加载成功")
        print(f"   环境: {config.environment.value}")
        print(f"   版本: {config.version}")
        print(f"   日志级别: {config.log_level.value}")
        
        # 测试配置更新
        manager.update(log_level=LogLevel.DEBUG, max_workers=8)
        print("✅ 配置更新成功")
        
        # 测试获取配置
        value = manager.get('version')
        print(f"✅ 配置获取成功: version = {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_system_bootstrap():
    """测试系统引导"""
    print("\n🚀 测试 2: 系统引导")
    print("=" * 80)
    
    try:
        from first_principle_agent.core.system_config import (
            SystemBootstrap, SystemConfig
        )
        
        # 创建配置
        config = SystemConfig()
        
        # 创建引导器
        bootstrap = SystemBootstrap(config)
        print("✅ SystemBootstrap 创建成功")
        
        # 执行引导
        success = bootstrap.bootstrap()
        
        if success:
            print("✅ 系统引导成功")
            print(f"   引导ID: {bootstrap.boot_id}")
            print(f"   初始化组件: {len(bootstrap.components_initialized)} 个")
            print(f"   错误数量: {len(bootstrap.errors)} 个")
            
            # 获取状态
            status = bootstrap.get_status()
            print(f"✅ 获取引导状态成功")
            
            return True
        else:
            print("❌ 系统引导失败")
            return False
        
    except Exception as e:
        print(f"❌ 系统引导测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cli_commands():
    """测试CLI命令"""
    print("\n💻 测试 3: CLI 配置命令")
    print("=" * 80)
    
    try:
        from first_principle_agent.core.system_config import ConfigCLI
        
        cli = ConfigCLI()
        print("✅ ConfigCLI 创建成功")
        
        # 测试 show 命令
        print("\n📌 测试 config show:")
        success = cli.run(["show"])
        if success:
            print("✅ show 命令执行成功")
        else:
            print("❌ show 命令执行失败")
            return False
        
        # 测试 set 命令
        print("\n📌 测试 config set:")
        success = cli.run(["set", "max_workers", "10"])
        if success:
            print("✅ set 命令执行成功")
        else:
            print("❌ set 命令执行失败")
            return False
        
        # 测试 reset 命令
        print("\n📌 测试 config reset:")
        success = cli.run(["reset"])
        if success:
            print("✅ reset 命令执行成功")
        else:
            print("❌ reset 命令执行失败")
            return False
        
        # 测试 bootstrap 命令
        print("\n📌 测试 config bootstrap:")
        success = cli.run(["bootstrap"])
        if success:
            print("✅ bootstrap 命令执行成功")
        else:
            print("❌ bootstrap 命令执行失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ CLI 命令测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_main_cli():
    """测试主CLI集成"""
    print("\n🎯 测试 4: 主 CLI 集成")
    print("=" * 80)
    
    try:
        # 导入主模块
        import first_principle_agent.__main__ as main_module
        
        print("✅ 主模块导入成功")
        
        # 检查函数是否存在
        assert hasattr(main_module, 'run_config'), "run_config 函数不存在"
        assert hasattr(main_module, 'print_banner'), "print_banner 函数不存在"
        
        print("✅ 所有必需的函数都存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 主 CLI 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    results = []
    
    # 运行测试
    results.append(("配置管理器", test_config_manager()))
    results.append(("系统引导", test_system_bootstrap()))
    results.append(("CLI 命令", test_cli_commands()))
    results.append(("主 CLI 集成", test_main_cli()))
    
    # 打印汇总
    print("\n" + "=" * 80)
    print("📊 测试结果汇总")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n总计: {passed}/{len(results)} 通过, {failed}/{len(results)} 失败")
    
    if failed == 0:
        print("\n🎉 所有测试通过！第60阶段完成！")
        print(f"📈 项目进度: 60/100 阶段完成")
        return 0
    else:
        print(f"\n⚠️  部分测试失败，请检查！")
        return 1


if __name__ == "__main__":
    sys.exit(main())
