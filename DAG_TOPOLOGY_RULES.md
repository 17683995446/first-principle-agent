# DAG拓扑图应用场景与约束规则
## 阶段7成果

---

## 一、DAG基础概念回顾

### 1.1 什么是DAG
DAG（Directed Acyclic Graph，有向无环图）是一种：
- **有向**：边有方向，从一个节点指向另一个节点
- **无环**：不存在从某节点出发经过若干边又回到该节点的路径
- **图**：由节点（顶点）和边组成的数据结构

### 1.2 DAG在任务规划中的意义
```
任务规划问题本质上是DAG构建问题：
- 节点 = 子任务
- 边 = 依赖关系
- 拓扑排序 = 执行顺序
- 无环约束 = 可执行性保证
```

---

## 二、DAG核心术语定义

### 2.1 节点（Node）
```python
DAGNode = {
    "id": str,              # 唯一标识符
    "name": str,            # 节点名称
    "type": str,            # 节点类型：task | action | checkpoint
    "status": str,          # 状态：pending | running | completed | failed | skipped
    "inputs": list,         # 输入列表
    "outputs": list,        # 输出列表
    "attributes": dict,     # 自定义属性
    "metadata": dict         # 元数据
}
```

### 2.2 边（Edge）
```python
DAGEdge = {
    "id": str,              # 唯一标识符
    "from_node": str,       # 起始节点ID
    "to_node": str,         # 目标节点ID
    "type": str,            # 边类型：requires | produces | parallel | conditional
    "weight": float,        # 依赖权重：0.0-1.0
    "attributes": dict      # 自定义属性
}
```

### 2.3 DAG图结构
```python
TaskDAG = {
    "id": str,              # 图的唯一标识符
    "nodes": list[DAGNode], # 节点列表
    "edges": list[DAGEdge], # 边列表
    "metadata": dict,        # 元数据
    "critical_path": list[str],  # 关键路径
    "parallel_groups": dict  # 并行分组
}
```

---

## 三、DAG应用场景

### 3.1 场景1：软件开发流程

#### 应用示例
```
用户需求：开发一个用户登录系统
```

#### DAG建模
```python
# 节点定义
nodes = [
    {"id": "n1", "name": "需求分析", "type": "task"},
    {"id": "n2", "name": "系统设计", "type": "task"},
    {"id": "n3", "name": "数据库设计", "type": "task"},
    {"id": "n4", "name": "API开发", "type": "task"},
    {"id": "n5", "name": "前端开发", "type": "task"},
    {"id": "n6", "name": "集成测试", "type": "task"},
    {"id": "n7", "name": "部署上线", "type": "task"}
]

# 边定义（依赖关系）
edges = [
    {"id": "e1", "from_node": "n1", "to_node": "n2", "type": "requires", "weight": 1.0},
    {"id": "e2", "from_node": "n2", "to_node": "n3", "type": "requires", "weight": 0.9},
    {"id": "e3", "from_node": "n2", "to_node": "n4", "type": "requires", "weight": 1.0},
    {"id": "e4", "from_node": "n2", "to_node": "n5", "type": "requires", "weight": 0.9},
    {"id": "e5", "from_node": "n3", "to_node": "n4", "type": "requires", "weight": 1.0},
    {"id": "e6", "from_node": "n4", "to_node": "n6", "type": "requires", "weight": 1.0},
    {"id": "e7", "from_node": "n5", "to_node": "n6", "type": "requires", "weight": 0.8},
    {"id": "e8", "from_node": "n6", "to_node": "n7", "type": "requires", "weight": 1.0}
]
```

#### 可视化
```
n1(需求分析)
  ↓
n2(系统设计)
  ↙   ↘
n3(数据库)  n4(API开发)
  ↓           ↓
             n5(前端开发)
               ↘   ↙
                  n6(集成测试)
                     ↓
                  n7(部署上线)
```

---

### 3.2 场景2：数据分析流水线

#### 应用示例
```
用户需求：数据清洗 → 特征工程 → 模型训练 → 模型评估
```

