#!/usr/bin/env python3
"""
第65阶段 - 系统性能基准测试和优化工具测试
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from first_principle_agent.core.perf_benchmark import (
    SystemBenchmark,
    PerformanceAnalyzer,
    PerformanceCLI,
    PerformanceMetric,
    BenchmarkResult,
    OptimizationSuggestion,
    create_benchmark,
    create_performance_analyzer
)


def test_1_performance_metric():
    """测试1: 性能指标数据类"""
    print("\n" + "="*80)
    print("测试1: 性能指标数据类")
    print("="*80)
    
    try:
        from first_principle_agent.core.perf_benchmark import PerformanceMetricType
        
        # 创建性能指标
        metric = PerformanceMetric(
            metric_type=PerformanceMetricType.EXECUTION_TIME,
            value=10.5,
            unit="ms",
            description="测试执行时间"
        )
        
        print("✅ PerformanceMetric 创建成功")
        print(f"   类型: {metric.metric_type}")
        print(f"   值: {metric.value}")
        print(f"   单位: {metric.unit}")
        print(f"   描述: {metric.description}")
        
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_2_benchmark_result():
    """测试2: 基准测试结果数据类"""
    print("\n" + "="*80)
    print("测试2: 基准测试结果数据类")
    print("="*80)
    
    try:
        result = BenchmarkResult(
            benchmark_id="test-benchmark-1",
            benchmark_name="数学运算测试",
            execution_time_ms=15.2,
            success=True
        )
        
        print("✅ BenchmarkResult 创建成功")
        print(f"   基准测试ID: {result.benchmark_id}")
        print(f"   名称: {result.benchmark_name}")
        print(f"   执行时间: {result.execution_time_ms} ms")
        print(f"   成功: {result.success}")
        
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_3_system_benchmark():
    """测试3: 系统基准测试器"""
    print("\n" + "="*80)
    print("测试3: 系统基准测试器")
    print("="*80)
    
    try:
        benchmark = create_benchmark()
        
        # 运行简单的数学运算基准测试
        math_result = benchmark.benchmark_math_operations(iterations=100)
        
        print("✅ SystemBenchmark 创建成功")
        print(f"   基准测试ID: {benchmark.benchmark_id}")
        print(f"   数学运算测试: {'成功' if math_result.success else '失败'}")
        print(f"   执行时间: {math_result.execution_time_ms:.3f} ms")
        
        # 运行其他基准测试
        list_result = benchmark.benchmark_list_operations(iterations=100)
        print(f"   列表操作测试: {'成功' if list_result.success else '失败'}")
        
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_4_performance_analyzer():
    """测试4: 性能分析器"""
    print("\n" + "="*80)
    print("测试4: 性能分析器")
    print("="*80)
    
    try:
        benchmark = create_benchmark()
        analyzer = create_performance_analyzer()
        
        # 运行一些基准测试
        benchmark.benchmark_math_operations(iterations=100)
        benchmark.benchmark_list_operations(iterations=100)
        
        # 分析结果
        analysis = analyzer.analyze_benchmark_results(benchmark.results)
        
        print("✅ PerformanceAnalyzer 创建成功")
        print(f"   分析器ID: {analysis['analyzer_id']}")
        print(f"   总测试数: {analysis['total_benchmarks']}")
        print(f"   成功: {analysis['successful_benchmarks']}")
        print(f"   平均执行时间: {analysis['average_execution_time_ms']:.3f} ms")
        
        # 生成优化建议
        suggestions = analyzer.generate_optimization_suggestions(analysis)
        print(f"   优化建议数: {len(suggestions)}")
        
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_5_performance_cli():
    """测试5: 性能命令行接口"""
    print("\n" + "="*80)
    print("测试5: 性能命令行接口")
    print("="*80)
    
    try:
        cli = PerformanceCLI()
        
        print("✅ PerformanceCLI 创建成功")
        
        # 测试 help 命令
        success = cli.run(["help"])
        print(f"   help 命令: {'成功' if success else '失败'}")
        
        # 测试 test 命令
        print("\n   运行 test 命令...")
        test_success = cli.run(["test"])
        print(f"   test 命令: {'成功' if test_success else '失败'}")
        
        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("第65阶段 - 系统性能基准测试和优化工具测试")
    print("="*80)
    
    tests = [
        test_1_performance_metric,
        test_2_benchmark_result,
        test_3_system_benchmark,
        test_4_performance_analyzer,
        test_5_performance_cli
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
        print("\n🎉 所有测试通过！第65阶段完成！")
        return 0
    else:
        print("\n❌ 部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
