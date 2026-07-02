# 卡素民宿 AI 配置与交付规划 Agent｜最小改造审计

审计时间：2026-06-24  
审计范围：当前 `MoveRenovateAI` 仓库。  
执行原则：本阶段只阅读指导文档与仓库，输出改造审计，不直接进行业务代码改造。

## 1. 当前可运行状态

### 1.1 项目结构判断

当前仓库已经具备指导文档要求复用的主体结构：

- 前端：`frontend/`，Vue 3 + TypeScript + Vite + Arco Design。
- 后端：`backend/`，FastAPI + SQLAlchemy async。
- Agent：`backend/app/agent/moving_agent/` 与 `backend/app/agent/renovating_agent/`，均为 LangGraph 线性工作流。
- RAG：`backend/app/rag/knowledge_base.py`，使用 Chroma + Embeddings。
- 数据模型：`Project`、`Checklist`、`ChecklistItem`、`Budget`、`Phase`、`Conversation` 已存在。
- 本地开发数据库默认值：`sqlite+aiosqlite:///./moverenovateai.db`。
- Docker 配置：`docker-compose.yml` 使用 PostgreSQL + Redis + backend + frontend。

### 1.2 已做的轻量验证

- `python -m compileall app`：后端 Python 文件语法编译通过。
- `npm --version`：本机可用 npm，版本为 `10.9.2`。
- 当前目录不是 Git 仓库：`git status` 返回 `fatal: not a git repository`。

### 1.3 当前环境阻塞点

- 当前 Python 环境缺少 `langgraph`，直接导入失败：`ModuleNotFoundError: No module named 'langgraph'`。
- 当前 Python 环境中的 SQLAlchemy 版本偏旧，导入 `async_sessionmaker` 失败。需要按 `backend/requirements.txt` 安装依赖，或使用独立虚拟环境。
- `frontend/node_modules` 不存在，需要先执行 `npm install`。
- `backend/.env` 不存在，且默认 `LLM_PROVIDER=deepseek`，没有 API Key 时 Agent 实际对话会失败。
- `backend/moverenovateai.db` 尚不存在，需要启动后端或初始化数据库后生成。
- API 鉴权存在明显实现风险：前端通过 `Authorization: Bearer ...` 发送 token，但 `projects.py` 与 `agent.py` 中多处使用 `token: str = Depends(lambda: None)`，不会自动读取 Header token，登录后调用项目/对话接口可能仍返回未授权。
- RAG 初始化会创建 Embeddings 客户端并写入 Chroma；无 API Key 或依赖不齐时会失败，但 `main.py` 已捕获知识库初始化异常并降级为 warning。

## 2. 可直接复用的文件

### 2.1 后端

- `backend/app/main.py`：FastAPI 入口可复用，只需替换应用描述和部分文案。
- `backend/app/config.py`：配置结构可复用，默认 SQLite 符合本地最小闭环方向。
- `backend/app/database.py`：数据库会话与初始化逻辑可复用。
- `backend/app/models/project.py`：核心数据模型可复用，尤其 `Project.requirements = Column(JSON, default=dict)` 已满足“优先使用 requirements JSONB/JSON”的要求。
- `backend/app/api/projects.py`：项目 CRUD 可复用，但需要补充 `requirements`、`budgets`、`phases` 的读写和返回。
- `backend/app/api/agent.py`：对话入口、历史记录、保存到项目链路可复用，但意图识别、保存结构、鉴权方式需要调整。
- `backend/app/agent/state.py`：TypedDict 可保留文件位置，替换为民宿配置与交付规划字段。
- `backend/app/agent/renovating_agent/graph.py`：LangGraph 骨架可复用为“空间配置 Agent”。
- `backend/app/agent/moving_agent/graph.py`：LangGraph 骨架可复用为“交付规划 Agent”。
- `backend/app/rag/knowledge_base.py`：RAG 封装可复用，只需替换默认知识与查询文案。

### 2.2 前端

