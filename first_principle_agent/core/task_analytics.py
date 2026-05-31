"""
TaskAnalytics - 第55阶段：任务执行结果分析和报告系统
提供任务执行分析、指标收集、报告生成等功能
"""
import uuid
import time
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime


class AnalysisType(Enum):
    """分析类型"""
    PERFORMANCE = "performance"
    SUCCESS_RATE = "success_rate"
    EXECUTION_TIME = "execution_time"
    DEPENDENCY = "dependency"
    RESOURCE_USAGE = "resource_usage"
    PATTERN = "pattern"
    TREND = "trend"


class ReportFormat(Enum):
    """报告格式"""
    TEXT = "text"
    JSON = "json"
    HTML = "html"
    MARKDOWN = "markdown"
    SUMMARY = "summary"


@dataclass
class AnalysisResult:
    """分析结果"""
    analysis_id: str
    analysis_type: AnalysisType
    success: bool
    timestamp: float = field(default_factory=time.time)
    duration: float = 0.0
    metrics: Dict[str, Any] = field(default_factory=dict)
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def add_insight(self, insight: str):
        """添加洞察"""
        self.insights.append(insight)
    
    def add_recommendation(self, recommendation: str):
        """添加建议"""
        self.recommendations.append(recommendation)
    
    def add_warning(self, warning: str):
        """添加警告"""
        self.warnings.append(warning)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "analysis_id": self.analysis_id,
            "analysis_type": self.analysis_type.value,
            "success": self.success,
            "timestamp": self.timestamp,
            "duration": self.duration,
            "metrics": self.metrics,
            "insights": self.insights,
            "recommendations": self.recommendations,
            "warnings": self.warnings,
            "errors": self.errors
        }


