#!/usr/bin/env python3
"""
API网关和接口管理 - 第72阶段
提供完整的API接口管理系统，支持接口注册、路由、中间件和请求处理
"""

import json
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Callable, Any, Set
from functools import wraps
from datetime import datetime


class HTTPMethod(Enum):
    """HTTP方法"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class ResponseFormat(Enum):
    """响应格式"""
    JSON = "json"
    TEXT = "text"
    HTML = "html"
    XML = "xml"


class MiddlewareType(Enum):
    """中间件类型"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RATE_LIMITING = "rate_limiting"
    LOGGING = "logging"
    VALIDATION = "validation"
    CACHING = "caching"
    CUSTOM = "custom"


@dataclass
class APIEndpoint:
    """API端点"""
    path: str
    method: HTTPMethod
    handler: Callable
    description: str = ""
    tags: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    responses: Dict[int, str] = field(default_factory=dict)
    deprecated: bool = False
    authenticated: bool = False
    rate_limit: Optional[int] = None  # 每分钟请求数
    timeout: int = 30  # 超时时间（秒）
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIResponse:
    """API响应"""
    status_code: int
    data: Any
    message: str = ""
    format: ResponseFormat = ResponseFormat.JSON
    headers: Dict[str, str] = field(default_factory=dict)
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class RequestContext:
    """请求上下文"""
    method: str
    path: str
    headers: Dict[str, str] = field(default_factory=dict)
    query_params: Dict[str, Any] = field(default_factory=dict)
    body: Any = None
    user: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_header(self, name: str, default: str = "") -> str:
        """获取请求头"""
        return self.headers.get(name.lower(), default)
    
    def get_query(self, name: str, default: Any = None) -> Any:
        """获取查询参数"""
        return self.query_params.get(name, default)


MiddlewareFunc = Callable[[RequestContext, Callable], Optional[APIResponse]]


class APIGateway:
    """API网关"""
    
    def __init__(self):
        self.endpoints: Dict[str, List[APIEndpoint]] = {}
        self.middlewares: Dict[MiddlewareType, List[MiddlewareFunc]] = {}
        self.global_middlewares: List[MiddlewareFunc] = []
        self.request_count = 0
        self.response_times: List[float] = []
        self._init_middlewares()
    
    def _init_middlewares(self):
        """初始化中间件"""
        pass
    
    def register_endpoint(
        self,
        path: str,
        method: HTTPMethod,
        handler: Callable,
        description: str = "",
        tags: Optional[List[str]] = None,
        authenticated: bool = False,
        rate_limit: Optional[int] = None,
        **kwargs
    ) -> bool:
        """注册API端点"""
        try:
            endpoint = APIEndpoint(
                path=path,
                method=method,
                handler=handler,
                description=description,
                tags=tags or [],
                authenticated=authenticated,
                rate_limit=rate_limit,
                **kwargs
            )
            
            if path not in self.endpoints:
                self.endpoints[path] = []
            
            # 检查是否已存在相同路径和方法的端点
            for i, ep in enumerate(self.endpoints[path]):
                if ep.method == method:
                    self.endpoints[path][i] = endpoint
                    print(f"✅ 端点已更新: {method.value} {path}")
                    return True
            
            self.endpoints[path].append(endpoint)
            print(f"✅ 端点注册成功: {method.value} {path}")
            return True
            
        except Exception as e:
            print(f"❌ 注册端点失败: {e}")
            return False
    
    def get_endpoint(self, path: str, method: HTTPMethod) -> Optional[APIEndpoint]:
        """获取端点"""
        if path not in self.endpoints:
            return None
        
        for endpoint in self.endpoints[path]:
            if endpoint.method == method:
                return endpoint
        
        return None
    
    def list_endpoints(self, tags: Optional[List[str]] = None) -> List[APIEndpoint]:
        """列出端点"""
        result = []
        for endpoints in self.endpoints.values():
            for endpoint in endpoints:
                if tags is None or any(tag in endpoint.tags for tag in tags):
                    result.append(endpoint)
        
        return result
    
    def register_middleware(
        self,
        middleware_type: MiddlewareType,
        middleware_func: MiddlewareFunc,
        global_scope: bool = False
    ) -> bool:
        """注册中间件"""
        try:
            if global_scope:
                self.global_middlewares.append(middleware_func)
            else:
                if middleware_type not in self.middlewares:
                    self.middlewares[middleware_type] = []
                self.middlewares[middleware_type].append(middleware_func)
            
            print(f"✅ 中间件注册成功: {middleware_type.value}")
            return True
        except Exception as e:
            print(f"❌ 注册中间件失败: {e}")
            return False
    
    def handle_request(self, context: RequestContext) -> APIResponse:
        """处理请求"""
        start_time = time.time()
        self.request_count += 1
        
        try:
            # 查找端点
            method = HTTPMethod[context.method.upper()]
            endpoint = self.get_endpoint(context.path, method)
            
            if not endpoint:
                return APIResponse(
                    status_code=404,
                    data=None,
                    message=f"端点未找到: {context.method} {context.path}"
                )
            
            # 检查是否废弃
            if endpoint.deprecated:
                return APIResponse(
                    status_code=410,
                    data=None,
                    message=f"端点已废弃: {context.method} {context.path}"
                )
            
            # 执行全局中间件
            for middleware in self.global_middlewares:
                response = middleware(context, endpoint.handler)
                if response:
                    self._record_response_time(time.time() - start_time)
                    return response
            
            # 执行类型特定中间件
            if endpoint.authenticated:
                auth_middlewares = self.middlewares.get(MiddlewareType.AUTHENTICATION, [])
                for middleware in auth_middlewares:
                    response = middleware(context, endpoint.handler)
                    if response:
                        self._record_response_time(time.time() - start_time)
                        return response
            
            # 执行处理器
            result = endpoint.handler(context)
            
            # 包装响应
            if isinstance(result, APIResponse):
                response = result
            else:
                response = APIResponse(
                    status_code=200,
                    data=result,
                    message="成功"
                )
            
            self._record_response_time(time.time() - start_time)
            return response
            
        except Exception as e:
            self._record_response_time(time.time() - start_time)
            return APIResponse(
                status_code=500,
                data=None,
                message=f"处理请求失败: {str(e)}"
            )
    
    def _record_response_time(self, duration: float):
        """记录响应时间"""
        self.response_times.append(duration)
        # 只保留最近1000条记录
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        avg_response_time = (
            sum(self.response_times) / len(self.response_times)
            if self.response_times else 0
        )
        
        return {
            "total_requests": self.request_count,
            "registered_endpoints": len(self.list_endpoints()),
            "active_middlewares": len(self.global_middlewares),
            "avg_response_time": avg_response_time,
            "recent_response_times": self.response_times[-10:]
        }


