# Financing-Report-Agent

基于 LangGraph 的金融研究报告自动生成 Agent，通过多智能体协作完成从信息采集、知识图谱推理、报告撰写到质量评审的全流程自动化。

## 系统架构

```
用户输入研究主题
      ↓
  ┌──────────┐
  │ Researcher│ ← Bocha 网络搜索 + 实时数据采集
  └────┬─────┘
       ↓
  ┌──────────────┐
  │ Graph Reasoner│ ← Neo4j 知识图谱推理 + 向量检索
  └────┬─────────┘
       ↓
  ┌──────────┐
  │  Writer   │ ← 结构化报告生成
  └────┬─────┘
       ↓
  ┌──────────┐
  │  Critic   │ ← 质量评审（最多 3 轮迭代）
  └────┬─────┘
       ↓
  ┌──────────┐
  │ Finalizer │ ← PDF 报告导出
  └──────────┘
```

## 技术栈

| 组件 | 技术 |
|------|------|
| Agent 框架 | LangGraph + LangChain |
| 后端 | FastAPI + Uvicorn |
| 知识图谱 | Neo4j |
| 向量数据库 | Milvus |
| 关系数据库 | MySQL 8.4（LangGraph Checkpoint） |
| 缓存/消息队列 | Redis + Celery |
| 网络搜索 | Bocha Web Search API |
| 前端 | Gradio |
| 监控 | Prometheus + Grafana |
| PDF 生成 | WeasyPrint |
| 嵌入模型 | sentence-transformers |

## 快速开始

### 1. 启动基础服务

```bash
docker compose up -d mysql neo4j redis prometheus grafana
```

服务端口：
- MySQL: 3306
- Neo4j: 7474 (Web) / 7687 (Bolt)
- Redis: 6379
- Prometheus: 9090
- Grafana: 3000

### 2. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
export BOCHA_API_KEY="your-bocha-api-key"
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password"
export MYSQL_URI="mysql+aiomysql://user:password@localhost:3306/aether_invest"
export REDIS_URL="redis://localhost:6379/0"
```

### 4. 启动后端

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. 启动 Celery Worker（可选，异步任务）

```bash
celery -A app.celery_app.celery_app worker -l info
```

### 6. 启动前端

```bash
cd frontend
python gradio_app.py
```

## 项目结构

```
Financing-Report-Agent/
├── backend/
│   ├── app/
│   │   ├── agents/          # 智能体节点（researcher, writer, critic, graph_reasoner）
│   │   ├── graph/           # LangGraph 工作流定义
│   │   ├── routers/         # API 路由
│   │   ├── main.py          # FastAPI 入口
│   │   ├── tools.py         # 工具函数（搜索、PDF 生成、Neo4j 查询）
│   │   ├── db.py            # 数据库连接
│   │   ├── metrics.py       # Prometheus 指标
│   │   └── utils.py         # 日志等工具
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   └── gradio_app.py        # Gradio 前端
├── grafana/
│   └── dashboard.json       # Grafana 监控面板
├── docker-compose.yml       # 基础服务编排
├── prometheus.yml           # Prometheus 配置
├── pyproject.toml
└── neo4j1.ipynb             # Neo4j 数据导入 Notebook
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/research` | 启动研究任务 |
| POST | `/stream/{thread_id}` | SSE 流式获取 Agent 执行过程 |

## 核心特性

- **多智能体协作**: Researcher → Graph Reasoner → Writer → Critic 四阶段流水线
- **知识图谱推理**: Neo4j 存储金融实体关系，支持图谱推理
- **迭代优化**: Critic 评审不通过自动回退 Writer 重写（最多 3 轮）
- **人工介入**: 支持在 Critic 阶段插入人工反馈
- **PDF 报告导出**: WeasyPrint 生成结构化 PDF
- **实时监控**: Prometheus 采集 + Grafana 面板
- **SSE 流式输出**: 实时查看 Agent 执行过程
