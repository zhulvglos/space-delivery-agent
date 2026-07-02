# 空间配置与交付规划 Agent 平台

> 基于瑞泽·海度假民宿已建项目复盘，将卡素 Capsule Cabin 产品选型、空间配置、智能设备建议与装配式交付任务拆解为可交互的 AI Agent PoC。

## 项目简介

本项目是一个面向装配式民宿扩建场景的全栈 AI 应用 Demo。它不是宣称真实项目建设阶段已经使用 AI，而是基于已建成项目的参与经验、产品资料图、户型图与现场交付复盘，回溯式抽象出一套可演示的产品化闭环：

```text
业主需求输入 -> 产品型号推荐 -> 空间模块配置 -> 智能设备建议 -> 交付阶段看板 -> 项目档案沉淀
```

当前固定案例为“瑞泽·海度假民宿 38㎡单体扩建（规则型 PoC）”，产品体系为卡素 Capsule Cabin。系统支持 38㎡单体产品 Capsule Cabin S 与 56㎡拼装产品 Capsule Cabin M 的需求匹配，并输出配置清单、示例预算层级、7 阶段装配式交付任务、验收点与风险提示。

## 当前成果

- 首页已改造为“卡素民宿真实案例 + 回溯式 AI PoC”展示页，包含项目位置、已知规模、装配式交付流程与产品资产说明。
- AI 规划台支持“空间配置 Agent”和“交付规划 Agent”双 Agent 流程。
- 未配置 LLM API Key 时，系统使用瑞泽·海项目复盘规则兜底，保证 Demo 可运行。
- 配置 LLM API Key 后，LLM 会在规则护栏内复核方案并补充业主侧判断。
- 项目详情页可展示 Demo 项目的产品配置、空间模块、配置清单、智能设备、交付阶段与风险提示。
- 后端提供免登录 Demo API，也保留登录、项目 CRUD、对话历史和保存项目能力。

## 核心功能

### 空间配置 Agent

复用原 `renovating_agent` LangGraph 骨架，业务语义已替换为空间配置：

| 能力 | 输出 |
| --- | --- |
| 需求解析 | 入住人数、运营模式、面积偏好、智能化等级、预算层级、场地条件 |
| 产品推荐 | Capsule Cabin S / Capsule Cabin M |
| 空间配置 | 榻榻米、衣柜/挂衣空间、卫浴、沙发区、水吧台、换鞋区、活动区等 |
| 智能设备 | 智能门锁、灯光、空调、窗帘、传感器、监控、稳定 Wi-Fi |
| 预算说明 | 示例配置预算层级，不保存真实报价 |
| 方案输出 | 结构化配置方案、推荐依据、人工确认项与能力边界 |

### 交付规划 Agent

复用原 `moving_agent` LangGraph 骨架，业务语义已替换为装配式交付规划：

| 能力 | 输出 |
| --- | --- |
| 读取配置 | 接收已确认的产品型号、面积、空间模块与智能化配置 |
| 交付阶段 | 设计确认、工厂加工/预制、运输、现场基础、吊装、拼接安装、调试验收 |
| 任务拆解 | 每阶段任务清单、验收点、风险项 |
| 风险评估 | 道路运输、吊装空间、基础不平、排水、防水、防腐、供电网络等 |
| 看板输出 | 7 阶段交付看板数据，可在前端卡片化展示 |

### RAG 与规则知识库

系统内置瑞泽·海项目复盘与卡素产品知识：

- 瑞泽·海度假民宿位于威海滨海度假区，共 13 套客房。
- 其中 7 套为约 38㎡单体产品，6 套为约 56㎡拼装产品。
- Capsule Cabin S 面向紧凑型单体扩建，最多支持 4 人入住。
- Capsule Cabin M 更适合多人入住、活动区、简餐区和更宽松空间需求。
- 交付流程按装配式产品的设计、生产、运输、现场、吊装、安装、调试拆解。
- 系统明确保留 PoC 边界，不替代正式设计、报价、施工组织、消防审批或工程承诺。

## 技术栈

