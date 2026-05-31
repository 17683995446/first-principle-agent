import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from first_principle_agent.layers import TaskNormalizer, DAGBuilder, DependencyAnalyzer
from first_principle_agent.core import DAGNode, DAGEdge, TaskDAG


def test_dependency_analyzer():
    print("="*60)
    print("测试1：基本依赖分析")
    print("="*60)

    normalizer = TaskNormalizer()
    dag_builder = DAGBuilder()
    analyzer = DependencyAnalyzer()

    test_requirement = "完成项目，包括需求分析、系统设计、编码开发、测试验证、部署上线。"

    task_tuple, errors = normalizer.normalize(test_requirement)
    if errors:
        print(f"归一化错误: {errors}")
        return

    dag = dag_builder.build_from_task_tuple(task_tuple)

    dag = dag_builder.add_sequential_dependency(dag, "subtask_1", "subtask_2")
    dag = dag_builder.add_sequential_dependency(dag, "subtask_2", "subtask_3")
    dag = dag_builder.add_sequential_dependency(dag, "subtask_3", "subtask_4")

    analysis = analyzer.analyze_dependencies(dag)

    print("✅ 依赖分析成功！")
    print(f"  节点数: {analysis['node_count']}")
    print(f"  边数: {analysis['edge_count']}")
    print(f"  源节点: {analysis['source_nodes']}")
    print(f"  汇节点: {analysis['sink_nodes']}")
    print(f"  最长路径长度: {analysis['longest_path_length']}")
    print(f"  孤岛数量: {len(analysis['islands'])}")
    print(f"  孤岛: {analysis['islands']}")

    print("\n" + "="*60)
    print("测试2：节点直接依赖和被依赖")
    print("="*60)

    subtask3_deps = analyzer.get_node_dependencies(dag, "subtask_3")
    print(f"  subtask_3 的直接依赖: {subtask3_deps}")

    subtask3_dependents = analyzer.get_node_dependents(dag, "subtask_3")
    print(f"  subtask_3 的被依赖: {subtask3_dependents}")

    print("\n" + "="*60)
    print("测试3：完整依赖链分析")
    print("="*60)

    subtask4_full_deps = analyzer.get_full_dependency_chain(dag, "subtask_4")
    print(f"  subtask_4 的完整依赖链: {subtask4_full_deps}")

    root_full_dependents = analyzer.get_full_dependent_chain(dag, "root")
    print(f"  root 的完整被依赖链: {root_full_dependents}")

    print("\n" + "="*60)
    print("测试4：构建更复杂的DAG并分析")
    print("="*60)

    complex_dag = TaskDAG(dag_id="complex_test")
    nodes = [
        DAGNode("A", "需求调研"),
        DAGNode("B", "系统设计"),
        DAGNode("C", "数据库设计"),
        DAGNode("D", "前端开发"),
        DAGNode("E", "后端开发"),
        DAGNode("F", "测试集成"),
        DAGNode("G", "部署上线")
    ]
    for node in nodes:
        complex_dag.nodes.append(node)

    edges = [
        DAGEdge("A→B", "A", "B", "requires"),
        DAGEdge("B→C", "B", "C", "requires"),
        DAGEdge("B→D", "B", "D", "requires"),
        DAGEdge("B→E", "B", "E", "requires"),
        DAGEdge("C→F", "C", "F", "requires"),
        DAGEdge("D→F", "D", "F", "requires"),
        DAGEdge("E→F", "E", "F", "requires"),
        DAGEdge("F→G", "F", "G", "requires")
    ]
    for edge in edges:
        complex_dag.edges.append(edge)

    complex_analysis = analyzer.analyze_dependencies(complex_dag)

    print("✅ 复杂DAG分析成功！")
    print(f"  节点数: {complex_analysis['node_count']}")
    print(f"  边数: {complex_analysis['edge_count']}")
    print(f"  源节点: {complex_analysis['source_nodes']}")
    print(f"  汇节点: {complex_analysis['sink_nodes']}")
    print(f"  最长路径长度: {complex_analysis['longest_path_length']}")

    print("\n  节点依赖关系:")
    for node in nodes:
        deps = analyzer.get_node_dependencies(complex_dag, node.id)
        dependents = analyzer.get_node_dependents(complex_dag, node.id)
        print(f"    {node.id} ({node.name}):")
        print(f"      依赖: {deps}")
        print(f"      被依赖: {dependents}")

    print("\n  完整依赖链:")
    print(f"    F的完整依赖: {analyzer.get_full_dependency_chain(complex_dag, 'F')}")
    print(f"    B的完整被依赖: {analyzer.get_full_dependent_chain(complex_dag, 'B')}")

    print("\n" + "="*60)
    print("🎉 所有测试通过！")


if __name__ == "__main__":
    test_dependency_analyzer()
