# PromptPlay AI

PromptPlay AI 是一个 AI Native 互动游戏平台 MVP。玩家可以在首页浏览已发布游戏，并在 Play 页面运行远端 HTML5 游戏产物；创作者登录后可以在 Create 页面提交创意和素材，通过 LangGraph Agent 流程生成游戏、预览并发布回首页。

## 交付材料

- 源码仓库：https://github.com/zhouyeyyds/game-agent
- Demo 地址：本地演示，`http://localhost:5173`
- 交付清单：[docs/delivery.md](docs/delivery.md)
- 系统设计文档：[docs/architecture.md](docs/architecture.md)
- 远端产物协议：[docs/runtime-protocol.md](docs/runtime-protocol.md)
- 演示检查清单：[docs/demo-checklist.md](docs/demo-checklist.md)

## 技术栈

- 前端：Vue 3、Vite、TypeScript、Vue Router、Pinia、Element Plus、Tailwind CSS。
- 后端：FastAPI、SQLAlchemy、Pydantic、MySQL。
- 对象存储：MinIO，兼容 S3 API。
- Agent 流程：LangGraph、OpenAI-compatible Chat Completion API、结构化 JSON 游戏包生成。
- 运行时：远端 manifest + sandbox iframe，协议为 `game-manifest-v1`。
- 认证：邮箱密码登录，httpOnly JWT Cookie session；GitHub OAuth 演示链路；Google OAuth 保留为计划入口。
- 可观测性：`request_id`、telemetry 事件、Agent 日志、任务 token/调用/费用指标。
- 本地部署：Docker Compose 启动 MySQL 和 MinIO；FastAPI 与 Vite 本地运行。

## 本地启动

复制环境变量：

```bash
cp .env.example .env
```

启动数据库和对象存储：

```bash
docker compose up -d mysql minio
```

安装并启动后端：

```bash
cd apps/api
uv sync
uv run python -m app.db.seed
uv run fastapi dev app/main.py --host 0.0.0.0 --port 18000
```

从仓库根目录安装并启动前端：

```bash
pnpm install
pnpm dev:web
```

本地访问地址：

```text
前端: http://localhost:5173
后端 FastAPI: http://localhost:18000
MySQL: 127.0.0.1:13306 -> container 3306
MinIO API: http://192.168.150.101:19000
MinIO Console: http://192.168.150.101:19001
```

演示账号：

```text
demo@example.com / password123
```

MinIO 控制台账号：

```text
game_agent_minio / game_agent_minio_password
```

## 测试数据

MySQL 和 MinIO 就绪后执行 seed：

```bash
cd apps/api
uv run python -m app.db.seed
```

seed 会创建：

- 演示用户：`demo@example.com / password123`。
- 两个已发布远端示例游戏：`Neon Robot Mystery`、`Forest Rune Quest`。
- MinIO 中的远端产物：`games/{gameId}/versions/1/index.html`、`game.js`、`styles.css`、`manifest.json`。

交付要求中需要至少 3 个示例游戏，并且至少 1 个来自 Create 流程。演示时请登录 demo 账号，在 Create 页面生成并发布一个新游戏；该流程会写入 `games`、`game_versions`、`generation_tasks`、`agent_logs`，并上传游戏产物到 MinIO。

## 环境变量

`.env.example` 已列出需要的变量名和本地默认值，不提交真实密钥。

变量分组：

- 前端：`VITE_API_BASE_URL`
- API/运行时：`APP_ENV`、`API_HOST`、`API_PORT`、`FRONTEND_ORIGIN`
- 认证：`JWT_SECRET`、`JWT_COOKIE_NAME`
- GitHub OAuth：`GITHUB_OAUTH_CLIENT_ID`、`GITHUB_OAUTH_CLIENT_SECRET`、`GITHUB_OAUTH_CALLBACK_URL`
- 数据库：`MYSQL_*`、`DATABASE_URL`
- 对象存储：`MINIO_*`
- LLM/Agent：`LLM_PROVIDER`、`LLM_BASE_URL`、`LLM_API_KEY`、`LLM_MODEL`、`LLM_TEMPERATURE`、`LLM_TIMEOUT_SECONDS`、`LLM_MAX_RETRIES`、`LLM_INPUT_COST_PER_1M_TOKENS`、`LLM_OUTPUT_COST_PER_1M_TOKENS`、`AGENT_MAX_REPAIR_ATTEMPTS`

GitHub OAuth 本地回调地址：

```text
http://localhost:18000/api/auth/oauth/github/callback
```

## 核心接口

```text
GET  /health
GET  /ready
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
GET  /api/auth/oauth/providers
GET  /api/auth/oauth/github/start?redirect=/create
GET  /api/games?status=published
GET  /api/games/{game_id}/play
POST /api/assets
POST /api/generation-tasks
GET  /api/generation-tasks
GET  /api/generation-tasks/{task_id}
GET  /api/generation-tasks/{task_id}/logs
POST /api/generation-tasks/{task_id}/publish
POST /api/telemetry/events
```

## 测试与验证

后端测试：

```powershell
cd apps/api
$env:PYTHONPATH='.'
uv run pytest
```

前端构建：

```bash
pnpm build:web
```

最近一次本地验证：

- `uv run pytest`：35 passed。
- `pnpm build:web`：通过。

## 完成度说明

已完成：

- 邮箱注册、邮箱登录、退出登录和受保护 Create 路由。
- GitHub OAuth 授权回调和账号绑定；Google 入口明确提示 demo 阶段未接入。
- Home 从后端/数据库读取已发布游戏。
- Play 动态拉取 manifest，并在 sandbox iframe 中运行远端生成文件。
- Create 支持创意输入、素材上传、任务历史、Agent 日志、重试、取消、删除、预览、发布、下架和发布状态展示。
- LLM 驱动的生成流程可以输出静态 HTML/CSS/JS 游戏包并上传到 MinIO。
- 已实现 `request_id`、用户操作埋点、manifest/iframe 埋点、token/调用次数/费用统计。
- 已补齐架构、运行协议、交付清单和演示清单文档。

Mock 或 demo 限制：

- 当前没有线上 Demo URL，演示方式为本地启动。
- seed 游戏是确定性的 demo bundle；验收要求中的 Create 生成游戏需要演示时通过 Create 流程生成并发布。
- Google OAuth 只保留计划入口。
- 生成任务使用 FastAPI `BackgroundTasks`，生产环境建议迁移到持久化 worker 队列。
- 上传素材目前传给 Agent 的主要是元信息和 URL，暂未做视频/PDF/DOCX 深度内容解析。

