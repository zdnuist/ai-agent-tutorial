# 06 - RAG 实战：构建企业级知识库

> **AI Agent 开发教程 第 06 课**  
> 📅 2026 年 3 月 | 👨‍💻 [@Gale2World](https://github.com/zdnuist)

---

## 📋 课程目标

学完本课后，你将能够：
- ✅ 理解 RAG 的工作原理
- ✅ 实现文档加载和分块
- ✅ 构建向量检索系统
- ✅ 开发问答机器人

---

## 一、什么是 RAG？

### 1.1 定义

**RAG（Retrieval-Augmented Generation）** = 检索 + 生成

```
用户问题 → 检索相关知识 → 增强 Prompt → LLM 生成答案
```

### 1.2 为什么需要 RAG？

| 问题 | 纯 LLM | RAG 方案 |
|------|-------|---------|
| **知识时效** | 训练数据截止 | 可更新知识库 |
| **领域知识** | 通用知识 | 专业领域知识 |
| **幻觉问题** | 可能编造 | 基于事实 |
| **数据隐私** | 数据出域 | 本地部署 |

### 1.3 典型应用场景

```
📚 企业知识库问答
📖 文档智能搜索
💼 客服机器人
🔬 科研文献检索
⚖️ 法律咨询系统
```

---

## 二、RAG 架构

### 2.1 核心组件

```
┌─────────────────────────────────────────┐
│             RAG 系统                     │
├─────────────────────────────────────────┤
│  ┌─────────┐    ┌─────────┐            │
│  │ 索引层   │    │ 检索层   │            │
│  │ - 文档加载│    │ - 向量检索│            │
│  │ - 文本分块│    │ - 重排序  │            │
│  │ - 向量化  │    │ - 上下文  │            │
│  └─────────┘    └─────────┘            │
│         ↓              ↓                │
│  ┌─────────────────────────┐           │
│  │      生成层 (LLM)        │           │
│  └─────────────────────────┘           │
└─────────────────────────────────────────┘
```

### 2.2 工作流程

```
1. 索引阶段（离线）
   文档 → 加载 → 分块 → 向量化 → 存储

2. 检索阶段（在线）
   问题 → 向量化 → 检索 TopK → 重排序

3. 生成阶段
   问题 + 上下文 → Prompt → LLM → 答案
```

---

## 三、实现方案

### 3.1 环境准备

```bash
pip install langchain chromadb openai tiktoken
pip install pypdf python-docx
```

### 3.2 文档加载

```python
from langchain.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    DirectoryLoader
)

class DocumentLoader:
    """文档加载器"""
    
    def __init__(self, directory: str):
        self.directory = directory
    
    def load_all(self) -> List:
        """加载目录下所有文档"""
        loaders = [
            # PDF 文件
            DirectoryLoader(
                self.directory,
                glob="**/*.pdf",
                loader_cls=PyPDFLoader
            ),
            # Word 文件
            DirectoryLoader(
                self.directory,
                glob="**/*.docx",
                loader_cls=Docx2txtLoader
            ),
            # 文本文件
            DirectoryLoader(
                self.directory,
                glob="**/*.txt",
                loader_cls=TextLoader
            )
        ]
        
        documents = []
        for loader in loaders:
            try:
                docs = loader.load()
                documents.extend(docs)
                print(f"✅ 加载 {len(docs)} 个文档")
            except Exception as e:
                print(f"❌ 加载失败：{e}")
        
        return documents
```

### 3.3 文本分块

```python
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    TokenTextSplitter
)

class TextChunker:
    """文本分块器"""
    
    def __init__(self, chunk_size=500, chunk_overlap=50):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", " ", ""]
        )
    
    def split(self, documents) -> List:
        """分块处理"""
        chunks = self.splitter.split_documents(documents)
        print(f"📊 分块完成：{len(chunks)} 个块")
        return chunks
    
    def split_text(self, text: str) -> List[str]:
        """分块文本"""
        return self.splitter.split_text(text)
```

### 3.4 向量化

```python
from langchain.embeddings import OpenAIEmbeddings
import chromadb

class VectorStore:
    """向量存储"""
    
    def __init__(self, persist_dir="./chroma_db"):
        # 初始化 embeddings
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key="your-api-key"
        )
        
        # 初始化 ChromaDB
        self.client = chromadb.Client(
            chromadb.config.Settings(
                persist_directory=persist_dir,
                anonymized_telemetry=False
            )
        )
        
        self.collection = None
    
    def create_collection(self, name: str = "documents"):
        """创建集合"""
        if self.collection:
            self.client.delete_collection(name)
        
        self.collection = self.client.create_collection(
            name=name,
            metadata={"description": "文档知识库"}
        )
        return self.collection
    
    def add_documents(self, chunks, collection_name: str = "documents"):
        """添加文档到向量库"""
        if not self.collection:
            self.create_collection(collection_name)
        
        # 批量添加
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            self.collection.add(
                documents=[c.page_content for c in batch],
                metadatas=[
                    {
                        "source": c.metadata.get("source", ""),
                        "page": c.metadata.get("page", 0)
                    } for c in batch
                ],
                ids=[f"doc_{i}_{j}" for j in range(len(batch))]
            )
        
        print(f"✅ 添加 {len(chunks)} 个文档块")
    
    def search(self, query: str, k: int = 5) -> List:
        """检索相关文档"""
        results = self.collection.query(
            query_texts=[query],
            n_results=k
        )
        
        return [{
            "content": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i] if "distances" in results else None
        } for i in range(len(results["documents"][0]))]
```

---

## 四、完整 RAG 系统

### 4.1 问答机器人

```python
from openai import OpenAI

class RAGBot:
    """RAG 问答机器人"""
    
    def __init__(self, api_key: str, vector_store: VectorStore):
        self.client = OpenAI(api_key=api_key)
        self.vector_store = vector_store
        self.system_prompt = """你是一位专业的知识库助手。
请基于提供的上下文信息回答问题。
如果上下文中没有相关信息，请如实告知。
回答要求：
1. 准确引用来源
2. 条理清晰
3. 简洁明了"""
    
    def ask(self, question: str, k: int = 5) -> Dict:
        """提问"""
        # 1. 检索相关文档
        contexts = self.vector_store.search(question, k=k)
        
        # 2. 构建 Prompt
        context_text = "\n\n".join([
            f"[来源 {i+1}] {c['content']}"
            for i, c in enumerate(contexts)
        ])
        
        prompt = f"""{self.system_prompt}

## 上下文信息
{context_text}

## 问题
{question}

## 回答
"""
        
        # 3. 调用 LLM
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        
        return {
            "question": question,
            "answer": answer,
            "sources": contexts,
            "model": "gpt-4"
        }
    
    def chat(self, question: str) -> str:
        """简化版聊天"""
        result = self.ask(question)
        return result["answer"]
```

### 4.2 使用示例

```python
# 初始化
vector_store = VectorStore(persist_dir="./company_kb")
bot = RAGBot(api_key="your-key", vector_store=vector_store)

# 构建知识库
loader = DocumentLoader("./company_docs")
documents = loader.load_all()

chunker = TextChunker(chunk_size=500, chunk_overlap=50)
chunks = chunker.split(documents)

vector_store.add_documents(chunks)

# 提问
result = bot.ask("公司的年假政策是什么？")

print(f"问题：{result['question']}")
print(f"答案：{result['answer']}")
print(f"来源：{len(result['sources'])} 个文档")
```

---

## 五、高级技巧

### 5.1 混合检索

```python
class HybridSearch:
    """混合检索：向量 + 关键词"""
    
    def __init__(self, vector_store, bm25_index):
        self.vector_store = vector_store
        self.bm25_index = bm25_index
    
    def search(self, query: str, k: int = 5):
        # 向量检索
        vector_results = self.vector_store.search(query, k=k*2)
        
        # 关键词检索
        bm25_results = self.bm25_index.search(query, k=k*2)
        
        # 融合结果（RRF 算法）
        fused = self.reciprocal_rank_fusion(
            vector_results,
            bm25_results,
            k=k
        )
        
        return fused
```

### 5.2 智能分块

```python
class SmartChunker:
    """智能分块：按语义分块"""
    
    def __init__(self, embedding_model):
        self.embeddings = embedding_model
    
    def semantic_split(self, text: str, threshold: float = 0.5):
        """根据语义相似度分块"""
        sentences = self._split_sentences(text)
        
        chunks = []
        current_chunk = [sentences[0]]
        
        for sent in sentences[1:]:
            # 计算与当前块的相似度
            similarity = self._calculate_similarity(
                current_chunk,
                sent
            )
            
            if similarity < threshold:
                # 开始新块
                chunks.append(" ".join(current_chunk))
                current_chunk = [sent]
            else:
                current_chunk.append(sent)
        
        chunks.append(" ".join(current_chunk))
        return chunks
```

---

## 六、性能优化

### 6.1 缓存策略

```python
from functools import lru_cache
import hashlib

class QueryCache:
    """查询缓存"""
    
    def __init__(self, max_size=1000):
        self.cache = {}
        self.max_size = max_size
    
    def _hash(self, query: str) -> str:
        return hashlib.md5(query.encode()).hexdigest()
    
    def get(self, query: str):
        key = self._hash(query)
        return self.cache.get(key)
    
    def set(self, query: str, result: Dict):
        key = self._hash(query)
        
        if len(self.cache) >= self.max_size:
            # 删除最旧的
            self.cache.pop(next(iter(self.cache)))
        
        self.cache[key] = result
```

### 6.2 异步处理

```python
import asyncio

class AsyncRAGBot:
    """异步 RAG 机器人"""
    
    async def ask(self, question: str):
        # 并行检索和缓存查询
        cache_task = asyncio.create_task(self._get_cache(question))
        search_task = asyncio.create_task(self._search(question))
        
        cache_result, contexts = await asyncio.gather(
            cache_task,
            search_task
        )
        
        if cache_result:
            return cache_result
        
        # 生成答案
        answer = await self._generate(question, contexts)
        
        # 异步缓存
        asyncio.create_task(self._cache(question, answer))
        
        return answer
```

---

## 七、常见问题

### Q1: 检索不准确怎么办？

**A:** 调整分块大小、尝试不同的 embedding 模型、添加重排序

### Q2: 回答太长怎么办？

**A:** 限制上下文数量、优化 Prompt、设置 max_tokens

### Q3: 如何评估 RAG 质量？

**A:** 使用 RAGAS 等评估框架，关注检索准确率和答案质量

---

## 📝 课后作业

1. 搭建一个 RAG 知识库
2. 实现文档加载和向量化
3. 开发问答接口
4. 测试检索准确率

---

## 🔗 参考资料

- [LangChain RAG](https://python.langchain.com/docs/use_cases/question_answering)
- [RAGAS 评估](https://docs.ragas.io)
- [ChromaDB 文档](https://docs.trychroma.com)

---

**下一课：** [07 - Agent 评估](07_agent_evaluation.md)
