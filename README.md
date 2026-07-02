# MoveRenovateAI（搬装智脑）

> AI 驱动的搬家 + 装修规划平台，基于 LangGraph Agent 工作流 + RAG 知识库 + Vue 3 前端

---

## 项目简介

MoveRenovateAI 是一款面向搬家和装修需求的全栈 AI 应用。用户通过自然语言对话，即可获得：
- 搬家场景：自动生成物品清单、打包方案、费用估算、还原指南
- 装修场景：自动生成预算分配、施工阶段规划、材料建议

系统通过 LangGraph 状态图驱动多节点 Agent 工作流，结合 Chroma 向量知识库提供专业建议，并将 AI 生成的方案持久化为可追踪的项目数据。

---

## 核心功能

### 搬家规划 Agent（Moving Agent）

| 功能 | 说明 |
|------|------|
| 需求解析 | 从自然语言提取出发地、目的地、房间数、搬家日期、预算 |
| 物品清单 | 按房间类型生成物品列表，标记易碎品和贵重品 |
| 打包方案 | 为每个箱子规划编号、标签和物品组合 |
| 费用估算 | 7 项成本明细（基础费/距离/物品/箱子/楼层/易碎/贵重） |
| 还原指南 | 新家物品拆箱还原的分步指引 |
| 对话回复 | Markdown 表格格式的结构化汇总 |

### 装修规划 Agent（Renovating Agent）

| 功能 | 说明 |
|------|------|
| 需求解析 | 提取户型、面积、当前状态、风格偏好、预算区间、重点需求 |
| 预算分配 | 6 大类（设计/基装/主材/软装/家电/其他），按面积和风格计算 |
| 施工阶段 | 9 个标准阶段（设计→拆改→水电→泥瓦→木工→油漆→安装→软装→保洁） |
| 对话回复 | 带进度条的预算展示、阶段列表、实用建议 |

### RAG 知识库

- 使用 Chroma 向量数据库存储专业装修和搬家知识
- 内置 8 条默认知识：搬家准备/打包技巧/安全事项/水电改造/防水/木工/油漆/预算控制
- 支持语义相似度检索，为 Agent 回复提供专业参考

---

## 技术栈

| 技术 | 用途 | 版本 |
|------|------|------|
| Python | 后端核心语言 | 3.11+ |
| FastAPI | 异步 Web 框架 | 0.109 |
| LangGraph | Agent 状态图工作流 | 0.0.40 |
| LangChain | LLM 集成层 | 0.1.20 |
| Chroma | 向量数据库（RAG） | 0.4.22 |
| SQLAlchemy | 异步 ORM | 2.0 |
| PostgreSQL | 生产数据库 | 15+ |
| SQLite + aiosqlite | 开发数据库 | - |
| Redis | 缓存 | 7.0+ |
| Vue 3 | 前端框架 | 3.4 |
| TypeScript | 前端类型系统 | 5.3 |
| Vite | 前端构建工具 | 5.1 |
| Pinia | 状态管理 | 2.1 |
| Arco Design Vue | UI 组件库 | 2.55 |
| Axios | HTTP 客户端 | 1.6 |
| Docker Compose | 容器编排部署 | - |

---

## 项目结构

