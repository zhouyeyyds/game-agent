# PromptPlay AI

AI Native 互动游戏平台 MVP。玩家从 Home 发现并游玩远端 HTML5 游戏；创作者后续可在 Create 页面通过 Agent 生成、预览并发布游戏。

## 技术栈

- 前端：Vue 3 + Vite + TypeScript + Vue Router + Pinia + Naive UI + Tailwind CSS
- 后端：FastAPI + SQLAlchemy + MySQL
- 对象存储：MinIO
- Agent 规划：LangGraph + GameSpec + 模板渲染

## 当前进度

已完成第一阶段骨架：

- Monorepo 目录结构
- Docker Compose：MySQL + MinIO
- FastAPI 配置、数据库、MinIO、Auth、Games、Health 基础接口
- Vue app shell、Home、Login、Register、Create 占位、Play 远端 iframe runtime
- Seed 脚本可创建 demo 用户和 2 个远端示例游戏

## 本地启动

1. 复制环境变量：

```bash
cp .env.example .env
```

2. 启动依赖：

```bash
docker compose up -d mysql minio
```

为避免和你已有虚拟机/本机服务冲突，本项目默认端口改为：

```text
MySQL: 192.168.150.101:13306 -> container 3306
MinIO API: http://192.168.150.101:19000 -> container 9000
MinIO Console: http://192.168.150.101:19001 -> container 9001
FastAPI: http://localhost:18000
Vite: http://localhost:5173
```

3. 安装并启动后端：

```bash
cd apps/api
uv sync
uv run python -m app.db.seed
uv run fastapi dev app/main.py --host 0.0.0.0 --port 18000
```

4. 安装并启动前端：

```bash
pnpm install
pnpm dev:web
```

默认账号：

```text
demo@example.com / password123
```

MinIO 控制台：

```text
http://192.168.150.101:19001
game_agent_minio / game_agent_minio_password
```

## 关键接口

- `GET /health`
- `GET /ready`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET /api/games?status=published`
- `GET /api/games/{game_id}/play`
