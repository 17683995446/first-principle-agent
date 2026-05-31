# 系统整体设计与规范（第10-18阶段综合成果）
## 第10-18阶段综合成果

---

## 第10阶段：系统整体设计思维导图

### 10.1 系统核心架构思维导图

```
┌─────────────────────────────────────────────────────────────────┐
│              基于第一性原理的AI Agent任务规划系统                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │            第一性原理六大公理体系                         │  │
│  ├─────────────────────────────────────────────────────────┤  │
│  │ 1. 目标归一化公理  → 解决目标偏移类缺陷                  │  │
│  │ 2. 流程完整性公理  → 解决流程残缺类缺陷                  │  │
│  │ 3. 依赖关系公理    → 解决依赖混乱类缺陷                  │  │
│  │ 4. 粒度控制公理    → 解决粒度失控类缺陷                  │  │
│  │ 5. 终止公理        → 解决无限循环类缺陷                  │  │
│  │ 6. 健壮性公理      → 解决执行脆弱类缺陷                  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │               四层单向依赖架构                            │  │
│  ├─────────────────────────────────────────────────────────┤  │
│  │                                                          │  │
│  │  ┌───────────────────────────────────────────────────┐  │  │
│  │  │ 第1层：任务归一建模层                              │  │  │
│  │  │ - 输入：用户原始需求                              │  │  │
│  │  │ - 输出：Task四元组 (Target/Condition/Boundary/     │  │  │
│  │  │                    EndRule)                        │  │  │
│  │  │ - 核心能力：歧义消解、目标提取、边界约束            │  │  │
│  │  └───────────────────────────────────────────────────┘  │  │
│  │                              ↓                           │  │
│  │  ┌───────────────────────────────────────────────────┐  │  │
│  │  │ 第2层：拓扑依赖拆解层                              │  │  │
│  │  │ - 输入：Task四元组                                │  │  │
│  │  │ - 输出：DAG有向无环图                             │  │  │
│  │  │ - 核心能力：任务分解、依赖分析、DAG验证            │  │  │
│  │  └───────────────────────────────────────────────────┘  │  │
│  │                              ↓                           │  │
│  │  ┌───────────────────────────────────────────────────┐  │  │
│  │  │ 第3层：原子动作收敛层                              │  │  │
│  │  │ - 输入：DAG节点                                   │  │  │
│  │  │ - 输出：AtomicAction队列                          │  │  │
│  │  │ - 核心能力：动作拆分、原子验证、粒度控制           │  │  │
│  │  └───────────────────────────────────────────────────┘  │  │
│  │                              ↓                           │  │
│  │  ┌───────────────────────────────────────────────────┐  │  │
│  │  │ 第4层：分段校验收敛层                              │  │  │
│  │  │ - 输入：执行流程                                  │  │  │
│  │  │ - 输出：健壮的执行结果                            │  │  │
│  │  │ - 核心能力：分段校验、熔断机制、回滚恢复           │  │  │
│  │  └───────────────────────────────────────────────────┘  │  │
│  │                                                          │  │
│  └─────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │               核心数据结构                               │  │
│  ├─────────────────────────────────────────────────────────┤  │
│  │ - TaskTuple: 任务四元组                                 │  │
│  │ - DAG: 有向无环图 (Node, Edge)                          │  │
│  │ - AtomicAction: 原子动作                               │  │
│  │ - Checkpoint: 校验点                                    │  │
│  │ - RollbackPoint: 回滚点                                │  │
│  └─────────────────────────────────────────────────────────┘  │
│                              ↓                                  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │               设计约束                                   │  │
│  ├─────────────────────────────────────────────────────────┤  │
│  │ ✅ 模型无关 - 不绑定特定LLM                             │  │
│  │ ✅ 框架无关 - 可嵌入任意Agent框架                       │  │
│  │ ✅ 零外部服务依赖 - 无需数据库/队列                      │  │
│  │ ✅ 本地持久化 - JSON文件存储                            │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 第11阶段：系统功能范围划定

### 11.1 核心功能范围（必须包含）

| 功能模块 | 功能描述 | 优先级 |
|----------|----------|--------|
| 任务归一建模 | 用户需求 → 任务四元组 | P0 |
| 拓扑依赖拆解 | 任务四元组 → DAG | P0 |
| 原子动作收敛 | DAG节点 → 原子动作 | P0 |
| 分段校验收敛 | 执行流程 → 健壮执行 | P0 |
| DAG拓扑验证 | 无环、连通性检查 | P0 |
| 原子动作验证 | 三条标准校验 | P0 |
| 执行结果持久化 | 本地JSON存储 | P0 |

### 11.2 剔除的冗余非必要模块

| 模块 | 剔除原因 |
|------|----------|
| Web UI界面 | 不是核心，可后续单独添加 |
| REST API服务 | 不是核心，可后续单独添加 |
| 分布式调度 | 增加复杂度，单机优先 |
| 用户认证授权 | 增加复杂度，暂不需要 |
| 消息队列 | 增加依赖，本地调用优先 |
| 实时监控仪表盘 | 非核心功能 |
| 多租户隔离 | 增加复杂度，单机优先 |
| 自动扩展/弹性伸缩 | 增加复杂度，单机优先 |

---

## 第12阶段：模型无关、框架无关适配设计要求

### 12.1 模型无关设计

```python
# 模型无关接口定义
class BaseLLMAdapter:
    """
    基础LLM适配器，所有具体LLM实现都需要继承此接口
    """
    
    def __init__(self, config: dict):
        """
        初始化适配器
        """
        self.config = config
    
    def extract_target(self, user_request: str) -> str:
        """
        从用户请求中提取目标（Target）
        模型无关的抽象方法
        """
        raise NotImplementedError
    
    def extract_conditions(self, user_request: str) -> list[str]:
        """
        提取前置条件
        """
        raise NotImplementedError
    
    def decompose_task(self, task: TaskTuple) -> list[str]:
        """
        任务分解
        """
        raise NotImplementedError
    
    def generate_dag_edges(self, subtasks: list[str]) -> list[dict]:
        """
        生成DAG边（依赖关系）
        """
        raise NotImplementedError

