# 分段校验、熔断、回滚基础机制规则
## 阶段9成果

---

## 一、整体机制架构

### 1.1 三层保障机制
```
┌───────────────────────────────────────────────────┐
│           健壮性保障三层机制                        │
├───────────────────────────────────────────────────┤
│  1. 分段校验（预防）→ 在关键节点主动检查状态      │
│  2. 熔断机制（止损）→ 连续失败时停止执行          │
│  3. 回滚机制（恢复）→ 失败后恢复到安全状态        │
└───────────────────────────────────────────────────┘
```

### 1.2 机制之间的关系
```
正常执行
    ↓
分段校验点 → 检查通过 → 继续执行
                    ↓ 检查失败
                熔断机制触发
                    ↓
                回滚机制执行
                    ↓
                恢复到安全状态
```

---

## 二、分段校验机制

### 2.1 什么是分段校验
分段校验是在任务执行的关键节点设置检查点，验证当前状态是否符合预期，确保：
- 前置条件满足
- 中间结果正确
- 系统状态正常
- 没有偏离预期目标

### 2.2 校验点设置规则

#### 规则1：关键节点必须设置校验点
```python
def should_set_checkpoint(node: DAGNode) -> bool:
    """
    判断一个节点是否应该设置校验点
    """
    # 规则1.1：关键路径上的节点
    if node.id in critical_path:
        return True
    
    # 规则1.2：有多个后继的节点（分支点）
    if len(get_successors(dag, node.id)) > 1:
        return True
    
    # 规则1.3：资源消耗大的节点
    if node.attributes.get("resource_cost", 0) > threshold:
        return True
    
    # 规则1.4：不可逆操作的前一个节点
    if has_irreversible_successors(dag, node.id):
        return True
    
    return False
```

#### 规则2：校验点类型
```python
CheckpointType = {
    "INPUT_VALIDATION": "输入校验",      # 执行前校验输入
    "STATE_VALIDATION": "状态校验",       # 执行后校验状态
    "OUTPUT_VALIDATION": "输出校验",      # 执行后校验输出
    "CONSISTENCY_CHECK": "一致性检查",    # 检查数据一致性
    "BOUNDARY_CHECK": "边界检查"          # 检查是否超出边界
}
```

### 2.3 校验点数据结构
```python
Checkpoint = {
    "id": str,                          # 校验点唯一ID
    "node_id": str,                     # 关联的节点ID
    "type": str,                        # 校验点类型
    "description": str,                 # 校验点描述
    "validation_rules": list[dict],     # 校验规则列表
    "failure_action": str,              # 失败时的动作
    "timeout": float,                   # 校验超时时间
    "severity": str                     # 严重程度：WARNING | ERROR | CRITICAL
}

ValidationRule = {
    "id": str,                          # 规则ID
    "description": str,                 # 规则描述
    "check": callable,                  # 检查函数
    "expected_value": any,              # 期望值
    "tolerance": float,                 # 容差（数值类型）
    "error_message": str                # 失败时的错误信息
}
```

### 2.4 分段校验执行流程
```python
def execute_with_checkpoints(dag: TaskDAG, start_node: str):
    """
    带校验点的执行流程
    """
    # 获取拓扑排序
    execution_order = topological_sort(dag)
    
    for node_id in execution_order:
        node = dag.get_node(node_id)
        
        # 1. 执行前置校验点
        pre_checkpoints = get_pre_checkpoints(dag, node_id)
        for checkpoint in pre_checkpoints:
            passed, errors = execute_checkpoint(checkpoint)
            if not passed:
                handle_checkpoint_failure(checkpoint, errors)
                return
        
        # 2. 执行节点
        success, result = execute_node(node)
        
        # 3. 执行后置校验点
        post_checkpoints = get_post_checkpoints(dag, node_id)
        for checkpoint in post_checkpoints:
            passed, errors = execute_checkpoint(checkpoint)
            if not passed:
                handle_checkpoint_failure(checkpoint, errors)
                return
        
        # 4. 记录状态
        save_execution_state(node_id, success, result)
```

---

## 三、熔断机制

### 3.1 什么是熔断机制
熔断机制是防止系统在连续失败时无限重试的保护机制，类似电路中的保险丝：
- **闭合状态**：正常执行
- **半开状态**：尝试恢复，允许少量请求
- **断开状态**：停止执行，直接返回错误

### 3.2 熔断状态机
```
         连续失败达到阈值
    ┌───────────────────────┐
    ↓                       │
┌─────────┐    超过时间窗    ┌─────────┐
│  闭合   │  ─────────────→  │  断开   │
└─────────┘                  └─────────┘
    ↑                         ↓
    │  成功次数达到阈值        │
    └─────────────────────────┘
         切换到半开状态
```

