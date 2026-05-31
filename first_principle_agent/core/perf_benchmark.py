#!/usr/bin/env python3
"""
系统性能基准测试和优化工具 - 第65阶段
提供系统性能测试、基准测试和性能优化建议功能
"""

import time
import random
import json
import statistics
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class PerformanceMetricType(Enum):
    """性能指标类型"""
    EXECUTION_TIME = "execution_time"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    THROUGHPUT = "throughput"
    LATENCY = "latency"


@dataclass
class PerformanceMetric:
    """性能指标数据类"""
    metric_type: PerformanceMetricType
    value: float
    unit: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    description: str = ""


@dataclass
class BenchmarkResult:
    """基准测试结果"""
    benchmark_id: str
    benchmark_name: str
    execution_time_ms: float = 0.0
    success: bool = True
    metrics: List[PerformanceMetric] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: str = ""


@dataclass
class OptimizationSuggestion:
    """优化建议"""
    category: str
    priority: str
    suggestion: str
    impact: str
    complexity: str


class SystemBenchmark:
    """系统基准测试"""
    
    def __init__(self):
        self.benchmark_id = f"benchmark-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.results: List[BenchmarkResult] = []
    
    def benchmark_function(
        self, 
        func: Callable, 
        func_name: str,
        iterations: int = 100,
        warmup: int = 10
    ) -> BenchmarkResult:
        """对函数进行基准测试"""
        result = BenchmarkResult(
            benchmark_id=self.benchmark_id,
            benchmark_name=func_name,
            success=True
        )
        
        # 预热
        for _ in range(warmup):
            try:
                func()
            except Exception:
                pass
        
        # 正式测试
        exec_times = []
        for i in range(iterations):
            start = time.time()
            try:
                func()
                end = time.time()
                exec_times.append((end - start) * 1000)  # 转换为毫秒
            except Exception as e:
                result.success = False
                result.details["error"] = str(e)
                break
        
        if result.success:
            result.execution_time_ms = statistics.mean(exec_times)
            result.metrics.append(
                PerformanceMetric(
                    metric_type=PerformanceMetricType.EXECUTION_TIME,
                    value=result.execution_time_ms,
                    unit="ms",
                    description=f"{func_name} 平均执行时间"
                )
            )
            
            if len(exec_times) > 1:
                result.metrics.append(
                    PerformanceMetric(
                        metric_type=PerformanceMetricType.EXECUTION_TIME,
                        value=statistics.stdev(exec_times),
                        unit="ms",
                        description=f"{func_name} 执行时间标准差"
                    )
                )
            
            result.metrics.append(
                PerformanceMetric(
                    metric_type=PerformanceMetricType.THROUGHPUT,
                    value=1000 / result.execution_time_ms if result.execution_time_ms > 0 else 0,
                    unit="ops/s",
                    description=f"{func_name} 吞吐量"
                )
            )
            
            result.details["iterations"] = iterations
            result.details["warmup"] = warmup
            result.details["min_time_ms"] = min(exec_times)
            result.details["max_time_ms"] = max(exec_times)
        
        result.end_time = datetime.now().isoformat()
        self.results.append(result)
        return result
    
    def benchmark_math_operations(self, iterations: int = 10000) -> BenchmarkResult:
        """数学运算基准测试"""
        def math_func():
            result = 0
            for i in range(100):
                result += i * 2
                result = result / 3
                result = result ** 2
            return result
        
        return self.benchmark_function(math_func, "数学运算", iterations=iterations)
    
    def benchmark_list_operations(self, iterations: int = 10000) -> BenchmarkResult:
        """列表操作基准测试"""
        def list_func():
            lst = list(range(100))
            lst.append(100)
            lst.pop()
            lst.reverse()
            lst.sort()
            return lst
        
        return self.benchmark_function(list_func, "列表操作", iterations=iterations)
    
    def benchmark_string_operations(self, iterations: int = 10000) -> BenchmarkResult:
        """字符串操作基准测试"""
        def string_func():
            s = "test string" * 10
            s = s.upper()
            s = s.lower()
            s = s.replace("t", "T")
            return s
        
        return self.benchmark_function(string_func, "字符串操作", iterations=iterations)
    
    def benchmark_dictionary_operations(self, iterations: int = 10000) -> BenchmarkResult:
        """字典操作基准测试"""
        def dict_func():
            d = {str(i): i for i in range(100)}
            d["key"] = "value"
            _ = d.get("key", None)
            d.pop("key", None)
            return d
        
        return self.benchmark_function(dict_func, "字典操作", iterations=iterations)
    
    def run_all_benchmarks(self) -> List[BenchmarkResult]:
        """运行所有基准测试"""
        print("🏃 开始运行系统基准测试...")
        self.benchmark_math_operations()
        self.benchmark_list_operations()
        self.benchmark_string_operations()
        self.benchmark_dictionary_operations()
        print("✅ 所有基准测试完成！")
        return self.results


