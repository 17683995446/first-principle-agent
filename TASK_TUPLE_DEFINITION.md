# 任务四元组定义文档
## 阶段5成果

---

## 任务四元组总览

任务四元组是第1层（任务归一建模层）的核心输出，将模糊的用户需求转换为形式化、可验证的标准化结构。

```python
TaskTuple = {
    "target": str,           # [必需] 唯一目标
    "condition": list,       # [必需] 前置条件列表
    "boundary": dict,        # [必需] 边界约束
    "end_rule": dict,        # [必需] 终止规则
    "context": dict,         # [可选] 上下文信息
    "priority": int,         # [可选] 优先级，默认5
    "metadata": dict         # [可选] 元数据
}
```

---

## 字段1：Target（唯一目标）

### 📋 字段含义
任务的**唯一、明确、无歧义**的最终目标。

### 🎯 判定标准
1. **唯一性**：只有一个目标，不能有多个并列目标
2. **明确性**：使用精确、无歧义的语言
3. **可验证性**：能够明确判断目标是否达成
4. **完整性**：包含所有必要信息，不缺失关键要素

### ❌ 错误示例
```python
# 错误：多个目标
target = "买牛奶和面包"

# 错误：模糊歧义
target = "改进一下"

# 错误：不可验证
target = "变得更好"

# 错误：不完整
target = "做蛋糕"  # 没有说明是做什么蛋糕
```

### ✅ 正确示例
```python
# 正确：唯一、明确、可验证、完整
target = "制作一个10寸、可食用的巧克力奶油蛋糕"

# 正确：明确的交付物
target = "生成一份包含1000字的关于AI伦理的报告，格式为PDF"

# 正确：可验证的标准
target = "将网站首页加载速度从5秒优化到1秒以内"
```

### 🛠️ 验证函数
```python
def validate_target(target: str) -> tuple[bool, list[str]]:
    errors = []
    
    # 检查非空
    if not target or not target.strip():
        errors.append("目标不能为空")
    
    # 检查是否包含多个目标（通过关键词检测）
    multi_target_keywords = ["和", "与", "及", "以及", "同时", "并且"]
    for keyword in multi_target_keywords:
        if keyword in target:
            # 需要进一步判断是否真的是多个目标
            pass  # 更复杂的逻辑
    
    # 检查是否有歧义词汇
    ambiguous_words = ["改进", "优化", "更好", "差不多", "大概"]
    for word in ambiguous_words:
        if word in target:
            errors.append(f"目标包含歧义词汇: {word}")
    
    # 检查是否有可验证的标准
    if not any(criteria in target.lower() for criteria in 
              ["达到", "完成", "生成", "制作", "优化到", "从...到"]):
        errors.append("目标缺少可验证的成功标准")
    
    return len(errors) == 0, errors
```

---

## 字段2：Condition（前置条件）

### 📋 字段含义
任务开始执行前**必须满足**的条件列表。

### 🎯 判定标准
1. **必要性**：确实是执行任务必需的，不是可有可无的
2. **可验证性**：能够明确判断条件是否满足
3. **原子性**：每个条件只描述一件事
4. **完整性**：列出所有关键前置条件

### ❌ 错误示例
```python
# 错误：不明确
condition = ["有材料"]

# 错误：非必要
condition = ["天气好", "心情好"]

# 错误：不是前置条件（而是后置条件）
condition = ["蛋糕做好"]
```

### ✅ 正确示例
```python
# 正确：明确、必要、可验证
condition = [
    "厨房可用",
    "已购买低筋面粉500g",
    "已购买鸡蛋10个",
    "已购买牛奶500ml",
    "已购买巧克力200g",
    "烤箱功能正常"
]

# 正确：软件任务前置条件
condition = [
    "Python 3.8+ 已安装",
    "Git 仓库已克隆",
    "依赖包 requirements.txt 已安装",
    "数据库连接正常"
]
```

### 🛠️ 验证函数
```python
def validate_condition(condition: list) -> tuple[bool, list[str]]:
    errors = []
    
    if not isinstance(condition, list):
        errors.append("前置条件必须是列表类型")
        return False, errors
    
    for i, cond in enumerate(condition):
        if not cond or not cond.strip():
            errors.append(f"条件 {i+1} 不能为空")
        
        # 检查是否是断言式陈述
        if not any(cond.startswith(prefix) for prefix in 
                  ["有", "已", "可以", "能够", "正常"]):
            # 不一定需要严格前缀，但应该是陈述句式
            pass
    
    return len(errors) == 0, errors
```

---