# 示例：OpenAI适配器实现
class OpenAIAdapter(BaseLLMAdapter):
    def __init__(self, config: dict):
        super().__init__(config)
        self.client = OpenAI(api_key=config["api_key"])
    
    def extract_target(self, user_request: str) -> str:
        # 使用OpenAI API实现目标提取
        response = self.client.chat.completions.create(
            model=self.config.get("model", "gpt-4"),
            messages=[
                {"role": "system", "content": "Extract the single, clear target..."},
                {"role": "user", "content": user_request}
            ]
        )
        return response.choices[0].message.content

# 示例：Claude适配器实现
class ClaudeAdapter(BaseLLMAdapter):
    def __init__(self, config: dict):
        super().__init__(config)
        self.client = Anthropic(api_key=config["api_key"])
    
    def extract_target(self, user_request: str) -> str:
        # 使用Claude API实现目标提取
        response = self.client.messages.create(
            model=self.config.get("model", "claude-3-sonnet-20240229"),
            max_tokens=1000,
            messages=[{"role": "user", "content": "..."}]
        )
        return response.content[0].text
```

### 12.2 框架无关设计

```python
# 框架无关的插件接口
class BaseAgentFrameworkAdapter:
    """
    基础Agent框架适配器
    """
    
    def register_task_planner(self, planner):
        """
        注册任务规划器到Agent框架
        """
        raise NotImplementedError
    
    def execute_with_planner(self, user_request: str):
        """
        使用规划器执行
        """
        raise NotImplementedError

# 示例：LangChain适配器
class LangChainAdapter(BaseAgentFrameworkAdapter):
    def __init__(self):
        self.planner = None
    
    def register_task_planner(self, planner):
        self.planner = planner
    
    def execute_with_planner(self, user_request: str):
        # 集成到LangChain的Agent中
        from langchain.agents import AgentExecutor, create_react_agent
        from langchain.tools import Tool
        
        tools = [
            Tool(
                name="task_planner",
                func=self.planner.plan,
                description="..."
            )
        ]
        
        # ...创建agent并执行

