"""
测试第56阶段：TaskWorkflowExecutor任务工作流编排器
"""
import unittest
from first_principle_agent.core import (
    TaskWorkflowExecutor,
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowStep,
    WorkflowContext,
    WorkflowStatus,
    WorkflowStepType,
    WorkflowStepStatus,
    WorkflowMetrics,
    create_workflow_executor
)


class TestWorkflowStep(unittest.TestCase):
    """WorkflowStep测试"""
    
    def test_workflow_step_creation(self):
        """测试工作流步骤创建"""
        step = WorkflowStep(
            step_id="step-1",
            name="Test Step",
            step_type=WorkflowStepType.TASK
        )
        
        self.assertEqual(step.step_id, "step-1")
        self.assertEqual(step.name, "Test Step")
        self.assertEqual(step.step_type, WorkflowStepType.TASK)
        self.assertEqual(step.status, WorkflowStepStatus.PENDING)
    
    def test_can_execute(self):
        """测试检查是否可以执行"""
        step = WorkflowStep(
            step_id="step-1",
            name="Test Step",
            step_type=WorkflowStepType.TASK
        )
        
        self.assertTrue(step.can_execute())
        
        step.status = WorkflowStepStatus.RUNNING
        self.assertFalse(step.can_execute())
    
    def test_is_completed(self):
        """测试检查是否完成"""
        step = WorkflowStep(
            step_id="step-1",
            name="Test Step",
            step_type=WorkflowStepType.TASK
        )
        
        self.assertFalse(step.is_completed())
        
        step.status = WorkflowStepStatus.COMPLETED
        self.assertTrue(step.is_completed())
    
    def test_execute_time(self):
        """测试获取执行时间"""
        step = WorkflowStep(
            step_id="step-1",
            name="Test Step",
            step_type=WorkflowStepType.TASK
        )
        
        self.assertEqual(step.execute_time(), 0.0)
        
        step.start_time = 100.0
        step.end_time = 105.0
        self.assertEqual(step.execute_time(), 5.0)


class TestWorkflowContext(unittest.TestCase):
    """WorkflowContext测试"""
    
    def test_get_set_data(self):
        """测试获取和设置数据"""
        context = WorkflowContext(workflow_id="wf-1")
        
        context.set_data("key1", "value1")
        self.assertEqual(context.get_data("key1"), "value1")
        self.assertEqual(context.get_data("key2", "default"), "default")
    
    def test_get_set_result(self):
        """测试获取和设置结果"""
        context = WorkflowContext(workflow_id="wf-1")
        
        context.set_result("step-1", "result1")
        self.assertEqual(context.get_result("step-1"), "result1")
        self.assertEqual(context.get_result("step-2", "default"), "default")


class TestWorkflowDefinition(unittest.TestCase):
    """WorkflowDefinition测试"""
    
    def setUp(self):
        """测试前准备"""
        self.executor = create_workflow_executor()
    
    def test_create_workflow(self):
        """测试创建工作流"""
        workflow = self.executor.create_workflow(
            name="Test Workflow",
            description="Test Description"
        )
        
        self.assertEqual(workflow.name, "Test Workflow")
        self.assertEqual(workflow.description, "Test Description")
        self.assertIsNotNone(workflow.workflow_id)
    
    def test_add_step(self):
        """测试添加步骤"""
        workflow = self.executor.create_workflow(name="Test Workflow")
        
        step = self.executor.add_step(
            workflow=workflow,
            name="Step 1",
            step_type=WorkflowStepType.TASK
        )
        
        self.assertEqual(len(workflow.steps), 1)
        self.assertEqual(step.name, "Step 1")
    
    def test_get_step(self):
        """测试获取步骤"""
        workflow = self.executor.create_workflow(name="Test Workflow")
        
        step = self.executor.add_step(
            workflow=workflow,
            name="Step 1",
            step_type=WorkflowStepType.TASK
        )
        
        retrieved = workflow.get_step(step.step_id)
        self.assertEqual(retrieved, step)
    
    def test_get_ready_steps(self):
        """测试获取就绪步骤"""
        workflow = self.executor.create_workflow(name="Test Workflow")
        
        step1 = self.executor.add_step(
            workflow=workflow,
            name="Step 1",
            step_type=WorkflowStepType.TASK
        )
        
        step2 = self.executor.add_step(
            workflow=workflow,
            name="Step 2",
            step_type=WorkflowStepType.TASK,
            dependencies=[step1.step_id]
        )
        
        ready = workflow.get_ready_steps()
        self.assertEqual(len(ready), 1)
        self.assertEqual(ready[0], step1)


