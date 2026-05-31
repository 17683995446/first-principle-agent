"""
测试第55阶段：TaskAnalytics任务执行结果分析和报告系统
"""
import unittest
import time
from first_principle_agent.core import (
    TaskAnalytics,
    TaskMetricsCollector,
    TaskReportGenerator,
    AnalysisResult,
    Report,
    AnalysisType,
    ReportFormat,
    create_analytics_system
)


class TestTaskMetricsCollector(unittest.TestCase):
    """TaskMetricsCollector测试"""
    
    def setUp(self):
        """测试前准备"""
        self.collector = TaskMetricsCollector()
    
    def test_record_value(self):
        """测试记录指标值"""
        self.collector.record_value("test_metric", 100.0)
        self.collector.record_value("test_metric", 200.0)
        
        stats = self.collector.get_metric_stats("test_metric")
        
        self.assertEqual(stats["count"], 2)
        self.assertEqual(stats["min"], 100.0)
        self.assertEqual(stats["max"], 200.0)
        self.assertEqual(stats["mean"], 150.0)
    
    def test_increment_counter(self):
        """测试增加计数器"""
        self.collector.increment_counter("test_counter")
        self.collector.increment_counter("test_counter", 5)
        
        self.assertEqual(self.collector.counters["test_counter"], 6)
    
    def test_set_gauge(self):
        """测试设置仪表值"""
        self.collector.set_gauge("test_gauge", 42.5)
        
        self.assertEqual(self.collector.gauges["test_gauge"], 42.5)
    
    def test_get_all_metrics(self):
        """测试获取所有指标"""
        self.collector.record_value("metric1", 10.0)
        self.collector.increment_counter("counter1")
        self.collector.set_gauge("gauge1", 100.0)
        
        all_metrics = self.collector.get_all_metrics()
        
        self.assertIn("metrics", all_metrics)
        self.assertIn("counters", all_metrics)
        self.assertIn("gauges", all_metrics)
        self.assertIn("uptime", all_metrics)
        self.assertEqual(all_metrics["counters"]["counter1"], 1)
        self.assertEqual(all_metrics["gauges"]["gauge1"], 100.0)


class TestTaskAnalytics(unittest.TestCase):
    """TaskAnalytics测试"""
    
    def setUp(self):
        """测试前准备"""
        self.analytics = TaskAnalytics()
    
    def test_analyze_success_rate(self):
        """测试分析成功率"""
        result = self.analytics.analyze_success_rate(
            total_tasks=100,
            successful_tasks=95,
            failed_tasks=5
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.analysis_type, AnalysisType.SUCCESS_RATE)
        self.assertEqual(result.metrics["success_rate"], 95.0)
        self.assertGreater(len(result.insights), 0)
    
    def test_analyze_success_rate_zero_tasks(self):
        """测试分析零任务"""
        result = self.analytics.analyze_success_rate(
            total_tasks=0,
            successful_tasks=0,
            failed_tasks=0
        )
        
        self.assertFalse(result.success)
        self.assertIn("No tasks to analyze", result.errors)
    
    def test_analyze_execution_time(self):
        """测试分析执行时间"""
        execution_times = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = self.analytics.analyze_execution_time(execution_times)
        
        self.assertTrue(result.success)
        self.assertEqual(result.analysis_type, AnalysisType.EXECUTION_TIME)
        self.assertEqual(result.metrics["mean"], 3.0)
        self.assertEqual(result.metrics["min"], 1.0)
        self.assertEqual(result.metrics["max"], 5.0)
    
    def test_analyze_execution_time_empty(self):
        """测试分析空执行时间"""
        result = self.analytics.analyze_execution_time([])
        
        self.assertFalse(result.success)
        self.assertIn("No execution times to analyze", result.errors)
    
    def test_analyze_performance(self):
        """测试分析性能"""
        result = self.analytics.analyze_performance(
            throughput=100.0,
            latency=50.0,
            error_rate=0.01
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.analysis_type, AnalysisType.PERFORMANCE)
        self.assertEqual(result.metrics["throughput"], 100.0)
        self.assertGreater(len(result.insights), 0)
    
    def test_analyze_trend(self):
        """测试分析趋势"""
        historical_data = {
            "requests": [10, 20, 30, 40, 50]
        }
        result = self.analytics.analyze_trend(historical_data, "requests")
        
        self.assertTrue(result.success)
        self.assertEqual(result.analysis_type, AnalysisType.TREND)
        self.assertGreater(result.metrics["change_percent"], 0)
    
    def test_analyze_trend_insufficient_data(self):
        """测试趋势分析数据不足"""
        historical_data = {
            "requests": [10]
        }
        result = self.analytics.analyze_trend(historical_data, "requests")
        
        self.assertFalse(result.success)
    
    def test_get_all_results(self):
        """测试获取所有结果"""
        self.analytics.analyze_success_rate(100, 90, 10)
        self.analytics.analyze_execution_time([1.0, 2.0, 3.0])
        
        results = self.analytics.get_all_results()
        
        self.assertEqual(len(results), 2)


