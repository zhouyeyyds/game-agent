# 远端产物协议

## Game Manifest v1

Play 页面会先调用 `GET /api/games/{gameId}/play` 获取 play descriptor。descriptor 中包含 `manifestUrl`，前端随后从 MinIO 或其他 S3-compatible 对象存储拉取远端 manifest。

manifest 示例：

```json
{
  "schemaVersion": "game-manifest-v1",
  "gameId": "...",
  "versionId": "...",
  "title": "...",
  "entry": "index.html",
  "entryUrl": "http://${VM_HOST}:19000/game-agent/games/.../index.html",
  "assets": [],
  "permissions": {
    "network": false,
    "storage": false
  }
}
```

后端返回的 play descriptor 示例：

```json
{
  "gameId": "...",
  "title": "...",
  "runtime": "iframe_manifest_v1",
  "manifestUrl": "http://${VM_HOST}:19000/game-agent/games/.../manifest.json",
  "storagePrefix": "games/.../versions/...",
  "sandbox": {
    "allowScripts": true,
    "allowSameOrigin": false,
    "allowForms": false,
    "allowPopups": false
  }
}
```

## iframe 沙箱

生成游戏在以下 iframe 中运行：

```html
<iframe sandbox="allow-scripts"></iframe>
```

当前运行时刻意不启用 `allow-same-origin`、`allow-forms`、`allow-popups`，避免生成代码获得更高浏览器权限。

## postMessage 协议

游戏向父页面发送：

```json
{ "type": "game.ready" }
{ "type": "game.completed", "result": "win", "durationMs": 1000 }
{ "type": "game.error", "message": "..." }
```

父页面向游戏发送：

```json
{ "type": "game.restart" }
```

## Play 埋点

Play 页面会上报：

```text
manifest_fetch_start
manifest_fetch_success
manifest_fetch_failed
iframe_ready
game_completed
iframe_error
play_restart
play_fullscreen
```

这些事件会发送到 `POST /api/telemetry/events`，payload 中包含 `gameId`、manifest URL、加载耗时、iframe 消息内容或错误详情。
