#!/usr/bin/env python3
"""
测试永动知识图谱Agent
"""

import sys
import time
import logging
from knowledge_graph_agent import EternalAgent, KnowledgeGraph

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def test_knowledge_graph():
    """测试知识图谱的基本功能"""
    logging.info("=== 测试知识图谱 ===")
    kg = KnowledgeGraph("test_kg.json")
    
    node1_id = kg.add_node("测试节点1", node_type="test")
    node2_id = kg.add_node("测试节点2", node_type="test")
    kg.add_edge(node1_id, node2_id, "related_to", 0.8)
    
    assert len(kg.nodes) == 2, "节点添加失败"
    assert len(kg.edges) == 1, "边添加失败"
    
    related = kg.get_related_nodes(node1_id)
    assert len(related) == 1, "关联查询失败"
    
    kg.save_to_disk()
    kg2 = KnowledgeGraph("test_kg.json")
    assert len(kg2.nodes) == 2, "持久化加载失败"
    
    logging.info("✓ 知识图谱测试通过")
    return True


def test_agent_initialization():
    """测试Agent初始化"""
    logging.info("=== 测试Agent初始化 ===")
    agent = EternalAgent("test_agent_kg.json")
    
    assert len(agent.kg.nodes) >= 1, "初始节点创建失败"
    assert agent.cycle_count == 0, "初始循环计数错误"
    
    logging.info("✓ Agent初始化测试通过")
    return True


def test_agent_cycles():
    """测试Agent执行几个循环"""
    logging.info("=== 测试Agent循环执行 ===")
    agent = EternalAgent("test_cycles_kg.json")
    
    initial_nodes = len(agent.kg.nodes)
    initial_edges = len(agent.kg.edges)
    
    for _ in range(5):
        agent.run_cycle()
    
    assert agent.cycle_count == 5, "循环计数错误"
    assert len(agent.kg.nodes) > initial_nodes, "节点没有增长"
    assert len(agent.kg.edges) > initial_edges, "边没有增长"
    
    logging.info(f"✓ Agent循环测试通过: {agent.cycle_count} 次循环")
    logging.info(f"  节点: {initial_nodes} → {len(agent.kg.nodes)}")
    logging.info(f"  边: {initial_edges} → {len(agent.kg.edges)}")
    return True


def cleanup():
    """清理测试文件"""
    import os
    test_files = ["test_kg.json", "test_agent_kg.json", "test_cycles_kg.json"]
    for f in test_files:
        if os.path.exists(f):
            os.remove(f)


def main():
    try:
        test_knowledge_graph()
        test_agent_initialization()
        test_agent_cycles()
        logging.info("\n=== 所有测试通过! ===")
        return 0
    except Exception as e:
        logging.error(f"\n测试失败: {e}", exc_info=True)
        return 1
    finally:
        cleanup()


if __name__ == "__main__":
    sys.exit(main())