class TestWorkflowExecution(unittest.TestCase):
    """WorkflowExecution测试"""
    
    def setUp(self):
        """测试前准备"""
        self.executor = create_workflow_executor()
    
    def test_execute_simple_workflow(self):
        """测试执行简单工作流"""
        workflow = self.executor.create_workflow(name="Test Workflow")
        
        self.executor.add_step(
            workflow=workflow,
            name="Step 1",
            step_type=WorkflowStepType.TASK
        )
        
        execution = self.executor.execute_workflow(workflow.workflow_id)
        
        self.assertEqual(execution.status, WorkflowStatus.COMPLETED)
        self.assertEqual(len(execution.completed_steps), 1)
    
    def test_execute_workflow_with_dependencies(self):
        """测试执行有依赖的工作流"""
        workflow = self.executor.create_workflow(name="Test Workflow")
        
        step1 = self.executor.add_step(
            workflow=workflow,
            name="Step 1",
            step_type=WorkflowStepType.TASK
        )
        
        step2 = self.executor.add_step(
            workflow=workflow,
            name="Step 2",
            step_type=WorkflowStepType.TASK,
            dependencies=[step1.step_id]
        )
        
        execution = self.executor.execute_workflow(workflow.workflow_id)
        
        self.assertEqual(execution.status, WorkflowStatus.COMPLETED)
        self.assertEqual(len(execution.completed_steps), 2)
    
    def test_execution_time(self):
        """测试执行时间"""
        workflow = self.executor.create_workflow(name="Test Workflow")
        
        self.executor.add_step(
            workflow=workflow,
            name="Step 1",
            step_type=WorkflowStepType.TASK
        )
        
        execution = self.executor.execute_workflow(workflow.workflow_id)
        
        self.assertGreater(execution.execution_time(), 0)
    
    def test_progress(self):
        """测试进度"""
        workflow = self.executor.create_workflow(name="Test Workflow")
        
        self.executor.add_step(
            workflow=workflow,
            name="Step 1",
            step_type=WorkflowStepType.TASK
        )
        
        execution = self.executor.execute_workflow(workflow.workflow_id)
        
        self.assertEqual(execution.progress(), 1.0)