## 字段3：Boundary（边界约束）

### 📋 字段含义
任务执行的**边界限制**，明确哪些做、哪些不做。

### 🎯 判定标准
1. **明确性**：边界清晰，不模糊
2. **可判定性**：能够明确判断是否越界
3. **完整性**：包含关键的边界约束
4. **正反两方面**：最好说明"做什么"和"不做什么"

### 📐 Boundary 子字段定义
```python
boundary = {
    "include": list,     # 包含的内容
    "exclude": list,     # 排除的内容
    "constraints": dict  # 其他约束条件
}
```

### ❌ 错误示例
```python
# 错误：边界模糊
boundary = {
    "include": ["一些东西"],
    "exclude": ["不要太复杂"]
}

# 错误：无意义的约束
boundary = {
    "constraints": {"越快越好": True}
}
```

### ✅ 正确示例
```python
# 正确：明确的边界
boundary = {
    "include": [
        "制作蛋糕本体",
        "涂抹奶油",
        "巧克力装饰"
    ],
    "exclude": [
        "不研究蛋糕历史",
        "不写蛋糕制作教程",
        "不拍视频"
    ],
    "constraints": {
        "时间限制": "2小时内",
        "预算限制": "100元以内",
        "工具限制": "只使用家里现有的工具"
    }
}

# 正确：软件开发边界
boundary = {
    "include": [
        "用户登录功能",
        "密码重置功能"
    ],
    "exclude": [
        "不做第三方登录",
        "不做社交分享功能",
        "不做付费模块"
    ],
    "constraints": {
        "技术栈": "React + Node.js",
        "兼容浏览器": "Chrome 90+, Firefox 88+",
        "响应式": "支持移动端"
    }
}
```

### 🛠️ 验证函数
```python
def validate_boundary(boundary: dict) -> tuple[bool, list[str]]:
    errors = []
    
    if not isinstance(boundary, dict):
        errors.append("边界约束必须是字典类型")
        return False, errors
    
    required_keys = ["include", "exclude", "constraints"]
    for key in required_keys:
        if key not in boundary:
            errors.append(f"边界约束缺少必需字段: {key}")
    
    # 检查 include 和 exclude 是否有重叠
    include_set = set(boundary.get("include", []))
    exclude_set = set(boundary.get("exclude", []))
    overlap = include_set & exclude_set
    if overlap:
        errors.append(f"边界约束中 include 和 exclude 有重叠: {overlap}")
    
    return len(errors) == 0, errors
```

---

## 字段4：EndRule（终止规则）

### 📋 字段含义
任务**何时结束**的明确规则，包括成功终止和失败终止。

### 🎯 判定标准
1. **可判定性**：能够明确判断是否满足终止条件
2. **完整性**：包含成功终止和失败终止两种情况
3. **收敛性**：确保任务一定会终止（防止无限循环）
4. **可量化**：尽可能使用量化指标

### 📐 EndRule 子字段定义
```python
end_rule = {
    "success_criteria": list,   # 成功终止条件
    "failure_criteria": list,   # 失败终止条件
    "timeout": float,           # 超时时间（秒）
    "max_attempts": int         # 最大尝试次数
}
```

### ❌ 错误示例
```python
# 错误：无终止条件
end_rule = {}

# 错误：不可判定
end_rule = {
    "success_criteria": ["做得差不多就行"]
}

# 错误：无超时保护
end_rule = {
    "success_criteria": ["完成"]
}
```

### ✅ 正确示例
```python
# 正确：明确、可判定、有收敛保证
end_rule = {
    "success_criteria": [
        "蛋糕外观完整",
        "蛋糕内部熟透",
        "甜度适中",
        "可安全食用"
    ],
    "failure_criteria": [
        "蛋糕烤焦",
        "蛋糕塌陷",
        "原材料变质"
    ],
    "timeout": 7200,  # 2小时超时
    "max_attempts": 3  # 最多尝试3次
}

# 正确：软件任务终止规则
end_rule = {
    "success_criteria": [
        "所有单元测试通过",
        "代码覆盖率 ≥ 80%",
        "无严重bug",
        "性能指标达标"
    ],
    "failure_criteria": [
        "构建失败超过5次",
        "关键路径不可用",
        "数据丢失"
    ],
    "timeout": 86400,  # 24小时超时
    "max_attempts": 5
}
```

