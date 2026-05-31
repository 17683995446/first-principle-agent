# 原子动作判定三条硬性校验标准
## 阶段8成果

---

## 一、核心定义

### 1.1 什么是原子动作
原子动作是任务分解的最小单位，具有以下特征：
- **不可再分**：继续分解会失去实际意义
- **单一职责**：只做一件事
- **可独立验证**：有明确的成功/失败标准
- **可重复执行**：重复执行产生相同的结果

### 1.2 原子动作的形式化定义
```python
AtomicAction = {
    "id": str,                     # 唯一标识符
    "name": str,                   # 动作名称
    "description": str,            # 动作描述
    "inputs": list[str],           # 输入列表
    "outputs": list[str],          # 输出列表
    "parameters": dict,            # 参数定义
    "success_criteria": list[str], # 成功标准
    "failure_criteria": list[str], # 失败标准
    "estimated_time": float,       # 预估耗时（秒）
    "retry_policy": dict,          # 重试策略
    "rollback": dict               # 回滚策略
}
```

---

## 二、第一条硬性校验标准：不可再分原则

### 2.1 标准定义
**一个动作是原子的，当且仅当它不能被有意义地进一步分解为更小的可执行单元**

### 2.2 判定规则
```python
def rule_1_not_decomposable(action: AtomicAction) -> tuple[bool, str]:
    """
    规则1：不可再分原则
    检查动作是否可以被有意义地进一步分解
    """
    warnings = []
    
    # 检查点1：动作名称是否包含"和"
    if "和" in action.name or "并" in action.name or "与" in action.name:
        warnings.append(
            f"动作名称 '{action.name}' 包含并列连接词，"
            f"可能需要分解为多个动作"
        )
    
    # 检查点2：动作描述是否包含多个步骤
    step_words = ["第一步", "第二步", "然后", "接着", "之后"]
    for word in step_words:
        if word in action.description:
            warnings.append(
                f"动作描述包含步骤描述词 '{word}'，"
                f"可能需要进一步分解"
            )
    
    # 检查点3：预估耗时检查
    if action.estimated_time and action.estimated_time > 300:  # >5分钟
        warnings.append(
            f"预估耗时 {action.estimated_time} 秒超过建议阈值，"
            f"建议进一步分解为更小的动作"
        )
    
    # 检查点4：输出数量检查
    if len(action.outputs) > 3:
        warnings.append(
            f"输出数量 {len(action.outputs)} 超过建议阈值，"
            f"建议考虑分解为多个单一输出的动作"
        )
    
    if warnings:
        return False, "\n".join(warnings)
    
    return True, "符合不可再分原则"
```

### 2.3 错误示例
```python
# 错误：这个动作可以分解为多个小动作
bad_action = {
    "name": "下载并处理文件",  # ❌ 包含"并"
    "description": "首先下载文件，然后解压，最后处理数据",  # ❌ 包含步骤
    "outputs": ["下载的文件", "解压的文件", "处理后的数据"]  # ❌ 输出太多
}
```

### 2.4 正确示例
```python
# 正确：每个动作都是单一职责
good_actions = [
    {
        "name": "下载文件",
        "description": "从指定URL下载文件到本地",
        "outputs": ["下载的文件"]
    },
    {
        "name": "解压文件",
        "description": "将压缩文件解压到指定目录",
        "outputs": ["解压的文件"]
    },
    {
        "name": "处理数据",
        "description": "对数据进行清洗和转换",
        "outputs": ["处理后的数据"]
    }
]
```

---

## 三、第二条硬性校验标准：单一职责原则

### 3.1 标准定义
**一个动作应该只负责完成一件明确的任务，不应该承担多个不相关的职责**

### 3.2 判定规则
```python
def rule_2_single_responsibility(action: AtomicAction) -> tuple[bool, str]:
    """
    规则2：单一职责原则
    检查动作是否只承担一个职责
    """
    warnings = []
    
    # 检查点1：输入输出关联性
    if len(action.inputs) > 0 and len(action.outputs) > 0:
        # 检查输入和输出之间是否有逻辑联系
        input_types = [inp.split(":")[0] if ":" in inp else inp for inp in action.inputs]
        output_types = [out.split(":")[0] if ":" in out else out for out in action.outputs]
        
        # 检查是否有不相关的输入或输出
        unrelated = []
        # 这里需要更复杂的语义分析，简化为关键字匹配
        for inp in input_types:
            has_match = any(inp in out or out in inp for out in output_types)
            if not has_match and len(output_types) > 0:
                unrelated.append(inp)
        
        if unrelated:
            warnings.append(
                f"发现可能不相关的输入: {unrelated}"
            )
    
    # 检查点2：动作关键词检查
    multi_verbs = ["创建并保存", "读取并写入", "下载并处理"]
    for verb in multi_verbs:
        if verb in action.name:
            warnings.append(
                f"动作名称 '{verb}' 包含多个动词，"
                f"可能违反单一职责原则"
            )
    
    # 检查点3：成功标准数量
    if len(action.success_criteria) > 3:
        warnings.append(
            f"成功标准数量 {len(action.success_criteria)} 较多，"
            f"建议考虑是否可以拆分"
        )
    
    if warnings:
        return False, "\n".join(warnings)
    
    return True, "符合单一职责原则"
```

