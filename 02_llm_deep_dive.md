# 02 - 深入理解 LLM：大语言模型的核心原理

> **AI Agent 开发教程 第 02 课**  
> 📅 2026 年 3 月 | 👨‍💻 [@Gale2World](https://github.com/zdnuist)

---

## 📋 课程目标

学完本课后，你将能够：
- ✅ 理解 LLM 的工作原理和架构
- ✅ 掌握 Token、上下文窗口等核心概念
- ✅ 了解不同模型的特点和选型策略
- ✅ 学会优化 Prompt 提升模型效果

---

## 一、LLM 是什么？

### 1.1 定义

**大语言模型（Large Language Model, LLM）** 是一种基于深度学习的人工智能模型，能够理解、生成和处理自然语言。

### 1.2 核心能力

| 能力 | 说明 | 示例 |
|------|------|------|
| **文本生成** | 根据输入生成连贯文本 | 写文章、写代码 |
| **问答** | 回答问题 | 客服机器人 |
| **翻译** | 多语言互译 | 中英翻译 |
| **摘要** | 提取关键信息 | 新闻摘要 |
| **推理** | 逻辑推理 | 数学题解答 |

---

## 二、LLM 工作原理

### 2.1 Transformer 架构

现代 LLM 都基于 **Transformer** 架构，核心组件：

```
输入文本 → Tokenization → Embedding → Transformer 层 → 输出
```

### 2.2 关键概念

#### Token（词元）

Token 是模型处理文本的基本单位：

```python
# 示例：文本分词
text = "Hello, AI Agent!"
tokens = ["Hello", ",", " AI", " Agent", "!"]
# 5 个 tokens
```

**重要规则：**
- 1000 tokens ≈ 750 个英文单词
- 1000 tokens ≈ 500-600 个中文字符
- 代码通常消耗更多 tokens

#### Context Window（上下文窗口）

模型一次能处理的最大 token 数量：

| 模型 | 上下文窗口 | 适用场景 |
|------|-----------|---------|
| GPT-3.5 | 4K tokens | 短对话 |
| GPT-4 | 8K/32K tokens | 长文档 |
| Claude 3 | 200K tokens | 书籍分析 |
| Gemini 1.5 | 1M tokens | 视频转录 |

---

## 三、主流模型对比

### 3.1 国际模型

| 模型 | 厂商 | 优势 | 价格 |
|------|------|------|------|
| **GPT-4** | OpenAI | 综合能力最强 | $0.03/1K tokens |
| **Claude 3** | Anthropic | 长文本处理 | $0.025/1K tokens |
| **Gemini** | Google | 多模态 | $0.0005/1K tokens |

### 3.2 国内模型

| 模型 | 厂商 | 优势 | 价格 |
|------|------|------|------|
| **通义千问** | 阿里 | 中文优化 | ¥0.008/1K tokens |
| **文心一言** | 百度 | 知识图谱 | ¥0.012/1K tokens |
| **DeepSeek** | 深度求索 | 性价比高 | ¥0.001/1K tokens |

### 3.3 选型建议

```python
# 根据场景选择模型
def select_model(task):
    if task == "代码生成":
        return "Claude 3.5 Sonnet"  # 代码能力最强
    elif task == "长文档分析":
        return "Claude 3 200K"  # 上下文最大
    elif task == "快速问答":
        return "GPT-3.5"  # 便宜快速
    elif task == "中文内容":
        return "通义千问"  # 中文优化
    else:
        return "GPT-4"  # 通用最强
```

---

## 四、Prompt 工程

### 4.1 基础结构

```
角色 + 任务 + 要求 + 示例 = 好 Prompt
```

### 4.2 实用技巧

#### 技巧 1：明确角色

```markdown
❌ 差：写一个 Python 函数

✅ 好：你是一位资深 Python 工程师，请编写一个...
```

#### 技巧 2：提供示例

```markdown
❌ 差：把这句话翻译成英文

✅ 好：请将以下中文翻译成英文，保持专业术语准确：
   示例：
   输入：这个功能需要优化
   输出：This feature needs optimization
   
   现在翻译：...
```

#### 技巧 3：分步思考

```markdown
请按以下步骤解决问题：
1. 分析问题需求
2. 列出可能的解决方案
3. 评估每个方案的优缺点
4. 给出最终建议
```

### 4.3 常见错误

| 错误 | 问题 | 改进 |
|------|------|------|
| 太模糊 | "写点东西" | "写一篇 500 字的技术博客" |
| 缺少上下文 | "修复这个 bug" | "这是代码...期望行为是...实际行为是..." |
| 一次性太多 | 10 个问题一起问 | 逐个问题询问 |

---

## 五、成本优化

### 5.1 Token 计算

```python
# 估算成本
def estimate_cost(input_tokens, output_tokens, model="gpt-4"):
    rates = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5": {"input": 0.0015, "output": 0.002},
        "claude-3": {"input": 0.025, "output": 0.075},
    }
    rate = rates.get(model, rates["gpt-4"])
    cost = (input_tokens * rate["input"] + output_tokens * rate["output"]) / 1000
    return cost

# 示例：1000 输入 + 500 输出
print(estimate_cost(1000, 500, "gpt-4"))  # $0.06
```

### 5.2 省钱技巧

1. **使用缓存** - 相同问题直接返回缓存答案
2. **选择合适模型** - 简单任务用小模型
3. **压缩 Prompt** - 去除冗余描述
4. **批量处理** - 多个问题一起问

---

## 六、实战练习

### 练习 1：搭建简单对话

```python
from openai import OpenAI

client = OpenAI(api_key="your-api-key")

def chat(message):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "你是一位友好的 AI 助手"},
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content

# 测试
print(chat("你好，请介绍一下自己"))
```

### 练习 2：代码生成

```python
def generate_code(description):
    prompt = f"""
你是一位资深 Python 工程师。请根据以下描述编写代码：

{description}

要求：
1. 代码完整可运行
2. 添加必要的注释
3. 包含错误处理
4. 提供使用示例
"""
    # 调用 API...
```

---

## 七、常见问题

### Q1: 模型输出不稳定怎么办？

**A:** 设置 `temperature=0.7` 平衡创造性和稳定性

### Q2: 如何处理长文档？

**A:** 使用支持大上下文的模型（如 Claude 3 200K）

### Q3: 输出包含错误信息？

**A:** 添加"如果不确定请说明"的要求

---

## 📝 课后作业

1. 注册一个 LLM API 账号
2. 编写一个简单对话程序
3. 尝试不同的 Prompt 技巧
4. 计算你的使用成本

---

## 🔗 参考资料

- [Transformer 论文](https://arxiv.org/abs/1706.03762)
- [OpenAI API 文档](https://platform.openai.com/docs)
- [Prompt 工程指南](https://github.com/prompt-engineering/awesome-prompt-engineering)

---

**下一课：** [03 - Memory 机制详解](03_memory_mechanism.md)