- `frontend/src/views/Home.vue`：可改造为“卡素民宿真实案例 + 回溯式 AI PoC”首页。
- `frontend/src/views/AIChat.vue`：可改造为“创建配置方案 / 调整方案”的 Agent 交互页。
- `frontend/src/views/Projects.vue`：可改造为“民宿配置项目列表”。
- `frontend/src/views/ProjectDetail.vue`：可扩展展示产品选型、配置清单、预算区间、交付阶段、风险点。
- `frontend/src/api/agent.ts` 与 `frontend/src/api/projects.ts`：API 包装可复用。
- `frontend/src/router/index.ts`：路由结构足够，暂不需要新增复杂页面。

### 2.3 现有素材

- 当前已有 `CAPSULE CABIN/` 目录，包含 8 张宣传手册图片：
  - `DM宣传手册202548.jpg`
  - `DM宣传手册202549.jpg`
  - `DM宣传手册202550.jpg`
  - `DM宣传手册202551.jpg`
  - `DM宣传手册202552.jpg`
  - `DM宣传手册202553.jpg`
  - `DM宣传手册202554.jpg`
  - `DM宣传手册202555.jpg`
- 后续可从中筛选、复制或重命名到 `assets/capsule_cabin/`，但需要人工确认是否含不宜公开的信息。

## 3. 需要替换的旧业务文本与功能

### 3.1 后端 Agent

`backend/app/agent/moving_agent/nodes.py` 当前包含以下旧业务，应整体替换为“交付规划 Agent”语义：

- 搬家需求解析：出发地址、目标地址、房间、搬家日期、搬家人数。
- 物品清单生成：衣物、电器、书籍、厨具、家具等。
- 打包方案：箱号、标签、易碎品、贵重品、打包优先级。
- 搬家费用估算：起步价、距离费、物品费、箱子费、楼层费等。
- 新家还原指南。
- 最终回复中的“搬家信息、物品统计、费用估算、温馨提示”。

建议替换为：

- 读取已确认配置。
- 生成 7 个交付阶段。
- 生成每阶段任务、验收点、风险。
- 输出交付看板数据。
- 明确 PoC 边界。

`backend/app/agent/renovating_agent/nodes.py` 当前包含以下旧业务，应整体替换为“空间配置 Agent”语义：

- 泛装修需求解析：户型、房屋面积、毛坯/旧房、装修风格、预算范围。
- 装修预算：设计费、基装、主材、软装、家电、管理费。
- 泛家装施工阶段：设计、拆改、水电、泥瓦、木工、油漆、安装、软装、保洁。
- 真实金额式预算总价与材料清单。
- 装修建议：环保、通风、隐蔽工程等泛家装话术。

建议替换为：

- 解析民宿需求：面积偏好、客群、风格、运营方式、智能化等级、场地条件、预算等级。
- 推荐 Capsule Cabin S / M。
- 生成空间模块、配置项、智能设备建议。
- 输出示例预算区间，不输出真实报价。
- 输出结构化配置方案与人工确认项。

### 3.2 Agent 路由与保存链路

`backend/app/api/agent.py` 当前旧语义包括：

- `detect_project_type()` 只识别搬家/装修关键词。
- 默认无法识别时走 `moving`。
- `save-to-project` 只处理 `items`，并保存为 `moving_items` / `AI生成的物品清单`。

建议替换为：

- 识别“配置方案/户型推荐/38㎡/56㎡/智能化/空间模块”等为 `space_configuration`。
- 识别“交付/阶段/验收/吊装/运输/调试/风险”等为 `delivery_planning`。
- 默认可走空间配置 Agent，避免用户未明确关键词时进入旧搬家逻辑。
- 保存时同时写入 `Project.requirements`、配置清单、示例预算类别、交付阶段。

### 3.3 RAG

`backend/app/rag/knowledge_base.py` 当前默认知识为：

- 搬家准备、搬家打包、搬家安全。
- 装修水电、防水、木工、油漆、装修预算。

应替换为 6-10 条卡素产品与装配式交付知识：

- Capsule Cabin S / M 产品规格。
- 工厂预制、运输、现场吊装、拼接、调试、验收。
- 滨海防腐、防水、通风、设备保护。
- 智能门锁、照明、空调控制、烟感/水浸、网络预留。
- 现场基础、道路运输、吊装空间需专业确认。
- PoC 边界：不替代结构、消防、施工和报价确认。

