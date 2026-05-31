import unittest
import time

from first_principle_agent.core.task_pipeline import (
    TaskPipeline,
    PipelineConfig,
    PipelineStatus,
    PipelineStageType,
    PipelineStage,
    PipelineResult,
    PipelineStageResult,
    create_pipeline
)
from first_principle_agent.core.task_tuple import TaskTuple
from first_principle_agent.core.task_execution_engine import ExecutionStatus


class TestTaskPipeline(unittest.TestCase):
    """测试任务管道"""

    def test_pipeline_creation(self):
        """测试管道创建"""
        pipeline = create_pipeline("test-pipeline")
        
        self.assertIsNotNone(pipeline.id)
        self.assertEqual(pipeline.name, "test-pipeline")
        self.assertEqual(pipeline.status, PipelineStatus.IDLE)
        self.assertEqual(len(pipeline.stages), 0)
        
        pipeline.reset()

    def test_add_stage_chained(self):
        """测试链式添加阶段"""
        pipeline = create_pipeline("chained-pipeline")
        
        # 链式调用添加阶段
        pipeline.add_stage("stage1").add_stage("stage2").add_stage("stage3")
        
        self.assertEqual(len(pipeline.stages), 3)
        pipeline.reset()

    def test_execute_simple_pipeline(self):
        """测试简单管道执行"""
        pipeline = create_pipeline("simple-pipeline")
        
        # 添加任务阶段
        pipeline.add_stage(
            "add-one",
            task=lambda x: x + 1
        ).add_stage(
            "double",
            task=lambda x: x * 2
        ).add_stage(
            "add-ten",
            task=lambda x: x + 10
        )
        
        result = pipeline.execute(5)
        
        self.assertEqual(result.status, PipelineStatus.COMPLETED)
        self.assertEqual(result.final_output, 22)  # ((5+1)*2)+10 = 22
        self.assertEqual(len(result.stage_results), 3)
        
        pipeline.reset()

    def test_transform_stage(self):
        """测试转换阶段"""
        pipeline = create_pipeline("transform-pipeline")
        
        pipeline.add_stage(
            "uppercase",
            transform=lambda s: s.upper(),
            stage_type=PipelineStageType.TRANSFORM
        ).add_stage(
            "add-suffix",
            transform=lambda s: s + "-DONE",
            stage_type=PipelineStageType.TRANSFORM
        )
        
        result = pipeline.execute("hello")
        
        self.assertEqual(result.final_output, "HELLO-DONE")
        pipeline.reset()

    def test_conditional_stage_true(self):
        """测试条件分支（真分支）"""
        pipeline = create_pipeline("conditional-pipeline")
        
        # 创建条件阶段
        true_stage = PipelineStage(
            id="true-stage",
            name="true-action",
            stage_type=PipelineStageType.TASK,
            task=lambda x: x * 100
        )
        
        false_stage = PipelineStage(
            id="false-stage",
            name="false-action",
            stage_type=PipelineStageType.TASK,
            task=lambda x: x * -1
        )
        
        pipeline.add_stage(
            "initial",
            task=lambda x: x
        ).add_conditional(
            "check-positive",
            condition=lambda x: x > 0,
            true_stage=true_stage,
            false_stage=false_stage
        )
        
        result = pipeline.execute(42)
        
        self.assertEqual(result.final_output, 4200)
        pipeline.reset()

    def test_conditional_stage_false(self):
        """测试条件分支（假分支）"""
        pipeline = create_pipeline("conditional-pipeline-false")
        
        true_stage = PipelineStage(
            id="true",
            name="true",
            stage_type=PipelineStageType.TASK,
            task=lambda x: x * 100
        )
        
        false_stage = PipelineStage(
            id="false",
            name="false",
            stage_type=PipelineStageType.TASK,
            task=lambda x: x * -1
        )
        
        pipeline.add_conditional(
            "check",
            condition=lambda x: x > 0,
            true_stage=true_stage,
            false_stage=false_stage
        )
        
        result = pipeline.execute(-5)
        
        self.assertEqual(result.final_output, 5)
        pipeline.reset()

    def test_retry_on_failure(self):
        """测试失败重试"""
        pipeline = create_pipeline("retry-pipeline")
        
        # 模拟偶尔失败的函数
        attempts = {"count": 0}
        
        def flaky_func(x):
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise ValueError("Temporary failure")
            return x * 2
        
        pipeline.add_stage(
            "flaky",
            task=flaky_func,
            retry_on_failure=True,
            max_retries=3
        )
        
        result = pipeline.execute(10)
        
        self.assertEqual(result.status, PipelineStatus.COMPLETED)
        self.assertEqual(result.final_output, 20)
        self.assertEqual(attempts["count"], 3)
        
        pipeline.reset()

    def test_stop_on_failure(self):
        """测试失败时停止"""
        config = PipelineConfig(stop_on_failure=True, propagate_exceptions=False)
        pipeline = create_pipeline("stop-pipeline", config)
        
        pipeline.add_stage(
            "ok",
            task=lambda x: x + 1
        ).add_stage(
            "fail",
            task=lambda x: 1 / 0  # Division by zero
        ).add_stage(
            "never-reached",
            task=lambda x: x * 100
        )
        
        result = pipeline.execute(5)
        
        self.assertEqual(result.status, PipelineStatus.FAILED)
        self.assertEqual(len(result.stage_results), 2)
        self.assertEqual(result.stage_results[0].status, ExecutionStatus.COMPLETED)
        self.assertEqual(result.stage_results[1].status, ExecutionStatus.FAILED)
        
        pipeline.reset()

    def test_execution_history(self):
        """测试执行历史"""
        pipeline = create_pipeline("history-pipeline")
        
        pipeline.add_stage("inc", task=lambda x: x + 1)
        
        # 执行两次
        pipeline.execute(1)
        pipeline.execute(2)
        
        history = pipeline.get_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].final_output, 2)
        self.assertEqual(history[1].final_output, 3)
        
        pipeline.reset()

    def test_get_current_result(self):
        """测试获取当前结果"""
        pipeline = create_pipeline("current-result-pipeline")
        
        pipeline.add_stage("test", task=lambda x: x * 2)
        
        pipeline.execute(5)
        current_result = pipeline.get_current_result()
        
        self.assertIsNotNone(current_result)
        self.assertEqual(current_result.final_output, 10)
        
        pipeline.reset()

    def test_remove_stage(self):
        """测试移除阶段"""
        pipeline = create_pipeline("remove-stage-pipeline")
        
        pipeline.add_stage("stage1").add_stage("stage2").add_stage("stage3")
        self.assertEqual(len(pipeline.stages), 3)
        
        stage_id = pipeline.stages[1].id
        success = pipeline.remove_stage(stage_id)
        
        self.assertTrue(success)
        self.assertEqual(len(pipeline.stages), 2)
        
        pipeline.reset()

    def test_clear_stages(self):
        """测试清空阶段"""
        pipeline = create_pipeline("clear-pipeline")
        
        pipeline.add_stage("s1").add_stage("s2").add_stage("s3")
        self.assertEqual(len(pipeline.stages), 3)
        
        pipeline.clear_stages()
        self.assertEqual(len(pipeline.stages), 0)
        
        pipeline.reset()

    def test_empty_pipeline(self):
        """测试空管道执行"""
        pipeline = create_pipeline("empty-pipeline")
        
        result = pipeline.execute(42)
        
        self.assertEqual(result.status, PipelineStatus.COMPLETED)
        self.assertEqual(result.final_output, 42)
        
        pipeline.reset()