### 3.3 错误示例
```python
# 错误：这个动作承担了多个职责
bad_action = {
    "name": "创建用户并发送欢迎邮件并生成报告",  # ❌ 多个职责
    "inputs": ["用户信息", "邮件模板", "报告模板"],
    "outputs": ["用户ID", "邮件ID", "报告文件"],
    "success_criteria": [
        "用户创建成功",
        "邮件发送成功",
        "报告生成成功"
    ]
}
```

### 3.4 正确示例
```python
# 正确：每个动作只做一件事
good_actions = [
    {
        "name": "创建用户",
        "inputs": ["用户信息"],
        "outputs": ["用户ID"],
        "success_criteria": ["用户创建成功"]
    },
    {
        "name": "发送欢迎邮件",
        "inputs": ["用户ID", "邮件模板"],
        "outputs": ["邮件ID"],
        "success_criteria": ["邮件发送成功"]
    },
    {
        "name": "生成报告",
        "inputs": ["用户ID", "报告模板"],
        "outputs": ["报告文件"],
        "success_criteria": ["报告生成成功"]
    }
]
```

---

## 四、第三条硬性校验标准：可独立验证原则

### 4.1 标准定义
**一个原子动作必须有明确的、可验证的成功标准和失败标准，能够独立判断动作是否完成**

### 4.2 判定规则
```python
def rule_3_independently_verifiable(action: AtomicAction) -> tuple[bool, str]:
    """
    规则3：可独立验证原则
    检查动作是否有明确的验证标准
    """
    errors = []
    warnings = []
    
    # 检查点1：成功标准不能为空
    if not action.success_criteria or len(action.success_criteria) == 0:
        errors.append("缺少成功标准，无法验证动作是否完成")
    
    # 检查点2：失败标准不能为空
    if not action.failure_criteria or len(action.failure_criteria) == 0:
        errors.append("缺少失败标准，无法验证动作是否失败")
    
    # 检查点3：成功标准是否明确可验证
    vague_words = ["差不多", "大概", "可能", "应该", "好像"]
    for criteria in action.success_criteria:
        for word in vague_words:
            if word in criteria:
                warnings.append(
                    f"成功标准 '{criteria}' 包含模糊词汇 '{word}'，"
                    f"建议使用更明确的表述"
                )
        
        # 检查是否有量化指标
        quantifiable_words = ["成功", "完成", "存在", "等于", "大于", "小于"]
        if not any(word in criteria for word in quantifiable_words):
            warnings.append(
                f"成功标准 '{criteria}' 建议包含更明确的可验证表述"
            )
    
    # 检查点4：输出定义
    if not action.outputs or len(action.outputs) == 0:
        warnings.append("缺少输出定义，建议明确动作的输出")
    
    if errors:
        return False, "\n".join(errors)
    
    if warnings:
        return True, "\n".join(warnings)
    
    return True, "符合可独立验证原则"
```

### 4.3 错误示例
```python
# 错误：缺少明确的验证标准
bad_action = {
    "name": "改进代码质量",
    "success_criteria": ["代码变得更好"],  # ❌ 模糊
    "failure_criteria": []  # ❌ 空
}
```

### 4.4 正确示例
```python
# 正确：有明确的验证标准
good_action = {
    "name": "运行代码质量检查",
    "inputs": ["代码仓库"],
    "outputs": ["质量报告"],
    "success_criteria": [
        "所有单元测试通过",
        "代码覆盖率 >= 80%",
        "无严重bug",
        "代码风格检查通过"
    ],
    "failure_criteria": [
        "测试失败",
        "覆盖率不达标",
        "发现严重bug"
    ]
}
```

---

## 五、综合验证流程