class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self):
        self.analyzer_id = f"analyzer-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def analyze_benchmark_results(
        self, 
        results: List[BenchmarkResult]
    ) -> Dict[str, Any]:
        """分析基准测试结果"""
        if not results:
            return {"status": "no_data"}
        
        analysis = {
            "analyzer_id": self.analyzer_id,
            "timestamp": datetime.now().isoformat(),
            "total_benchmarks": len(results),
            "successful_benchmarks": sum(1 for r in results if r.success),
            "failed_benchmarks": sum(1 for r in results if not r.success),
            "average_execution_time_ms": statistics.mean([
                r.execution_time_ms for r in results if r.success
            ]) if results else 0,
            "individual_results": []
        }
        
        for result in results:
            analysis["individual_results"].append({
                "name": result.benchmark_name,
                "success": result.success,
                "execution_time_ms": result.execution_time_ms,
                "metrics": [
                    {
                        "type": m.metric_type.value,
                        "value": m.value,
                        "unit": m.unit,
                        "description": m.description
                    }
                    for m in result.metrics
                ]
            })
        
        return analysis
    
    def generate_optimization_suggestions(
        self,
        analysis: Dict[str, Any]
    ) -> List[OptimizationSuggestion]:
        """生成优化建议"""
        suggestions = []
        
        avg_time = analysis.get("average_execution_time_ms", 0)
        
        if avg_time > 50:
            suggestions.append(
                OptimizationSuggestion(
                    category="性能优化",
                    priority="高",
                    suggestion="考虑使用更高效的算法实现",
                    impact="可以显著提升系统性能",
                    complexity="中等"
                )
            )
        
        suggestions.append(
            OptimizationSuggestion(
                category="内存优化",
                priority="中",
                suggestion="对于频繁调用的函数，考虑使用缓存技术",
                impact="可以减少重复计算，提升响应速度",
                complexity="低"
            )
        )
        
        suggestions.append(
            OptimizationSuggestion(
                category="并发优化",
                priority="中",
                suggestion="对于可并行化的任务，考虑使用多线程或多进程",
                impact="可以充分利用多核CPU提升性能",
                complexity="高"
            )
        )
        
        suggestions.append(
            OptimizationSuggestion(
                category="代码优化",
                priority="低",
                suggestion="定期对热点代码进行性能分析和优化",
                impact="可以持续改善系统性能",
                complexity="中等"
            )
        )
        
        return suggestions