```
MoveRenovateAI/
├── docker-compose.yml              # 容器编排：backend / postgres / redis / frontend
├── 项目说明.md                      # 本文件
├── 系统架构.png                      # 系统架构图
├── ER图.png                         # 数据库 ER 图
│
├── sql/
│   └── init.sql                    # PostgreSQL 建表 DDL（7 张表 + 7 个索引）
│
├── backend/
│   ├── Dockerfile                  # Python 3.11-slim 镜像
│   ├── requirements.txt            # 23 个 Python 依赖
│   ├── .env.example                # 环境变量模板（LLM Key / DB / Redis / RAG）
│   └── app/
│       ├── __init__.py             # 包初始化，暴露 settings 单例
│       ├── config.py               # pydantic-settings 配置类，@lru_cache 单例
│       ├── database.py             # 异步引擎 + AsyncSession + 依赖注入 get_db()
│       ├── main.py                 # FastAPI 入口，生命周期 / CORS / 路由挂载
│       │
│       ├── models/
│       │   ├── __init__.py         # 导出 7 个 ORM 模型类
│       │   ├── user.py             # User 模型（13 字段，projects / conversations 关系）
│       │   └── project.py          # Project / Checklist / ChecklistItem / Budget / Phase / Conversation
│       │
│       ├── llm/
│       │   ├── __init__.py
│       │   └── client.py           # LLMClient 多 Provider 支持（OpenAI / DeepSeek / Qwen）
│       │
│       ├── agent/
│       │   ├── __init__.py
│       │   ├── state.py            # MovingAgentState / RenovatingAgentState TypedDict
│       │   ├── moving_agent/
│       │   │   ├── __init__.py
│       │   │   ├── nodes.py        # 6 个节点：解析需求→物品清单→打包方案→费用→还原指南→回复
│       │   │   └── graph.py        # LangGraph 线性状态图，单例入口 run_moving_agent()
│       │   └── renovating_agent/
│       │       ├── __init__.py
│       │       ├── nodes.py        # 4 个节点：解析需求→预算分配→施工阶段→回复
│       │       └── graph.py        # LangGraph 线性状态图，单例入口 run_renovating_agent()
│       │
│       ├── rag/
│       │   ├── __init__.py
│       │   └── knowledge_base.py   # Chroma 向量库，语义检索 + 默认知识初始化
│       │
│       └── api/
│           ├── __init__.py
│           ├── auth.py             # 注册 / 登录 / 获取当前用户（JWT）
│           ├── projects.py         # 项目 CRUD（列表/创建/详情/更新/删除）
│           └── agent.py            # AI 对话 / 历史记录 / 保存到项目
│
└── frontend/
    ├── Dockerfile                  # 多阶段构建：Node 编译 → Nginx 部署
    ├── nginx.conf                  # SPA 路由 + /api 反向代理到 backend:8000
    ├── package.json                # Vue 3 + Arco Design + Pinia + Axios + ECharts
    ├── vite.config.ts              # 端口 5173，/api 代理到 localhost:8000
    ├── tsconfig.json               # Vue 3 + TypeScript 编译配置
    ├── tsconfig.node.json          # vite.config.ts 的 TypeScript 配置
    ├── index.html                  # Vite 入口 HTML（#app 挂载点）
    └── src/
        ├── main.ts                 # 创建 App，挂载 Pinia / Router / ArcoVue
        ├── App.vue                 # 根组件，Arco 中文语言包 + <router-view>
        ├── env.d.ts                # .vue 模块和 import.meta.env 类型声明
        ├── router/
        │   └── index.ts            # 6 条路由（home / chat / projects / project/:id / login）
        ├── api/
        │   ├── index.ts            # Axios 实例，Bearer Token 拦截器，401 跳转登录
        │   ├── agent.ts            # AI 对话相关 API
        │   └── projects.ts         # 项目 CRUD API
        └── views/
            ├── Home.vue            # 首页：英雄区 + 3 功能卡片 + 最近项目
            ├── AIChat.vue          # AI 对话页：快捷模板 / 消息列表 / 方案卡片 / 建议标签
            ├── Projects.vue        # 项目列表页：类型筛选 / 分页 / 创建弹窗 / 删除确认
            ├── ProjectDetail.vue   # 项目详情页：信息描述 / 清单进度条
            └── Login.vue           # 登录页：用户名+密码 / JWT 存储 / 渐变背景
```

---

## 数据库设计

共 7 张表，全部使用 UUID 主键 + `gen_random_uuid()` 自动填充：

| 表名 | 说明 | 核心字段 |
|------|------|---------|
| `users` | 用户 | username, email, password_hash, preferences (JSON) |
| `projects` | 项目 | project_type, title, 地址, 户型, 面积, 风格, 预算 |
| `checklists` | 清单 | project_id, checklist_type, name, total_items, completed_items |
| `checklist_items` | 清单项 | checklist_id, name, category, room, is_fragile, is_valuable, pack_order |
| `budgets` | 预算明细 | project_id, category, item_name, quantity, unit_price |
| `phases` | 施工阶段 | project_id, name, 阶段序号, 工期, tasks/checkpoints (JSON) |
| `conversations` | 对话记录 | user_id, role, content, metadata (JSON), session_id |

索引：users(username) / users(email) / projects(user_id) / checklist_items(checklist_id) / budgets(project_id) / phases(project_id) / conversations(user_id+created_at)

---

