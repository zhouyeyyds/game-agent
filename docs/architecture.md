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
- Agent 生成结构化静态 Web 游戏文件包，后端校验后上传到 MinIO。
- 当前产物协议为 `generated-game-bundle-v1`：`index.html`、`game.js`、`styles.css` 和可选 `data/*.json`。

## LangGraph 生成链路

Create 页面提交 `ideaText` 和素材 ID 后，后端创建 `GenerationTask`，再由后台任务执行
LangGraph。当前图节点如下：

```text
idea_analyzer
  -> asset_interpreter
  -> game_designer
  -> code_generation_agent
  -> bundle_security_scan
  -> repair_bundle, 条件重试
  -> upload
  -> finalizer
```

- `idea_analyzer` 提取创意摘要、玩法类型、场景、难度，并加载任务关联素材。
- `asset_interpreter` 将上传素材整理成 LLM 可用的引用上下文。
- `game_designer` 生成静态 Web 游戏包约束、目标玩法、文件限制和安全边界。
- `code_generation_agent` 调用真实 LLM 生成 `generated-game-bundle-v1` JSON。
- `bundle_security_scan` 使用 Pydantic 和规则扫描校验文件路径、文件大小和危险 API。
- `repair_bundle` 在校验失败时调用模型修复 JSON，最多重试 `AGENT_MAX_REPAIR_ATTEMPTS` 次。
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

没有可用 `LLM_API_KEY` 时，生成任务会失败并写入配置错误日志。系统不再提供 mock 生成 fallback。
`code_generation_agent` 会根据 `creatorIdea`、`requirementProfile`、素材上下文和设计约束生成完整静态游戏包。

## 游戏产物形态

模型返回结构化文件包 JSON：

```text
GeneratedGameBundle
  -> title / description / tags
  -> entry = index.html
  -> permissions = network false, storage false, externalScripts false
  -> files[]
     -> index.html
     -> game.js
     -> styles.css
     -> data/*.json, optional
```

后端只接受严格静态包：禁止外链、网络请求、浏览器存储、`eval`、动态 import、
`iframe/object/embed` 等危险能力。Play 仍通过 sandbox iframe 加载远端 `index.html`。
