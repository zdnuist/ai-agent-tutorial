# 03 - Memory 机制详解：让 Agent 拥有长期记忆

> **AI Agent 开发教程 第 03 课**  
> 📅 2026 年 3 月 | 👨‍💻 [@Gale2World](https://github.com/zdnuist)

---

## 📋 课程目标

学完本课后，你将能够：
- ✅ 理解 Agent Memory 的工作原理
- ✅ 实现短期记忆和长期记忆
- ✅ 掌握向量数据库的使用
- ✅ 构建有记忆的 AI Agent

---

## 一、为什么需要 Memory？

### 1.1 问题场景

```
用户：我叫张三
Agent: 你好张三！

[10 分钟后]

用户：我叫什么名字？
Agent: 抱歉，我不知道...
```

**没有记忆的 Agent 就像金鱼，只有 7 秒记忆！**

### 1.2 Memory 的作用

| 作用 | 说明 | 示例 |
|------|------|------|
| **上下文连贯** | 记住对话历史 | 多轮对话 |
| **个性化** | 记住用户偏好 | 喜欢的风格 |
| **知识积累** | 存储 learned 信息 | 项目文档 |
| **任务跟踪** | 记住任务状态 | 待办事项 |

---

## 二、Memory 架构

### 2.1 三层记忆模型

```
┌─────────────────────────────────────┐
│         长期记忆 (Long-term)         │
│    向量数据库存储，永久保存          │
├─────────────────────────────────────┤
│         短期记忆 (Short-term)        │
│    对话历史，有限上下文             │
├─────────────────────────────────────┤
│         工作记忆 (Working)           │
│    当前任务相关，临时缓存           │
└─────────────────────────────────────┘
```

### 2.2 记忆类型对比

| 类型 | 容量 | 持久性 | 访问速度 | 用途 |
|------|------|--------|---------|------|
| **工作记忆** | 小 | 临时 | 极快 | 当前任务 |
| **短期记忆** | 中 | 会话级 | 快 | 对话历史 |
| **长期记忆** | 大 | 永久 | 中 | 知识库 |

---

## 三、实现方案

### 3.1 短期记忆：对话历史

```python
class ShortTermMemory:
    def __init__(self, max_length=10):
        self.history = []
        self.max_length = max_length
    
    def add(self, role, content):
        """添加消息到历史"""
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now()
        })
        
        # 保持固定长度
        if len(self.history) > self.max_length:
            self.history.pop(0)
    
    def get_context(self):
        """获取对话上下文"""
        return self.history
    
    def clear(self):
        """清空历史"""
        self.history = []

# 使用示例
memory = ShortTermMemory(max_length=20)
memory.add("user", "我叫张三")
memory.add("assistant", "你好张三！很高兴认识你")
```

### 3.2 长期记忆：向量数据库

#### 安装依赖

```bash
pip install chromadb langchain
```

#### 实现代码

```python
import chromadb
from chromadb.config import Settings

class LongTermMemory:
    def __init__(self, persist_dir="./memory_db"):
        # 初始化客户端
        self.client = chromadb.Client(Settings(
            persist_directory=persist_dir,
            anonymized_telemetry=False
        ))
        
        # 创建集合
        self.collection = self.client.get_or_create_collection(
            name="agent_memory",
            metadata={"description": "Agent 长期记忆"}
        )
    
    def add_memory(self, text, metadata=None):
        """添加记忆"""
        self.collection.add(
            documents=[text],
            metadatas=[metadata or {}],
            ids=[f"mem_{datetime.now().timestamp()}"]
        )
    
    def search(self, query, n_results=5):
        """搜索相关记忆"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results["documents"][0]
    
    def get_all(self):
        """获取所有记忆"""
        return self.collection.get()

# 使用示例
memory = LongTermMemory()

# 添加记忆
memory.add_memory(
    "用户喜欢 Python 编程",
    {"type": "preference", "user": "张三"}
)

memory.add_memory(
    "项目使用 FastAPI 框架",
    {"type": "project_info", "project": "api-server"}
)

# 搜索记忆
related = memory.search("用户的技术偏好")
print(related)  # ["用户喜欢 Python 编程"]
```

---

## 四、完整 Agent 实现

### 4.1 有记忆的 Agent 类

```python
from openai import OpenAI

class AgentWithMemory:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.short_memory = ShortTermMemory(max_length=20)
        self.long_memory = LongTermMemory()
        self.system_prompt = "你是一位友好的 AI 助手"
    
    def chat(self, user_input):
        # 1. 从长期记忆检索相关信息
        relevant_memories = self.long_memory.search(user_input, n_results=3)
        
        # 2. 构建上下文
        context = self._build_context(relevant_memories)
        
        # 3. 准备消息
        messages = [
            {"role": "system", "content": self.system_prompt + context}
        ] + self.short_memory.get_context()
        
        messages.append({"role": "user", "content": user_input})
        
        # 4. 调用 API
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        
        assistant_reply = response.choices[0].message.content
        
        # 5. 更新短期记忆
        self.short_memory.add("user", user_input)
        self.short_memory.add("assistant", assistant_reply)
        
        # 6. 重要信息存入长期记忆
        self._extract_and_store(user_input, assistant_reply)
        
        return assistant_reply
    
    def _build_context(self, memories):
        """构建上下文"""
        if not memories:
            return ""
        
        context = "\n相关背景信息：\n"
        for mem in memories:
            context += f"- {mem}\n"
        return context
    
    def _extract_and_store(self, user_input, reply):
        """提取重要信息存储"""
        # 简单规则：包含个人信息的存入长期记忆
        keywords = ["我叫", "我喜欢", "我是", "记住"]
        if any(kw in user_input for kw in keywords):
            self.long_memory.add_memory(
                f"用户说：{user_input}",
                {"type": "user_info"}
            )

# 使用示例
agent = AgentWithMemory(api_key="your-key")

print(agent.chat("我叫张三"))
# 输出：你好张三！很高兴认识你

print(agent.chat("记住我喜欢 Python"))
# 输出：好的，我已经记住你喜欢 Python 了

print(agent.chat("我喜欢什么？"))
# 输出：你喜欢 Python
```

---

## 五、高级技巧

### 5.1 记忆压缩

```python
def compress_memory(memories):
    """压缩记忆，减少 token 消耗"""
    # 使用 LLM 总结
    prompt = f"""
请总结以下对话历史，保留关键信息：

{memories}

要求：
1. 保留人名、时间、事件等关键信息
2. 压缩到原文的 30%
3. 保持语义完整
"""
    # 调用 API 获取总结...
```

### 5.2 记忆优先级

```python
class PriorityMemory:
    def __init__(self):
        self.memories = []
    
    def add(self, text, importance=1):
        """添加记忆，importance 1-5"""
        self.memories.append({
            "text": text,
            "importance": importance,
            "access_count": 0,
            "last_access": datetime.now()
        })
    
    def get_relevant(self, query, top_k=5):
        """获取相关记忆，考虑重要性"""
        # 按重要性和访问频率排序
        sorted_mems = sorted(
            self.memories,
            key=lambda x: x["importance"] * (x["access_count"] + 1),
            reverse=True
        )
        return sorted_mems[:top_k]
```

### 5.3 记忆遗忘

```python
def forget_old_memories(memories, days=30):
    """遗忘超过 N 天且未访问的记忆"""
    cutoff = datetime.now() - timedelta(days=days)
    
    filtered = [
        m for m in memories
        if m["last_access"] > cutoff or m["importance"] >= 4
    ]
    
    return filtered
```

---

## 六、实战项目

### 个人助手 Agent

```python
class PersonalAssistant:
    def __init__(self):
        self.agent = AgentWithMemory(api_key="your-key")
    
    def run(self):
        print("🤖 个人助手已启动（输入 quit 退出）")
        
        while True:
            user_input = input("你：").strip()
            
            if user_input.lower() in ["quit", "exit", "bye"]:
                print("再见！👋")
                break
            
            if not user_input:
                continue
            
            reply = self.agent.chat(user_input)
            print(f"助手：{reply}\n")

# 启动
if __name__ == "__main__":
    assistant = PersonalAssistant()
    assistant.run()
```

---

## 七、常见问题

### Q1: 向量数据库怎么选？

**A:** 
- 本地开发：Chroma（简单）
- 生产环境：Pinecone/Weaviate（高性能）
- 大规模：Milvus（分布式）

### Q2: 记忆太多怎么办？

**A:** 实现记忆压缩和遗忘机制

### Q3: 如何保证记忆准确性？

**A:** 定期验证和更新记忆，设置置信度

---

## 📝 课后作业

1. 实现一个简单的对话记忆系统
2. 集成 ChromaDB 存储长期记忆
3. 测试 Agent 能否记住你的个人信息
4. 实现记忆压缩功能

---

## 🔗 参考资料

- [ChromaDB 文档](https://docs.trychroma.com)
- [LangChain Memory](https://python.langchain.com/docs/modules/memory)
- [向量数据库对比](https://github.com/awesome-vector-databases)

---

**下一课：** [04 - Tools 系统开发](04_tools_system.md)