| 模块 | 技术 |
| --- | --- |
| 前端 | Vue 3、TypeScript、Vite、Pinia、Vue Router、Arco Design Vue、ECharts |
| 后端 | FastAPI、SQLAlchemy Async、Pydantic Settings、JWT |
| Agent | LangGraph 工作流骨架，规则兜底 + 可选 LLM 复核 |
| LLM | OpenAI / DeepSeek / Qwen 兼容客户端 |
| 知识库 | Chroma / LangChain Chroma，内置项目复盘知识 |
| 数据库 | 开发默认 SQLite，生产可切换 PostgreSQL |
| 部署 | Docker Compose、Nginx、Redis |

## 项目结构

```text
MoveRenovateAI/
├── README.md
├── docker-compose.yml
├── 系统架构.png
├── ER图.png
├── assets/capsule_cabin/                 # 案例图片与户型资料
├── docs/
│   └── capsule_cabin_refactor_audit.md   # 从旧搬装项目改造为民宿 PoC 的审计记录
├── portfolio_assets/capsule_cabin_agent/ # 作品集说明、Demo 脚本与截图
├── sql/
│   └── init.sql
├── backend/
│   ├── app/
│   │   ├── api/agent.py                  # Demo API、对话 API、保存项目
│   │   ├── agent/
│   │   │   ├── renovating_agent/         # 空间配置 Agent
│   │   │   └── moving_agent/             # 交付规划 Agent
│   │   ├── rag/knowledge_base.py         # 瑞泽·海项目复盘知识库
│   │   ├── llm/                          # 多 Provider LLM 客户端与结构化兜底
│   │   └── models/                       # 用户、项目、清单、预算、阶段、对话模型
│   ├── data/
│   │   ├── demo_capsule_cabin.json
│   │   └── capsule_cabin_knowledge.json
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── views/Home.vue                # 案例展示首页
    │   ├── views/AIChat.vue              # Agent 规划台
    │   ├── views/Projects.vue            # 项目列表
    │   ├── views/ProjectDetail.vue       # Demo 项目详情
    │   └── api/agent.ts                  # Demo Chat / Demo Project API
    └── package.json
```

## API 概览

### Demo API

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/v1/agent/demo-case` | 获取固定 Demo 案例 |
| POST | `/api/v1/agent/demo-chat` | 免登录调用空间配置 / 交付规划 Agent |
| GET | `/api/v1/agent/demo-project` | 获取 Demo 项目详情数据 |

### 登录态 API

| 模块 | 路径 | 说明 |
| --- | --- | --- |
| Auth | `/api/v1/auth/register`、`/api/v1/auth/login`、`/api/v1/auth/me` | 注册、登录、当前用户 |
| Agent | `/api/v1/agent/chat`、`/api/v1/agent/history`、`/api/v1/agent/save-to-project` | 对话、历史、保存方案 |
| Projects | `/api/v1/projects` | 项目列表、创建、详情、更新、删除 |

## 本地运行

### 后端

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

如果只体验规则型 Demo，可以不配置 LLM Key。若要启用 LLM 复核，在 `backend/.env` 中配置：

```ini
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-xxx

# 或
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxx

# 或
LLM_PROVIDER=qwen
QWEN_API_KEY=sk-xxx
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问地址：

- 前端：http://localhost:5173
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

### Docker Compose

```bash
docker-compose up -d
```

## Demo 话术

可以在 AI 规划台输入：

```text
基于瑞泽·海度假民宿复盘，为滨海度假区新增一套 38㎡卡素单体产品，自助入住，配置基础智能控制。
```

或：

```text
为 6 人亲子/小团体入住场景推荐卡素 56㎡拼装产品，要求保留活动区和简餐区，并配置自助入住。
```

生成配置方案后，可继续生成交付规划：

```text
基于上一轮已确认配置，生成 7 阶段装配式交付看板。
```

也可以做风险评估：

```text
滨海场地道路较窄、吊装空间有限，评估该场景下的交付风险与前置确认项。
```

## 能力边界

本项目是基于真实项目复盘的 AI PoC，用于展示产品经理视角下的业务结构化、Agent 工作流设计和工程落地能力。

它不构成：

- 正式建筑设计、结构设计或施工图成果
- 正式报价、合同价格或成本承诺
- 正式施工组织、工期承诺或工程交付承诺
- 消防、审批、合规、验收等专业结论
- 对真实项目建设过程已经使用 AI 的事实声明

## 仓库信息

- 中文名：空间配置与交付规划 Agent 平台
- 英文仓库名：space-delivery-agent
- 当前定位：卡素 Capsule Cabin 民宿配置与装配式交付规划 AI PoC
