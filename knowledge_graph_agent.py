#!/usr/bin/env python3
"""
基于第一性原理 · 轻量化永动知识图谱Agent
"""

import json
import time
import random
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


# ==================== 2.1 存续公理（Alive）====================
# 全局异常隔离、自愈重启、无限主循环、资源熔断保护
MAX_RETRY_COUNT = 3
SLEEP_INTERVAL = 2
SAVE_INTERVAL = 10


# ==================== 5.1 节点（Node）====================
@dataclass
class Node:
    id: str
    content: str
    created_at: float
    is_valid: bool = True
    type: str = "general"

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()


# ==================== 5.2 边（Edge）====================
@dataclass
class Edge:
    from_id: str
    to_id: str
    weight: float
    relation: str
    created_at: float

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()


# ==================== 6.2 记忆层：轻量化第一性原理知识图谱 ====================
class KnowledgeGraph:
    def __init__(self, storage_path: str = "kg_storage.json"):
        self.storage_path = Path(storage_path)
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self._load_from_disk()

    def _load_from_disk(self):
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.nodes = {n['id']: Node(**n) for n in data.get('nodes', [])}
                    self.edges = [Edge(**e) for e in data.get('edges', [])]
                    logging.info(f"Loaded {len(self.nodes)} nodes and {len(self.edges)} edges from disk")
            except Exception as e:
                logging.warning(f"Failed to load from disk: {e}, starting fresh")

    def save_to_disk(self):
        try:
            data = {
                'nodes': [asdict(node) for node in self.nodes.values()],
                'edges': [asdict(edge) for edge in self.edges]
            }
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logging.info(f"Saved {len(self.nodes)} nodes and {len(self.edges)} edges to disk")
        except Exception as e:
            logging.error(f"Failed to save to disk: {e}")

    def add_node(self, content: str, node_type: str = "general") -> str:
        node_id = f"node_{int(time.time() * 1000000)}"
        self.nodes[node_id] = Node(
            id=node_id,
            content=content,
            created_at=time.time(),
            is_valid=True,
            type=node_type
        )
        logging.debug(f"Added node: {node_id} - {content[:50]}...")
        return node_id

    def add_edge(self, from_id: str, to_id: str, relation: str, weight: float = 1.0):
        if from_id not in self.nodes or to_id not in self.nodes:
            logging.warning(f"Cannot add edge: node not found")
            return
        edge = Edge(
            from_id=from_id,
            to_id=to_id,
            weight=weight,
            relation=relation,
            created_at=time.time()
        )
        self.edges.append(edge)
        logging.debug(f"Added edge: {from_id} -> {to_id} ({relation}, weight={weight})")

    def get_related_nodes(self, node_id: str) -> List[Tuple[str, Edge]]:
        related = []
        for edge in self.edges:
            if edge.from_id == node_id:
                related.append((edge.to_id, edge))
            elif edge.to_id == node_id:
                related.append((edge.from_id, edge))
        return related

    def get_high_weight_edges(self, min_weight: float = 0.5) -> List[Edge]:
        return [e for e in self.edges if e.weight >= min_weight]

    def prune_low_value_knowledge(self, min_weight: float = 0.1, min_age_days: int = 30):
        cutoff_time = time.time() - (min_age_days * 86400)
        self.edges = [e for e in self.edges if e.weight >= min_weight or e.created_at > cutoff_time]
        valid_node_ids = set()
        for edge in self.edges:
            valid_node_ids.add(edge.from_id)
            valid_node_ids.add(edge.to_id)
        self.nodes = {k: v for k, v in self.nodes.items() if k in valid_node_ids or v.created_at > cutoff_time}
        logging.info(f"Pruned knowledge graph, remaining: {len(self.nodes)} nodes, {len(self.edges)} edges")