class PerformanceCLI:
    """性能命令行接口"""
    
    def __init__(self):
        self.benchmark = SystemBenchmark()
        self.analyzer = PerformanceAnalyzer()
    
    def run(self, args: List[str]) -> bool:
        """运行性能命令"""
        if not args:
            return self._show_help()
        
        command = args[0].lower()
        
        if command == "help":
            return self._show_help()
        elif command == "run":
            return self._run_benchmarks(args[1:])
        elif command == "analyze":
            return self._analyze_results()
        elif command == "suggestions":
            return self._show_suggestions()
        elif command == "test":
            return self._test_performance_system()
        else:
            print(f"❌ 未知命令: {command}")
            return False
    
    def _show_help(self) -> bool:
        """显示帮助"""
        help_text = """
🚀 性能基准测试命令:
  help                - 显示帮助信息
  run                 - 运行性能基准测试
  analyze             - 分析基准测试结果
  suggestions         - 显示优化建议
  test                - 测试性能系统

使用示例:
  # 运行基准测试
  python -m first_principle_agent perf run
  
  # 分析结果
  python -m first_principle_agent perf analyze
  
  # 显示优化建议
  python -m first_principle_agent perf suggestions
        """
        print(help_text)
        return True
    
    def _run_benchmarks(self, args: List[str]) -> bool:
        """运行基准测试"""
        print("\n🏃 运行系统性能基准测试...")
        print("=" * 80)
        
        try:
            results = self.benchmark.run_all_benchmarks()
            
            print("\n📊 基准测试结果:")
            print("-" * 80)
            for result in results:
                status = "✅" if result.success else "❌"
                print(f"{status} {result.benchmark_name}: {result.execution_time_ms:.3f} ms")
            
            print("\n✅ 基准测试完成！")
            return True
        except Exception as e:
            print(f"\n❌ 基准测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _analyze_results(self) -> bool:
        """分析基准测试结果"""
        if not self.benchmark.results:
            print("\n⚠️ 没有基准测试结果，请先运行 'perf run'")
            return False
        
        print("\n📈 分析基准测试结果...")
        print("=" * 80)
        
        try:
            analysis = self.analyzer.analyze_benchmark_results(self.benchmark.results)
            
            print(f"\n📋 分析ID: {analysis['analyzer_id']}")
            print(f"📊 总测试数: {analysis['total_benchmarks']}")
            print(f"✅ 成功: {analysis['successful_benchmarks']}")
            print(f"❌ 失败: {analysis['failed_benchmarks']}")
            print(f"⏱️  平均执行时间: {analysis['average_execution_time_ms']:.3f} ms")
            
            print(f"\n📊 详细结果:")
            for idx, result in enumerate(analysis["individual_results"], 1):
                status = "✅" if result["success"] else "❌"
                print(f"\n{idx}. {status} {result['name']}")
                print(f"   执行时间: {result['execution_time_ms']:.3f} ms")
                
                for metric in result["metrics"]:
                    print(f"   - {metric['description']}: {metric['value']:.3f} {metric['unit']}")
            
            print("\n✅ 分析完成！")
            return True
        except Exception as e:
            print(f"\n❌ 分析失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _show_suggestions(self) -> bool:
        """显示优化建议"""
        if not self.benchmark.results:
            print("\n⚠️ 没有基准测试结果，请先运行 'perf run'")
            return False
        
        print("\n💡 生成性能优化建议...")
        print("=" * 80)
        
        try:
            analysis = self.analyzer.analyze_benchmark_results(self.benchmark.results)
            suggestions = self.analyzer.generate_optimization_suggestions(analysis)
            
            if suggestions:
                for idx, suggestion in enumerate(suggestions, 1):
                    priority_emoji = "🔴" if suggestion.priority == "高" else "🟡" if suggestion.priority == "中" else "🟢"
                    print(f"\n{idx}. {priority_emoji} [{suggestion.category}] {suggestion.priority}")
                    print(f"   💡 建议: {suggestion.suggestion}")
                    print(f"   📈 影响: {suggestion.impact}")
                    print(f"   ⚙️  复杂度: {suggestion.complexity}")
            else:
                print("当前系统性能良好，没有特别的优化建议。")
            
            return True
        except Exception as e:
            print(f"\n❌ 生成建议失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _test_performance_system(self) -> bool:
        """测试性能系统"""
        print("\n🧪 测试性能基准测试系统...")
        print("=" * 80)
        
        try:
            # 测试基准测试创建
            print("✅ 系统基准测试器创建成功")
            
            # 运行少量测试
            print("\n🏃 运行小型基准测试...")
            math_result = self.benchmark.benchmark_math_operations(iterations=100)
            list_result = self.benchmark.benchmark_list_operations(iterations=100)
            
            print(f"✅ 数学运算测试完成: {math_result.execution_time_ms:.3f} ms")
            print(f"✅ 列表操作测试完成: {list_result.execution_time_ms:.3f} ms")
            
            # 测试分析器
            print("\n📊 测试结果分析...")
            analysis = self.analyzer.analyze_benchmark_results(self.benchmark.results)
            print(f"✅ 分析器工作正常")
            
            # 测试建议生成
            print("\n💡 测试建议生成...")
            suggestions = self.analyzer.generate_optimization_suggestions(analysis)
            print(f"✅ 生成了 {len(suggestions)} 条建议")
            
            print("\n" + "=" * 80)
            print("🎉 性能基准测试系统测试完成！")
            print("=" * 80)
            
            return True
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False


def create_benchmark() -> SystemBenchmark:
    """创建系统基准测试工厂函数"""
    return SystemBenchmark()


def create_performance_analyzer() -> PerformanceAnalyzer:
    """创建性能分析器工厂函数"""
    return PerformanceAnalyzer()
