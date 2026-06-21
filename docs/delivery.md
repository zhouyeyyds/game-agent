# 交付清单

## 必交项

| 提交项 | 状态 | 说明 |
| --- | --- | --- |
| 源码仓库 | 已完成 | GitHub remote：`https://github.com/zhouyeyyds/game-agent.git`；当前仓库已有 18 次提交。 |
| Demo 地址 | 本地演示 | 前端 `http://localhost:5173`，后端 `http://localhost:18000`；当前未配置线上地址。 |
| 启动命令 | 已完成 | 见 README 的“本地启动”和 [docs/demo-checklist.md](demo-checklist.md)。 |
| 测试数据 | 已完成 | `uv run python -m app.db.seed` 会创建 demo 用户和两个已发布远端游戏；演示时可使用 [docs/prompt/game.txt](prompt/game.txt) 通过 Create 生成并发布至少一个游戏。 |
| 环境变量 | 已完成 | `.env.example` 列出前端、后端、GitHub OAuth、MySQL、MinIO、LLM 等变量，不包含真实密钥。 |
| 系统设计文档 | 已完成 | [docs/architecture.md](architecture.md)、[docs/runtime-protocol.md](runtime-protocol.md)。 |
| 技术栈 | 已完成 | README 的“技术栈”章节。 |
| 完成度说明 | 已完成 | README 的“完成度说明”章节；本文件下方也列出 demo 限制和后续迭代。 |
| 测试与验证证据 | 已完成 | 截图见 [docs/demo-assets.md](demo-assets.md)，包含登录、Home、Create 和 Play；演示视频见 [docs/video/AgentPlay演示视频.mp4](video/AgentPlay演示视频.mp4)。 |
| 演示视频 | 已完成 | [docs/video/AgentPlay演示视频.mp4](video/AgentPlay演示视频.mp4)，覆盖登录、Create、发布、Home 和 Play。 |
| AI 协作记录 | 已完成 | 测试生成提示词见 [docs/prompt/game.txt](prompt/game.txt)，可用于复现 Create 生成链路。 |

## 启动命令

从仓库根目录执行：

```bash
cp .env.example .env
docker compose up -d mysql minio
```

后端：

```bash
cd apps/api
uv sync
uv run python -m app.db.seed
uv run fastapi dev app/main.py --host 0.0.0.0 --port 18000
```

前端：

```bash
pnpm install
pnpm dev:web
```

## 测试数据说明

seed 脚本：

```bash
cd apps/api
uv run python -m app.db.seed
```

会创建：

- 用户：`demo@example.com / password123`
- 已发布游戏：
  - `Neon Robot Mystery`
  - `Forest Rune Quest`
- MinIO 远端产物：
  - `games/{gameId}/versions/1/index.html`
  - `games/{gameId}/versions/1/game.js`
  - `games/{gameId}/versions/1/styles.css`
  - `games/{gameId}/versions/1/manifest.json`

为了满足“至少 3 个示例游戏，其中至少 1 个由 Create 流程生成并发布”的要求，演示步骤如下：

1. 启动 MySQL、MinIO、后端和前端。
2. 使用 `demo@example.com` 登录。
3. 打开 `/create`。
4. 输入创意并可选上传素材；可直接使用 [docs/prompt/game.txt](prompt/game.txt) 中的测试提示词。
5. 等待任务生成成功。
6. 预览并发布。
7. 回到 Home，确认新生成游戏出现在首页。

## 演示资产

- 演示视频：[docs/video/AgentPlay演示视频.mp4](video/AgentPlay演示视频.mp4)。
- 界面截图：[docs/demo-assets.md](demo-assets.md) 汇总登录、Home、Create、Play 的截图路径和说明。
- 测试提示词：[docs/prompt/game.txt](prompt/game.txt)，包含“霓虹躲避球”和“森林符文解谜”两组生成游戏提示词。

## 已交付能力

- Auth：邮箱注册、邮箱登录、退出、session 恢复、受保护 Create 路由、GitHub OAuth、Google 计划入口。
- Home：已发布游戏从 API/数据库加载。
- Play：远端 manifest fetch、iframe runtime、运行时元信息、manifest/iframe 埋点。
- Create：创意输入、素材上传、生成任务生命周期、Agent 日志、重试、取消、删除、预览、发布、下架、任务历史发布状态、生成成本指标。
- Agent：LangGraph 节点包括创意分析、素材解释、玩法设计、代码生成、安全扫描、修复、上传、结束。
- Storage：上传素材和生成游戏都存储在 MinIO。
- Observability：`request_id`、telemetry 事件、token/调用/费用指标、Agent 日志。

## Mock、Demo 限制和已知问题

- Demo 地址目前是本地地址；如需线上演示，需要额外部署。
- seed 游戏是确定性 demo bundle；真实 Create 生成依赖可用的 `LLM_API_KEY`。
- Google OAuth 未做真实 callback；UI 和 API 会明确提示未接入。
- GitHub OAuth 不持久化 provider access token。
- 后台生成使用 FastAPI `BackgroundTasks`，适合 demo，但进程重启时不具备持久化任务保障。
- 数据库升级使用轻量 `create_all + ensure_runtime_schema`，生产环境建议迁移到 Alembic。
- 运行时隔离依赖浏览器 iframe sandbox；生产环境建议增加独立静态资源域名和 CSP。
- Play 侧相关游戏、评分、部分资源大小展示仍是展示性数据。

## 如果再给一周的迭代计划

- 部署线上 Demo，使用 HTTPS、托管数据库和 S3-compatible 对象存储。
- 将生成任务迁移到持久化 worker 队列。
- 引入 Alembic migration 和后台管理/审核页面。
- 增强生成产物审核和安全校验。
- 实现 Google OAuth callback。
- 增加 Play 推荐、搜索、标签筛选、评分和收藏接口。
- 增加视频/PDF/DOCX 内容抽取和可选多模态模型调用。