### 5.1 完整验证函数
```python
def validate_atomic_action(action: AtomicAction) -> tuple[bool, dict]:
    """
    对原子动作进行三条标准的完整验证
    """
    results = {}
    
    # 规则1：不可再分原则
    rule1_passed, rule1_msg = rule_1_not_decomposable(action)
    results["rule_1"] = {
        "passed": rule1_passed,
        "message": rule1_msg
    }
    
    # 规则2：单一职责原则
    rule2_passed, rule2_msg = rule_2_single_responsibility(action)
    results["rule_2"] = {
        "passed": rule2_passed,
        "message": rule2_msg
    }
    
    # 规则3：可独立验证原则
    rule3_passed, rule3_msg = rule_3_independently_verifiable(action)
    results["rule_3"] = {
        "passed": rule3_passed,
        "message": rule3_msg
    }
    
    # 综合结果
    all_passed = rule1_passed and rule2_passed and rule3_passed
    
    return all_passed, results
```

### 5.2 验证流程示意图
```
输入原子动作
    ↓
┌─────────────────────┐
│ 规则1：不可再分    │
│ - 检查连接词       │
│ - 检查步骤描述     │
│ - 检查预估耗时     │
│ - 检查输出数量     │
└─────────────────────┘
    ↓
┌─────────────────────┐
│ 规则2：单一职责    │
│ - 检查职责数量     │
│ - 检查关键词       │
│ - 检查成功标准     │
└─────────────────────┘
    ↓
┌─────────────────────┐
│ 规则3：可独立验证  │
│ - 检查成功标准     │
│ - 检查失败标准     │
│ - 检查可验证性     │
└─────────────────────┘
    ↓
输出验证结果
```

---

## 六、完整示例：蛋糕制作流程

### 6.1 复合任务分解
```python
# 复合任务：制作蛋糕
compound_task = {
    "name": "制作巧克力蛋糕",
    "description": "制作一个完整的巧克力奶油蛋糕"
}
```

### 6.2 分解为原子动作
```python
# 分解后的原子动作列表
atomic_actions = [
    # 步骤1：准备材料
    {
        "name": "购买面粉",
        "inputs": ["面粉类型", "数量"],
        "outputs": ["面粉"],
        "success_criteria": ["面粉购买成功"],
        "failure_criteria": ["无库存", "预算不足"]
    },
    {
        "name": "购买鸡蛋",
        "inputs": ["数量"],
        "outputs": ["鸡蛋"],
        "success_criteria": ["鸡蛋购买成功"],
        "failure_criteria": ["无库存"]
    },
    # ... 更多材料准备动作
    
    # 步骤2：制作蛋糕
    {
        "name": "混合干料",
        "inputs": ["面粉", "糖", "泡打粉"],
        "outputs": ["干料混合物"],
        "success_criteria": ["材料均匀混合"],
        "failure_criteria": ["混合不均匀"]
    },
    {
        "name": "混合湿料",
        "inputs": ["鸡蛋", "牛奶", "油"],
        "outputs": ["湿料混合物"],
        "success_criteria": ["材料均匀混合"],
        "failure_criteria": ["混合不均匀"]
    },
    {
        "name": "合并面糊",
        "inputs": ["干料混合物", "湿料混合物"],
        "outputs": ["面糊"],
        "success_criteria": ["干湿料充分混合", "无干粉"],
        "failure_criteria": ["混合过度", "混合不足"]
    },
    {
        "name": "烘烤蛋糕",
        "inputs": ["面糊", "烤箱温度", "时间"],
        "outputs": ["蛋糕胚"],
        "success_criteria": ["烘烤完成", "牙签插入拔出干净"],
        "failure_criteria": ["烤焦", "未烤熟"]
    },
    # ... 更多制作步骤
    
    # 步骤3：装饰蛋糕
    {
        "name": "打发奶油",
        "inputs": ["奶油", "糖"],
        "outputs": ["打发的奶油"],
        "success_criteria": ["奶油打发至8分发"],
        "failure_criteria": ["打发过度", "未打发"]
    },
    {
        "name": "涂抹奶油",
        "inputs": ["蛋糕胚", "打发的奶油"],
        "outputs": ["涂抹奶油的蛋糕"],
        "success_criteria": ["奶油均匀涂抹"],
        "failure_criteria": ["涂抹不均"]
    }
]
```

### 6.3 逐个验证
```python
for i, action in enumerate(atomic_actions):
    passed, results = validate_atomic_action(action)
    print(f"\n动作 {i+1}: {action['name']}")
    print(f"验证结果: {'通过' if passed else '未通过'}")
    for rule, result in results.items():
        print(f"  {rule}: {'✅' if result['passed'] else '❌'} - {result['message']}")
```

---

## 七、阶段8完成检查清单

- [x] 定义原子动作的形式化结构
- [x] 制定第一条标准：不可再分原则
- [x] 制定第二条标准：单一职责原则
- [x] 制定第三条标准：可独立验证原则
- [x] 实现每条标准的验证函数
- [x] 提供错误和正确示例
- [x] 提供综合验证流程
- [x] 提供完整的应用示例

✅ **阶段8已完成！**
