<template>
  <main class="create-page" :class="{ 'create-page--idle': activeCreateView === CreateStartView }">
    <component
      :is="activeCreateView"
      v-if="activeCreateView === CreateStartView"
      v-model:idea="idea"
      :uploaded-assets="uploadedAssets"
      :tasks="tasks"
      :loading="loading"
      :history-loading="historyLoading"
      :canceling="canceling"
      :retrying="retrying"
      :can-generate="canGenerate"
      :is-image-asset="isImageAsset"
      :format-bytes="formatBytes"
      :format-task-title="formatTaskTitle"
      :format-task-time="formatTaskTime"
      :task-status-label="taskStatusLabel"
      :task-progress-for="taskProgressFor"
      :task-result-summary="taskResultSummary"
      :can-cancel-task="canCancelTask"
      :can-retry-task="canRetryTask"
      @optimize-description="fillInspiration"
      @generate="generate"
      @upload="handleUpload"
      @clear-assets="clearAssets"
      @remove-asset="removeAsset"
      @load-history="loadTaskHistory"
      @view-history-task="viewHistoryTask"
      @cancel-history-task="cancelHistoryTask"
      @retry-history-task="retryHistoryTask"
    />

    <component
      :is="activeCreateView"
      v-else-if="activeCreateView === CreateRunningView && currentTask"
      v-model:realtime-logs="realtimeLogs"
      :task="currentTask"
      :task-title="taskTitle"
      :task-tags="taskTags"
      :uploaded-assets="uploadedAssets"
      :workflow-steps="workflowSteps"
      :workflow-counts="workflowCounts"
      :current-workflow-step="currentWorkflowStep"
      :task-progress="taskProgress"
      :execution-cards="executionCards"
      :task-info-rows="taskInfoRows"
      :resource-rows="resourceRows"
      :artifact-cards="artifactCards"
      :canceling="canceling"
      :retrying="retrying"
      :is-image-asset="isImageAsset"
      :format-bytes="formatBytes"
      @cancel-current="cancelCurrent"
      @regenerate="regenerate"
      @copy="copyText"
    />

    <component
      :is="activeCreateView"
      v-else-if="activeCreateView === CreateSuccessView"
      v-model:publish-title="publishTitle"
      v-model:publish-description="publishDescription"
      :preview-manifest="previewManifest"
      :publish-tags="publishTags"
      :build-info-rows="buildInfoRows"
      :publishing="publishing"
      @back-to-edit="backToEdit"
      @regenerate="regenerate"
      @publish="publish"
      @copy="copyText"
    />

    <component
      :is="activeCreateView"
      v-else-if="currentTask"
      :status="currentTask.status"
      :title="terminalStateTitle"
      :message="terminalStateMessage"
      :retrying="retrying"
      @regenerate="regenerate"
      @back-to-edit="backToEdit"
    />
  </main>
</template>

<script setup lang="ts">
import {
  Aim,
  Box,
  Cloudy,
  Compass,
  DataLine,
  Document,
  Finished,
  Flag,
  MoreFilled,
  Picture,
  Promotion,
  User,
  VideoPlay,
  View,
  Wallet,
} from "@element-plus/icons-vue";
import { ElMessage, type UploadRequestOptions } from "element-plus";
import { storeToRefs } from "pinia";
import {
  computed,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
  type Component,
} from "vue";

import { uploadAsset, type AssetResponse } from "@/api/assets";
import type { AgentLogResponse, GenerationTaskResponse } from "@/api/tasks";
import type { GameManifest } from "@/api/types";
import CreateFailureView from "@/components/create/CreateFailureView.vue";
import CreateRunningView from "@/components/create/CreateRunningView.vue";
import CreateStartView from "@/components/create/CreateStartView.vue";
import CreateSuccessView from "@/components/create/CreateSuccessView.vue";
import { useCreateTaskStore } from "@/stores/createTask";

interface InfoRow {
  label: string;
  value: string;
  copy?: boolean;
}

interface InspirationItem {
  title: string;
  summary: string;
  prompt: string;
  icon: Component;
  className: string;
}

type WorkflowStepState = "done" | "running" | "failed" | "waiting";

const createTask = useCreateTaskStore();
const {
  currentTask,
  tasks,
  logs,
  loading,
  historyLoading,
  publishing,
  canceling,
  retrying,
  error,
} = storeToRefs(createTask);

const idea = ref("");
const uploadedAssets = ref<AssetResponse[]>([]);
const uploadingCount = ref(0);
const previewManifest = ref<GameManifest | null>(null);
const publishTitle = ref("迷雾之城：冥歌");
const publishDescription = ref(
  "在迷雾与诅咒笼罩的古城中探寻真相，你的选择将决定众人的命运。",
);
const publishTags = ref(["角色扮演", "剧情", "暗黑奇幻", "单机"]);
const inspirationOffset = ref(0);
const realtimeLogs = ref(true);