def api_route(
    path: str,
    method: HTTPMethod,
    description: str = "",
    tags: Optional[List[str]] = None,
    authenticated: bool = False,
    rate_limit: Optional[int] = None
):
    """API路由装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # 存储路由元数据
        wrapper._api_route = True
        wrapper._api_path = path
        wrapper._api_method = method
        wrapper._api_description = description
        wrapper._api_tags = tags or []
        wrapper._api_authenticated = authenticated
        wrapper._api_rate_limit = rate_limit
        
        return wrapper
    return decorator


class APICLI:
    """API管理命令行接口"""
    
    def __init__(self):
        self.gateway = APIGateway()
        self._register_default_endpoints()
    
    def _register_default_endpoints(self):
        """注册默认端点"""
        self.gateway.register_endpoint(
            path="/api/health",
            method=HTTPMethod.GET,
            handler=lambda ctx: APIResponse(
                status_code=200,
                data={"status": "healthy"},
                message="服务正常"
            ),
            description="健康检查端点",
            tags=["system"]
        )
        
        self.gateway.register_endpoint(
            path="/api/stats",
            method=HTTPMethod.GET,
            handler=lambda ctx: APIResponse(
                status_code=200,
                data=self.gateway.get_statistics(),
                message="统计信息"
            ),
            description="获取API统计信息",
            tags=["system"]
        )
        
        self.gateway.register_endpoint(
            path="/api/endpoints",
            method=HTTPMethod.GET,
            handler=lambda ctx: APIResponse(
                status_code=200,
                data=[
                    {"path": ep.path, "method": ep.method.value, "description": ep.description}
                    for ep in self.gateway.list_endpoints()
                ],
                message="端点列表"
            ),
            description="列出所有API端点",
            tags=["system"]
        )
    
    def run(self, args: List[str]) -> bool:
        """运行API命令"""
        if not args:
            return self._show_help()
        
        command = args[0].lower()
        
        if command == "help":
            return self._show_help()
        elif command == "list":
            return self._list_endpoints(args[1:])
        elif command == "register":
            return self._register_endpoint(args[1:])
        elif command == "stats":
            return self._show_statistics()
        elif command == "test":
            return self._test_api_gateway()
        else:
            print(f"❌ 未知命令: {command}")
            return False
    
    def _show_help(self) -> bool:
        """显示帮助"""
        help_text = """
