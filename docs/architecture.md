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