# ==================== 6.3 内核层：永续自治智能体主体 ====================
class EternalAgent:
    def __init__(self, storage_path: str = "kg_storage.json"):
        self.kg = KnowledgeGraph(storage_path)
        self.running = False
        self.cycle_count = 0
        self.last_save_time = time.time()
        self._initialize_initial_knowledge()

    def _initialize_initial_knowledge(self):
        if len(self.kg.nodes) == 0:
            initial_content = "系统启动，开始永动知识图谱构建"
            node_id = self.kg.add_node(initial_content, node_type="system")
            logging.info(f"Initialized with first node: {node_id}")

    def _execute_task(self, task_content: str) -> Tuple[str, List[Tuple[str, str, float]]]:
        task_node_id = self.kg.add_node(task_content, node_type="task")
        
        time.sleep(0.1)
        
        result_content = f"执行结果：{task_content} - 完成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        result_node_id = self.kg.add_node(result_content, node_type="result")
        
        new_relations = [
            (task_node_id, result_node_id, "produces", 1.0),
            (result_node_id, task_node_id, "derived_from", 0.8)
        ]
        
        return result_node_id, new_relations

    def _infer_new_tasks(self) -> List[str]:
        if len(self.kg.nodes) < 2:
            return [f"探索认知空间 - 第{self.cycle_count + 1}次"]
        
        high_weight_edges = self.kg.get_high_weight_edges(min_weight=0.5)
        if not high_weight_edges:
            return [f"知识关联分析 - 第{self.cycle_count + 1}次"]
        
        random_edge = random.choice(high_weight_edges)
        from_node = self.kg.nodes.get(random_edge.from_id)
        to_node = self.kg.nodes.get(random_edge.to_id)
        
        if from_node and to_node:
            return [f"深度关联探索：{from_node.content[:20]}... 与 {to_node.content[:20]}..."]
        
        return [f"知识迭代优化 - 第{self.cycle_count + 1}次"]

    def _knowledge_review(self):
        if self.cycle_count % 50 == 0 and self.cycle_count > 0:
            self.kg.prune_low_value_knowledge(min_weight=0.1, min_age_days=30)
        
        if time.time() - self.last_save_time > SAVE_INTERVAL:
            self.kg.save_to_disk()
            self.last_save_time = time.time()

    def run_cycle(self):
        self.cycle_count += 1
        
        retry_count = 0
        while retry_count < MAX_RETRY_COUNT:
            try:
                new_tasks = self._infer_new_tasks()
                
                for task in new_tasks:
                    result_node_id, new_relations = self._execute_task(task)
                    
                    for from_id, to_id, relation, weight in new_relations:
                        self.kg.add_edge(from_id, to_id, relation, weight)
                
                self._knowledge_review()
                
                if self.cycle_count % 10 == 0:
                    logging.info(f"Cycle {self.cycle_count}: Nodes={len(self.kg.nodes)}, Edges={len(self.kg.edges)}")
                
                break
                
            except Exception as e:
                retry_count += 1
                logging.error(f"Cycle {self.cycle_count} error (retry {retry_count}/{MAX_RETRY_COUNT}): {e}")
                if retry_count >= MAX_RETRY_COUNT:
                    logging.error(f"Max retries reached, skipping cycle {self.cycle_count}")
                time.sleep(SLEEP_INTERVAL)

    def start(self):
        self.running = True
        logging.info("=== 永动知识图谱Agent 启动 ===")
        
        try:
            while self.running:
                self.run_cycle()
                time.sleep(0.5)
        except KeyboardInterrupt:
            logging.info("=== 收到停止信号 ===")
        finally:
            self.stop()

    def stop(self):
        self.running = False
        self.kg.save_to_disk()
        logging.info(f"=== 永动知识图谱Agent 停止 ===")
        logging.info(f"总循环次数: {self.cycle_count}")
        logging.info(f"最终状态: {len(self.kg.nodes)} 节点, {len(self.kg.edges)} 边")


# ==================== 6.4 系统唯一启动入口 ====================
def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    agent = EternalAgent()
    agent.start()


if __name__ == "__main__":
    main()
