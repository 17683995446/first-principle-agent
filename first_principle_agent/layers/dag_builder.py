from typing import Any, Dict, List, Optional
from ..core import TaskTuple, DAGNode, DAGEdge, TaskDAG
import uuid


class DAGBuilder:
    """DAG构建器 - 将归一化的TaskTuple转换为有向无环图"""

    def __init__(self):
        pass

    def build_from_task_tuple(self, task_tuple: TaskTuple, dag_id: Optional[str] = None) -> TaskDAG:
        """
        从TaskTuple构建DAG

        Args:
            task_tuple: 归一化的任务元组
            dag_id: 可选的DAG ID

        Returns:
            构建的TaskDAG对象
        """
        if not dag_id:
            dag_id = f"dag_{uuid.uuid4().hex[:8]}"

        dag = TaskDAG(dag_id=dag_id)

        root_node = DAGNode(
            node_id="root",
            name=task_tuple.target,
            node_type="task",
            status="pending",
            attributes={"role": "root"}
        )
        dag.nodes.append(root_node)

        sub_tasks = self._extract_sub_tasks(task_tuple)
        for idx, sub_task in enumerate(sub_tasks):
            node_id = f"subtask_{idx+1}"
            node = DAGNode(
                node_id=node_id,
                name=sub_task,
                node_type="task",
                status="pending",
                attributes={"role": "subtask"}
            )
            dag.nodes.append(node)

            edge_id = f"edge_root_{node_id}"
            edge = DAGEdge(
                edge_id=edge_id,
                from_node="root",
                to_node=node_id,
                edge_type="requires",
                weight=1.0
            )
            dag.edges.append(edge)

        return dag

    def _extract_sub_tasks(self, task_tuple: TaskTuple) -> List[str]:
        """从TaskTuple中提取子任务"""
        sub_tasks = []
        include_items = task_tuple.boundary.get("include", [])
        for item in include_items:
            if item and item != "未明确指定范围" and len(item.strip()) > 1:
                sub_tasks.append(item.strip())
        if not sub_tasks:
            sub_tasks = ["执行任务"]
        return sub_tasks

    def add_node(self, dag: TaskDAG, node: DAGNode) -> TaskDAG:
        """向DAG添加节点"""
        dag.nodes.append(node)
        return dag

    def add_edge(self, dag: TaskDAG, edge: DAGEdge) -> TaskDAG:
        """向DAG添加边"""
        dag.edges.append(edge)
        return dag

    def add_sequential_dependency(self, dag: TaskDAG, from_node_id: str, to_node_id: str) -> TaskDAG:
        """添加顺序依赖关系（from_node → to_node）"""
        edge_id = f"edge_{from_node_id}_{to_node_id}"
        edge = DAGEdge(
            edge_id=edge_id,
            from_node=from_node_id,
            to_node=to_node_id,
            edge_type="requires",
            weight=1.0
        )
        dag.edges.append(edge)
        return dag

    def add_parallel_group(self, dag: TaskDAG, node_ids: List[str]) -> TaskDAG:
        """将多个节点标记为并行执行组"""
        group_id = len(dag.parallel_groups)
        dag.parallel_groups[group_id] = node_ids
        return dag