# 示例：AutoGen适配器
class AutoGenAdapter(BaseAgentFrameworkAdapter):
    def __init__(self):
        self.planner = None
    
    def register_task_planner(self, planner):
        self.planner = planner
    
    def execute_with_planner(self, user_request: str):
        # 集成到AutoGen中
        from autogen import AssistantAgent, UserProxyAgent
        
        # ...配置agents，注册planner作为工具
```

---

## 第13阶段：任务串行、并行、依赖三种执行关系

### 13.1 三种执行关系定义

#### 关系1：串行执行（Sequential）
```
任务A → 任务B → 任务C
- A完成后才能开始B
- B完成后才能开始C
```

```python
def is_sequential(node_a: DAGNode, node_b: DAGNode, dag: TaskDAG) -> bool:
    """
    判断两个节点是否是串行关系（A必须在B之前执行）
    """
    # 检查A是否是B的直接或间接前驱
    return has_path(dag, node_a.id, node_b.id)
```

#### 关系2：并行执行（Parallel）
```
任务A ┐
      ├─→ 任务C
任务B ┘
- A和B可以同时执行
- C需要等待A和B都完成
```

```python
def is_parallel(node_a: DAGNode, node_b: DAGNode, dag: TaskDAG) -> bool:
    """
    判断两个节点是否是并行关系（可以同时执行，互不依赖）
    """
    # 检查A和B之间没有路径
    return (
        not has_path(dag, node_a.id, node_b.id) and
        not has_path(dag, node_b.id, node_a.id)
    )

def group_parallel_tasks(dag: TaskDAG) -> list[list[str]]:
    """
    分组并行任务
    """
    topo_order = topological_sort(dag)
    groups = []
    executed = set()
    
    while len(executed) < len(dag.nodes):
        current_group = []
        for node_id in topo_order:
            if node_id in executed:
                continue
            # 所有前驱都已执行
            predecessors = get_predecessors(dag, node_id)
            if all(p in executed for p in predecessors):
                current_group.append(node_id)
        groups.append(current_group)
        executed.update(current_group)
    
    return groups
```

#### 关系3：依赖关系（Dependency）
```
任务A ──depends_on──→ 任务B
- B依赖A的输出
- A必须在B之前完成
```

```python
DependencyType = {
    "DATA_FLOW": "数据流依赖",     # A的输出是B的输入
    "CONTROL_FLOW": "控制流依赖",  # B的执行取决于A的结果
    "RESOURCE": "资源依赖",        # A和B竞争同一资源
    "TEMPORAL": "时间依赖"         # A必须在B之前完成，但无数据交换
}

class DependencyEdge:
    def __init__(
        self,
        from_node: str,
        to_node: str,
        type: str,
        data_mapping: dict = None
    ):
        self.from_node = from_node
        self.to_node = to_node
        self.type = type
        self.data_mapping = data_mapping or {}  # A的输出 -> B的输入
```

### 13.2 三种关系组合示例
```
         任务A (并行起点)
        /       \
    任务B     任务C (并行)
        \       /
         任务D (依赖B和C)
            ↓
         任务E (依赖D)
```

---

## 第14阶段：任务合法/非法判定边界阈值

### 14.1 合法性判定规则

| 判定维度 | 合法阈值 | 非法阈值 | 说明 |
|----------|----------|----------|------|
| 目标明确性 | 明确可验证 | 模糊、歧义 | 目标必须是单一、清晰的 |
| 任务四元组完整性 | 4个字段都有值 | 缺少必要字段 | Target/Condition/Boundary/EndRule |
| DAG无环 | 0个环 | ≥1个环 | 有环的DAG无法执行 |
| DAG连通性 | 所有节点可达 | 存在孤立节点 | 孤立节点无法执行 |
| 原子动作数量 | ≤50个 | ≥100个 | 过多动作表示分解不够 |
| 预估总执行时间 | ≤24小时 | ≥72小时 | 过长时间需要拆分 |
| 依赖链长度 | ≤20层 | ≥50层 | 过深的依赖链 |

### 14.2 判定函数
```python
TaskValidationConfig = {
    "max_atomic_actions": 50,
    "max_execution_time_hours": 24,
    "max_dependency_chain_length": 20,
    "min_success_criteria_count": 1,
    "max_failure_criteria_count": 10
}