class TestPipelineConfig(unittest.TestCase):
    """测试管道配置"""

    def test_config_defaults(self):
        """测试默认配置"""
        config = PipelineConfig()
        
        self.assertTrue(config.stop_on_failure)
        self.assertTrue(config.propagate_exceptions)
        self.assertFalse(config.enable_parallel_stages)
        self.assertEqual(config.max_parallel_stages, 4)

    def test_config_serialization(self):
        """测试配置序列化"""
        config = PipelineConfig(
            stop_on_failure=False,
            enable_parallel_stages=True,
            max_parallel_stages=8
        )
        
        data = config.to_dict()
        restored = PipelineConfig.from_dict(data)
        
        self.assertFalse(restored.stop_on_failure)
        self.assertTrue(restored.enable_parallel_stages)
        self.assertEqual(restored.max_parallel_stages, 8)


class TestPipelineResult(unittest.TestCase):
    """测试管道结果"""

    def test_result_serialization(self):
        """测试结果序列化"""
        result = PipelineResult(
            pipeline_id="test-pipeline",
            status=PipelineStatus.COMPLETED,
            start_time=time.time(),
            end_time=time.time() + 10,
            total_time=10.0,
            final_output="SUCCESS"
        )
        
        data = result.to_dict()
        restored = PipelineResult.from_dict(data)
        
        self.assertEqual(restored.pipeline_id, "test-pipeline")
        self.assertEqual(restored.status, PipelineStatus.COMPLETED)


class TestPipelineStage(unittest.TestCase):
    """测试管道阶段"""

    def test_stage_serialization(self):
        """测试阶段序列化"""
        stage = PipelineStage(
            id="test-stage",
            name="Test Stage",
            stage_type=PipelineStageType.TASK,
            enabled=True,
            retry_on_failure=True,
            max_retries=3
        )
        
        data = stage.to_dict()
        restored = PipelineStage.from_dict(data)
        
        self.assertEqual(restored.id, "test-stage")
        self.assertEqual(restored.name, "Test Stage")
        self.assertEqual(restored.stage_type, PipelineStageType.TASK)
        self.assertTrue(restored.retry_on_failure)


if __name__ == "__main__":
    unittest.main()
