from typing import Any, Dict, List, Optional
from ..core import TaskDAG, DAGNode, AtomicAction, AtomicActionPlan, ActionType
import uuid


class AtomicActionSplitter:
    """原子动作拆分器 - 将DAG节点拆分为更细粒度的原子动作"""

    def __init__(self):
        self.action_counter = 0

    def split_task(self, task_node: DAGNode) -> List[AtomicAction]:
        """
        将单个任务节点拆分为原子动作
        
        Args:
            task_node: DAG任务节点
            
        Returns:
            原子动作列表
        """
        actions = []
        
        # 根据节点类型确定需要哪些动作
        node_type = task_node.node_type.lower() if hasattr(task_node, 'node_type') else "task"
        
        # 添加初始化动作
        init_action = self._create_action(
            base_name=task_node.name,
            suffix="init",
            action_type=ActionType.INIT,
            description=f"Initialize {task_node.name}"
        )
        actions.append(init_action)
        
        # 根据任务类型添加具体动作
        if node_type in ["read", "input", "fetch"]:
            actions.extend(self._split_read_task(task_node, init_action))
        elif node_type in ["write", "output", "save"]:
            actions.extend(self._split_write_task(task_node, init_action))
        elif node_type in ["compute", "process", "transform"]:
            actions.extend(self._split_compute_task(task_node, init_action))
        elif node_type in ["call", "api", "request"]:
            actions.extend(self._split_call_task(task_node, init_action))
        else:
            actions.extend(self._split_generic_task(task_node, init_action))
        
        # 添加清理动作
        cleanup_action = self._create_action(
            base_name=task_node.name,
            suffix="cleanup",
            action_type=ActionType.CLEANUP,
            description=f"Cleanup after {task_node.name}"
        )
        cleanup_action.add_dependency(actions[-1].action_id)
        actions.append(cleanup_action)
        
        return actions

    def split_dag(self, dag: TaskDAG) -> AtomicActionPlan:
        """
        将整个DAG拆分为原子动作计划
        
        Args:
            dag: 任务DAG
            
        Returns:
            原子动作计划
        """
        plan = AtomicActionPlan(
            plan_id=f"plan_{dag.id}",
            name=f"Atomic Action Plan for {dag.id}"
        )
        
        # 跟踪节点ID到其原子动作ID的映射
        node_actions_map: Dict[str, List[str]] = {}
        
        # 拆分每个节点
        for node in dag.nodes:
            actions = self.split_task(node)
            node_actions_map[node.id] = [action.action_id for action in actions]
            for action in actions:
                plan.add_action(action)
        
        # 设置动作间的依赖关系
        self._set_action_dependencies(plan, dag, node_actions_map)
        
        return plan

    def _create_action(
        self,
        base_name: str,
        suffix: str,
        action_type: ActionType,
        description: str = ""
    ) -> AtomicAction:
        """创建原子动作"""
        self.action_counter += 1
        action_id = f"action_{self.action_counter:04d}"
        return AtomicAction(
            action_id=action_id,
            action_type=action_type,
            name=f"{base_name}_{suffix}",
            description=description
        )

    def _split_read_task(self, task_node: DAGNode, init_action: AtomicAction) -> List[AtomicAction]:
        """拆分读任务"""
        actions = []
        
        # 验证源
        validate_action = self._create_action(
            base_name=task_node.name,
            suffix="validate_source",
            action_type=ActionType.VALIDATE,
            description=f"Validate source for {task_node.name}"
        )
        validate_action.add_dependency(init_action.action_id)
        actions.append(validate_action)
        
        # 执行读操作
        read_action = self._create_action(
            base_name=task_node.name,
            suffix="read",
            action_type=ActionType.READ,
            description=f"Read data for {task_node.name}"
        )
        read_action.add_dependency(validate_action.action_id)
        actions.append(read_action)
        
        # 验证读取的数据
        validate_data_action = self._create_action(
            base_name=task_node.name,
            suffix="validate_data",
            action_type=ActionType.VALIDATE,
            description=f"Validate read data for {task_node.name}"
        )
        validate_data_action.add_dependency(read_action.action_id)
        actions.append(validate_data_action)
        
        return actions

    def _split_write_task(self, task_node: DAGNode, init_action: AtomicAction) -> List[AtomicAction]:
        """拆分写任务"""
        actions = []
        
        # 验证数据
        validate_action = self._create_action(
            base_name=task_node.name,
            suffix="validate_data",
            action_type=ActionType.VALIDATE,
            description=f"Validate data for {task_node.name}"
        )
        validate_action.add_dependency(init_action.action_id)
        actions.append(validate_action)
        
        # 准备目标
        prepare_action = self._create_action(
            base_name=task_node.name,
            suffix="prepare_target",
            action_type=ActionType.COMPUTE,
            description=f"Prepare target for {task_node.name}"
        )
        prepare_action.add_dependency(validate_action.action_id)
        actions.append(prepare_action)
        
        # 执行写操作
        write_action = self._create_action(
            base_name=task_node.name,
            suffix="write",
            action_type=ActionType.WRITE,
            description=f"Write data for {task_node.name}"
        )
        write_action.add_dependency(prepare_action.action_id)
        actions.append(write_action)
        
        # 验证写入结果
        verify_action = self._create_action(
            base_name=task_node.name,
            suffix="verify",
            action_type=ActionType.VALIDATE,
            description=f"Verify write result for {task_node.name}"
        )
        verify_action.add_dependency(write_action.action_id)
        actions.append(verify_action)
        
        return actions

    def _split_compute_task(self, task_node: DAGNode, init_action: AtomicAction) -> List[AtomicAction]:
        """拆分计算任务"""
        actions = []
        
        # 验证输入
        validate_input = self._create_action(
            base_name=task_node.name,
            suffix="validate_input",
            action_type=ActionType.VALIDATE,
            description=f"Validate input for {task_node.name}"
        )
        validate_input.add_dependency(init_action.action_id)
        actions.append(validate_input)
        
        # 准备计算
        prepare_compute = self._create_action(
            base_name=task_node.name,
            suffix="prepare",
            action_type=ActionType.COMPUTE,
            description=f"Prepare computation for {task_node.name}"
        )
        prepare_compute.add_dependency(validate_input.action_id)
        actions.append(prepare_compute)
        
        # 执行计算
        compute_action = self._create_action(
            base_name=task_node.name,
            suffix="compute",
            action_type=ActionType.COMPUTE,
            description=f"Compute {task_node.name}"
        )
        compute_action.add_dependency(prepare_compute.action_id)
        actions.append(compute_action)
        
        # 转换/处理结果
        transform_action = self._create_action(
            base_name=task_node.name,
            suffix="transform",
            action_type=ActionType.TRANSFORM,
            description=f"Transform result of {task_node.name}"
        )
        transform_action.add_dependency(compute_action.action_id)
        actions.append(transform_action)
        
        # 验证输出
        validate_output = self._create_action(
            base_name=task_node.name,
            suffix="validate_output",
            action_type=ActionType.VALIDATE,
            description=f"Validate output of {task_node.name}"
        )
        validate_output.add_dependency(transform_action.action_id)
        actions.append(validate_output)
        
        return actions

    def _split_call_task(self, task_node: DAGNode, init_action: AtomicAction) -> List[AtomicAction]:
        """拆分调用任务"""
        actions = []
        
        # 准备请求
        prepare_request = self._create_action(
            base_name=task_node.name,
            suffix="prepare_request",
            action_type=ActionType.COMPUTE,
            description=f"Prepare request for {task_node.name}"
        )
        prepare_request.add_dependency(init_action.action_id)
        actions.append(prepare_request)
        
        # 发送请求
        send_request = self._create_action(
            base_name=task_node.name,
            suffix="send",
            action_type=ActionType.SEND,
            description=f"Send request for {task_node.name}"
        )
        send_request.add_dependency(prepare_request.action_id)
        actions.append(send_request)
        
        # 接收响应
        receive_response = self._create_action(
            base_name=task_node.name,
            suffix="receive",
            action_type=ActionType.RECEIVE,
            description=f"Receive response for {task_node.name}"
        )
        receive_response.add_dependency(send_request.action_id)
        actions.append(receive_response)
        
        # 处理响应
        process_response = self._create_action(
            base_name=task_node.name,
            suffix="process_response",
            action_type=ActionType.COMPUTE,
            description=f"Process response for {task_node.name}"
        )
        process_response.add_dependency(receive_response.action_id)
        actions.append(process_response)
        
        # 验证结果
        validate_result = self._create_action(
            base_name=task_node.name,
            suffix="validate_result",
            action_type=ActionType.VALIDATE,
            description=f"Validate result of {task_node.name}"
        )
        validate_result.add_dependency(process_response.action_id)
        actions.append(validate_result)
        
        return actions

    def _split_generic_task(self, task_node: DAGNode, init_action: AtomicAction) -> List[AtomicAction]:
        """拆分通用任务"""
        actions = []
        
        # 验证
        validate_action = self._create_action(
            base_name=task_node.name,
            suffix="validate",
            action_type=ActionType.VALIDATE,
            description=f"Validate {task_node.name}"
        )
        validate_action.add_dependency(init_action.action_id)
        actions.append(validate_action)
        
        # 执行
        execute_action = self._create_action(
            base_name=task_node.name,
            suffix="execute",
            action_type=ActionType.COMPUTE,
            description=f"Execute {task_node.name}"
        )
        execute_action.add_dependency(validate_action.action_id)
        actions.append(execute_action)
        
        # 验证结果
        verify_action = self._create_action(
            base_name=task_node.name,
            suffix="verify",
            action_type=ActionType.VALIDATE,
            description=f"Verify result of {task_node.name}"
        )
        verify_action.add_dependency(execute_action.action_id)
        actions.append(verify_action)
        
        return actions

    def _set_action_dependencies(
        self,
        plan: AtomicActionPlan,
        dag: TaskDAG,
        node_actions_map: Dict[str, List[str]]
    ) -> None:
        """设置动作间的依赖关系"""
        # 对于每条DAG边，将源节点的最后一个动作作为目标节点第一个动作的依赖
        for edge in dag.edges:
            source_actions = node_actions_map.get(edge.from_node, [])
            target_actions = node_actions_map.get(edge.to_node, [])
            
            if source_actions and target_actions:
                # 源节点的最后一个动作
                last_source_action_id = source_actions[-1]
                # 目标节点的第一个动作
                first_target_action_id = target_actions[0]
                
                target_action = plan.get_action(first_target_action_id)
                if target_action:
                    target_action.add_dependency(last_source_action_id)