🌐 API网关和接口管理命令:
  help                 - 显示帮助信息
  list [tags]          - 列出所有API端点，可选按标签过滤
  register <path> <method> <handler> [desc] - 注册新端点
  stats                - 显示API统计信息
  test                 - 测试API网关

使用示例:
  # 列出所有端点
  python -m first_principle_agent api list
  
  # 按标签过滤
  python -m first_principle_agent api list system
  
  # 查看统计信息
  python -m first_principle_agent api stats
  
  # 测试API网关
  python -m first_principle_agent api test
"""
        print(help_text)
        return True
    
    def _list_endpoints(self, args: List[str]) -> bool:
        """列出端点"""
        tags = args if args else None
        endpoints = self.gateway.list_endpoints(tags=tags)
        
        print(f"\n🌐 API端点列表 ({len(endpoints)} 个):")
        print("=" * 80)
        
        for endpoint in endpoints:
            auth_icon = "🔐" if endpoint.authenticated else "📖"
            rate_icon = f"⚡{endpoint.rate_limit}/min" if endpoint.rate_limit else ""
            
            print(f"\n{auth_icon} {endpoint.method.value} {endpoint.path}")
            print(f"   描述: {endpoint.description}")
            if endpoint.tags:
                print(f"   标签: {', '.join(endpoint.tags)}")
            if rate_icon:
                print(f"   限流: {rate_icon}")
            if endpoint.deprecated:
                print(f"   ⚠️  已废弃")
        
        print("\n" + "=" * 80)
        return True
    
    def _register_endpoint(self, args: List[str]) -> bool:
        """注册端点"""
        if len(args) < 3:
            print("❌ 参数不足: 需要 <path> <method> <handler> [description]")
            return False
        
        path = args[0]
        method_name = args[1].upper()
        handler_name = args[2]
        description = args[3] if len(args) > 3 else ""
        
        try:
            method = HTTPMethod[method_name]
        except KeyError:
            print(f"❌ 未知HTTP方法: {method_name}")
            return False
        
        # 创建一个简单的处理器
        def handler(ctx):
            return {"message": f"处理 {path} 请求"}
        
        return self.gateway.register_endpoint(
            path=path,
            method=method,
            handler=handler,
            description=description
        )
    
    def _show_statistics(self) -> bool:
        """显示统计信息"""
        stats = self.gateway.get_statistics()
        
        print(f"\n📊 API统计信息:")
        print("=" * 80)
        print(f"总请求数: {stats['total_requests']}")
        print(f"注册端点数: {stats['registered_endpoints']}")
        print(f"活动中间件数: {stats['active_middlewares']}")
        print(f"平均响应时间: {stats['avg_response_time']:.4f}秒")
        
        if stats['recent_response_times']:
            print(f"\n最近响应时间:")
            for i, rt in enumerate(stats['recent_response_times'], 1):
                print(f"   {i}. {rt:.4f}秒")
        
        print("\n" + "=" * 80)
        return True
    
    def _test_api_gateway(self) -> bool:
        """测试API网关"""
        print("\n🧪 测试API网关...")
        print("=" * 80)
        
        try:
            # 测试端点注册
            print("\n📝 测试端点注册...")
            test_gateway = APIGateway()
            
            test_gateway.register_endpoint(
                path="/test/echo",
                method=HTTPMethod.GET,
                handler=lambda ctx: {"echo": "test"},
                description="测试端点"
            )
            
            endpoint = test_gateway.get_endpoint("/test/echo", HTTPMethod.GET)
            assert endpoint is not None
            print("✅ 端点注册成功")
            
            # 测试请求处理
            print("\n🚀 测试请求处理...")
            context = RequestContext(
                method="GET",
                path="/test/echo",
                headers={},
                query_params={}
            )
            
            response = test_gateway.handle_request(context)
            assert response.status_code == 200
            print("✅ 请求处理成功")
            
            # 测试404响应
            print("\n🔍 测试404响应...")
            context = RequestContext(
                method="GET",
                path="/not/exist",
                headers={},
                query_params={}
            )
            
            response = test_gateway.handle_request(context)
            assert response.status_code == 404
            print("✅ 404响应正确")
            
            # 测试统计信息
            print("\n📊 测试统计信息...")
            stats = test_gateway.get_statistics()
            assert stats['total_requests'] >= 2
            print(f"✅ 统计信息正确: 总请求数={stats['total_requests']}")
            
            print("\n" + "=" * 80)
            print("🎉 API网关测试完成！")
            print("=" * 80)
            
            return True
            
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False


def create_api_gateway() -> APIGateway:
    """创建API网关工厂函数"""
    return APIGateway()


def create_api_cli() -> APICLI:
    """创建API CLI工厂函数"""
    return APICLI()

