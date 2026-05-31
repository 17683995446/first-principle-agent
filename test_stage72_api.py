#!/usr/bin/env python3
"""
第72阶段：API网关和接口管理测试
"""

import sys


def test_data_structures():
    """测试数据结构"""
    print("\n" + "="*80)
    print("📦 测试1: 数据结构")
    print("="*80)
    
    try:
        from first_principle_agent.core.api_gateway import (
            HTTPMethod, ResponseFormat, MiddlewareType,
            APIEndpoint, APIResponse, RequestContext
        )
        
        print("\n✅ 成功导入数据结构类")
        
        # 测试 HTTPMethod
        print("\n🔢 测试 HTTPMethod...")
        assert HTTPMethod.GET.value == "GET"
        assert HTTPMethod.POST.value == "POST"
        print("✅ HTTPMethod 测试成功")
        
        # 测试 RequestContext
        print("\n📝 测试 RequestContext...")
        context = RequestContext(
            method="GET",
            path="/test",
            headers={"content-type": "application/json"},
            query_params={"key": "value"}
        )
        assert context.method == "GET"
        assert context.path == "/test"
        assert context.get_header("content-type") == "application/json"
        assert context.get_query("key") == "value"
        print("✅ RequestContext 测试成功")
        
        # 测试 APIResponse
        print("\n📄 测试 APIResponse...")
        response = APIResponse(
            status_code=200,
            data={"message": "success"},
            message="OK"
        )
        assert response.status_code == 200
        assert response.data["message"] == "success"
        print("✅ APIResponse 测试成功")
        
        print("\n✅ 数据结构测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 数据结构测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_gateway():
    """测试API网关"""
    print("\n" + "="*80)
    print("🌐 测试2: API网关")
    print("="*80)
    
    try:
        from first_principle_agent.core.api_gateway import (
            APIGateway, HTTPMethod
        )
        
        print("\n📦 创建API网关...")
        gateway = APIGateway()
        print("✅ APIGateway 创建成功")
        
        # 测试端点注册
        print("\n📝 测试端点注册...")
        def test_handler(ctx):
            return {"message": "test"}
        
        result = gateway.register_endpoint(
            path="/test",
            method=HTTPMethod.GET,
            handler=test_handler,
            description="测试端点"
        )
        assert result is True
        print("✅ 端点注册成功")
        
        # 测试获取端点
        print("\n🔍 测试获取端点...")
        endpoint = gateway.get_endpoint("/test", HTTPMethod.GET)
        assert endpoint is not None
        assert endpoint.path == "/test"
        print("✅ 获取端点成功")
        
        # 测试请求处理
        print("\n🚀 测试请求处理...")
        from first_principle_agent.core.api_gateway import RequestContext
        
        context = RequestContext(
            method="GET",
            path="/test",
            headers={},
            query_params={}
        )
        
        response = gateway.handle_request(context)
        assert response.status_code == 200
        print("✅ 请求处理成功")
        
        # 测试404
        print("\n🔍 测试404响应...")
        context = RequestContext(
            method="GET",
            path="/not/found",
            headers={},
            query_params={}
        )
        
        response = gateway.handle_request(context)
        assert response.status_code == 404
        print("✅ 404响应正确")
        
        print("\n✅ API网关测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ API网关测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_cli():
    """测试API CLI"""
    print("\n" + "="*80)
    print("🖥️  测试3: API CLI")
    print("="*80)
    
    try:
        from first_principle_agent.core.api_gateway import APICLI
        
        print("\n💻 创建APICLI...")
        cli = APICLI()
        print("✅ APICLI 创建成功")
        
        # 测试 help 命令
        print("\n❓ 测试 help 命令...")
        result = cli.run(["help"])
        assert result is True
        print("✅ help 命令成功")
        
        # 测试 list 命令
        print("\n📋 测试 list 命令...")
        result = cli.run(["list"])
        assert result is True
        print("✅ list 命令成功")
        
        # 测试 stats 命令
        print("\n📊 测试 stats 命令...")
        result = cli.run(["stats"])
        assert result is True
        print("✅ stats 命令成功")
        
        # 测试 test 命令
        print("\n🧪 测试 test 命令...")
        result = cli.run(["test"])
        assert result is True
        print("✅ test 命令成功")
        
        print("\n✅ API CLI测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ API CLI测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_factory_functions():
    """测试工厂函数"""
    print("\n" + "="*80)
    print("🏭 测试4: 工厂函数")
    print("="*80)
    
    try:
        from first_principle_agent.core.api_gateway import (
            create_api_gateway, create_api_cli
        )
        
        print("\n📦 测试 create_api_gateway...")
        gateway = create_api_gateway()
        print("✅ create_api_gateway 成功")
        
        print("\n💻 测试 create_api_cli...")
        cli = create_api_cli()
        print("✅ create_api_cli 成功")
        
        print("\n✅ 工厂函数测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 工厂函数测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*80)
    print("🧪 第72阶段：API网关和接口管理 - 完整测试套件")
    print("="*80)
    
    tests = [
        ("数据结构测试", test_data_structures),
        ("API网关测试", test_api_gateway),
        ("API CLI测试", test_api_cli),
        ("工厂函数测试", test_factory_functions)
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
        print("🎉 所有测试通过！第72阶段完成！")
    else:
        print("⚠️  部分测试失败，请检查上述错误")
    print("="*80)
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