const taskTags = ["开放世界", "生存建造", "太空探索", "策略经营"];
const generationSteps = [
  {
    key: "idea",
    title: "需求解析",
    icon: Compass,
    description:
      "分析用户输入的创意描述与上传素材，提取核心玩法、世界观与关键要素。",
  },
  {
    key: "spec",
    title: "世界观/玩法设计",
    icon: Flag,
    description: "生成完整的世界观设定与核心玩法循环。",
  },
  {
    key: "render",
    title: "素材理解",
    icon: Picture,
    description: "理解并索引上传素材内容，提取角色设定与美术风格关键词。",
  },
  {
    key: "upload",
    title: "角色与场景生成",
    icon: VideoPlay,
    description:
      "根据世界观与玩法设计，生成角色设定与场景概念图，并输出可用资源。",
  },
  {
    key: "ready",
    title: "代码生成",
    icon: DataLine,
    description: "生成游戏逻辑、交互脚本和页面结构。",
  },
  {
    key: "build",
    title: "构建打包",
    icon: Box,
    description: "将项目构建为可运行版本并打包。",
  },
  {
    key: "storage",
    title: "上传对象存储",
    icon: Cloudy,
    description: "上传构建产物并生成访问地址。",
  },
  {
    key: "db",
    title: "写入数据库",
    icon: Finished,
    description: "保存元数据，等待写入数据库。",
  },
];
const inspirations: InspirationItem[] = [
  {
    title: "奇幻大陆冒险",
    summary: "探索未知大陆，收集遗失的神器",
    prompt:
      "做一个奇幻大陆冒险 RPG，玩家扮演年轻旅人，探索森林、遗迹和山谷，收集遗失神器并解开王国衰落之谜。",
    icon: Promotion,
    className: "violet",
  },
  {
    title: "赛博都市跑酷",
    summary: "在霓虹都市中穿梭，躲避追捕",
    prompt:
      "做一个赛博都市跑酷游戏，玩家需要躲避巡逻无人机，收集能量芯片，并在限定时间内抵达楼顶撤离点。",
    icon: Aim,
    className: "red",
  },
  {
    title: "像素农场物语",
    summary: "经营自己的农场，结识小镇居民",
    prompt:
      "做一个像素农场模拟经营游戏，玩家种植作物、照顾动物、升级农具，并通过节日事件与小镇居民建立关系。",
    icon: Box,
    className: "green",
  },
  {
    title: "末日生存挑战",
    summary: "在废土世界中生存，寻找物资",
    prompt:
      "做一个末日生存挑战游戏，玩家需要探索废弃城市、搜集水和食物、修复避难所，并防御夜间袭击。",
    icon: Wallet,
    className: "purple",
  },
  {
    title: "解谜密室逃脱",
    summary: "在神秘房间中解开机关",
    prompt:
      "做一个解谜密室逃脱游戏，玩家在古老宅邸中寻找线索，破解机关锁，逐步揭开家族秘密。",
    icon: View,
    className: "teal",
  },
];
const artifactCards = [
  { name: "角色设定图", status: "生成中", icon: User },
  { name: "场景概念图", status: "生成中", icon: Picture },
  { name: "游戏Logo", status: "等待中", icon: Aim },
  { name: "游戏Demo", status: "等待中", icon: VideoPlay },
  { name: "设计文档", status: "等待中", icon: Document },
  { name: "更多产物", status: "生成中", icon: MoreFilled },
];

const activeCreateView = computed(() => {
  if (!currentTask.value) return CreateStartView;
  if (
    currentTask.value.status === "pending" ||
    currentTask.value.status === "running"
  ) {
    return CreateRunningView;
  }
  if (currentTask.value.status === "succeeded") return CreateSuccessView;
  return CreateFailureView;
});