#### DAG建模
```python
nodes = [
    {"id": "d1", "name": "数据采集", "type": "task"},
    {"id": "d2", "name": "数据清洗", "type": "task"},
    {"id": "d3", "name": "特征工程", "type": "task"},
    {"id": "d4", "name": "模型训练", "type": "task"},
    {"id": "d5", "name": "模型评估", "type": "task"}
]

edges = [
    {"id": "de1", "from_node": "d1", "to_node": "d2", "type": "requires"},
    {"id": "de2", "from_node": "d2", "to_node": "d3", "type": "requires"},
    {"id": "de3", "from_node": "d3", "to_node": "d4", "type": "requires"},
    {"id": "de4", "from_node": "d4", "to_node": "d5", "type": "requires"}
]
```

---

### 3.3 场景3：并行任务调度

#### 应用示例
```
场景：下载文件A、B、C可以并行，但处理它们需要串行
```

#### DAG建模
```python
nodes = [
    {"id": "p1", "name": "下载文件A", "type": "task", "parallel_group": "download"},
    {"id": "p2", "name": "下载文件B", "type": "task", "parallel_group": "download"},
    {"id": "p3", "name": "下载文件C", "type": "task", "parallel_group": "download"},
    {"id": "p4", "name": "处理文件A", "type": "task"},
    {"id": "p5", "name": "处理文件B", "type": "task"},
    {"id": "p6", "name": "处理文件C", "type": "task"},
    {"id": "p7", "name": "生成报告", "type": "task"}
]

edges = [
    # 下载任务并行
    # 无边，表示并行
    
    # 处理任务依赖各自的下载任务
    {"id": "pe1", "from_node": "p1", "to_node": "p4", "type": "requires"},
    {"id": "pe2", "from_node": "p2", "to_node": "p5", "type": "requires"},
    {"id": "pe3", "from_node": "p3", "to_node": "p6", "type": "requires"},
    
    # 生成报告依赖所有处理任务
    {"id": "pe4", "from_node": "p4", "to_node": "p7", "type": "requires"},
    {"id": "pe5", "from_node": "p5", "to_node": "p7", "type": "requires"},
    {"id": "pe6", "from_node": "p6", "to_node": "p7", "type": "requires"}
]

parallel_groups = {
    "download": ["p1", "p2", "p3"]
}
```

#### 可视化
```
[p1]──→ [p4]──┐
[p2]──→ [p5]──┼──→ [p7]
[p3]──→ [p6]──┘
 (并行下载)   (串行处理)  (汇总)
```

---

### 3.4 场景4：条件分支流程

#### 应用示例
```
场景：根据文件类型决定处理方式
```

#### DAG建模
```python
nodes = [
    {"id": "c1", "name": "读取文件", "type": "task"},
    {"id": "c2", "name": "判断类型", "type": "task"},
    {"id": "c3", "name": "处理CSV", "type": "task"},
    {"id": "c4", "name": "处理JSON", "type": "task"},
    {"id": "c5", "name": "处理XML", "type": "task"},
    {"id": "c6", "name": "统一输出", "type": "task"}
]

edges = [
    {"id": "ce1", "from_node": "c1", "to_node": "c2", "type": "requires"},
    {"id": "ce2", "from_node": "c2", "to_node": "c3", "type": "conditional", "attributes": {"condition": "type == 'csv'"}},
    {"id": "ce3", "from_node": "c2", "to_node": "c4", "type": "conditional", "attributes": {"condition": "type == 'json'"}},
    {"id": "ce4", "from_node": "c2", "to_node": "c5", "type": "conditional", "attributes": {"condition": "type == 'xml'"}},
    {"id": "ce5", "from_node": "c3", "to_node": "c6", "type": "requires"},
    {"id": "ce6", "from_node": "c4", "to_node": "c6", "type": "requires"},
    {"id": "ce7", "from_node": "c5", "to_node": "c6", "type": "requires"}
]
```

---

## 四、DAG约束规则

### 4.1 无环约束（核心约束）

