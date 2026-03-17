# 07 - Agent 评估：量化智能体的能力

> **AI Agent 开发教程 第 07 课**  
> 📅 2026 年 3 月 | 👨‍💻 [@Gale2World](https://github.com/zdnuist)

---

## 📋 课程目标

学完本课后，你将能够：
- ✅ 理解 Agent 评估的维度
- ✅ 设计评估指标体系
- ✅ 实现自动化评估流程
- ✅ 持续优化 Agent 性能

---

## 一、为什么需要评估？

### 1.1 评估的重要性

```
没有评估 = 盲目开发

✅ 发现性能瓶颈
✅ 对比不同方案
✅ 追踪改进效果
✅ 保证产品质量
```

### 1.2 评估挑战

| 挑战 | 说明 | 解决方案 |
|------|------|---------|
| **主观性** | 质量判断主观 | 标准化评分 |
| **多样性** | 任务类型多样 | 分类评估 |
| **成本** | 人工评估昂贵 | 自动化评估 |
| **时效** | 模型快速迭代 | 持续监控 |

---

## 二、评估维度

### 2.1 核心指标

```
┌────────────────────────────────────────┐
│          Agent 评估指标体系             │
├────────────────────────────────────────┤
│  准确性 (Accuracy)                      │
│  - 任务完成率                          │
│  - 答案正确率                          │
│  - 代码通过率                          │
├────────────────────────────────────────┤
│  效率 (Efficiency)                      │
│  - 响应时间                            │
│  - Token 消耗                          │
│  - 工具调用次数                        │
├────────────────────────────────────────┤
│  可靠性 (Reliability)                   │
│  - 错误率                              │
│  - 超时率                              │
│  - 一致性                              │
├────────────────────────────────────────┤
│  安全性 (Safety)                        │
│  - 有害内容过滤                        │
│  - 隐私保护                            │
│  - 权限控制                            │
└────────────────────────────────────────┘
```

### 2.2 指标定义

| 指标 | 公式 | 目标值 |
|------|------|--------|
| **任务完成率** | 成功任务数/总任务数 | > 90% |
| **答案正确率** | 正确答案数/总答案数 | > 85% |
| **平均响应时间** | 总耗时/请求数 | < 3s |
| **Token 效率** | 有效输出/总消耗 | > 60% |
| **错误率** | 错误次数/总请求数 | < 5% |

---

## 三、评估方法

### 3.1 人工评估

```python
class HumanEvaluator:
    """人工评估"""
    
    def __init__(self, criteria: List[Dict]):
        self.criteria = criteria  # 评估标准
    
    def evaluate(self, task: str, output: str) -> Dict:
        """评估单个输出"""
        scores = {}
        
        for criterion in self.criteria:
            print(f"\n评估维度：{criterion['name']}")
            print(f"说明：{criterion['description']}")
            print(f"任务：{task}")
            print(f"输出：{output[:200]}...")
            
            score = input("评分 (1-5): ")
            comment = input("评语：")
            
            scores[criterion['name']] = {
                "score": int(score),
                "comment": comment
            }
        
        return {
            "scores": scores,
            "average": sum(s["score"] for s in scores.values()) / len(scores)
        }
```

### 3.2 自动化评估

```python
from openai import OpenAI

class AutoEvaluator:
    """自动化评估"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.eval_prompt = """你是一位专业的评估专家。
请根据以下标准评估 Agent 的输出：

评估标准：
{criteria}

任务：{task}
期望输出：{expected}
实际输出：{output}

请逐项评分（1-5 分）并给出理由：
"""
    
    def evaluate(self, task: str, output: str, expected: str = None) -> Dict:
        """自动评估"""
        criteria = """
1. 准确性：输出是否正确回答了问题
2. 完整性：是否覆盖了所有要点
3. 简洁性：是否简洁明了
4. 专业性：是否使用专业术语
5. 安全性：是否包含有害内容
"""
        
        prompt = self.eval_prompt.format(
            criteria=criteria,
            task=task,
            expected=expected or "无",
            output=output
        )
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._parse_evaluation(response.choices[0].message.content)
    
    def _parse_evaluation(self, text: str) -> Dict:
        """解析评估结果"""
        # 简单解析，实际可用正则或 LLM 提取
        return {
            "raw_text": text,
            "scores": self._extract_scores(text)
        }
    
    def _extract_scores(self, text: str) -> Dict:
        # 提取分数逻辑
        return {"accuracy": 4, "completeness": 3}
```

### 3.3 基于测试集的评估

```python
class BenchmarkEvaluator:
    """基准测试评估"""
    
    def __init__(self, test_cases: List[Dict]):
        self.test_cases = test_cases
    
    def run_benchmark(self, agent) -> Dict:
        """运行基准测试"""
        results = []
        
        for i, case in enumerate(self.test_cases):
            print(f"运行测试 {i+1}/{len(self.test_cases)}")
            
            # 执行任务
            output = agent.run(case["input"])
            
            # 评估结果
            passed = self._check_output(output, case["expected"])
            
            results.append({
                "case_id": i,
                "input": case["input"],
                "expected": case["expected"],
                "output": output,
                "passed": passed
            })
        
        # 统计
        passed_count = sum(1 for r in results if r["passed"])
        
        return {
            "total": len(results),
            "passed": passed_count,
            "failed": len(results) - passed_count,
            "pass_rate": passed_count / len(results),
            "details": results
        }
    
    def _check_output(self, output: str, expected: str) -> bool:
        # 简单字符串匹配，实际可用语义相似度
        return expected.lower() in output.lower()
```

---

## 四、评估框架

### 4.1 RAGAS 框架

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)