def validate_task_legality(
    task: TaskTuple,
    dag: TaskDAG,
    config: TaskValidationConfig
) -> tuple[bool, list[str]]:
    """
    判定任务是否合法
    """
    errors = []
    
    # 1. 检查任务四元组完整性
    if not task.target or not task.condition or not task.boundary or not task.end_rule:
        errors.append("任务四元组缺少必要字段")
    
    # 2. 检查DAG无环
    has_cycle, cycles = validate_no_cycles(dag)
    if has_cycle:
        errors.append(f"DAG存在环: {cycles}")
    
    # 3. 检查DAG连通性
    is_connected, unreachable = validate_connectivity(dag)
    if not is_connected:
        errors.append(f"存在不可达节点: {unreachable}")
    
    # 4. 检查原子动作数量
    if len(dag.nodes) > config.max_atomic_actions:
        errors.append(f"原子动作数量过多: {len(dag.nodes)} > {config.max_atomic_actions}")
    
    # 5. 检查依赖链长度
    max_chain = calculate_max_dependency_chain(dag)
    if max_chain > config.max_dependency_chain_length:
        errors.append(f"依赖链过长: {max_chain} > {config.max_dependency_chain_length}")
    
    return len(errors) == 0, errors
```

---

## 第15阶段：缺陷根治对应关系表

### 15.1 缺陷-架构-解决逻辑对应表

| 缺陷ID | 缺陷类型 | 对应架构层 | 解决逻辑 | 参考文档 |
|--------|----------|------------|----------|----------|
| D1.1 | 目标发散 | 任务归一建模层 | 目标归一化公理，强制单一Target | TASK_TUPLE_DEFINITION.md |
| D1.2 | 目标降级 | 任务归一建模层 | 目标验证，对比原始需求 | TASK_TUPLE_DEFINITION.md |
| D1.3 | 目标遗漏 | 任务归一建模层 | 完整性校验，Checklist检查 | TASK_TUPLE_DEFINITION.md |
| D1.4 | 目标歧义 | 任务归一建模层 | 歧义消解，多轮确认 | TASK_TUPLE_DEFINITION.md |
| D1.5-8 | 其他目标偏移 | 任务归一建模层 | 边界约束，EndRule定义 | TASK_TUPLE_DEFINITION.md |
| D2.1-6 | 流程残缺类 | 分段校验收敛层 | 分段校验，Checkpoint验证 | FAULT_TOLERANCE_RULES.md |
| D3.1-7 | 依赖混乱类 | 拓扑依赖拆解层 | DAG验证，无环检查 | DAG_TOPOLOGY_RULES.md |
| D4.1-5 | 粒度失控类 | 原子动作收敛层 | 三条硬性校验标准 | ATOMIC_ACTION_RULES.md |
| D5.1-3 | 无限循环类 | 分段校验收敛层 | 终止公理，熔断机制 | FAULT_TOLERANCE_RULES.md |
| D6.1-6 | 执行脆弱类 | 分段校验收敛层 | 熔断+回滚机制 | FAULT_TOLERANCE_RULES.md |

### 15.2 固化解决逻辑代码
```python
class DefectResolver:
    """
    缺陷解决器
    """
    
    def __init__(self):
        self.resolvers = {
            "D1": self._resolve_target_defect,
            "D2": self._resolve_flow_defect,
            "D3": self._resolve_dependency_defect,
            "D4": self._resolve_granularity_defect,
            "D5": self._resolve_loop_defect,
            "D6": self._resolve_robustness_defect
        }
    
    def resolve(self, defect_id: str, context: dict):
        """
        解决缺陷
        """
        prefix = defect_id.split(".")[0]
        if prefix in self.resolvers:
            return self.resolvers[prefix](defect_id, context)
        return None
    
    def _resolve_target_defect(self, defect_id: str, context: dict):
        """
        解决目标偏移类缺陷
        """
        task = context.get("task")
        if defect_id == "D1.1":
            # 目标发散：重新提取单一目标
            return self._extract_single_target(task)
        # ...其他缺陷处理
    
    def _resolve_dependency_defect(self, defect_id: str, context: dict):
        """
        解决依赖混乱类缺陷
        """
        dag = context.get("dag")
        if defect_id == "D3.1":
            # 循环依赖：打破环
            return self._break_cycles(dag)
        # ...其他缺陷处理
