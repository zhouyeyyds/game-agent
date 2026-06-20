# 演示检查清单

## 启动

1. 复制环境变量：`cp .env.example .env`。
2. 启动依赖：`docker compose up -d mysql minio`。
3. 初始化测试数据：`cd apps/api && uv run python -m app.db.seed`。
4. 启动后端：`uv run fastapi dev app/main.py --host 0.0.0.0 --port 18000`。
5. 从仓库根目录启动前端：`pnpm dev:web`。

## 玩家流程

1. 打开 `http://localhost:5173`。
2. 确认 Home 调用 `GET /api/games?status=published`。
3. 确认游戏卡片展示标题、简介、作者、标签、发布时间和 Play 入口。
4. 点击任意游戏。
5. 确认 Play 调用 `GET /api/games/{gameId}/play`。
6. 确认 Play 根据 `manifestUrl` 从对象存储拉取远端 manifest。
7. 展示 Runtime Info 面板中的 manifest URL 和 storage prefix。
8. 点击重新开始、全屏，确认 iframe 游戏仍可运行。

## 创作者流程

1. 使用 `demo@example.com / password123` 登录。
2. 打开 Create 页面。
3. 可选上传图片或文件素材。
4. 输入创意并提交。
5. 观察任务状态、工作流进度、Agent 日志和资源消耗指标。
6. 等待生成成功，预览生成游戏。
7. 发布游戏。
8. 回到 Home，确认新生成游戏已展示。
9. 从 Home 打开新游戏，确认 Play 可以运行。
10. 回到 Create，确认任务历史中显示发布状态。

## OAuth 演示

1. 配置 GitHub OAuth App callback URL：

   ```text
   http://localhost:18000/api/auth/oauth/github/callback
   ```

2. 在 `.env` 中设置：

   ```env
   GITHUB_OAUTH_CLIENT_ID=...
   GITHUB_OAUTH_CLIENT_SECRET=...
   ```

3. 重启后端。
4. 点击 GitHub 登录，确认授权回调后进入 `/create`。
5. 点击 Google，确认界面提示 demo 阶段未接入。

## 可展示证据

- MinIO 控制台存在 `games/.../manifest.json`、`index.html`、`game.js`、`styles.css`。
- SQL 查询已发布游戏：

  ```sql
  SELECT title, status, published_at FROM games ORDER BY published_at DESC;
  ```

- SQL 查询任务指标：

  ```sql
  SELECT status, model_call_count, total_tokens, estimated_cost_usd
  FROM generation_tasks
  ORDER BY created_at DESC
  LIMIT 5;
  ```

- SQL 查询埋点事件：

  ```sql
  SELECT event_type, entity_type, entity_id, created_at
  FROM telemetry_events
  ORDER BY created_at DESC
  LIMIT 20;
  ```