### 🛠️ 验证函数
```python
def validate_end_rule(end_rule: dict) -> tuple[bool, list[str]]:
    errors = []
    
    if not isinstance(end_rule, dict):
        errors.append("终止规则必须是字典类型")
        return False, errors
    
    required_keys = ["success_criteria", "failure_criteria", "timeout", "max_attempts"]
    for key in required_keys:
        if key not in end_rule:
            errors.append(f"终止规则缺少必需字段: {key}")
    
    # 检查 timeout 是否有效
    if "timeout" in end_rule and (not isinstance(end_rule["timeout"], (int, float)) or end_rule["timeout"] <= 0):
        errors.append("超时时间必须是正数")
    
    # 检查 max_attempts 是否有效
    if "max_attempts" in end_rule and (not isinstance(end_rule["max_attempts"], int) or end_rule["max_attempts"] <= 0):
        errors.append("最大尝试次数必须是正整数")
    
    # 检查成功和失败条件是否都有
    if not end_rule.get("success_criteria"):
        errors.append("成功终止条件不能为空")
    if not end_rule.get("failure_criteria"):
        errors.append("失败终止条件不能为空")
    
    return len(errors) == 0, errors
```

---

## 字段5-7：可选字段

### Context（上下文信息）
```python
context = {
    "user_id": str,           # 用户ID
    "request_time": float,    # 请求时间戳
    "session_id": str,        # 会话ID
    "history": list,          # 历史对话
    "environment": dict       # 环境信息
}
```

### Priority（优先级）
```python
# 1-10，1最低，10最高，默认5
priority = 7
```

### Metadata（元数据）
```python
metadata = {
    "version": str,           # 版本号
    "created_at": float,      # 创建时间
    "updated_at": float,      # 更新时间
    "source": str,            # 来源
    "tags": list              # 标签
}
```

---

## 任务四元组完整验证

### 🛠️ 完整验证函数
```python
def validate_task_tuple(task_tuple: dict) -> tuple[bool, list[str]]:
    all_errors = []
    
    # 验证 Target
    target_ok, target_errors = validate_target(task_tuple.get("target", ""))
    if not target_ok:
        all_errors.extend([f"[Target] {e}" for e in target_errors])
    
    # 验证 Condition
    cond_ok, cond_errors = validate_condition(task_tuple.get("condition", []))
    if not cond_ok:
        all_errors.extend([f"[Condition] {e}" for e in cond_errors])
    
    # 验证 Boundary
    boundary_ok, boundary_errors = validate_boundary(task_tuple.get("boundary", {}))
    if not boundary_ok:
        all_errors.extend([f"[Boundary] {e}" for e in boundary_errors])
    
    # 验证 EndRule
    end_ok, end_errors = validate_end_rule(task_tuple.get("end_rule", {}))
    if not end_ok:
        all_errors.extend([f"[EndRule] {e}" for e in end_errors])
    
    return len(all_errors) == 0, all_errors
```

### ✅ 完整示例
```python
task_tuple = {
    "target": "制作一个10寸、可食用的巧克力奶油蛋糕",
    "condition": [
        "厨房可用",
        "已购买低筋面粉500g",
        "已购买鸡蛋10个",
        "已购买牛奶500ml",
        "已购买巧克力200g",
        "烤箱功能正常"
    ],
    "boundary": {
        "include": [
            "制作蛋糕本体",
            "涂抹奶油",
            "巧克力装饰"
        ],
        "exclude": [
            "不研究蛋糕历史",
            "不写蛋糕制作教程"
        ],
        "constraints": {
            "时间限制": "2小时内",
            "预算限制": "100元以内"
        }
    },
    "end_rule": {
        "success_criteria": [
            "蛋糕外观完整",
            "蛋糕内部熟透",
            "可安全食用"
        ],
        "failure_criteria": [
            "蛋糕烤焦",
            "蛋糕塌陷"
        ],
        "timeout": 7200,
        "max_attempts": 3
    },
    "context": {
        "user_id": "user_123",
        "request_time": 1716666666
    },
    "priority": 5,
    "metadata": {
        "version": "1.0",
        "created_at": 1716666666
    }
}

# 验证
is_valid, errors = validate_task_tuple(task_tuple)
print(f"验证结果: {'通过' if is_valid else '失败'}")
if errors:
    print("错误:", errors)
```

---

## 阶段5完成检查清单

- [x] 定义 Target 字段含义与判定标准
- [x] 定义 Condition 字段含义与判定标准
- [x] 定义 Boundary 字段含义与判定标准
- [x] 定义 EndRule 字段含义与判定标准
- [x] 提供错误和正确示例
- [x] 提供验证函数
- [x] 提供完整示例
- [x] 输出任务四元组定义文档

✅ **阶段5已完成！**