#### 规则定义
```python
def validate_no_cycles(dag: TaskDAG) -> tuple[bool, list[list[str]]]:
    """
    验证DAG中不存在环
    返回：(是否有环, 环的列表)
    """
    # 使用深度优先搜索检测环
    visited = set()
    rec_stack = set()
    cycles = []
    
    def dfs(node_id, path):
        visited.add(node_id)
        rec_stack.add(node_id)
        path.append(node_id)
        
        # 找到所有后继节点
        successors = get_successors(dag, node_id)
        
        for successor in successors:
            if successor not in visited:
                if dfs(successor, path[:]):
                    return True
            elif successor in rec_stack:
                # 发现环
                cycle_start = path.index(successor)
                cycle = path[cycle_start:] + [successor]
                cycles.append(cycle)
                return True
        
        rec_stack.remove(node_id)
        return False
    
    for node in dag.nodes:
        if node.id not in visited:
            dfs(node.id, [])
    
    return len(cycles) == 0, cycles
```

#### 违反示例
```python
# 错误的依赖定义，形成环
edges = [
    {"from_node": "A", "to_node": "B"},  # A依赖B
    {"from_node": "B", "to_node": "C"},  # B依赖C
    {"from_node": "C", "to_node": "A"}   # C依赖A → 形成环！
]
```

#### 正确示例
```python
# 正确的依赖定义，无环
edges = [
    {"from_node": "A", "to_node": "B"},
    {"from_node": "B", "to_node": "C"}
]
```

---

### 4.2 连通性约束

#### 规则定义
所有节点必须从根节点可达，确保没有孤立的任务。

```python
def validate_connectivity(dag: TaskDAG) -> tuple[bool, list[str]]:
    """
    验证所有节点都从根节点可达
    """
    # 找到所有根节点（入度为0的节点）
    roots = [n for n in dag.nodes if get_in_degree(dag, n.id) == 0]
    
    if not roots:
        return False, ["没有根节点"]
    
    # 使用BFS检查可达性
    reachable = set()
    queue = list(roots)
    
    while queue:
        node = queue.pop(0)
        if node.id not in reachable:
            reachable.add(node.id)
            successors = get_successors(dag, node.id)
            queue.extend([dag.nodes_by_id[s] for s in successors])
    
    # 找出不可达的节点
    unreachable = [n.id for n in dag.nodes if n.id not in reachable]
    
    return len(unreachable) == 0, unreachable
```

---

### 4.3 依赖完备性约束

#### 规则定义
每个任务的输入必须已经存在或可生成。

```python
def validate_dependency_completeness(dag: TaskDAG) -> tuple[bool, list[str]]:
    """
    验证每个任务的依赖都已满足
    """
    errors = []
    
    for node in dag.nodes:
        for edge in dag.edges:
            if edge.to_node == node.id:
                from_node = dag.get_node(edge.from_node)
                # 检查from_node的输出是否包含to_node需要的输入
                required_input = edge.attributes.get("required_input")
                if required_input and required_input not in from_node.outputs:
                    errors.append(
                        f"节点 {node.id} 需要的输入 {required_input} "
                        f"无法从节点 {from_node.id} 获取"
                    )
    
    return len(errors) == 0, errors
```

---

### 4.4 单入度约束（可选）

#### 规则定义
每个任务最好只有一个直接前驱，简化执行逻辑。

```python
def validate_single_predecessor(dag: TaskDAG) -> tuple[bool, dict]:
    """
    验证每个任务是否只有一个直接前驱
    返回：(是否满足约束, 不满足约束的节点及其前驱数)
    """
    warnings = {}
    
    for node in dag.nodes:
        predecessors = get_predecessors(dag, node.id)
        if len(predecessors) > 1:
            warnings[node.id] = len(predecessors)
    
    return len(warnings) == 0, warnings
```

---

### 4.5 并行性约束

#### 规则定义
相同并行组内的任务必须满足并行执行条件。

```python
def validate_parallelism(dag: TaskDAG) -> tuple[bool, list[str]]:
    """
    验证并行组内的任务是否可以并行执行
    """
    errors = []
    
    for group_name, node_ids in dag.parallel_groups.items():
        # 检查并行任务之间是否有依赖
        for i, node_a in enumerate(node_ids):
            for node_b in node_ids[i+1:]:
                if has_path(dag, node_a, node_b) or has_path(dag, node_b, node_a):
                    errors.append(
                        f"并行组 '{group_name}' 中的任务 {node_a} 和 {node_b} "
                        f"存在依赖关系，不能并行执行"
                    )
    
    return len(errors) == 0, errors
```