@dataclass
class Report:
    """分析报告"""
    report_id: str
    title: str
    format: ReportFormat
    generated_at: float = field(default_factory=time.time)
    period_start: Optional[float] = None
    period_end: Optional[float] = None
    summary: str = ""
    sections: List[Dict[str, Any]] = field(default_factory=list)
    analysis_results: List[AnalysisResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_section(self, title: str, content: Any, section_type: str = "general"):
        """添加报告章节"""
        self.sections.append({
            "title": title,
            "type": section_type,
            "content": content
        })
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "title": self.title,
            "format": self.format.value,
            "generated_at": self.generated_at,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "summary": self.summary,
            "sections": self.sections,
            "analysis_results": [r.to_dict() for r in self.analysis_results],
            "metadata": self.metadata
        }
    
    def to_text(self) -> str:
        """转换为文本格式"""
        lines = [
            "=" * 80,
            f"{self.title}",
            "=" * 80,
            f"生成时间: {datetime.fromtimestamp(self.generated_at).strftime('%Y-%m-%d %H:%M:%S')}",
            f"报告ID: {self.report_id}",
            ""
        ]
        
        if self.period_start and self.period_end:
            lines.append(f"时间段: {datetime.fromtimestamp(self.period_start).strftime('%Y-%m-%d %H:%M:%S')} - {datetime.fromtimestamp(self.period_end).strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("")
        
        lines.append("-" * 80)
        lines.append("摘要")
        lines.append("-" * 80)
        lines.append(self.summary)
        lines.append("")
        
        for section in self.sections:
            lines.append("-" * 80)
            lines.append(section["title"])
            lines.append("-" * 80)
            lines.append(str(section["content"]))
            lines.append("")
        
        return "\n".join(lines)
    
    def to_markdown(self) -> str:
        """转换为Markdown格式"""
        lines = [
            f"# {self.title}",
            "",
            f"**生成时间**: {datetime.fromtimestamp(self.generated_at).strftime('%Y-%m-%d %H:%M:%S')}",
            f"**报告ID**: {self.report_id}",
            ""
        ]
        
        if self.period_start and self.period_end:
            lines.append(f"**时间段**: {datetime.fromtimestamp(self.period_start).strftime('%Y-%m-%d %H:%M:%S')} - {datetime.fromtimestamp(self.period_end).strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        lines.append("## 摘要")
        lines.append("")
        lines.append(self.summary)
        lines.append("")
        
        for section in self.sections:
            lines.append("---")
            lines.append("")
            lines.append(f"## {section['title']}")
            lines.append("")
            lines.append(str(section['content']))
            lines.append("")
        
        return "\n".join(lines)


class TaskMetricsCollector:
    """任务指标收集器"""
    
    def __init__(self):
        """初始化指标收集器"""
        self.metrics: Dict[str, List[float]] = defaultdict(list)
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = {}
        self.timestamps: Dict[str, List[float]] = defaultdict(list)
        self._start_time = time.time()
    
    def record_value(self, metric_name: str, value: float):
        """记录指标值"""
        self.metrics[metric_name].append(value)
        self.timestamps[metric_name].append(time.time())
    
    def increment_counter(self, counter_name: str, value: int = 1):
        """增加计数器"""
        self.counters[counter_name] += value
    
    def set_gauge(self, gauge_name: str, value: float):
        """设置仪表值"""
        self.gauges[gauge_name] = value
    
    def get_metric_stats(self, metric_name: str) -> Dict[str, float]:
        """获取指标统计"""
        values = self.metrics.get(metric_name, [])
        if not values:
            return {}
        
        sorted_values = sorted(values)
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / len(values),
            "median": sorted_values[len(values) // 2],
            "p95": sorted_values[int(len(values) * 0.95)] if len(values) > 1 else sorted_values[0],
            "p99": sorted_values[int(len(values) * 0.99)] if len(values) > 1 else sorted_values[0]
        }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """获取所有指标"""
        return {
            "metrics": {name: self.get_metric_stats(name) for name in self.metrics.keys()},
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "uptime": time.time() - self._start_time
        }


class TaskAnalytics:
    """任务分析引擎"""
    
    def __init__(self):
        """初始化分析引擎"""
        self.results: List[AnalysisResult] = []
        self.collector = TaskMetricsCollector()
    
    def analyze_success_rate(
        self,
        total_tasks: int,
        successful_tasks: int,
        failed_tasks: int
    ) -> AnalysisResult:
        """分析成功率"""
        analysis_id = str(uuid.uuid4())
        start_time = time.time()
        
        result = AnalysisResult(
            analysis_id=analysis_id,
            analysis_type=AnalysisType.SUCCESS_RATE,
            success=True
        )
        
        if total_tasks == 0:
            result.success = False
            result.errors.append("No tasks to analyze")
            return result
        
        success_rate = (successful_tasks / total_tasks) * 100
        failure_rate = (failed_tasks / total_tasks) * 100
        
        result.metrics = {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": success_rate,
            "failure_rate": failure_rate
        }
        
        if success_rate >= 95:
            result.add_insight(f"任务成功率为 {success_rate:.2f}%，表现优秀")
        elif success_rate >= 80:
            result.add_insight(f"任务成功率为 {success_rate:.2f}%，表现良好")
        else:
            result.add_insight(f"任务成功率仅为 {success_rate:.2f}%，需要改进")
            result.add_warning(f"成功率低于80%，建议检查失败原因")
            result.add_recommendation("建议增加重试机制和错误处理")
        
        result.duration = time.time() - start_time
        self.results.append(result)
        return result
    
    def analyze_execution_time(
        self,
        execution_times: List[float]
    ) -> AnalysisResult:
        """分析执行时间"""
        analysis_id = str(uuid.uuid4())
        start_time = time.time()
        
        result = AnalysisResult(
            analysis_id=analysis_id,
            analysis_type=AnalysisType.EXECUTION_TIME,
            success=True
        )
        
        if not execution_times:
            result.success = False
            result.errors.append("No execution times to analyze")
            return result
        
        sorted_times = sorted(execution_times)
        n = len(sorted_times)
        
        avg_time = sum(execution_times) / n
        min_time = min(execution_times)
        max_time = max(execution_times)
        median_time = sorted_times[n // 2]
        p95_time = sorted_times[int(n * 0.95)]
        
        variance = sum((t - avg_time) ** 2 for t in execution_times) / n
        std_dev = variance ** 0.5
        
        result.metrics = {
            "count": n,
            "min": min_time,
            "max": max_time,
            "mean": avg_time,
            "median": median_time,
            "p95": p95_time,
            "std_dev": std_dev,
            "total": sum(execution_times)
        }
        
        if std_dev / avg_time > 0.5:
            result.add_insight(f"执行时间波动较大（标准差/均值={std_dev/avg_time:.2f}）")
            result.add_warning("执行时间不稳定，可能存在资源争用或网络延迟")
            result.add_recommendation("建议优化任务分配和资源管理")
        else:
            result.add_insight(f"执行时间相对稳定")
        
        if max_time > avg_time * 3:
            result.add_warning(f"存在异常慢的任务（最大时间是最小时间的 {max_time/min_time:.1f} 倍）")
            result.add_recommendation("建议识别并优化慢任务")
        
        result.duration = time.time() - start_time
        self.results.append(result)
        return result
    
    def analyze_performance(
        self,
        throughput: float,
        latency: float,
        error_rate: float
    ) -> AnalysisResult:
        """分析性能"""
        analysis_id = str(uuid.uuid4())
        start_time = time.time()
        
        result = AnalysisResult(
            analysis_id=analysis_id,
            analysis_type=AnalysisType.PERFORMANCE,
            success=True
        )
        
        result.metrics = {
            "throughput": throughput,
            "latency": latency,
            "error_rate": error_rate
        }
        
        if error_rate < 0.01:
            result.add_insight(f"错误率为 {error_rate*100:.2f}%，表现优秀")
        elif error_rate < 0.05:
            result.add_insight(f"错误率为 {error_rate*100:.2f}%，在可接受范围内")
        else:
            result.add_insight(f"错误率为 {error_rate*100:.2f}%，偏高")
            result.add_warning("错误率超过5%，需要优化")
            result.add_recommendation("建议增加错误处理和重试机制")
        
        if latency < 100:
            result.add_insight(f"延迟为 {latency:.2f}ms，性能优秀")
        elif latency < 500:
            result.add_insight(f"延迟为 {latency:.2f}ms，性能良好")
        else:
            result.add_insight(f"延迟为 {latency:.2f}ms，偏高")
            result.add_warning("延迟超过500ms，可能影响用户体验")
            result.add_recommendation("建议优化关键路径和减少不必要的等待")
        
        result.duration = time.time() - start_time
        self.results.append(result)
        return result
    
    def analyze_trend(
        self,
        historical_data: Dict[str, List[float]],
        metric_name: str
    ) -> AnalysisResult:
        """分析趋势"""
        analysis_id = str(uuid.uuid4())
        start_time = time.time()
        
        result = AnalysisResult(
            analysis_id=analysis_id,
            analysis_type=AnalysisType.TREND,
            success=True
        )
        
        if metric_name not in historical_data or not historical_data[metric_name]:
            result.success = False
            result.errors.append(f"No historical data for metric: {metric_name}")
            return result
        
        data = historical_data[metric_name]
        if len(data) < 2:
            result.success = False
            result.errors.append("Not enough data points for trend analysis")
            return result
        
        first_half = data[:len(data)//2]
        second_half = data[len(data)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        trend_ratio = second_avg / first_avg if first_avg != 0 else 1.0
        change_percent = (trend_ratio - 1.0) * 100
        
        result.metrics = {
            "metric_name": metric_name,
            "data_points": len(data),
            "first_half_avg": first_avg,
            "second_half_avg": second_avg,
            "change_percent": change_percent,
            "trend_direction": "increasing" if trend_ratio > 1.05 else "decreasing" if trend_ratio < 0.95 else "stable"
        }
        
        if abs(change_percent) < 5:
            result.add_insight(f"{metric_name} 保持稳定")
        elif change_percent > 0:
            result.add_insight(f"{metric_name} 呈现上升趋势 (+{change_percent:.1f}%)")
            result.add_recommendation("如果这是负面指标，考虑优化以降低")
        else:
            result.add_insight(f"{metric_name} 呈现下降趋势 ({change_percent:.1f}%)")
            result.add_recommendation("如果这是正面指标，继续保持")
        
        result.duration = time.time() - start_time
        self.results.append(result)
        return result
    
    def get_all_results(self) -> List[AnalysisResult]:
        """获取所有分析结果"""
        return self.results


class TaskReportGenerator:
    """报告生成器"""
    
    def __init__(self, analytics: Optional[TaskAnalytics] = None):
        """初始化报告生成器"""
        self.analytics = analytics or TaskAnalytics()
    
    def generate_summary_report(
        self,
        title: str = "任务执行摘要报告"
    ) -> Report:
        """生成摘要报告"""
        report_id = str(uuid.uuid4())
        
        report = Report(
            report_id=report_id,
            title=title,
            format=ReportFormat.SUMMARY
        )
        
        if self.analytics.results:
            insights_text = "\n".join([
                f"- {insight}"
                for result in self.analytics.results
                for insight in result.insights
            ])
            recommendations_text = "\n".join([
                f"- {rec}"
                for result in self.analytics.results
                for rec in result.recommendations
            ])
            
            report.summary = f"共完成 {len(self.analytics.results)} 项分析\n\n主要洞察：\n{insights_text}\n\n建议：\n{recommendations_text}"
        else:
            report.summary = "暂无分析数据"
        
        report.add_section(
            "分析概览",
            f"共执行 {len(self.analytics.results)} 项分析",
            "summary"
        )
        
        metrics = self.analytics.collector.get_all_metrics()
        report.add_section(
            "指标统计",
            str(metrics),
            "metrics"
        )
        
        return report
    
    def generate_detailed_report(
        self,
        title: str = "任务执行详细报告",
        format: ReportFormat = ReportFormat.MARKDOWN
    ) -> Report:
        """生成详细报告"""
        report_id = str(uuid.uuid4())
        
        report = Report(
            report_id=report_id,
            title=title,
            format=format
        )
        
        report.add_section(
            "摘要",
            self.generate_summary_report().summary,
            "summary"
        )
        
        for result in self.analytics.results:
            section_content = [
                f"**分析类型**: {result.analysis_type.value}",
                f"**状态**: {'成功' if result.success else '失败'}",
                f"**耗时**: {result.duration:.4f}秒",
                "",
                "**指标**:",
                str(result.metrics),
                ""
            ]
            
            if result.insights:
                section_content.append("**洞察**:")
                for insight in result.insights:
                    section_content.append(f"- {insight}")
                section_content.append("")
            
            if result.recommendations:
                section_content.append("**建议**:")
                for rec in result.recommendations:
                    section_content.append(f"- {rec}")
                section_content.append("")
            
            if result.warnings:
                section_content.append("**警告**:")
                for warning in result.warnings:
                    section_content.append(f"- {warning}")
                section_content.append("")
            
            report.add_section(
                f"分析 - {result.analysis_type.value}",
                "\n".join(section_content),
                result.analysis_type.value
            )
            report.analysis_results.append(result)
        
        report.add_section(
            "指标详情",
            str(self.analytics.collector.get_all_metrics()),
            "metrics"
        )
        
        return report
    
    def export_report(
        self,
        report: Report,
        format: ReportFormat = ReportFormat.MARKDOWN
    ) -> str:
        """导出报告"""
        if format == ReportFormat.TEXT:
            return report.to_text()
        elif format == ReportFormat.MARKDOWN:
            return report.to_markdown()
        elif format == ReportFormat.JSON:
            import json
            return json.dumps(report.to_dict(), indent=2, ensure_ascii=False)
        else:
            return str(report.to_dict())


def create_analytics_system() -> tuple:
    """
    创建分析系统工厂函数
    
    Returns:
        (TaskAnalytics, TaskReportGenerator): 分析引擎和报告生成器
    """
    analytics = TaskAnalytics()
    generator = TaskReportGenerator(analytics)
    return analytics, generator