```

---

## 第16阶段：100阶段整体节奏确认

### 16.1 阶段节奏总览

| 阶段范围 | 阶段数 | 预计工作量 | 交付物类型 |
|----------|--------|------------|------------|
| 1-20 | 20 | 理论梳理 & 需求确权 | 设计文档、规范 |
| 21-50 | 30 | 四层架构模块开发 | 代码模块、单元测试 |
| 51-80 | 30 | 核心流程 & 代码工程落地 | 完整系统、集成测试 |
| 81-95 | 15 | 场景测试 & 缺陷迭代优化 | 测试报告、优化后的系统 |
| 96-100 | 5 | 文档固化 & 上线交付 & 复盘 | 完整文档、交付版本 |

### 16.2 关键里程碑
- M1 (阶段20完成)：理论与需求固化
- M2 (阶段50完成)：四层架构开发完成
- M3 (阶段80完成)：核心工程落地完成
- M4 (阶段95完成)：测试优化完成
- M5 (阶段100完成)：正式交付

---

## 第17阶段：每层模块交付物拆解

### 17.1 四层架构模块交付物

| 层级 | 模块名称 | 交付物 | 对应阶段 |
|------|----------|--------|----------|
| 任务归一建模层 | TaskNormalizer | TaskNormalizer类 + 单元测试 | 21-30 |
| 任务归一建模层 | ConditionExtractor | ConditionExtractor类 + 单元测试 | 21-30 |
| 任务归一建模层 | BoundaryDefiner | BoundaryDefiner类 + 单元测试 | 21-30 |
| 任务归一建模层 | EndRuleValidator | EndRuleValidator类 + 单元测试 | 21-30 |
| 拓扑依赖拆解层 | DAGBuilder | DAGBuilder类 + 单元测试 | 31-40 |
| 拓扑依赖拆解层 | DependencyAnalyzer | DependencyAnalyzer类 + 单元测试 | 31-40 |
| 拓扑依赖拆解层 | CycleDetector | CycleDetector类 + 单元测试 | 31-40 |
| 拓扑依赖拆解层 | TopologicalSorter | TopologicalSorter类 + 单元测试 | 31-40 |
| 原子动作收敛层 | AtomicActionSplitter | AtomicActionSplitter类 + 单元测试 | 41-45 |
| 原子动作收敛层 | AtomicActionValidator | AtomicActionValidator类 + 单元测试 | 41-45 |
| 分段校验收敛层 | CheckpointManager | CheckpointManager类 + 单元测试 | 46-50 |
| 分段校验收敛层 | CircuitBreaker | CircuitBreaker类 + 单元测试 | 46-50 |
| 分段校验收敛层 | RollbackManager | RollbackManager类 + 单元测试 | 46-50 |

---

## 第18阶段：统一命名规范、数据结构、接口基础约定

### 18.1 命名规范

#### 命名风格
```
- 类名：大驼峰命名法，如 TaskNormalizer, DAGBuilder
- 函数名：小写下划线命名法，如 extract_target(), validate_cycles()
- 变量名：小写下划线命名法，如 task_tuple, dag_nodes
- 常量名：大写下划线命名法，如 MAX_ATOMIC_ACTIONS, DEFAULT_TIMEOUT
- 私有属性：单下划线前缀，如 _internal_state, _cache
- 私有方法：单下划线前缀，如 _extract_single_target(), _validate_step()
```

#### 命名语义规范
```
动词前缀：
- create_ : 创建新对象
- get_ : 获取已存在对象
- update_ : 更新对象
- delete_ : 删除对象
- validate_ : 验证（返回bool）
- check_ : 检查（返回详情）
- extract_ : 提取信息
- parse_ : 解析文本/数据
- build_ : 构建复杂对象
- generate_ : 生成内容
- execute_ : 执行动作/流程
- rollback_ : 回滚操作
- save_ : 保存到持久化
- load_ : 从持久化加载
```

### 18.2 统一数据结构约定

```python
# 所有数据结构必须支持JSON序列化
class JSONSerializable:
    """
    基础序列化接口
    """
    def to_dict(self) -> dict:
        """
        转换为字典
        """
        raise NotImplementedError
    
    @classmethod
    def from_dict(cls, data: dict):
        """
        从字典创建对象
        """
        raise NotImplementedError
    
    def to_json(self, indent: int = 2) -> str:
        """
        转换为JSON字符串
        """
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str):
        """
        从JSON字符串创建对象
        """
        return cls.from_dict(json.loads(json_str))