---

## 五、DAG操作算法

### 5.1 拓扑排序

```python
def topological_sort(dag: TaskDAG) -> list[str]:
    """
    对DAG进行拓扑排序，返回节点的执行顺序
    """
    # 计算入度
    in_degree = {n.id: get_in_degree(dag, n.id) for n in dag.nodes}
    
    # 入度为0的节点加入队列
    queue = [n.id for n in dag.nodes if in_degree[n.id] == 0]
    result = []
    
    while queue:
        node_id = queue.pop(0)
        result.append(node_id)
        
        # 更新后继节点的入度
        for successor in get_successors(dag, node_id):
            in_degree[successor] -= 1
            if in_degree[successor] == 0:
                queue.append(successor)
    
    # 检查是否存在环
    if len(result) != len(dag.nodes):
        raise ValueError("图中存在环，无法进行拓扑排序")
    
    return result
```

### 5.2 关键路径识别

```python
def find_critical_path(dag: TaskDAG) -> list[str]:
    """
    找到DAG的关键路径（最长路径）
    """
    # 对节点进行拓扑排序
    topo_order = topological_sort(dag)
    
    # 计算到每个节点的最长路径
    dist = {node_id: 0 for node_id in topo_order}
    prev = {node_id: None for node_id in topo_order}
    
    for node_id in topo_order:
        for successor in get_successors(dag, node_id):
            weight = dag.get_edge(node_id, successor).weight
            if dist[successor] < dist[node_id] + weight:
                dist[successor] = dist[node_id] + weight
                prev[successor] = node_id
    
    # 找到最长路径的终点
    end_node = max(dist, key=dist.get)
    
    # 回溯构建路径
    path = []
    current = end_node
    while current is not None:
        path.append(current)
        current = prev[current]
    
    return list(reversed(path))
```

### 5.3 并行任务分组

```python
def group_parallel_tasks(dag: TaskDAG) -> list[list[str]]:
    """
    将可以并行执行的任务分组
    """
    topo_order = topological_sort(dag)
    groups = []
    executed = set()
    
    while len(executed) < len(dag.nodes):
        current_group = []
        
        for node_id in topo_order:
            if node_id in executed:
                continue
            
            # 检查所有前驱是否都已执行
            predecessors = get_predecessors(dag, node_id)
            if all(p in executed for p in predecessors):
                current_group.append(node_id)
        
        if not current_group:
            raise ValueError("无法继续调度，可能存在环")
        
        groups.append(current_group)
        executed.update(current_group)
    
    return groups
```

---

## 六、约束验证清单

### 完整验证流程
```python
def validate_dag(dag: TaskDAG) -> tuple[bool, dict]:
    """
    对DAG进行完整验证
    """
    results = {}
    
    # 1. 无环约束
    no_cycles, cycles = validate_no_cycles(dag)
    results["no_cycles"] = {"valid": no_cycles, "cycles": cycles}
    
    # 2. 连通性约束
    connected, unreachable = validate_connectivity(dag)
    results["connectivity"] = {"valid": connected, "unreachable": unreachable}
    
    # 3. 依赖完备性
    complete, missing = validate_dependency_completeness(dag)
    results["dependency_completeness"] = {"valid": complete, "missing": missing}
    
    # 4. 并行性约束
    parallel_valid, parallel_errors = validate_parallelism(dag)
    results["parallelism"] = {"valid": parallel_valid, "errors": parallel_errors}
    
    # 汇总结果
    all_valid = all(r["valid"] for r in results.values())
    
    return all_valid, results
```

---

## 七、阶段7完成检查清单

- [x] 定义DAG核心术语（节点、边、图结构）
- [x] 梳理4个典型应用场景
- [x] 定义5大约束规则（无环、连通性、依赖完备性、并行性）
- [x] 实现核心操作算法（拓扑排序、关键路径、并行分组）
- [x] 提供验证函数
- [x] 输出DAG约束规则文档

✅ **阶段7已完成！**