### 3.3 熔断配置
```python
CircuitBreakerConfig = {
    "failure_threshold": int,        # 失败阈值：连续失败N次触发
    "success_threshold": int,        # 成功阈值：连续成功N次恢复
    "timeout": float,                # 断开状态持续时间（秒）
    "half_open_max_calls": int,      # 半开状态允许的调用数
    "failure_window": float,         # 失败时间窗口（秒）
    "exceptions": list[type],        # 触发熔断的异常类型
    "fallback": callable            # 熔断时的降级方法
}
```

### 3.4 熔断实现
```python
class CircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = "CLOSED"  # CLOSED | OPEN | HALF_OPEN
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.lock = threading.Lock()
    
    def execute(self, func: callable, *args, **kwargs):
        """
        执行函数，带熔断保护
        """
        with self.lock:
            # 检查状态
            if self.state == "OPEN":
                # 检查是否可以切换到半开状态
                if time.time() - self.last_failure_time > self.config.timeout:
                    self.state = "HALF_OPEN"
                    self.success_count = 0
                else:
                    # 执行降级方法
                    if self.config.fallback:
                        return self.config.fallback(*args, **kwargs)
                    raise CircuitBreakerOpenError()
            
            # 半开状态，检查是否超过调用限制
            if self.state == "HALF_OPEN" and self.success_count >= self.config.half_open_max_calls:
                self.state = "OPEN"
                self.last_failure_time = time.time()
                if self.config.fallback:
                    return self.config.fallback(*args, **kwargs)
                raise CircuitBreakerOpenError()
        
        try:
            # 执行函数
            result = func(*args, **kwargs)
            
            # 成功，更新状态
            with self.lock:
                if self.state == "HALF_OPEN":
                    self.success_count += 1
                    if self.success_count >= self.config.success_threshold:
                        self.state = "CLOSED"
                        self.failure_count = 0
                else:
                    self.failure_count = 0
            
            return result
            
        except Exception as e:
            # 检查异常类型是否需要熔断
            if not any(isinstance(e, exc_type) for exc_type in self.config.exceptions):
                raise
            
            # 失败，更新状态
            with self.lock:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.config.failure_threshold:
                    self.state = "OPEN"
            
            raise
```

### 3.5 熔断触发规则
```python
def should_trigger_circuit_breaker(
    failure_count: int,
    failure_window: float,
    last_failure_time: float,
    current_time: float
) -> bool:
    """
    判断是否应该触发熔断
    """
    # 规则1：失败次数超过阈值
    if failure_count >= failure_threshold:
        return True
    
    # 规则2：在时间窗口内失败频率过高
    if current_time - last_failure_time < failure_window:
        if failure_count >= failure_threshold:
            return True
    
    return False
```

---

## 四、回滚机制

### 4.1 什么是回滚机制
回滚机制是在任务失败时，将系统恢复到执行前的安全状态的机制，包括：
- 数据回滚
- 状态恢复
- 资源释放

### 4.2 回滚点类型
```python
RollbackPointType = {
    "SAVEPOINT": "保存点",       # 轻量级保存点，快速回滚
    "CHECKPOINT": "检查点",      # 完整状态保存
    "SNAPSHOT": "快照"          # 全量数据快照
}
```

### 4.3 回滚点数据结构
```python
RollbackPoint = {
    "id": str,                          # 回滚点唯一ID
    "node_id": str,                     # 关联的节点ID
    "type": str,                        # 回滚点类型
    "state": dict,                      # 保存的状态
    "timestamp": float,                 # 创建时间戳
    "rollback_function": callable,     # 回滚函数
    "dependencies": list[str],          # 依赖的其他回滚点
    "description": str                  # 回滚点描述
}
```

### 4.4 回滚实现
```python
class RollbackManager:
    def __init__(self):
        self.rollback_points = {}  # rollback_id -> RollbackPoint
        self.execution_stack = []  # 执行顺序栈，用于逆序回滚
        self.lock = threading.Lock()
    
    def create_rollback_point(
        self,
        node_id: str,
        state: dict,
        rollback_function: callable,
        type: str = "SAVEPOINT"
    ) -> str:
        """
        创建回滚点
        """
        rollback_id = f"rollback_{uuid.uuid4().hex}"
        
        with self.lock:
            self.rollback_points[rollback_id] = RollbackPoint(
                id=rollback_id,
                node_id=node_id,
                type=type,
                state=deepcopy(state),
                timestamp=time.time(),
                rollback_function=rollback_function,
                dependencies=[],
                description=f"Rollback point for {node_id}"
            )
            self.execution_stack.append(rollback_id)
        
        return rollback_id
    
    def rollback_to(self, target_rollback_id: str):
        """
        回滚到指定的回滚点
        """
        with self.lock:
            # 找到目标回滚点在栈中的位置
            try:
                target_index = self.execution_stack.index(target_rollback_id)
            except ValueError:
                raise RollbackPointNotFoundError(target_rollback_id)
            
            # 从栈顶开始逆序回滚
            while self.execution_stack and self.execution_stack[-1] != target_rollback_id:
                rollback_id = self.execution_stack.pop()
                rollback_point = self.rollback_points[rollback_id]
                
                try:
                    rollback_point.rollback_function(rollback_point.state)
                except Exception as e:
                    logging.error(f"Rollback failed for {rollback_id}: {e}")
                
                # 移除已回滚的回滚点
                del self.rollback_points[rollback_id]
    
    def rollback_all(self):
        """
        回滚所有操作
        """
        with self.lock:
            # 逆序回滚
            while self.execution_stack:
                rollback_id = self.execution_stack.pop()
                rollback_point = self.rollback_points[rollback_id]
                
                try:
                    rollback_point.rollback_function(rollback_point.state)
                except Exception as e:
                    logging.error(f"Rollback failed for {rollback_id}: {e}")
                
                del self.rollback_points[rollback_id]
    
    def cleanup_old_rollback_points(self, max_age: float = 3600):
        """
        清理过期的回滚点
        """
        with self.lock:
            current_time = time.time()
            expired = [
                rid for rid, rp in self.rollback_points.items()
                if current_time - rp.timestamp > max_age
            ]
            
            for rid in expired:
                del self.rollback_points[rid]
                if rid in self.execution_stack:
                    self.execution_stack.remove(rid)
```

