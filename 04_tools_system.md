# 04 - Tools 系统开发：让 Agent 拥有"手脚"

> **AI Agent 开发教程 第 04 课**  
> 📅 2026 年 3 月 | 👨‍💻 [@Gale2World](https://github.com/zdnuist)

---

## 📋 课程目标

学完本课后，你将能够：
- ✅ 理解 Agent Tools 的工作原理
- ✅ 实现自定义工具函数
- ✅ 掌握 Function Calling 技术
- ✅ 构建能执行实际任务的 Agent

---

## 一、为什么需要 Tools？

### 1.1 LLM 的局限性

```
LLM 能做什么：
✅ 回答问题
✅ 生成文本
✅ 分析内容

LLM 不能做什么：
❌ 访问实时数据
❌ 执行代码
❌ 操作外部系统
❌ 调用 API
```

### 1.2 Tools 的作用

**Tools = Agent 的"手脚"**

| 工具类型 | 功能 | 示例 |
|---------|------|------|
| **搜索工具** | 获取实时信息 | Google 搜索 |
| **计算工具** | 精确计算 | 计算器 |
| **数据库工具** | 数据存取 | SQL 查询 |
| **API 工具** | 调用外部服务 | 天气 API |
| **文件工具** | 文件操作 | 读写文件 |

---

## 二、Function Calling 原理

### 2.1 工作流程

```
用户请求 → LLM 分析 → 选择工具 → 执行函数 → 返回结果 → 生成回复
```

### 2.2 工具定义结构

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "获取指定城市的天气信息",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，如'北京'"
                }
            },
            "required": ["city"]
        }
    }
}]
```

---

## 三、实现方案

### 3.1 基础工具类

```python
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):
    """工具基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述"""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> Dict:
        """参数定义"""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """执行工具"""
        pass
    
    def to_openai_format(self) -> Dict:
        """转换为 OpenAI 格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
```

### 3.2 实现具体工具

```python
# 天气查询工具
class WeatherTool(BaseTool):
    @property
    def name(self):
        return "get_weather"
    
    @property
    def description(self):
        return "获取指定城市的当前天气信息"
    
    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称"
                }
            },
            "required": ["city"]
        }
    
    def execute(self, city: str) -> str:
        # 实际调用天气 API
        return f"{city} 当前天气：晴，25°C"

# 计算器工具
class CalculatorTool(BaseTool):
    @property
    def name(self):
        return "calculator"
    
    @property
    def description(self):
        return "执行数学计算"
    
    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "数学表达式，如'2+2'"
                }
            },
            "required": ["expression"]
        }
    
    def execute(self, expression: str) -> str:
        try:
            # 安全计算
            result = eval(expression, {"__builtins__": {}}, {})
            return f"计算结果：{result}"
        except Exception as e:
            return f"计算错误：{str(e)}"

# 文件读取工具
class FileReadTool(BaseTool):
    @property
    def name(self):
        return "read_file"
    
    @property
    def description(self):
        return "读取文件内容"
    
    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "文件路径"
                }
            },
            "required": ["file_path"]
        }
    
    def execute(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"文件内容：\n{content}"
        except Exception as e:
            return f"读取失败：{str(e)}"
```

---

## 四、完整 Agent 实现

### 4.1 支持 Tools 的 Agent

```python
from openai import OpenAI
import json

class ToolAgent:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.tools = []
        self.tool_map = {}
    
    def add_tool(self, tool: BaseTool):
        """注册工具"""
        self.tools.append(tool.to_openai_format())
        self.tool_map[tool.name] = tool
    
    def chat(self, user_input: str):
        # 第一轮：判断是否需要调用工具
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "你是一位智能助手，可以使用工具完成任务"},
                {"role": "user", "content": user_input}
            ],
            tools=self.tools,
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        
        # 检查是否需要调用工具
        if message.tool_calls:
            # 执行工具调用
            results = []
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                
                # 执行对应工具
                if func_name in self.tool_map:
                    result = self.tool_map[func_name].execute(**func_args)
                    results.append({
                        "tool": func_name,
                        "result": result
                    })
            
            # 第二轮：基于工具结果生成回复
            messages = [
                {"role": "system", "content": "你是一位智能助手"},
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": str(results)}
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages
            )
            
            return response.choices[0].message.content
        else:
            # 不需要工具，直接回复
            return message.content

# 使用示例
agent = ToolAgent(api_key="your-key")

# 注册工具
agent.add_tool(WeatherTool())
agent.add_tool(CalculatorTool())
agent.add_tool(FileReadTool())

# 测试
print(agent.chat("北京天气怎么样？"))
# 输出：北京当前天气：晴，25°C

print(agent.chat("计算 123 * 456"))
# 输出：计算结果：56088
```

---

## 五、实战：GitHub 查询工具

```python
import requests

class GitHubTool(BaseTool):
    @property
    def name(self):
        return "github_search"
    
    @property
    def description(self):
        return "搜索 GitHub 仓库和 Issues"
    
    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词"
                },
                "type": {
                    "type": "string",
                    "enum": ["repo", "issue"],
                    "description": "搜索类型"
                }
            },
            "required": ["query"]
        }
    
    def execute(self, query: str, type: str = "repo") -> str:
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        
        if type == "repo":
            url = f"https://api.github.com/search/repositories?q={query}"
        else:
            url = f"https://api.github.com/search/issues?q={query}"
        
        response = requests.get(url, headers=headers)
        data = response.json()
        
        # 格式化结果
        results = []
        for item in data.get("items", [])[:5]:
            results.append({
                "title": item.get("name") or item.get("title"),
                "url": item.get("html_url"),
                "description": item.get("description", "")[:100]
            })
        
        return json.dumps(results, ensure_ascii=False)
```

---

## 六、高级技巧

### 6.1 工具链编排

```python
class ToolChain:
    def __init__(self):
        self.steps = []
    
    def add_step(self, tool: BaseTool, condition=None):
        self.steps.append({
            "tool": tool,
            "condition": condition
        })
    
    def execute(self, input_data):
        results = []
        current_data = input_data
        
        for step in self.steps:
            tool = step["tool"]
            condition = step["condition"]
            
            # 检查条件
            if condition and not condition(current_data):
                continue
            
            # 执行工具
            result = tool.execute(**current_data)
            results.append(result)
            
            # 更新数据
            current_data = self._parse_result(result)
        
        return results
```

### 6.2 错误处理

```python
def safe_execute(tool: BaseTool, **kwargs):
    """安全执行工具"""
    try:
        # 参数验证
        tool.parameters  # 触发验证
        
        # 执行
        result = tool.execute(**kwargs)
        return {"success": True, "result": result}
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "tool": tool.name
        }
```

---

## 七、常见问题

### Q1: 如何防止工具被滥用？

**A:** 添加权限检查和参数验证

### Q2: 工具执行超时怎么办？

**A:** 设置 timeout，添加重试机制

### Q3: 如何选择工具？

**A:** 让 LLM 根据任务自动选择，或手动指定

---

## 📝 课后作业

1. 实现 3 个自定义工具
2. 构建支持 Function Calling 的 Agent
3. 测试工具调用流程
4. 添加错误处理机制

---

## 🔗 参考资料

- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [LangChain Tools](https://python.langchain.com/docs/modules/agents/tools)
- [MCP Protocol](https://modelcontextprotocol.io)

---

**下一课：** [05 - 多 Agent 协作](05_multi_agent_collaboration.md)