## API 接口一览

### 认证 `/api/v1/auth`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/register` | 注册（username + email 唯一性校验，bcrypt 加密） |
| POST | `/登录` | 登录（支持用户名或邮箱），返回 JWT |
| GET | `/me` | 获取当前登录用户信息 |

### 项目 `/api/v1/projects`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 项目列表，支持 type / status 筛选，分页 |
| POST | `/` | 创建项目 |
| GET | `/{project_id}` | 项目详情（含清单 + 预算） |
| PUT | `/{project_id}` | 更新项目字段 |
| DELETE | `/{project_id}` | 删除项目（校验所有权） |

### AI 对话 `/api/v1/agent`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/chat` | 对话入口，自动识别搬家/装修意图，调用对应 Agent |
| GET | `/history` | 查询对话历史，分页 |
| DELETE | `/history` | 清空当前用户所有对话 |
| POST | `/save-to-project` | 将 AI 生成的方案保存为项目清单 |

---

## 环境配置

复制 `backend/.env.example` → `backend/.env`，按需填写：

```ini
# 应用
APP_NAME=MoveRenovateAI
DEBUG=True

# 数据库（开发用 SQLite，生产用 PostgreSQL）
DATABASE_URL=sqlite+aiosqlite:///./moverenovateai.db
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/moverenovateai

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-super-secret-key-change-in-production

# LLM（三选一，填对应的 KEY）
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-xxx
# OPENAI_API_KEY=sk-xxx
# QWEN_API_KEY=sk-xxx

# RAG
EMBEDDING_MODEL=text-embedding-3-small
VECTOR_STORE_TYPE=chroma
VECTOR_STORE_PATH=./data/vectorstore
```

---

## 运行指南

### 方式一：本地开发

```bash
# ---------- 后端 ----------
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # 编辑填入 DEEPSEEK_API_KEY
uvicorn app.main:app --reload --port 8000

# ---------- 前端 ----------
cd frontend
npm install
npm run dev                       # 访问 http://localhost:5173
```

### 方式二：Docker Compose

```bash
# 根目录执行
cp backend/.env.example .env      # 编辑填入 DEEPSEEK_API_KEY
docker-compose up -d

# 访问地址
# 前端：http://localhost:5173
# 后端 API：http://localhost:8000
# API 文档：http://localhost:8000/docs
# PostgreSQL：localhost:5432
# Redis：localhost:6379
```

---

## 系统架构

```
┌──────────────────────────────────────────────────────────────┐
│                      前端 (Vue 3 + Arco)                      │
│   Home  │  AIChat  │  Projects  │  ProjectDetail  │  Login   │
└────────────────────────┬─────────────────────────────────────┘
                         │ Axios (Bearer JWT)
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                    后端 (FastAPI + async)                      │
│  ┌─────────┐  ┌──────────┐  ┌─────────────────────────────┐ │
│  │auth API │  │projects  │  │       agent API             │ │
│  │注册/登录│  │CRUD      │  │  对话 → 意图识别 → Agent路由  │ │
│  └─────────┘  └──────────┘  └────────┬──────────┬─────────┘ │
│                                      │          │            │
│                        ┌─────────────▼──┐  ┌────▼──────────┐│
│                        │ Moving Agent   │  │Renovating Agent││
│                        │ (LangGraph)    │  │ (LangGraph)    ││
│                        │ 6 节点线性流    │  │ 4 节点线性流    ││
│                        └────────────────┘  └────────────────┘│
│                                      │          │            │
│  ┌──────────┐  ┌──────────────┐  ┌──▼──────────▼──┐        │
│  │LLMClient│  │RAG Knowledge │  │  SQLAlchemy    │        │
│  │OpenAI/  │  │Base (Chroma) │  │  ORM (async)   │        │
│  │DeepSeek/│  │语义检索       │  │                │        │
│  │Qwen     │  │              │  │                │        │
│  └─────────┘  └──────────────┘  └───────┬────────┘        │
└──────────────────────────────────────────┼──────────────────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                      │
              ┌─────▼─────┐        ┌──────▼──────┐        ┌──────▼──────┐
              │ PostgreSQL │        │   Redis     │        │   Chroma    │
              │ 持久化存储  │        │   缓存      │        │  向量知识库  │
              └───────────┘        └─────────────┘        └─────────────┘
```