class TestTaskWorkflowExecutor(unittest.TestCase):
    """TaskWorkflowExecutor测试"""
    
    def setUp(self):
        """测试前准备"""
        self.executor = create_workflow_executor()
    
    def test_create_executor(self):
        """测试创建执行器"""
        executor = create_workflow_executor()
        
        self.assertIsNotNone(executor)
        self.assertIsNotNone(executor.workflows)
        self.assertIsNotNone(executor.executions)
    
    def test_get_workflow(self):
        """测试获取工作流"""
        executor = create_workflow_executor()
        workflow = executor.create_workflow(name="Test")
        
        retrieved = executor.get_workflow(workflow.workflow_id)
        self.assertEqual(retrieved, workflow)
    
    def test_get_execution(self):
        """测试获取执行"""
        executor = create_workflow_executor()
        workflow = executor.create_workflow(name="Test")
        
        execution = executor.execute_workflow(workflow.workflow_id)
        
        retrieved = executor.get_execution(execution.execution_id)
        self.assertEqual(retrieved, execution)
    
    def test_get_metrics(self):
        """测试获取指标"""
        executor = create_workflow_executor()
        workflow = executor.create_workflow(name="Test")
        
        executor.add_step(
            workflow=workflow,
            name="Step 1",
            step_type=WorkflowStepType.TASK
        )
        
        executor.execute_workflow(workflow.workflow_id)
        
        metrics = executor.get_metrics()
        
        self.assertEqual(metrics.total_workflows, 1)
        self.assertEqual(metrics.completed_workflows, 1)
    
    def test_get_all_executions(self):
        """测试获取所有执行"""
        executor = create_workflow_executor()
        workflow = executor.create_workflow(name="Test")
        
        executor.add_step(
            workflow=workflow,
            name="Step 1",
            step_type=WorkflowStepType.TASK
        )
        
        executor.execute_workflow(workflow.workflow_id)
        
        executions = executor.get_all_executions()
        self.assertEqual(len(executions), 1)
    
    def test_register_callback(self):
        """测试注册回调"""
        executor = create_workflow_executor()
        events_received = []
        
        def callback(data):
            events_received.append(data)
        
        executor.register_callback("workflow_started", callback)
        
        workflow = executor.create_workflow(name="Test")
        executor.add_step(
            workflow=workflow,
            name="Step 1",
            step_type=WorkflowStepType.TASK
        )
        
        executor.execute_workflow(workflow.workflow_id)
        
        self.assertGreater(len(events_received), 0)


class TestWorkflowStepTypes(unittest.TestCase):
    """工作流步骤类型测试"""
    
    def setUp(self):
        """测试前准备"""
        self.executor = create_workflow_executor()
    
    def test_all_step_types(self):
        """测试所有步骤类型"""
        step_types = [
            WorkflowStepType.TASK,
            WorkflowStepType.PIPELINE,
            WorkflowStepType.PARALLEL,
            WorkflowStepType.CONDITIONAL,
            WorkflowStepType.LOOP,
            WorkflowStepType.SUBWORKFLOW,
            WorkflowStepType.CHECKPOINT,
            WorkflowStepType.ROLLBACK
        ]
        
        self.assertEqual(len(step_types), 8)
    
    def test_execute_conditional_step(self):
        """测试执行条件步骤"""
        workflow = self.executor.create_workflow(name="Test")
        
        step = self.executor.add_step(
            workflow=workflow,
            name="Conditional",
            step_type=WorkflowStepType.CONDITIONAL,
            config={"condition": True}
        )
        
        execution = self.executor.execute_workflow(workflow.workflow_id)
        
        self.assertEqual(execution.status, WorkflowStatus.COMPLETED)
    
    def test_execute_loop_step(self):
        """测试执行循环步骤"""
        workflow = self.executor.create_workflow(name="Test")
        
        step = self.executor.add_step(
            workflow=workflow,
            name="Loop",
            step_type=WorkflowStepType.LOOP,
            config={"iterations": 3}
        )
        
        execution = self.executor.execute_workflow(workflow.workflow_id)
        
        self.assertEqual(execution.status, WorkflowStatus.COMPLETED)


class TestWorkflowMetrics(unittest.TestCase):
    """WorkflowMetrics测试"""
    
    def setUp(self):
        """测试前准备"""
        self.executor = create_workflow_executor()
    
    def test_record_execution(self):
        """测试记录执行"""
        workflow = self.executor.create_workflow(name="Test")
        
        self.executor.add_step(
            workflow=workflow,
            name="Step 1",
            step_type=WorkflowStepType.TASK
        )
        
        self.executor.execute_workflow(workflow.workflow_id)
        
        metrics = self.executor.get_metrics()
        
        self.assertEqual(metrics.total_workflows, 1)
        self.assertEqual(metrics.completed_workflows, 1)
        self.assertGreater(metrics.total_execution_time, 0)


if __name__ == '__main__':
    unittest.main()
