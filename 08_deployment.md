# 08 - 部署上线：从开发到生产

> **AI Agent 开发教程 第 08 课**  
> 📅 2026 年 3 月 | 👨‍💻 [@Gale2World](https://github.com/zdnuist)

---

## 📋 课程目标

学完本课后，你将能够：
- ✅ 理解生产环境部署要求
- ✅ 实现 API 服务化
- ✅ 配置监控和日志
- ✅ 掌握 CI/CD 流程

---

## 一、部署架构

### 1.1 典型架构

```
┌─────────────────────────────────────────┐
│              用户层                      │
│    Web / App / API Client               │
└─────────────────┬───────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────┐
│              网关层                      │
│    Nginx / API Gateway / Load Balancer  │
└─────────────────┬───────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────┐
│             应用层                       │
│    Agent Service (FastAPI/Flask)        │
└─────────────────┬───────────────────────┘
                  │
         ┌────────┴────────┐
         ↓                 ↓
┌─────────────┐   ┌─────────────┐
│   数据库     │   │  向量数据库  │
│   PostgreSQL│   │   Chroma    │
└─────────────┘   └─────────────┘
```

### 1.2 部署方式对比

| 方式 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| **本地部署** | 数据安全、低延迟 | 运维成本高 | 企业内部 |
| **云服务** | 弹性扩展、易维护 | 数据出域 | 初创公司 |
| **混合部署** | 灵活、平衡 | 复杂度高 | 大型企业 |

---

## 二、API 服务化

### 2.1 FastAPI 实现

```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(
    title="AI Agent API",
    description="AI Agent 服务接口",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求模型
class ChatRequest(BaseModel):
    message: str
    conversation_id: str = None

class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    tokens_used: int

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# 聊天接口
@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # 调用 Agent
        agent = get_agent()
        response = await agent.chat(request.message)
        
        return ChatResponse(
            message=response["answer"],
            conversation_id=response["conversation_id"],
            tokens_used=response["tokens"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 启动服务
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=4
    )
```

### 2.2 认证授权

```python
from fastapi import Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """验证 JWT Token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

# 使用
@app.post("/api/v1/chat")
async def chat(
    request: ChatRequest,
    user: dict = Depends(verify_token)
):
    # user 包含认证信息
    pass
```

---

## 三、配置管理

### 3.1 环境变量

```python
# config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "AI Agent"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # API 配置
    API_KEY: str
    API_BASE_URL: str = "https://api.openai.com/v1"
    MODEL_NAME: str = "gpt-4"
    
    # 数据库配置
    DATABASE_URL: str
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    
    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "app.log"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

### 3.2 配置文件

```bash
# .env.example
# API 配置
API_KEY=your-api-key-here
API_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4

# 数据库
DATABASE_URL=postgresql://user:pass@localhost:5432/agent_db
CHROMA_PERSIST_DIR=/data/chroma_db

# 服务
HOST=0.0.0.0
PORT=8000
WORKERS=4

# 日志
LOG_LEVEL=INFO
LOG_FILE=/var/log/agent/app.log
```

---

## 四、容器化部署

### 4.1 Dockerfile

```dockerfile
# 多阶段构建
FROM python:3.11-slim as builder

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 运行阶段
FROM python:3.11-slim

WORKDIR /app

# 复制依赖
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app .

# 复制代码
COPY . .

# 环境变量
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 4.2 Docker Compose

```yaml
version: '3.8'

services:
  agent-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/agent_db
      - CHROMA_PERSIST_DIR=/data/chroma
    volumes:
      - chroma_data:/data/chroma
      - ./logs:/var/log/agent
    depends_on:
      - db
    restart: unless-stopped
  
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: agent_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - agent-api
    restart: unless-stopped

volumes:
  postgres_data:
  chroma_data:
```

---

## 五、监控和日志

### 5.1 日志配置

```python
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(log_file: str, level: str = "INFO"):
    """配置日志"""
    
    # 创建日志目录
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # 配置
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger("agent")
    return logger
```

### 5.2 性能监控

```python
from prometheus_client import Counter, Histogram, generate_latest
import time
from functools import wraps

# 指标定义
REQUEST_COUNT = Counter(
    'agent_requests_total',
    'Total requests',
    ['endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'agent_request_latency_seconds',
    'Request latency',
    ['endpoint']
)

# 监控装饰器
def monitor(endpoint: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time
                REQUEST_COUNT.labels(endpoint=endpoint, status=status).inc()
                REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
        
        return wrapper
    return decorator

# Prometheus 指标端点
@app.get("/metrics")
async def metrics():
    return generate_latest()
```

---

## 六、CI/CD 流程

### 6.1 GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests
        run: pytest tests/
  
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t agent-api:latest .
      
      - name: Push to registry
        run: |
          docker tag agent-api:latest registry.example.com/agent-api:latest
          docker push registry.example.com/agent-api:latest
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        run: |
          ssh user@server "cd /opt/agent && docker-compose pull && docker-compose up -d"
```

---

## 七、性能优化

### 7.1 缓存策略

```python
from functools import lru_cache
import redis

# 内存缓存
@lru_cache(maxsize=1000)
def cached_embedding(text: str):
    return get_embedding(text)

# Redis 缓存
class RedisCache:
    def __init__(self, host='localhost', port=6379):
        self.redis = redis.Redis(host=host, port=port)
    
    def get(self, key: str):
        return self.redis.get(key)
    
    def set(self, key: str, value: str, ttl: int = 3600):
        self.redis.setex(key, ttl, value)
```

### 7.2 异步处理

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncAgent:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    async def batch_process(self, tasks: List[str]):
        """批量处理"""
        loop = asyncio.get_event_loop()
        
        # 并发执行
        futures = [
            loop.run_in_executor(
                self.executor,
                self.process_task,
                task
            )
            for task in tasks
        ]
        
        results = await asyncio.gather(*futures)
        return results
```

---

## 八、常见问题

### Q1: 如何处理高并发？

**A:** 负载均衡、连接池、异步处理、缓存

### Q2: API 密钥如何管理？

**A:** 环境变量、密钥管理服务、定期轮换

### Q3: 如何保证服务可用性？

**A:** 健康检查、自动重启、多实例部署

---

## 📝 课后作业

1. 实现 FastAPI 服务
2. 编写 Dockerfile
3. 配置 CI/CD 流程
4. 添加监控指标

---

## 🔗 参考资料

- [FastAPI 文档](https://fastapi.tiangolo.com)
- [Docker 最佳实践](https://docs.docker.com/develop/develop-images/dockerfile_best-practices)
- [12-Factor App](https://12factor.net)

---

**下一课：** [09 - GitHub Bounty 实战](09_github_bounty_practice.md)