---

## 五、三层机制协同工作

### 5.1 完整执行流程图
```
开始执行
    ↓
创建回滚点 ←────────────────────────┐
    ↓                            │
执行前置校验点                     │
    ↓ 通过                       │ 失败
执行节点 ←──────────────┐        │
    ↓                    │        │
执行后置校验点            │        │
    ↓ 通过               │ 重试   │
记录状态                  │        │
    ↓                    └────────┘
检查是否需要熔断 → 是 → 触发熔断
    ↓ 否                    │
移除不需要的回滚点 ←──────────┘
    ↓
继续下一个节点
```

### 5.2 协同实现示例
```python
class RobustExecutor:
    """
    健壮的执行器，集成三段机制
    """
    def __init__(
        self,
        dag: TaskDAG,
        circuit_breaker_config: CircuitBreakerConfig
    ):
        self.dag = dag
        self.rollback_manager = RollbackManager()
        self.circuit_breakers = {}  # node_id -> CircuitBreaker
        self.execution_state = {}
        
        # 为每个节点创建熔断器
        for node in dag.nodes:
            self.circuit_breakers[node.id] = CircuitBreaker(
                circuit_breaker_config
            )
    
    def execute(self):
        """
        执行整个DAG
        """
        execution_order = topological_sort(self.dag)
        
        try:
            for node_id in execution_order:
                self._execute_node_with_robustness(node_id)
            
            logging.info("Execution completed successfully")
            
        except Exception as e:
            logging.error(f"Execution failed: {e}")
            # 执行回滚
            self.rollback_manager.rollback_all()
            raise
    
    def _execute_node_with_robustness(self, node_id: str):
        """
        执行单个节点，集成三段机制
        """
        node = self.dag.get_node(node_id)
        circuit_breaker = self.circuit_breakers[node_id]
        
        # 1. 创建回滚点
        rollback_id = self.rollback_manager.create_rollback_point(
            node_id=node_id,
            state=self._capture_current_state(),
            rollback_function=self._rollback_function_for(node)
        )
        
        try:
            # 2. 执行前置校验
            pre_checkpoints = get_pre_checkpoints(self.dag, node_id)
            for checkpoint in pre_checkpoints:
                passed, errors = execute_checkpoint(checkpoint)
                if not passed:
                    raise CheckpointFailedError(checkpoint.id, errors)
            
            # 3. 使用熔断器执行节点
            result = circuit_breaker.execute(
                execute_node,
                node
            )
            
            # 4. 执行后置校验
            post_checkpoints = get_post_checkpoints(self.dag, node_id)
            for checkpoint in post_checkpoints:
                passed, errors = execute_checkpoint(checkpoint)
                if not passed:
                    raise CheckpointFailedError(checkpoint.id, errors)
            
            # 5. 成功，记录状态
            self.execution_state[node_id] = {
                "status": "SUCCESS",
                "result": result,
                "timestamp": time.time()
            }
            
            # 6. 移除已成功的回滚点（不再需要）
            self.rollback_manager.cleanup_old_rollback_points()
            
        except Exception as e:
            logging.error(f"Node {node_id} failed: {e}")
            
            # 回滚到之前的状态
            self.rollback_manager.rollback_to(rollback_id)
            
            raise
```

---

## 六、阶段9完成检查清单

- [x] 定义三段保障机制：分段校验、熔断、回滚
- [x] 设计校验点设置规则
- [x] 实现校验点数据结构和执行流程
- [x] 设计熔断状态机和配置
- [x] 实现熔断器
- [x] 设计回滚点类型和数据结构
- [x] 实现回滚管理器
- [x] 实现三段机制协同工作
- [x] 提供完整示例

✅ **阶段9已完成！**