# 示例：TaskTuple实现序列化
class TaskTuple(JSONSerializable):
    def __init__(
        self,
        target: str,
        condition: list[str],
        boundary: dict,
        end_rule: dict,
        context: dict = None,
        priority: int = 0
    ):
        self.target = target
        self.condition = condition
        self.boundary = boundary
        self.end_rule = end_rule
        self.context = context or {}
        self.priority = priority
    
    def to_dict(self) -> dict:
        return {
            "target": self.target,
            "condition": self.condition,
            "boundary": self.boundary,
            "end_rule": self.end_rule,
            "context": self.context,
            "priority": self.priority
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            target=data["target"],
            condition=data["condition"],
            boundary=data["boundary"],
            end_rule=data["end_rule"],
            context=data.get("context", {}),
            priority=data.get("priority", 0)
        )
```

### 18.3 统一接口基础约定

```python
# 基础接口模式
class BaseComponent:
    """
    所有组件的基础接口
    """
    
    def __init__(self, config: dict = None):
        """
        初始化组件
        """
        self.config = config or {}
        self._initialized = False
        self._validate_config()
    
    def _validate_config(self):
        """
        验证配置
        """
        # 子类实现
        pass
    
    def initialize(self):
        """
        初始化
        """
        if not self._initialized:
            self._initialize()
            self._initialized = True
    
    def _initialize(self):
        """
        实际初始化逻辑（子类实现）
        """
        pass
    
    def shutdown(self):
        """
        关闭清理
        """
        if self._initialized:
            self._shutdown()
            self._initialized = False
    
    def _shutdown(self):
        """
        实际关闭逻辑（子类实现）
        """
        pass

# 处理器模式
class BaseProcessor(BaseComponent):
    """
    处理器基础接口
    """
    
    def process(self, input_data):
        """
        处理输入数据，返回输出数据
        """
        # 验证输入
        if not self._validate_input(input_data):
            raise ValueError("Invalid input data")
        
        # 处理
        result = self._process(input_data)
        
        # 验证输出
        if not self._validate_output(result):
            raise ValueError("Invalid output data")
        
        return result
    
    def _validate_input(self, input_data) -> bool:
        """
        验证输入
        """
        return True
    
    def _validate_output(self, output_data) -> bool:
        """
        验证输出
        """
        return True
    
    def _process(self, input_data):
        """
        实际处理逻辑（子类实现）
        """
        raise NotImplementedError

# 错误码约定
ErrorCode = {
    "SUCCESS": 0,
    "INVALID_INPUT": 1001,
    "INVALID_CONFIG": 1002,
    "TARGET_EXTRACTION_FAILED": 2001,
    "DAG_HAS_CYCLE": 3001,
    "DAG_HAS_UNREACHABLE": 3002,
    "ATOMIC_ACTION_INVALID": 4001,
    "CHECKPOINT_FAILED": 5001,
    "CIRCUIT_BREAKER_OPEN": 5002,
    "ROLLBACK_FAILED": 5003
}

class TaskPlanningError(Exception):
    """
    任务规划异常基类
    """
    def __init__(self, code: int, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(f"[{code}] {message}")
```

---

## 第10-18阶段完成检查清单

- [x] 第10阶段：输出系统整体设计思维导图，对齐设计边界
- [x] 第11阶段：划定系统功能范围，剔除冗余非必要模块
- [x] 第12阶段：明确模型无关、框架无关适配设计要求
- [x] 第13阶段：梳理任务串行、并行、依赖三种执行关系
- [x] 第14阶段：制定任务合法/非法判定边界阈值
- [x] 第15阶段：整理缺陷根治对应关系表，固化解决逻辑
- [x] 第16阶段：输出阶段目标文档，确认100阶段整体节奏
- [x] 第17阶段：拆分每层模块交付物，明确各阶段产出形式
- [x] 第18阶段：统一命名规范、数据结构、接口基础约定

✅ **第10-18阶段全部完成！**
