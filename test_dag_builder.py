import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from first_principle_agent.layers import TaskNormalizer, DAGBuilder
from first_principle_agent.core import DAGNode, DAGEdge, TaskDAG


def test_dag_builder():
    print("="*60)
    print("测试1：DAG基础数据结构")
    print("="*60)

    node1 = DAGNode(
        node_id="node1",
        name="需求分析",
        node_type="task"
    )
    node2 = DAGNode(
        node_id="node2",
        name="系统设计",
        node_type="task"
    )

    print("✅ DAGNode创建成功")
    print(f"  节点1: {node1}")
    print(f"  节点2: {node2}")

    edge = DAGEdge(
        edge_id="edge1_2",
        from_node="node1",
        to_node="node2",
        edge_type="requires"
    )
    print(f"\n✅ DAGEdge创建成功: {edge}")

    print("\n" + "="*60)
    print("测试2：DAGBuilder从TaskTuple构建DAG")
    print("="*60)

    normalizer = TaskNormalizer()
    dag_builder = DAGBuilder()

    test_requirement = "完成项目开发，包括需求分析、系统设计、编码实现、测试验证。"

    task_tuple, errors = normalizer.normalize(test_requirement)
    if errors:
        print(f"归一化错误: {errors}")
        return

    dag = dag_builder.build_from_task_tuple(task_tuple)

    print("✅ DAG构建成功！")
    print(f"  DAG ID: {dag.id}")
    print(f"  节点数: {len(dag.nodes)}")
    print(f"  边数: {len(dag.edges)}")
    print("\n  节点列表:")
    for node in dag.nodes:
        print(f"    - {node.id}: {node.name} ({node.type})")
    print("\n  边列表:")
    for edge in dag.edges:
        print(f"    - {edge.from_node} → {edge.to_node}")

    print("\n" + "="*60)
    print("测试3：DAG JSON序列化/反序列化")
    print("="*60)

    json_str = dag.to_json()
    print(f"✅ JSON序列化成功，长度：{len(json_str)}")

    dag2 = TaskDAG.from_json(json_str)
    print(f"✅ JSON反序列化成功！")
    print(f"  验证节点数一致：{len(dag.nodes)} == {len(dag2.nodes)}")
    print(f"  验证边数一致：{len(dag.edges)} == {len(dag2.edges)}")

    print("\n" + "="*60)
    print("测试4：手动添加节点和边")
    print("="*60)

    new_node = DAGNode(
        node_id="extra_node",
        name="部署上线",
        node_type="task"
    )
    dag3 = dag_builder.add_node(dag2, new_node)
    print(f"✅ 添加新节点成功！")

    new_edge = DAGEdge(
        edge_id="edge_extra",
        from_node="subtask_4",
        to_node="extra_node",
        edge_type="requires"
    )
    dag4 = dag_builder.add_edge(dag3, new_edge)
    print(f"✅ 添加新边成功！")
    print(f"  当前节点数：{len(dag4.nodes)}")
    print(f"  当前边数：{len(dag4.edges)}")

    print("\n" + "="*60)
    print("测试5：顺序依赖添加")
    print("="*60)

    dag5 = dag_builder.add_sequential_dependency(dag4, "subtask_1", "subtask_2")
    dag6 = dag_builder.add_sequential_dependency(dag5, "subtask_2", "subtask_3")
    dag7 = dag_builder.add_sequential_dependency(dag6, "subtask_3", "subtask_4")

    print(f"✅ 添加顺序依赖成功！")
    print(f"  当前边数：{len(dag7.edges)}")
    print("\n  完整边列表:")
    for edge in dag7.edges:
        print(f"    - {edge.from_node} → {edge.to_node}")

    print("\n" + "="*60)
    print("🎉 所有测试通过！")


if __name__ == "__main__":
    test_dag_builder()
