# 演示资产

本目录记录本地验收时使用的视频、截图和生成提示词，方便复现演示链路并作为交付证据。

## 演示视频

- [AgentPlay演示视频.mp4](video/AgentPlay演示视频.mp4)：覆盖登录、Create 生成、发布、Home 展示和 Play 游玩主流程。

## 界面截图

| 文件 | 说明 |
| --- | --- |
| [img/login.png](img/login.png) | 登录页，展示邮箱登录、注册切换和第三方登录入口。 |
| [img/home.png](img/home.png) | Home 工作台，展示已发布游戏列表、搜索、标签筛选和进入 Create/Play 的入口。 |
| [img/create1.png](img/create1.png) | Create 初始页，展示创意输入和素材上传区域。 |
| [img/create2.png](img/create2.png) | Create 生成流程页，展示任务进度、Agent 步骤和日志。 |
| [img/create3.png](img/create3.png) | Create 结果页，展示生成完成后的预览、发布和任务指标。 |
| [img/create4.png](img/create4.png) | Create 任务历史页，展示已生成/已发布任务的管理状态。 |
| [img/play1.png](img/play1.png) | Play 页面，展示远端游戏 iframe 运行效果和运行时信息。 |
| [img/play2.png](img/play2.png) | Play 页面交互状态，展示重新开始、全屏或运行反馈等操作。 |

所有截图分辨率为 `1910x925`，来自本地演示环境。

## 生成游戏提示词

- [prompt/game.txt](prompt/game.txt)：包含两组测试用游戏生成提示词：
  - 霓虹躲避球
  - 森林符文解谜

这些提示词可在 Create 页直接粘贴使用，用于验证 Agent 是否能生成包含 `index.html`、`styles.css`、`game.js` 的完整 HTML5 游戏包，并发布到 MinIO 远端产物路径。

## 推荐验收顺序

1. 使用 `demo@example.com / password123` 登录。
2. 参考 [prompt/game.txt](prompt/game.txt) 中任意一组提示词，在 Create 页提交生成任务。
3. 等待任务成功后预览并发布。
4. 回到 Home，确认新游戏出现在已发布游戏列表。
5. 打开 Play，确认页面动态拉取 manifest 并在 iframe 中运行游戏。
6. 对照截图和演示视频确认 UI、流程和埋点证据。
