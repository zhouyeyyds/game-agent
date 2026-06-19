# Runtime Protocol

## Game Manifest v1

Play 页面通过 `GET /api/games/{gameId}/play` 获取 manifest URL，再 fetch manifest。

```json
{
  "schemaVersion": "game-manifest-v1",
  "gameId": "...",
  "versionId": "...",
  "title": "...",
  "entry": "index.html",
  "entryUrl": "http://192.168.150.101:19000/game-agent/games/.../index.html",
  "assets": [],
  "permissions": {
    "network": false,
    "storage": false
  }
}
```

## iframe sandbox

Generated games run inside:

```html
<iframe sandbox="allow-scripts"></iframe>
```

## postMessage

Game to parent:

```json
{ "type": "game.ready" }
{ "type": "game.completed", "result": "win", "durationMs": 1000 }
{ "type": "game.error", "message": "..." }
```

Parent to game:

```json
{ "type": "game.restart" }
```