class TestTaskReportGenerator(unittest.TestCase):
    """TaskReportGenerator测试"""
    
    def setUp(self):
        """测试前准备"""
        self.analytics = TaskAnalytics()
        self.generator = TaskReportGenerator(self.analytics)
    
    def test_generate_summary_report(self):
        """测试生成摘要报告"""
        self.analytics.analyze_success_rate(100, 90, 10)
        
        report = self.generator.generate_summary_report(
            title="测试摘要报告"
        )
        
        self.assertEqual(report.title, "测试摘要报告")
        self.assertEqual(report.format, ReportFormat.SUMMARY)
        self.assertGreater(len(report.sections), 0)
    
    def test_generate_detailed_report(self):
        """测试生成详细报告"""
        self.analytics.analyze_success_rate(100, 90, 10)
        self.analytics.analyze_performance(100.0, 50.0, 0.01)
        
        report = self.generator.generate_detailed_report(
            title="测试详细报告",
            format=ReportFormat.MARKDOWN
        )
        
        self.assertEqual(report.title, "测试详细报告")
        self.assertEqual(report.format, ReportFormat.MARKDOWN)
        self.assertEqual(len(report.analysis_results), 2)
        self.assertGreater(len(report.sections), 0)
    
    def test_export_report_text(self):
        """测试导出文本报告"""
        report = self.generator.generate_summary_report()
        
        text = self.generator.export_report(report, ReportFormat.TEXT)
        
        self.assertIsInstance(text, str)
        self.assertIn("=", text)
        self.assertIn(report.title, text)
    
    def test_export_report_markdown(self):
        """测试导出Markdown报告"""
        report = self.generator.generate_summary_report()
        
        markdown = self.generator.export_report(report, ReportFormat.MARKDOWN)
        
        self.assertIsInstance(markdown, str)
        self.assertIn("#", markdown)
        self.assertIn(report.title, markdown)
    
    def test_export_report_json(self):
        """测试导出JSON报告"""
        report = self.generator.generate_summary_report()
        
        json_str = self.generator.export_report(report, ReportFormat.JSON)
        
        self.assertIsInstance(json_str, str)
        self.assertIn("report_id", json_str)


class TestAnalysisResult(unittest.TestCase):
    """AnalysisResult测试"""
    
    def test_add_insight(self):
        """测试添加洞察"""
        result = AnalysisResult(
            analysis_id="test-1",
            analysis_type=AnalysisType.SUCCESS_RATE,
            success=True
        )
        
        result.add_insight("测试洞察")
        
        self.assertEqual(len(result.insights), 1)
        self.assertEqual(result.insights[0], "测试洞察")
    
    def test_add_recommendation(self):
        """测试添加建议"""
        result = AnalysisResult(
            analysis_id="test-1",
            analysis_type=AnalysisType.SUCCESS_RATE,
            success=True
        )
        
        result.add_recommendation("测试建议")
        
        self.assertEqual(len(result.recommendations), 1)
        self.assertEqual(result.recommendations[0], "测试建议")
    
    def test_add_warning(self):
        """测试添加警告"""
        result = AnalysisResult(
            analysis_id="test-1",
            analysis_type=AnalysisType.SUCCESS_RATE,
            success=True
        )
        
        result.add_warning("测试警告")
        
        self.assertEqual(len(result.warnings), 1)
        self.assertEqual(result.warnings[0], "测试警告")
    
    def test_to_dict(self):
        """测试转换为字典"""
        result = AnalysisResult(
            analysis_id="test-1",
            analysis_type=AnalysisType.SUCCESS_RATE,
            success=True
        )
        result.add_insight("测试洞察")
        
        result_dict = result.to_dict()
        
        self.assertIn("analysis_id", result_dict)
        self.assertIn("analysis_type", result_dict)
        self.assertIn("insights", result_dict)


class TestReport(unittest.TestCase):
    """Report测试"""
    
    def test_add_section(self):
        """测试添加章节"""
        report = Report(
            report_id="test-1",
            title="测试报告",
            format=ReportFormat.SUMMARY
        )
        
        report.add_section("测试章节", "测试内容")
        
        self.assertEqual(len(report.sections), 1)
        self.assertEqual(report.sections[0]["title"], "测试章节")
        self.assertEqual(report.sections[0]["content"], "测试内容")
    
    def test_to_text(self):
        """测试转换为文本"""
        report = Report(
            report_id="test-1",
            title="测试报告",
            format=ReportFormat.TEXT
        )
        report.add_section("测试章节", "测试内容")
        
        text = report.to_text()
        
        self.assertIn("测试报告", text)
        self.assertIn("测试章节", text)
        self.assertIn("测试内容", text)
    
    def test_to_markdown(self):
        """测试转换为Markdown"""
        report = Report(
            report_id="test-1",
            title="测试报告",
            format=ReportFormat.MARKDOWN
        )
        report.add_section("测试章节", "测试内容")
        
        markdown = report.to_markdown()
        
        self.assertIn("# 测试报告", markdown)
        self.assertIn("## 测试章节", markdown)
        self.assertIn("测试内容", markdown)


class TestCreateAnalyticsSystem(unittest.TestCase):
    """create_analytics_system测试"""
    
    def test_create_analytics_system(self):
        """测试创建分析系统"""
        analytics, generator = create_analytics_system()
        
        self.assertIsInstance(analytics, TaskAnalytics)
        self.assertIsInstance(generator, TaskReportGenerator)
        self.assertEqual(analytics, generator.analytics)


if __name__ == '__main__':
    unittest.main()