### 3.4 前端

`frontend/src/views/Home.vue` 当前旧内容：

- MoveRenovateAI 搬家/装修规划助手。
- 搬家规划、装修规划、知识问答三张功能卡。
- 最近项目以搬家/装修显示。

应替换为：

- 卡素民宿真实案例 + 回溯式 AI PoC。
- 38㎡ Capsule Cabin S 与 56㎡ Capsule Cabin M 产品卡。
- PoC 声明：不替代专业设计与工程管理。
- 使用 `assets/capsule_cabin/` 下项目图片。

`frontend/src/views/AIChat.vue` 当前旧内容：

- 标题“搬家/装修规划助手”。
- 北京朝阳到海淀搬家、新房装修、旧房翻新快捷模板。
- 搬家清单卡：物品数、箱数、预算。
- 装修方案卡：户型、面积、风格、预算。

应替换为：

- 标题“卡素民宿 AI 配置与交付规划 Agent”。
- 指导文档指定的 4 条快捷模板。
- 空间配置方案卡：推荐产品、面积、空间模块、智能设备、预算区间说明。
- 交付规划卡：阶段数、验收点、风险提示。

`frontend/src/views/Projects.vue` 当前旧内容：

- 标签：全部 / 搬家 / 装修。
- 新建项目类型：搬家 / 装修。
- 列表展示金额为“元”。

应替换为：

- 民宿配置项目列表。
- 标签可改为：全部 / 配置方案 / 交付规划，或保留全部并弱化类型筛选。
- 新建项目默认使用 `capsule_cabin` 或 `homestay_config` 项目类型。
- 预算展示改为“示例预算区间”。

`frontend/src/views/ProjectDetail.vue` 当前旧内容：

- 项目类型显示搬家/装修。
- 仅展示基础信息与清单进度。

应扩展展示：

- 推荐产品：38㎡ / 56㎡。
- 空间模块。
- 配置清单。
- 智能设备建议。
- 示例配置预算区间。
- 交付阶段、任务、验收点。
- 风险提示。
- PoC 免责声明。

## 4. 最小改造文件列表

### 4.1 第一批建议改造

这些文件覆盖指导文档要求的最小闭环：

- `frontend/src/views/Home.vue`
- `frontend/src/views/AIChat.vue`
- `frontend/src/views/Projects.vue`
- `frontend/src/views/ProjectDetail.vue`
- `backend/app/agent/state.py`
- `backend/app/agent/renovating_agent/nodes.py`
- `backend/app/agent/renovating_agent/graph.py`
- `backend/app/agent/moving_agent/nodes.py`
- `backend/app/agent/moving_agent/graph.py`
- `backend/app/api/agent.py`
- `backend/app/api/projects.py`
- `backend/app/rag/knowledge_base.py`
- `backend/app/main.py`

### 4.2 新增文件与目录

- `backend/data/demo_capsule_cabin.json`
- `assets/capsule_cabin/`
- `portfolio_assets/capsule_cabin_agent/01_case_background.md`
- `portfolio_assets/capsule_cabin_agent/02_problem_solution.md`
- `portfolio_assets/capsule_cabin_agent/03_agent_workflow.md`
- `portfolio_assets/capsule_cabin_agent/04_system_architecture.md`
- `portfolio_assets/capsule_cabin_agent/05_demo_case.md`
- `portfolio_assets/capsule_cabin_agent/06_capability_boundary.md`
- `portfolio_assets/capsule_cabin_agent/07_resume_bullets.md`
- `portfolio_assets/capsule_cabin_agent/demo_script.md`
- `portfolio_assets/capsule_cabin_agent/screenshots/`

### 4.3 暂不建议改动

- 暂不重命名 `moving_agent/` 与 `renovating_agent/` 目录，避免扩大导入影响。
- 暂不重构 Docker、Redis、PostgreSQL。
- 暂不新增复杂多 Agent、复杂 RAG、BIM/CAD/地图/支付/订单/多租户能力。
- 暂不新增数据库字段，优先使用 `Project.requirements` JSON 保存产品型号、客群、运营方式、智能化等级、场地条件等。

## 5. 可能的运行风险

### 5.1 环境风险

