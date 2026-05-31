from typing import Any, Dict, List, Optional
from .base import JSONSerializable


class DAGNode(JSONSerializable):
    """DAG节点 - 代表一个子任务或原子动作"""

    def __init__(
        self,
        node_id: str,
        name: str,
        node_type: str = "task",
        status: str = "pending",
        inputs: Optional[List[str]] = None,
        outputs: Optional[List[str]] = None,
        attributes: Optional[Dict[str, Any]] = None
    ):
        self.id = node_id
        self.name = name
        self.type = node_type
        self.status = status
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.attributes = attributes or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "status": self.status,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "attributes": self.attributes
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DAGNode':
        return cls(
            node_id=data.get("id", ""),
            name=data.get("name", ""),
            node_type=data.get("type", "task"),
            status=data.get("status", "pending"),
            inputs=data.get("inputs", []),
            outputs=data.get("outputs", []),
            attributes=data.get("attributes", {})
        )

    def __repr__(self):
        return f"DAGNode(id={self.id!r}, name={self.name!r})"


class DAGEdge(JSONSerializable):
    """DAG边 - 代表节点之间的依赖关系"""

    def __init__(
        self,
        edge_id: str,
        from_node: str,
        to_node: str,
        edge_type: str = "requires",
        weight: float = 1.0,
        attributes: Optional[Dict[str, Any]] = None
    ):
        self.id = edge_id
        self.from_node = from_node
        self.to_node = to_node
        self.type = edge_type
        self.weight = weight
        self.attributes = attributes or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "from_node": self.from_node,
            "to_node": self.to_node,
            "type": self.type,
            "weight": self.weight,
            "attributes": self.attributes
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DAGEdge':
        return cls(
            edge_id=data.get("id", ""),
            from_node=data.get("from_node", ""),
            to_node=data.get("to_node", ""),
            edge_type=data.get("type", "requires"),
            weight=data.get("weight", 1.0),
            attributes=data.get("attributes", {})
        )

    def __repr__(self):
        return f"DAGEdge(from={self.from_node!r}, to={self.to_node!r})"


class TaskDAG(JSONSerializable):
    """任务DAG - 包含节点和边的完整任务依赖图"""

    def __init__(
        self,
        dag_id: str,
        nodes: Optional[List[DAGNode]] = None,
        edges: Optional[List[DAGEdge]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        critical_path: Optional[List[str]] = None,
        parallel_groups: Optional[Dict[int, List[str]]] = None
    ):
        self.id = dag_id
        self.nodes = nodes or []
        self.edges = edges or []
        self.metadata = metadata or {}
        self.critical_path = critical_path or []
        self.parallel_groups = parallel_groups or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "metadata": self.metadata,
            "critical_path": self.critical_path,
            "parallel_groups": self.parallel_groups
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskDAG':
        nodes = [DAGNode.from_dict(node_data) for node_data in data.get("nodes", [])]
        edges = [DAGEdge.from_dict(edge_data) for edge_data in data.get("edges", [])]
        return cls(
            dag_id=data.get("id", ""),
            nodes=nodes,
            edges=edges,
            metadata=data.get("metadata", {}),
            critical_path=data.get("critical_path", []),
            parallel_groups=data.get("parallel_groups", {})
        )

    def __repr__(self):
        return f"TaskDAG(id={self.id!r}, nodes={len(self.nodes)}, edges={len(self.edges)})"