def evaluate_rag(rag_system, test_data):
    """使用 RAGAS 评估 RAG 系统"""
    
    results = evaluate(
        dataset=test_data,
        metrics=[
            faithfulness,          # 忠实度
            answer_relevancy,      # 答案相关性
            context_precision,     # 上下文精确度
            context_recall         # 上下文召回率
        ]
    )
    
    return results
```

### 4.2 自定义评估框架

```python
class AgentEvaluator:
    """综合评估框架"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.metrics = {}
    
    def register_metric(self, name: str, metric_func):
        """注册评估指标"""
        self.metrics[name] = metric_func
    
    def evaluate(self, agent, test_suite) -> Dict:
        """全面评估"""
        results = {}
        
        for metric_name, metric_func in self.metrics.items():
            print(f"评估指标：{metric_name}")
            score = metric_func(agent, test_suite)
            results[metric_name] = score
        
        # 综合得分
        results["overall"] = sum(results.values()) / len(results)
        
        return results
    
    def generate_report(self, results: Dict) -> str:
        """生成评估报告"""
        report = "# Agent 评估报告\n\n"
        
        for metric, score in results.items():
            bar = "█" * int(score * 10)
            report += f"{metric}: {bar} {score:.2f}\n"
        
        return report
```

---

## 五、实战：代码 Agent 评估

### 5.1 构建测试集

```python
CODE_TEST_CASES = [
    {
        "id": 1,
        "task": "实现一个快速排序",
        "input": "def quick_sort(arr):",
        "expected": ["递归", "基准条件", "分区"],
        "test_code": "assert quick_sort([3,1,2]) == [1,2,3]"
    },
    {
        "id": 2,
        "task": "实现一个装饰器计算函数执行时间",
        "input": "def timer_decorator(func):",
        "expected": ["time", "wrapper", "return"],
        "test_code": "@timer_decorator\ndef test(): pass"
    }
]
```

### 5.2 评估执行

```python
class CodeAgentEvaluator:
    """代码 Agent 评估"""
    
    def __init__(self):
        self.test_cases = CODE_TEST_CASES
    
    def evaluate(self, agent) -> Dict:
        results = []
        
        for case in self.test_cases:
            # 生成代码
            code = agent.generate(case["task"])
            
            # 检查关键要素
            elements_found = sum(
                1 for elem in case["expected"]
                if elem.lower() in code.lower()
            )
            
            # 运行测试
            test_passed = self._run_test(code, case["test_code"])
            
            results.append({
                "task": case["task"],
                "elements_score": elements_found / len(case["expected"]),
                "test_passed": test_passed
            })
        
        return {
            "element_accuracy": sum(r["elements_score"] for r in results) / len(results),
            "test_pass_rate": sum(1 for r in results if r["test_passed"]) / len(results)
        }
    
    def _run_test(self, code: str, test: str) -> bool:
        try:
            exec(code + "\n" + test)
            return True
        except Exception as e:
            print(f"测试失败：{e}")
            return False
```

---

## 六、持续监控

### 6.1 监控仪表板

```python
class AgentMonitor:
    """Agent 监控"""
    
    def __init__(self):
        self.metrics_history = []
    
    def log_request(self, request_id: str, latency: float, tokens: int, success: bool):
        """记录请求"""
        self.metrics_history.append({
            "timestamp": datetime.now(),
            "request_id": request_id,
            "latency": latency,
            "tokens": tokens,
            "success": success
        })
    
    def get_stats(self, hours: int = 24) -> Dict:
        """获取统计数据"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [m for m in self.metrics_history if m["timestamp"] > cutoff]
        
        return {
            "total_requests": len(recent),
            "avg_latency": sum(m["latency"] for m in recent) / len(recent),
            "success_rate": sum(1 for m in recent if m["success"]) / len(recent),
            "total_tokens": sum(m["tokens"] for m in recent)
        }
```

---

## 七、常见问题

### Q1: 评估成本高怎么办？

**A:** 抽样评估、自动化评估、众包评估

### Q2: 如何保证评估客观性？

**A:** 多人评估取平均、使用标准答案、自动化测试

### Q3: 评估指标如何设定？

**A:** 根据业务需求、参考行业标准、持续迭代

---

## 📝 课后作业

1. 设计一个评估指标体系
2. 实现自动化评估脚本
3. 构建测试集（至少 10 个用例）
4. 生成评估报告

---

## 🔗 参考资料

- [RAGAS 框架](https://docs.ragas.io)
- [HELM 评估](https://crfm.stanford.edu/helm)
- [AgentBench](https://github.com/THUDM/AgentBench)

---

**下一课：** [08 - 部署上线](08_deployment.md)
