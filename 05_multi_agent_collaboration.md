# 05 - 多 Agent 协作：1+1>2 的智能系统

> **AI Agent 开发教程 第 05 课**  
> 📅 2026 年 3 月 | 👨‍💻 [@Gale2World](https://github.com/zdnuist)

---

## 📋 课程目标

学完本课后，你将能够：
- ✅ 理解多 Agent 协作的优势
- ✅ 设计 Agent 角色和分工
- ✅ 实现 Agent 间通信机制
- ✅ 构建多 Agent 协作系统

---

## 一、为什么需要多 Agent？

### 1.1 单 Agent 的局限

```
单 Agent 处理复杂任务：
❌ 知识覆盖面有限
❌ 容易陷入思维定式
❌ 难以处理多步骤任务
❌ 无法自我验证
```

### 1.2 多 Agent 的优势

| 优势 | 说明 | 示例 |
|------|------|------|
| **专业分工** | 每个 Agent 专注一个领域 | 程序员 + 设计师 |
| **相互验证** | 多个 Agent 交叉检查 | Code Review |
| **任务分解** | 复杂任务分步处理 | 项目管理 |
| **并行处理** | 同时处理多个子任务 | 数据收集 |

### 1.3 典型应用场景

```
📝 内容创作：策划 Agent → 写作 Agent → 编辑 Agent
💻 软件开发：架构 Agent → 编码 Agent → 测试 Agent
📊 数据分析：收集 Agent → 分析 Agent → 报告 Agent
🎯 项目管理：规划 Agent → 执行 Agent → 监控 Agent
```

---

## 二、多 Agent 架构

### 2.1 常见架构模式

#### 模式 1：Manager-Worker

```
        Manager Agent
           / | \
          /  |  \
         ↓   ↓   ↓
    Worker1 Worker2 Worker3
```

**适用场景：** 任务可明确分解

#### 模式 2：流水线

```
Agent1 → Agent2 → Agent3 → 输出
```

**适用场景：** 顺序处理流程

#### 模式 3：圆桌会议

```
    Agent1
   /      \
Agent2 —— Agent3
```

**适用场景：** 需要讨论决策

### 2.2 角色设计

| 角色 | 职责 | 能力要求 |
|------|------|---------|
| **Manager** | 任务分配、协调 | 规划能力、沟通 |
| **Executor** | 执行具体任务 | 专业技能 |
| **Reviewer** | 质量检查 | 批判性思维 |
| **Researcher** | 信息收集 | 搜索能力 |

---

## 三、实现方案

### 3.1 基础 Agent 类

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseAgent(ABC):
    """Agent 基类"""
    
    def __init__(self, name: str, role: str, api_key: str):
        self.name = name
        self.role = role
        self.api_key = api_key
        self.history = []
    
    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """系统提示词"""
        pass
    
    def chat(self, message: str, context: List[Dict] = None) -> str:
        """对话"""
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)
        
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        if context:
            messages.extend(context)
        
        messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        
        reply = response.choices[0].message.content
        self.history.append({"role": "user", "content": message})
        self.history.append({"role": "assistant", "content": reply})
        
        return reply
    
    def get_context(self, limit: int = 10) -> List[Dict]:
        """获取对话历史"""
        return self.history[-limit:]
```

### 3.2 实现具体角色

```python
# 项目经理 Agent
class ManagerAgent(BaseAgent):
    @property
    def system_prompt(self):
        return """你是一位经验丰富的项目经理。
你的职责：
1. 理解任务需求
2. 分解任务为可执行的子任务
3. 分配给合适的执行 Agent
4. 跟踪进度，协调资源
5. 确保按时交付

请用清晰的结构化格式输出任务分配。"""

# 程序员 Agent
class CoderAgent(BaseAgent):
    @property
    def system_prompt(self):
        return """你是一位资深软件工程师。
你的职责：
1. 根据需求编写高质量代码
2. 遵循最佳实践
3. 添加必要的注释
4. 确保代码可测试

请提供完整可运行的代码。"""

# 测试工程师 Agent
class TesterAgent(BaseAgent):
    @property
    def system_prompt(self):
        return """你是一位专业的测试工程师。
你的职责：
1. 审查代码质量
2. 设计测试用例
3. 发现潜在 bug
4. 提供改进建议

请给出详细的测试报告。"""

# 文档工程师 Agent
class WriterAgent(BaseAgent):
    @property
    def system_prompt(self):
        return """你是一位技术文档工程师。
你的职责：
1. 编写清晰的技术文档
2. 创建使用示例
3. 维护 API 文档
4. 确保文档准确易懂

请提供结构化的文档。"""
```

---

## 四、完整协作系统

### 4.1 协作框架

```python
class MultiAgentSystem:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.agents = {}
        self.shared_memory = []
    
    def add_agent(self, name: str, agent: BaseAgent):
        """注册 Agent"""
        self.agents[name] = agent
    
    def broadcast(self, message: str, exclude: str = None):
        """广播消息给所有 Agent"""
        results = {}
        for name, agent in self.agents.items():
            if name != exclude:
                results[name] = agent.chat(message)
        return results
    
    def run_pipeline(self, task: str) -> Dict:
        """运行流水线"""
        print(f"🚀 开始处理任务：{task}\n")
        
        # Step 1: 经理规划
        manager = self.agents["manager"]
        plan = manager.chat(f"请规划以下任务：{task}")
        print(f"📋 经理规划:\n{plan}\n")
        
        # Step 2: 程序员编码
        coder = self.agents["coder"]
        code = coder.chat(f"根据以下规划编写代码:\n{plan}")
        print(f"💻 程序员代码:\n{code}\n")
        
        # Step 3: 测试工程师审查
        tester = self.agents["tester"]
        review = tester.chat(f"请审查以下代码:\n{code}")
        print(f"✅ 测试报告:\n{review}\n")
        
        # Step 4: 文档工程师写文档
        writer = self.agents["writer"]
        doc = writer.chat(f"请为以下代码编写文档:\n{code}")
        print(f"📝 技术文档:\n{doc}\n")
        
        return {
            "plan": plan,
            "code": code,
            "review": review,
            "doc": doc
        }