- 当前本机 Python 环境未安装项目完整依赖，至少缺 `langgraph`，且 SQLAlchemy 版本不匹配。
- 前端依赖未安装，需 `npm install` 后才能构建或启动。
- 没有 `.env` 与 LLM API Key 时，Agent 无法真实调用模型。
- RAG 默认使用 Embeddings，缺 API Key 时知识库初始化可能失败。

### 5.2 SQLite 兼容风险

- ORM 模型使用 `sqlalchemy.dialects.postgresql.UUID`。指导文档要求优先使用 SQLite 跑通本地最小闭环，但该类型在 SQLite 下可能存在编译或运行兼容风险，需要在依赖安装后实际启动验证。
- 如果 SQLite 不兼容 PostgreSQL UUID 类型，最小修复方向是引入跨数据库 UUID 类型装饰器，或在 Demo 环境临时改为字符串 UUID；这属于运行修复，不建议扩大为数据库重构。

### 5.3 API 鉴权风险

- 当前 `projects.py`、`agent.py` 未正确使用 `OAuth2PasswordBearer` 或 Header 解析 token。
- 前端虽然设置了 `Authorization: Bearer ${token}`，后端接口却可能拿不到 token。
- 这会直接影响项目列表、对话、保存方案等闭环，需要在正式改造时优先修复。

### 5.4 数据保存风险

- 当前 `save-to-project` 只保存搬家物品清单，不保存装修方案、阶段、预算、风险。
- 项目详情 API 当前只返回清单，不返回 `requirements`、`budgets`、`phases`，会导致详情页无法展示完整方案。
- 需要补齐保存与读取结构，否则前端只能展示对话中的临时结果，不能形成项目档案闭环。

### 5.5 业务边界风险

- 旧代码里存在真实金额式预算估算、搬家费用估算、材料采购建议等表达。改造时必须全部替换为“示例配置预算区间，非正式报价”。
- 不能写成“卡素民宿建设时已使用 AI Agent”。
- 不能写成“AI 自动完成建筑设计、施工图、工程交付”。
- 不能伪造客户、合同、供应商、项目进度、真实报价。

### 5.6 素材风险

- `CAPSULE CABIN/` 下已有图片素材，但使用前需要检查是否包含客户、地址、联系方式、报价或其他不宜公开信息。
- 指导文档要求的 `assets/capsule_cabin/` 目录尚未创建，后续应建立并放入脱敏后的展示素材。

## 6. 建议的确认后执行顺序

确认后建议按以下顺序实施，保持最小闭环：

1. 修复本地运行基础：安装后端依赖、前端依赖，确认 SQLite 或必要兼容修复。
2. 修复 API 鉴权，让登录后的项目、对话、保存接口可用。
3. 新增 `backend/data/demo_capsule_cabin.json`。
4. 建立 `assets/capsule_cabin/`，从现有素材中筛选并命名展示图片。
5. 改造 `renovating_agent` 为“空间配置 Agent”。
6. 改造 `moving_agent` 为“交付规划 Agent”。
7. 改造 `agent.py` 的意图识别与保存到项目逻辑。
8. 改造 `projects.py`，返回详情页所需的 requirements、checklists、budgets、phases。
9. 改造前端四个页面。
10. 替换 RAG 默认知识。
11. 使用 SQLite 跑通：输入需求 → 生成配置 → 生成交付计划 → 保存项目 → 项目详情展示。
12. 输出作品集文档与截图。

## 7. 本阶段结论

当前仓库非常适合按指导文档做“最小语义替换”：

- 不需要新建系统。
- 不需要重构前后端框架。
- 不需要新增复杂数据库模型。
- 两个现有 Agent 的 LangGraph 骨架可以直接复用。
- `Project.requirements` 已经提供了保存民宿配置字段的低成本落点。

主要风险不在业务改造复杂度，而在本地运行基础：

- 依赖环境未就绪。
- 鉴权 token 获取方式需要修复。
- SQLite 与 PostgreSQL UUID 类型需实际验证。
- 保存项目与详情读取链路需要补齐。

建议得到确认后，先处理运行闭环和鉴权，再进入页面与 Agent 业务语义替换。
