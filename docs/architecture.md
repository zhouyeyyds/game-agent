# Architecture

PromptPlay AI 采用前后端分离架构：

```text
Vue 3 + Vite Web
  -> FastAPI API
  -> MySQL metadata
  -> MinIO game artifacts
  -> LangGraph generation pipeline
```

## 核心边界

- MySQL 保存用户、游戏元信息、版本、生成任务和 Agent 日志。
- MinIO 保存上传素材和生成后的游戏 bundle。
- Play 页面只根据后端返回的 manifest URL 加载远端游戏，不硬编码本地游戏组件。
- Agent 只生成结构化 GameSpec，平台模板渲染 HTML/CSS/JS。

## LangGraph 生成链路

Create 页面提交 `ideaText` 和素材 ID 后，后端创建 `GenerationTask`，再由后台任务执行
LangGraph。当前图节点如下：

```text
idea_analyzer
  -> asset_interpreter
  -> game_designer
  -> spec_writer
  -> spec_reviewer
  -> repair_spec, 条件重试
  -> render
  -> upload
  -> finalizer
```

- `idea_analyzer` 提取创意摘要，并加载任务关联素材。
- `asset_interpreter` 将上传素材整理成 Agent 可用的引用上下文。
- `game_designer` 生成玩法结构约束，明确场景、结局和可达性要求。
- `spec_writer` 调用模型生成 `game-spec-v1` JSON；`LLM_PROVIDER=mock` 时生成本地 mock spec。
- `spec_reviewer` 使用 Pydantic `GameSpec` 做硬校验。
- `repair_spec` 在校验失败时调用模型修复 JSON，最多重试 `AGENT_MAX_REPAIR_ATTEMPTS` 次。
- `render` 将通过校验的 `GameSpec` 渲染为静态 `index.html/game.js/styles.css/spec.json`。
- `upload` 上传 bundle 和 `manifest.json` 到 MinIO，并写入 `GameVersion`。
- `finalizer` 标记任务成功，前端即可预览和发布。

每个节点都会写入 `AgentLog`，用于 Create 页面展示可读的 Agent 执行过程。

## 模型配置

后端支持 OpenAI 兼容接口，不绑定固定供应商：

```env
LLM_PROVIDER=openai_compatible
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=
LLM_MODEL=gpt-4.1-mini
LLM_TEMPERATURE=0.4
LLM_TIMEOUT_SECONDS=60
LLM_MAX_RETRIES=2
AGENT_MAX_REPAIR_ATTEMPTS=2
```

本地无密钥演示时可以保留：

```env
LLM_PROVIDER=mock
```

mock 模式仍会走完整 LangGraph 节点、任务状态、Agent 日志、渲染、上传和发布闭环，只是不调用远程模型。