```

### 4.2 使用示例

```python
# 初始化系统
system = MultiAgentSystem(api_key="your-key")

# 注册 Agent
system.add_agent("manager", ManagerAgent("小明", "项目经理", "your-key"))
system.add_agent("coder", CoderAgent("小红", "程序员", "your-key"))
system.add_agent("tester", TesterAgent("小刚", "测试工程师", "your-key"))
system.add_agent("writer", WriterAgent("小丽", "文档工程师", "your-key"))

# 运行任务
result = system.run_pipeline("创建一个 Python 计算器，支持加减乘除")

# 保存结果
with open("output.md", "w") as f:
    f.write(f"# 项目输出\n\n")
    f.write(f"## 规划\n{result['plan']}\n\n")
    f.write(f"## 代码\n{result['code']}\n\n")
    f.write(f"## 审查\n{result['review']}\n\n")
    f.write(f"## 文档\n{result['doc']}\n\n")
```

---

## 五、高级技巧

### 5.1 Agent 间通信

```python
class MessageBus:
    """消息总线"""
    
    def __init__(self):
        self.subscribers = {}
        self.message_history = []
    
    def subscribe(self, agent_name: str, topics: List[str]):
        """订阅主题"""
        self.subscribers[agent_name] = topics
    
    def publish(self, topic: str, message: str):
        """发布消息"""
        self.message_history.append({
            "topic": topic,
            "message": message,
            "timestamp": datetime.now()
        })
        
        # 通知订阅者
        notifications = []
        for agent_name, topics in self.subscribers.items():
            if topic in topics:
                notifications.append(agent_name)
        
        return notifications
```

### 5.2 冲突解决

```python
class ConflictResolver:
    """冲突解决器"""
    
    def resolve(self, opinions: List[Dict]) -> str:
        """
        解决多个 Agent 的意见冲突
        
        opinions: [{"agent": "name", "opinion": "text"}]
        """
        # 方法 1：投票
        # 方法 2：权重评分
        # 方法 3：引入仲裁 Agent
        
        prompt = f"""
以下是多个专家的意见：
"""
        for o in opinions:
            prompt += f"\n{o['agent']}: {o['opinion']}\n"
        
        prompt += """
请分析各方观点，给出最终决策。
考虑因素：
1. 论据的充分性
2. 方案的可行性
3. 风险与收益
"""
        # 调用仲裁 Agent...
```

---

## 六、实战：代码审查系统

```python
class CodeReviewSystem:
    def __init__(self, api_key: str):
        self.system = MultiAgentSystem(api_key)
        self._setup_agents()
    
    def _setup_agents(self):
        self.system.add_agent("coder", CoderAgent("Dev", "开发者", self.system.api_key))
        self.system.add_agent("reviewer1", TesterAgent("Reviewer1", "审查员 1", self.system.api_key))
        self.system.add_agent("reviewer2", TesterAgent("Reviewer2", "审查员 2", self.system.api_key))
    
    def review(self, code: str) -> Dict:
        # 多个审查员独立审查
        review1 = self.system.agents["reviewer1"].chat(f"请审查代码:\n{code}")
        review2 = self.system.agents["reviewer2"].chat(f"请审查代码:\n{code}")
        
        # 汇总意见
        summary = self._merge_reviews(review1, review2)
        
        return {
            "review1": review1,
            "review2": review2,
            "summary": summary
        }
    
    def _merge_reviews(self, r1: str, r2: str) -> str:
        # 使用 Manager 汇总
        manager = self.system.agents.get("manager")
        if not manager:
            manager = ManagerAgent("Manager", "经理", self.system.api_key)
        
        return manager.chat(f"汇总以下两个审查意见:\n审查 1:\n{r1}\n\n审查 2:\n{r2}")
```

---

## 七、常见问题

### Q1: Agent 太多成本太高怎么办？

**A:** 使用小模型处理简单任务，大模型处理关键决策

### Q2: 如何避免 Agent 互相矛盾？

**A:** 设置明确的职责边界，引入仲裁机制

### Q3: 通信开销大怎么办？

**A:** 使用共享内存，减少重复信息传递

---

## 📝 课后作业

1. 实现 4 个不同角色的 Agent
2. 构建一个简单的多 Agent 协作系统
3. 测试任务分解和执行流程
4. 优化 Agent 间通信效率

---

## 🔗 参考资料

- [AutoGen 框架](https://microsoft.github.io/autogen)
- [LangGraph](https://python.langchain.com/docs/langgraph)
- [CrewAI](https://docs.crewai.com)

---

**下一课：** [06 - RAG 实战](06_rag_practice.md)