const canGenerate = computed(
  () =>
    idea.value.trim().length > 0 &&
    uploadingCount.value === 0 &&
    !loading.value,
);
const terminalStateTitle = computed(() =>
  currentTask.value?.status === "canceled" ? "任务已取消" : "任务失败",
);
const terminalStateMessage = computed(() => {
  if (currentTask.value?.status === "canceled") {
    return (
      currentTask.value.errorMessage ||
      "任务已按你的请求取消，可从历史列表重试。"
    );
  }
  return error.value || currentTask.value?.errorMessage || "任务失败，请重试。";
});
const visibleInspirations = computed<InspirationItem[]>(() => {
  const items: InspirationItem[] = [];
  for (let index = 0; index < 5; index += 1) {
    const item =
      inspirations[(inspirationOffset.value + index) % inspirations.length];
    if (item) items.push(item);
  }
  return items;
});
const taskTitle = computed(() => {
  const source =
    currentTask.value?.ideaText || idea.value || "星海漂流：文明重启";
  return source.length > 16 ? `${source.slice(0, 16)}...` : source;
});
const currentStepIndex = computed(() => {
  const index = generationSteps.findIndex(
    (step) => step.key === currentTask.value?.currentStep,
  );
  if (currentTask.value?.status === "succeeded")
    return generationSteps.length - 1;
  if (currentTask.value?.status === "canceled") return Math.max(0, index);
  if (currentTask.value?.status === "pending") return 0;
  return index >= 0 ? index : 3;
});
const taskProgress = computed(() => {
  if (currentTask.value?.status === "succeeded") return 100;
  if (currentTask.value?.status === "canceled")
    return Math.max(
      8,
      Math.round(((currentStepIndex.value + 1) / generationSteps.length) * 100),
    );
  if (currentTask.value?.status === "failed")
    return Math.max(
      12,
      Math.round(((currentStepIndex.value + 1) / generationSteps.length) * 100),
    );
  return Math.round(
    ((currentStepIndex.value + 1) / generationSteps.length) * 100,
  );
});
const workflowSteps = computed(() =>
  generationSteps.map((step, index) => {
    const state: WorkflowStepState =
      (currentTask.value?.status === "failed" ||
        currentTask.value?.status === "canceled") &&
      index === currentStepIndex.value
        ? "failed"
        : index < currentStepIndex.value
          ? "done"
          : index === currentStepIndex.value
            ? "running"
            : "waiting";
    return {
      ...step,
      state,
      label:
        state === "done"
          ? "已完成"
          : state === "running"
            ? "运行中"
            : state === "failed"
              ? "失败"
              : "等待中",
    };
  }),
);
const workflowCounts = computed(() => ({
  waiting: workflowSteps.value.filter((item) => item.state === "waiting")
    .length,
  running: workflowSteps.value.filter((item) => item.state === "running")
    .length,
  done: workflowSteps.value.filter((item) => item.state === "done").length,
  failed: workflowSteps.value.filter((item) => item.state === "failed").length,
}));
const currentWorkflowStep = computed(() =>
  workflowSteps.value.find((step) => step.state === "running"),
);
const executionCards = computed(() => {
  const fallback = generationSteps.slice(0, 6).map((step, index) => ({
    key: step.key,
    title: step.title,
    duration:
      index < currentStepIndex.value
        ? `00:0${index + 1}:${(32 + index * 11).toString().padStart(2, "0")}`
        : "",
    message: step.description,
    output:
      index < currentStepIndex.value
        ? `${step.title}结果`
        : index === currentStepIndex.value
          ? `${step.title}（中）`
          : "等待中",
    state:
      index < currentStepIndex.value
        ? "done"
        : index === currentStepIndex.value
          ? "running"
          : "waiting",
  }));

  if (logs.value.length === 0) return fallback;

  return logs.value.slice(0, 6).map((log: AgentLogResponse, index) => ({
    key: log.id,
    title: log.nodeName,
    duration: formatTime(log.createdAt),
    message: log.message,
    output: log.level === "error" ? "错误" : "查看输出",
    state: index === 0 ? "running" : "done",
  }));
});
const taskInfoRows = computed<InfoRow[]>(() => [
  {
    label: "任务状态",
    value: taskStatusLabel(currentTask.value?.status || "pending"),
  },
  { label: "任务 ID", value: currentTask.value?.id || "-", copy: true },
  {
    label: "创建时间",
    value: formatTaskTime(currentTask.value?.createdAt || null),
  },
  {
    label: "完成时间",
    value: formatTaskTime(currentTask.value?.finishedAt || null),
  },
  {
    label: "运行时长",
    value: currentTask.value ? taskDuration(currentTask.value) : "-",
  },
]);
const resourceRows = computed<InfoRow[]>(() => [
  { label: "总消耗", value: "1,240 积分" },
  { label: "Tokens 消耗", value: "3,245,678" },
  { label: "模型调用", value: "18 次" },
  { label: "智能体调用", value: "24 次" },
]);
const buildInfoRows = computed<InfoRow[]>(() => {
  const manifestUrl = currentTask.value?.result.manifestUrl || "-";
  const gameUrl = currentTask.value?.result.gameId
    ? `https://cdn.agentplay.com/games/${currentTask.value.result.gameId}/v1.0.0/index.html`
    : "-";
  return [
    { label: "版本号", value: "v1.0.0" },
    { label: "创建时间", value: "2024-06-12 16:42:58" },
    { label: "任务 ID", value: currentTask.value?.id || "-", copy: true },
    { label: "游戏地址（Game URL）", value: gameUrl, copy: true },
    { label: "Manifest URL", value: manifestUrl, copy: true },
    { label: "Bundle URL", value: deriveBundleUrl(manifestUrl), copy: true },
    {
      label: "发布状态",
      value: currentTask.value?.result.gameId ? "已发布" : "未发布",
    },
  ];
});

function isGameManifest(value: unknown): value is GameManifest {
  if (!value || typeof value !== "object") return false;
  const candidate = value as Partial<GameManifest>;
  return (
    candidate.schemaVersion === "game-manifest-v1" &&
    typeof candidate.entryUrl === "string" &&
    typeof candidate.title === "string"
  );
}

function isImageAsset(asset: AssetResponse) {
  return asset.contentType.startsWith("image/");
}

