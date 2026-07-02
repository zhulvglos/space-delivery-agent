# 部署到公网 Demo

本项目已支持单服务部署：Render 会构建前端静态文件，再由 FastAPI 同时提供页面和 API。

## Render Blueprint

1. 打开 Render。
2. New -> Blueprint。
3. 选择 GitHub 仓库 `zhulvglos/space-delivery-agent`。
4. Render 会读取根目录 `render.yaml` 并创建 `space-delivery-agent` Web Service。
5. 部署完成后，Render 生成的服务 URL 就是简历可放置的 Demo 地址。

## 访问路径

- 首页：`https://你的-render-url/`
- Agent 规划台：`https://你的-render-url/chat`
- API 文档：`https://你的-render-url/docs`
- 健康检查：`https://你的-render-url/health`

## 说明

- 默认使用 SQLite 和规则型 Demo，不需要 PostgreSQL、Redis 或 LLM Key。
- 未配置 LLM Key 时，空间配置与交付规划会走瑞泽·海项目复盘规则兜底。
- Render 免费服务可能会休眠，第一次打开可能需要等待 30-60 秒。
