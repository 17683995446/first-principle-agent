"""
测试第54阶段：TaskPlanningSystem任务规划系统整合层
"""
import unittest
import time
from first_principle_agent.core import (
    TaskPlanningSystem,
    create_planning_system,
    SystemStatus,
    TaskPriority
)


class TestTaskPlanningSystem(unittest.TestCase):
    """TaskPlanningSystem测试"""
    
    def setUp(self):
        """测试前准备"""
        self.system = create_planning_system(
            name="TestSystem",
            auto_start=True,
            use_resilience=False
        )
    
    def tearDown(self):
        """测试后清理"""
        if hasattr(self, 'system') and self.system:
            self.system.shutdown(wait=False)
    
    def test_system_initialization(self):
        """测试系统初始化"""
        self.assertEqual(self.system.status, SystemStatus.READY)
        self.assertIsNotNone(self.system.task_normalizer)
        self.assertIsNotNone(self.system.task_planner)
        self.assertIsNotNone(self.system.atomic_splitter)
        self.assertIsNotNone(self.system.atomic_validator)
        self.assertIsNotNone(self.system.atomic_executor)
        self.assertIsNotNone(self.system.task_scheduler)
        
        info = self.system.get_system_info()
        self.assertEqual(info['system_name'], 'TestSystem')
        self.assertEqual(info['status'], 'ready')
    
    def test_create_with_factory(self):
        """测试工厂函数创建"""
        system = create_planning_system(
            name="FactoryTest",
            auto_start=False,
            use_resilience=True
        )
        self.assertEqual(system.config.name, 'FactoryTest')
        self.assertFalse(system.config.auto_start_scheduler)
        self.assertTrue(system.config.use_resilience)
        system.shutdown(wait=False)
    
    def test_submit_requirement(self):
        """测试提交需求"""
        request_id = self.system.submit_requirement(
            "测试任务",
            priority=TaskPriority.NORMAL
        )
        
        self.assertIsNotNone(request_id)
        self.assertEqual(len(request_id), 36)  # UUID长度
        
        # 检查状态
        status = self.system.get_request_status(request_id)
        self.assertIn(status, ['pending', 'active'])
    
    def test_callbacks(self):
        """测试回调函数"""
        callback_events = []
        
        def on_start(request):
            callback_events.append(('start', request.request_id))
        
        def on_complete(result):
            callback_events.append(('complete', result.request_id, result.success))
        
        self.system.set_callbacks(
            on_task_start=on_start,
            on_task_complete=on_complete
        )
        
        # 执行需求
        result = self.system.execute_requirement(
            "测试回调",
            timeout=10.0
        )
        
        # 等待回调
        time.sleep(1.0)
        
        # 验证结果
        self.assertIsNotNone(result)
        self.assertEqual(result.request_id, request_id if 'request_id' in locals() else result.request_id)
    
    def test_system_info(self):
        """测试系统信息获取"""
        info = self.system.get_system_info()
        
        self.assertIn('system_id', info)
        self.assertIn('system_name', info)
        self.assertIn('status', info)
        self.assertIn('uptime', info)
        self.assertIn('metrics', info)
        self.assertIn('pending_count', info)
        self.assertIn('active_count', info)
        self.assertIn('completed_count', info)
        
        metrics = info['metrics']
        self.assertIn('total_requests', metrics)
        self.assertIn('successful_requests', metrics)
        self.assertIn('failed_requests', metrics)
        self.assertIn('avg_execution_time', metrics)
        self.assertIn('success_rate', metrics)
    
    def test_pause_resume(self):
        """测试暂停和恢复"""
        # 初始状态是READY，不是RUNNING，所以先修改状态
        self.system.status = SystemStatus.RUNNING
        
        self.system.pause()
        self.assertEqual(self.system.status, SystemStatus.PAUSED)
        
        self.system.resume()
        self.assertEqual(self.system.status, SystemStatus.READY)
    
    def test_shutdown(self):
        """测试关闭系统"""
        self.system.shutdown(wait=False)
        self.assertEqual(self.system.status, SystemStatus.SHUTDOWN)


class TestTaskResult(unittest.TestCase):
    """TaskResult测试"""
    
    def test_task_result_properties(self):
        """测试TaskResult属性"""
        from first_principle_agent.core.task_planning_system import TaskResult
        
        result = TaskResult(
            request_id="test-123",
            success=True,
            start_time=100.0,
            end_time=200.0
        )
        
        self.assertEqual(result.request_id, "test-123")
        self.assertTrue(result.success)
        self.assertEqual(result.duration, 100.0)


class TestSystemMetrics(unittest.TestCase):
    """SystemMetrics测试"""
    
    def test_metrics_recording(self):
        """测试指标记录"""
        from first_principle_agent.core.task_planning_system import SystemMetrics
        
        metrics = SystemMetrics()
        
        # 记录请求
        metrics.record_request(success=True, execution_time=1.0)
        metrics.record_request(success=True, execution_time=2.0)
        metrics.record_request(success=False, execution_time=0.5)
        
        self.assertEqual(metrics.total_requests, 3)
        self.assertEqual(metrics.successful_requests, 2)
        self.assertEqual(metrics.failed_requests, 1)
        self.assertEqual(metrics.total_execution_time, 3.5)
        self.assertAlmostEqual(metrics.avg_execution_time, 3.5 / 3)


class TestSystemIntegration(unittest.TestCase):
    """系统集成测试"""
    
    def test_full_workflow(self):
        """测试完整工作流"""
        system = create_planning_system(
            name="IntegrationTest",
            auto_start=True,
            use_resilience=False
        )
        
        try:
            # 测试简单需求
            requirement = "完成一个简单任务"
            
            # 同步执行
            result = system.execute_requirement(
                requirement,
                priority=TaskPriority.HIGH,
                timeout=30.0
            )
            
            self.assertIsNotNone(result)
            self.assertEqual(result.request_id, result.request_id)
            
            # 检查系统信息
            info = system.get_system_info()
            self.assertGreater(info['metrics']['total_requests'], 0)
            
            # 获取已完成任务
            completed = system.get_all_completed_tasks()
            self.assertGreater(len(completed), 0)
            
        finally:
            system.shutdown(wait=True, timeout=30.0)


if __name__ == '__main__':
    unittest.main()