function formatBytes(value: number) {
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / 1024 / 1024).toFixed(1)} MB`;
}

function formatTime(value: string) {
  return new Date(value).toLocaleTimeString();
}

function formatTaskTime(value: string | null) {
  if (!value) return "-";
  return new Date(value).toLocaleString();
}

function taskStatusLabel(status: GenerationTaskResponse["status"]) {
  const labels: Record<GenerationTaskResponse["status"], string> = {
    pending: "等待中",
    running: "运行中",
    succeeded: "已完成",
    failed: "失败",
    canceled: "已取消",
  };
  return labels[status];
}

function taskStepIndex(task: GenerationTaskResponse) {
  const index = generationSteps.findIndex(
    (step) => step.key === task.currentStep,
  );
  if (task.status === "succeeded") return generationSteps.length - 1;
  if (task.status === "pending") return 0;
  return index >= 0 ? index : 0;
}

function taskProgressFor(task: GenerationTaskResponse) {
  if (task.status === "succeeded") return 100;
  return Math.max(
    8,
    Math.round(((taskStepIndex(task) + 1) / generationSteps.length) * 100),
  );
}

function formatTaskTitle(task: GenerationTaskResponse) {
  const title = task.ideaText.trim() || "未命名生成任务";
  return title.length > 24 ? `${title.slice(0, 24)}...` : title;
}

function taskResultSummary(task: GenerationTaskResponse) {
  if (task.result.manifestUrl) return "产物已生成";
  if (task.status === "failed") return task.errorMessage || "生成失败";
  if (task.status === "canceled") return "已取消";
  return "生成中";
}

function taskDuration(task: GenerationTaskResponse) {
  if (!task.startedAt) return "-";
  const end = task.finishedAt
    ? new Date(task.finishedAt).getTime()
    : Date.now();
  const start = new Date(task.startedAt).getTime();
  if (Number.isNaN(start) || Number.isNaN(end) || end < start) return "-";
  const totalSeconds = Math.floor((end - start) / 1000);
  const minutes = Math.floor(totalSeconds / 60)
    .toString()
    .padStart(2, "0");
  const seconds = (totalSeconds % 60).toString().padStart(2, "0");
  return `${minutes}:${seconds}`;
}

function canCancelTask(task: GenerationTaskResponse) {
  return task.status === "pending" || task.status === "running";
}

function canRetryTask(task: GenerationTaskResponse) {
  return task.status === "failed" || task.status === "canceled";
}

function deriveBundleUrl(manifestUrl: string) {
  if (!manifestUrl || manifestUrl === "-") return "-";
  return manifestUrl
    .replace("/manifests/", "/bundles/")
    .replace(/manifest\.json$/i, "bundle.zip");
}

function fillInspiration() {
  idea.value = visibleInspirations.value[0]?.prompt || "";
}

function clearAssets() {
  uploadedAssets.value = [];
}

function removeAsset(assetId: string) {
  uploadedAssets.value = uploadedAssets.value.filter(
    (asset) => asset.id !== assetId,
  );
}

function resetForm() {
  idea.value = "";
  uploadedAssets.value = [];
}

async function handleUpload(options: UploadRequestOptions) {
  uploadingCount.value += 1;
  try {
    const asset = await uploadAsset(options.file);
    uploadedAssets.value.push(asset);
    options.onSuccess(asset);
    ElMessage.success(`已上传 ${asset.filename}`);
  } catch (caught) {
    const uploadError =
      caught instanceof Error ? caught : new Error("上传失败");
    options.onError(
      uploadError as Parameters<UploadRequestOptions["onError"]>[0],
    );
    ElMessage.error(uploadError.message);
  } finally {
    uploadingCount.value -= 1;
  }
}

async function generate() {
  if (!canGenerate.value) return;
  previewManifest.value = null;
  await createTask.startTask({
    ideaText: idea.value.trim(),
    assetIds: uploadedAssets.value.map((asset) => asset.id),
  });
}

async function regenerate() {
  previewManifest.value = null;
  if (currentTask.value) {
    if (
      canRetryTask(currentTask.value) ||
      currentTask.value.status === "succeeded"
    ) {
      const task = await createTask.retryTaskById(currentTask.value.id);
      if (task) ElMessage.success("已创建重试任务");
      return;
    }
    const sourceIdea = currentTask.value.ideaText;
    const sourceAssetIds = currentTask.value.assetIds;
    if (canCancelTask(currentTask.value)) {
      await createTask.cancelCurrentTask();
    }
    await createTask.startTask({
      ideaText: sourceIdea,
      assetIds: sourceAssetIds,
    });
    ElMessage.success("已重新生成");
    return;
  }
  await generate();
}

async function cancelCurrent() {
  const task = await createTask.cancelCurrentTask();
  if (task) ElMessage.success("任务已取消");
}

async function publish() {
  const task = await createTask.publishCurrentTask();
  if (task?.result.gameId) {
    ElMessage.success("已发布到首页");
  }
}

function backToEdit() {
  if (currentTask.value?.ideaText) idea.value = currentTask.value.ideaText;
  previewManifest.value = null;
  createTask.reset();
}

async function loadTaskHistory() {
  try {
    await createTask.loadHistory();
  } catch (caught) {
    ElMessage.error(
      caught instanceof Error ? caught.message : "加载任务历史失败",
    );
  }
}

async function viewHistoryTask(task: GenerationTaskResponse) {
  previewManifest.value = null;
  await createTask.selectTask(task);
}

async function cancelHistoryTask(task: GenerationTaskResponse) {
  await viewHistoryTask(task);
  await cancelCurrent();
}

async function retryHistoryTask(task: GenerationTaskResponse) {
  const nextTask = await createTask.retryTaskById(task.id);
  if (nextTask) ElMessage.success("已创建重试任务");
}

async function copyText(value: string) {
  if (!value || value === "-") return;
  try {
    await navigator.clipboard.writeText(value);
    ElMessage.success("已复制");
  } catch {
    ElMessage.warning("复制失败");
  }
}

watch(
  () => currentTask.value?.result.manifestUrl,
  async (manifestUrl) => {
    if (!manifestUrl) return;
    try {
      const response = await fetch(manifestUrl);
      if (!response.ok)
        throw new Error(`Manifest 请求失败: ${response.status}`);
      const payload = await response.json();
      if (!isGameManifest(payload)) throw new Error("Manifest 协议不合法");
      previewManifest.value = payload;
      publishTitle.value = payload.title;
    } catch (caught) {
      ElMessage.error(
        caught instanceof Error ? caught.message : "预览加载失败",
      );
    }
  },
);

onMounted(loadTaskHistory);

onBeforeUnmount(() => createTask.stopPolling());
</script>

<style>
.create-page {
  max-width: 1800px;
  margin: 0 auto;
  padding: 28px 44px 34px;
  color: #1e293b;
}

.create-page--idle {
  max-width: 1240px;
  padding: 12px 20px 34px;
}

.create-grid,
.task-layout,
.publish-layout {
  position: relative;
}

.task-layout,
.publish-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 390px;
  gap: 24px;
  align-items: start;
}

.create-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  align-items: start;
}

.create-main,
.task-main,
.publish-main,
.publish-side {
  display: grid;
  gap: 16px;
}

.create-main {
  gap: 26px;
}

.creator-card,
.config-panel,
.recent-task,
.task-idea-card,
.workflow-card,
.log-card,
.side-card,
.success-banner,
.preview-card,
.result-card,
.publish-card {
  border: 1px solid #dce4f0;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 8px 22px rgba(31, 42, 68, 0.04);
}

.creator-card {
  padding: 18px 20px;
}

.prompt-card,
.assets-card {
  border-color: #d9e1f1;
  border-radius: 8px;
  box-shadow: 0 10px 24px rgba(40, 54, 96, 0.06);
}

.step-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.step-title__index {
  display: grid;
  width: 22px;
  height: 22px;
  flex: 0 0 auto;
  place-items: center;
  border-radius: 999px;
  background: linear-gradient(135deg, #4268ff, #6d4dff);
  color: #fff;
  font-size: 13px;
  font-weight: 800;
}

.step-title h2 {
  margin: 0;
  color: #0f172a;
  font-size: 17px;
  font-weight: 800;
}

.step-title p {
  margin: 4px 0 0;
  color: #94a3b8;
  font-size: 12px;
}

.assets-card .step-title > div {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 8px;
}

.assets-card .step-title p {
  margin: 0;
}

.prompt-box {
  position: relative;
  margin-top: 14px;
  border: 1px solid #d7dfec;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.98);
  min-height: 242px;
  overflow: hidden;
  box-shadow: inset 0 0 0 1px rgba(226, 232, 240, 0.28);
}

.prompt-input {
  height: 242px;
}

.prompt-input :deep(.el-textarea__inner) {
  min-height: 242px !important;
  border: 0 !important;
  box-shadow: none !important;
  padding: 16px 16px 58px;
  color: #334155;
  font-size: 13px;
  line-height: 1.8;
}

.prompt-hints {
  position: absolute;
  top: 48px;
  left: 16px;
  display: grid;
  gap: 9px;
  pointer-events: none;
  color: #8f9aaf;
  font-size: 12px;
}

.prompt-hints p {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}

.prompt-actions {
  position: absolute;
  right: 12px;
  bottom: 9px;
  left: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  border-top: 1px solid transparent;
}

.prompt-actions__left,
.prompt-actions__right {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.prompt-actions__left :deep(.el-button) {
  height: 28px;
  padding: 0 8px;
  color: #6b78a4;
  font-size: 12px;
}

.prompt-actions__left :deep(.el-button:hover) {
  color: #5b5cff;
}

.prompt-ai-button {
  border-radius: 8px !important;
  background: #f7f6ff !important;
  color: #5b5cff !important;
}

.prompt-tool-icon {
  display: grid;
  width: 28px;
  height: 28px;
  flex: 0 0 auto;
  place-items: center;
  border: 0;
  background: transparent;
  color: #8f9aaf;
  cursor: pointer;
}

.prompt-divider {
  width: 1px;
  height: 28px;
  flex: 0 0 auto;
  background: #d7dfec;
}

.prompt-actions__right span {
  color: #8f9aaf;
  font-size: 12px;
}

.generate-button {
  width: 32px !important;
  height: 28px !important;
  min-width: 32px !important;
  margin-top: 0 !important;
  border: 0 !important;
  border-radius: 8px !important;
  background: linear-gradient(135deg, #98a5ff, #c8b8ff) !important;
  color: #fff !important;
  font-weight: 800;
  padding: 0 !important;
}

.generate-button :deep(.el-icon) {
  font-size: 15px;
}

.generate-button.is-disabled {
  opacity: 0.72;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.asset-count {
  display: flex;
  align-items: center;
  gap: 18px;
  color: #94a3b8;
  font-size: 13px;
}

.asset-count button {
  border: 0;
  background: transparent;
  color: #5b4dff;
  cursor: pointer;
  font-weight: 700;
}

.asset-layout {
  display: grid;
  grid-template-columns: minmax(300px, 386px) minmax(0, 1fr);
  gap: 16px;
  margin-top: 16px;
}

.asset-uploader {
  width: 100%;
}

.asset-uploader :deep(.el-upload-dragger) {
  display: grid;
  min-height: 142px;
  place-items: center;
  border: 1px dashed #9d8cff;
  border-radius: 8px;
  background: #fff;
  padding: 20px;
}

.asset-uploader :deep(.el-upload) {
  width: 100%;
}

.upload-drop {
  display: grid;
  place-items: center;
  gap: 9px;
  color: #64748b;
  text-align: center;
}

.upload-drop .el-icon {
  color: #694cff;
  font-size: 28px;
}

.upload-drop strong {
  color: #7a8498;
  font-size: 13px;
  font-weight: 600;
}

.upload-drop span {
  color: #8f9aaf;
  font-size: 11px;
  line-height: 1.6;
}

.asset-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.asset-card {
  position: relative;
  overflow: hidden;
  border: 1px solid #dce4f0;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 8px 18px rgba(40, 54, 96, 0.04);
}

.asset-card__preview {
  display: grid;
  height: 88px;
  place-items: center;
  background: #f1f5f9;
  color: #5b4dff;
  font-size: 30px;
}

.asset-card__preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.asset-card__meta {
  display: grid;
  gap: 4px;
  padding: 9px 34px 11px 12px;
}

.asset-card__meta strong {
  overflow: hidden;
  color: #1e293b;
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.asset-card__meta span {
  color: #94a3b8;
  font-size: 12px;
}

.asset-card__remove {
  position: absolute;
  right: 8px;
  bottom: 12px;
  border: 0;
  background: transparent;
  color: #64748b;
  cursor: pointer;
}

.inspiration-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 14px;
  margin-top: 16px;
}

.inspiration-item {
  display: grid;
  grid-template-columns: 38px minmax(0, 1fr);
  gap: 10px;
  align-items: center;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #fff;
  padding: 10px;
  cursor: pointer;
  text-align: left;
}

.inspiration-item > span {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  border-radius: 10px;
}

.inspiration-item .violet {
  background: #ede9fe;
  color: #6d5dfc;
}
.inspiration-item .red {
  background: #fee2e2;
  color: #ef4444;
}
.inspiration-item .green {
  background: #dcfce7;
  color: #10b981;
}
.inspiration-item .purple {
  background: #f3e8ff;
  color: #8b5cf6;
}
.inspiration-item .teal {
  background: #ccfbf1;
  color: #14b8a6;
}

.inspiration-item strong {
  display: block;
  overflow: hidden;
  color: #1e293b;
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.inspiration-item p {
  overflow: hidden;
  margin: 4px 0 0;
  color: #94a3b8;
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recent-task {
  padding: 16px 20px;
}

.recent-task__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.recent-task h2 {
  margin: 0;
  color: #0f172a;
  font-size: 16px;
  font-weight: 800;
}

.recent-task__empty {
  padding: 24px 0 10px;
}

.recent-task__list {
  display: grid;
  gap: 12px;
  min-height: 80px;
  margin-top: 14px;
}

.recent-task__row {
  display: grid;
  grid-template-columns: 92px minmax(220px, 1fr) 170px 180px 90px auto;
  gap: 18px;
  align-items: center;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #fff;
  padding: 10px 12px;
}

.recent-task__row img {
  width: 92px;
  height: 52px;
  border-radius: 7px;
  object-fit: cover;
}

.recent-task__name,
.recent-task__progress,
.recent-task__model,
.recent-task__duration {
  display: grid;
  gap: 7px;
  min-width: 0;
}

.recent-task span {
  color: #94a3b8;
  font-size: 12px;
}

.recent-task strong {
  color: #334155;
  font-size: 13px;
}

.recent-task__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-end;
}

.config-panel {
  position: sticky;
  top: 84px;
  padding: 22px;
}

.panel-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}

.panel-title h2,
.config-section h3,
.side-card h2,
.publish-card h2 {
  margin: 0;
  color: #0f172a;
  font-size: 17px;
  font-weight: 800;
}

.config-section {
  display: grid;
  gap: 10px;
  margin-top: 18px;
}

.config-section h3 {
  font-size: 13px;
}

.option-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.option-grid button,
.duration-grid button {
  height: 34px;
  border: 1px solid #dce4f0;
  border-radius: 7px;
  background: #fff;
  color: #334155;
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
}

.option-grid button.active,
.duration-grid button.active {
  border-color: #6d5dfc;
  background: #f5f3ff;
  color: #5b4dff;
  box-shadow: 0 0 0 1px rgba(91, 77, 255, 0.12);
}

.duration-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.advanced-row {
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: space-between;
  margin-top: 18px;
  border: 1px solid #dce4f0;
  border-radius: 8px;
  background: #f8fafc;
  padding: 12px;
  color: #334155;
  cursor: pointer;
  font-weight: 700;
}

.advanced-row span {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.publish-button {
  width: 100%;
  margin-top: 16px;
  border: 0 !important;
  background: linear-gradient(135deg, #3f63ff, #7a3cff) !important;
  color: #fff !important;
  font-weight: 800;
}

.points-row {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
  color: #94a3b8;
  font-size: 12px;
}

.privacy-note {
  display: flex;
  gap: 8px;
  margin: 26px 0 0;
  color: #94a3b8;
  font-size: 12px;
  line-height: 1.7;
}

.privacy-note .el-icon {
  color: #4f63ff;
  margin-top: 2px;
}

.breadcrumb {
  margin: 0 0 6px;
  color: #94a3b8;
  font-size: 13px;
}

.task-idea-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 520px;
  gap: 34px;
  padding: 26px;
}

.card-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #0f172a;
  font-size: 17px;
  font-weight: 800;
}

.task-idea-card h1 {
  display: inline-flex;
  align-items: center;
  margin: 24px 8px 14px 0;
  color: #0f172a;
  font-size: 24px;
  font-weight: 800;
}

.edit-icon {
  border: 0;
  background: transparent;
  color: #64748b;
  cursor: pointer;
}

.task-idea-card h3 {
  margin: 18px 0 8px;
  color: #1e293b;
  font-size: 14px;
  font-weight: 800;
}

.task-idea-card p {
  margin: 0;
  color: #475569;
  font-size: 14px;
  line-height: 1.8;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-row span {
  border: 1px solid #dce4f0;
  border-radius: 6px;
  background: #f8fafc;
  padding: 5px 12px;
  color: #475569;
  font-size: 12px;
  font-weight: 700;
}

.task-assets {
  border-left: 1px solid #e2e8f0;
  padding-left: 32px;
}

.task-assets__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.task-assets__head button {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border: 0;
  background: transparent;
  color: #64748b;
  cursor: pointer;
}

.task-assets__list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.task-assets__list article {
  overflow: hidden;
  border: 1px solid #dce4f0;
  border-radius: 8px;
  background: #fff;
}

.task-assets__list img,
.file-preview {
  width: 100%;
  height: 92px;
  object-fit: cover;
  background: #f1f5f9;
}

.file-preview {
  display: grid;
  place-items: center;
  color: #5b4dff;
  font-size: 30px;
}

.task-assets__list strong,
.task-assets__list span {
  display: block;
  overflow: hidden;
  padding: 0 10px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-assets__list strong {
  margin-top: 8px;
  color: #1e293b;
  font-size: 12px;
}

.task-assets__list span {
  margin: 4px 0 10px;
  color: #94a3b8;
  font-size: 12px;
}

.task-assets__empty {
  grid-column: 1 / -1;
  display: grid;
  min-height: 92px;
  place-items: center;
  border: 1px dashed #cbd5e1;
  border-radius: 8px;
  color: #94a3b8;
}

.workflow-card,
.log-card,
.preview-card,
.result-card {
  padding: 24px;
}

.workflow-card__head,
.log-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.workflow-card h2,
.log-card h2,
.preview-card h2,
.result-card h2 {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  color: #0f172a;
  font-size: 18px;
  font-weight: 800;
}

.workflow-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.workflow-stats span {
  border-radius: 999px;
  background: #f1f5f9;
  padding: 5px 12px;
  color: #64748b;
  font-size: 12px;
  font-weight: 800;
}

.workflow-stats .running {
  background: #ede9fe;
  color: #5b4dff;
}
.workflow-stats .done {
  background: #dcfce7;
  color: #059669;
}
.workflow-stats .failed {
  background: #fee2e2;
  color: #dc2626;
}

.workflow-steps {
  display: grid;
  grid-template-columns: repeat(8, minmax(0, 1fr));
  gap: 10px;
  margin-top: 28px;
}

.workflow-step {
  position: relative;
  display: grid;
  justify-items: center;
  gap: 8px;
  text-align: center;
}

.workflow-step i {
  position: absolute;
  top: 20px;
  left: calc(50% + 26px);
  width: calc(100% - 42px);
  height: 2px;
  background: #dce4f0;
}

.workflow-step.done i {
  background: #2fb56f;
}

.workflow-step__icon {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border-radius: 999px;
  background: #f1f5f9;
  color: #94a3b8;
  font-size: 20px;
}

.workflow-step.done .workflow-step__icon {
  background: #2fb56f;
  color: #fff;
}
.workflow-step.running .workflow-step__icon {
  background: linear-gradient(135deg, #3f63ff, #7a3cff);
  color: #fff;
}
.workflow-step.failed .workflow-step__icon {
  background: #ef4444;
  color: #fff;
}

.workflow-step strong {
  color: #1e293b;
  font-size: 13px;
}

.workflow-step span {
  color: #94a3b8;
  font-size: 12px;
}

.workflow-step.running strong,
.workflow-step.running span {
  color: #3f63ff;
}

.workflow-progress {
  display: grid;
  grid-template-columns: 72px minmax(0, 1fr) 48px;
  gap: 16px;
  align-items: center;
  margin-top: 28px;
}

.workflow-progress span,
.current-step span {
  color: #64748b;
  font-size: 13px;
}

.workflow-progress strong {
  color: #1e293b;
  font-size: 15px;
}

.current-step {
  display: grid;
  grid-template-columns: 72px auto minmax(0, 1fr) auto;
  gap: 16px;
  align-items: center;
  margin-top: 18px;
}

.current-step strong {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #4f63ff;
}

.current-step p {
  margin: 0;
  color: #64748b;
  font-size: 13px;
}

.current-step em {
  color: #334155;
  font-style: normal;
  font-weight: 700;
}

.log-card__head div {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: #64748b;
  font-size: 13px;
}

.log-list {
  display: grid;
  grid-template-columns: repeat(6, minmax(190px, 1fr));
  gap: 14px;
  margin-top: 18px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.log-list article {
  border: 1px solid #dce4f0;
  border-radius: 9px;
  background: #fff;
  padding: 14px;
}

.log-list article.active {
  border-color: #6d5dfc;
  box-shadow: 0 0 0 1px rgba(91, 77, 255, 0.12);
}

.log-list__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.log-list__top strong {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #1e293b;
  font-size: 13px;
}

.log-list__top .el-icon {
  color: #12a66a;
}

.log-list__top span {
  color: #64748b;
  font-size: 12px;
}

.log-list p {
  display: -webkit-box;
  min-height: 48px;
  margin: 14px 0;
  overflow: hidden;
  color: #64748b;
  font-size: 12px;
  line-height: 1.65;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.log-list__bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.log-list__bottom span {
  border-radius: 6px;
  background: #eef2ff;
  padding: 5px 9px;
  color: #4f63ff;
  font-size: 12px;
  font-weight: 700;
}

.log-list__bottom button {
  border: 1px solid #dce4f0;
  border-radius: 6px;
  background: #fff;
  color: #64748b;
  cursor: pointer;
  font-size: 12px;
  padding: 5px 9px;
}

.expand-logs {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 18px auto 0;
  border: 0;
  background: transparent;
  color: #334155;
  cursor: pointer;
  font-weight: 700;
}

.task-side {
  display: grid;
  gap: 0;
  border: 1px solid #dce4f0;
  border-radius: 12px;
  background: #fff;
  padding: 22px;
}

.side-card {
  border: 0;
  border-bottom: 1px solid #e2e8f0;
  border-radius: 0;
  box-shadow: none;
  padding: 0 0 22px;
  margin-bottom: 22px;
}

.side-card:last-of-type {
  border-bottom: 0;
  margin-bottom: 0;
}

.fire-dot {
  color: #ff7a1a;
}

.info-list {
  display: grid;
  gap: 14px;
  margin-top: 18px;
}

.info-list__row {
  display: grid;
  grid-template-columns: 96px minmax(0, 1fr) 24px;
  gap: 10px;
  align-items: center;
}

.info-list__row span {
  color: #64748b;
  font-size: 13px;
}

.info-list__row strong {
  overflow: hidden;
  color: #334155;
  font-size: 13px;
  text-align: right;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.info-list__row button {
  display: grid;
  width: 22px;
  height: 22px;
  place-items: center;
  border: 0;
  background: transparent;
  color: #64748b;
  cursor: pointer;
}

.artifact-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 18px;
}

.artifact-grid div {
  display: grid;
  min-height: 102px;
  place-items: center;
  gap: 6px;
  border: 1px solid #e2e8f0;
  border-radius: 9px;
  background: #fff;
  color: #94a3b8;
  text-align: center;
}

.artifact-grid .el-icon {
  font-size: 24px;
}

.artifact-grid strong {
  color: #334155;
  font-size: 12px;
}

.artifact-grid span {
  font-size: 12px;
}

.task-side__actions {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.task-side__note {
  margin: 12px 0 0;
  color: #94a3b8;
  font-size: 12px;
  text-align: center;
}

.success-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 26px;
}

.success-banner > div:first-child {
  display: flex;
  align-items: center;
  gap: 20px;
}

.success-banner span {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  border-radius: 999px;
  background: #16a34a;
  padding: 12px 18px;
  color: #fff;
  font-weight: 800;
}

.success-banner h1 {
  margin: 0;
  color: #0f172a;
  font-size: 22px;
  font-weight: 800;
}

.success-banner p {
  margin: 8px 0 0;
  color: #64748b;
  font-size: 13px;
}

.success-banner__actions {
  display: flex;
  gap: 12px;
}

.success-banner__actions .publish-button {
  width: auto;
  margin: 0;
  padding-inline: 24px;
}

.preview-card h2,
.result-card h2 {
  margin-bottom: 16px;
}

.preview-loading {
  display: grid;
  min-height: 420px;
  place-items: center;
  color: #64748b;
}

.preview-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.preview-actions p {
  margin: 0;
  color: #64748b;
  font-size: 13px;
}

.preview-actions div {
  display: flex;
  gap: 10px;
}

.result-steps {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  border: 1px solid #d5f0df;
  border-radius: 10px;
  background: #f6fff9;
  padding: 14px;
}

.result-steps div {
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr);
  gap: 10px;
  align-items: center;
}

.result-steps .el-icon {
  color: #16a34a;
  font-size: 22px;
}

.result-steps strong {
  display: block;
  color: #334155;
  font-size: 14px;
}

.result-steps span {
  color: #64748b;
  font-size: 12px;
}

.result-card > p {
  margin: 18px 0 0;
  color: #1e293b;
  font-weight: 800;
}

.publish-card {
  padding: 24px;
}

.publish-form {
  margin-top: 20px;
}

.cover-field {
  display: flex;
  align-items: center;
  gap: 14px;
}

.cover-field img {
  width: 112px;
  height: 72px;
  border-radius: 7px;
  object-fit: cover;
}

.cover-field p {
  margin: 10px 0 0;
  color: #94a3b8;
  font-size: 12px;
}

.publish-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.build-info {
  display: grid;
  gap: 14px;
  margin-top: 18px;
}

.build-info div {
  display: grid;
  grid-template-columns: 118px minmax(0, 1fr) 28px;
  gap: 10px;
  align-items: center;
}

.build-info span {
  color: #64748b;
  font-size: 13px;
}

.build-info strong {
  overflow: hidden;
  color: #334155;
  font-size: 13px;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.error-state {
  padding: 24px;
}

.terminal-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 20px;
}

:deep(.el-button) {
  border-radius: 7px;
  font-weight: 700;
}

:deep(.el-input__wrapper),
:deep(.el-select__wrapper),
:deep(.el-textarea__inner) {
  border-radius: 7px !important;
}

@media (max-width: 1320px) {
  .create-grid,
  .task-layout,
  .publish-layout {
    grid-template-columns: minmax(0, 1fr);
  }

  .config-panel {
    position: static;
  }

  .task-idea-card {
    grid-template-columns: minmax(0, 1fr);
  }

  .task-assets {
    border-left: 0;
    border-top: 1px solid #e2e8f0;
    padding-top: 20px;
    padding-left: 0;
  }
}

@media (max-width: 780px) {
  .create-page--idle {
    padding: 12px 12px 28px;
  }

  .creator-card {
    padding: 16px 14px;
  }

  .section-head,
  .prompt-actions {
    align-items: flex-start;
    flex-direction: column;
  }

  .prompt-actions__left {
    flex-wrap: wrap;
    gap: 6px;
  }

  .prompt-actions__right {
    align-self: flex-end;
  }

  .prompt-input,
  .prompt-input :deep(.el-textarea__inner) {
    min-height: 300px !important;
    height: 300px;
  }

  .asset-layout {
    grid-template-columns: minmax(0, 1fr);
  }

  .asset-list {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
