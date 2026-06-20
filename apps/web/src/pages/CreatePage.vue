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
      :retrying="retrying"
      :deleting-task-id="deletingTaskId"
      :can-generate="canGenerate"
      :is-image-asset="isImageAsset"
      :format-bytes="formatBytes"
      :format-task-title="formatTaskTitle"
      :format-task-time="formatTaskTime"
      :task-status-label="taskStatusLabel"
      :task-progress-for="taskProgressFor"
      :task-result-summary="taskResultSummary"
      :can-retry-task="canRetryTask"
      :can-delete-task="canDeleteTask"
      @optimize-description="fillInspiration"
      @generate="generate"
      @upload="handleUpload"
      @clear-assets="clearAssets"
      @remove-asset="removeAsset"
      @load-history="loadTaskHistory"
      @view-history-task="viewHistoryTask"
      @cancel-history-task="cancelHistoryTask"
      @retry-history-task="retryHistoryTask"
      @delete-history-task="deleteHistoryTask"
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
      @back-to-create="backToCreateStart"
      @regenerate="regenerate"
      @copy="copyText"
    />

    <component
      :is="activeCreateView"
      v-else-if="activeCreateView === CreateSuccessView"
      v-model:publish-title="publishTitle"
      v-model:publish-description="publishDescription"
      :preview-manifest="previewManifest"
      :cover-url="publishCoverUrl"
      :cover-uploading="coverUploading"
      :publish-tags="publishTags"
      :build-info-rows="buildInfoRows"
      :publishing="publishing"
      :published="isCurrentTaskPublished"
      :archived="isCurrentTaskArchived"
      :saving-publish-info="savingPublishInfo"
      :unpublishing-game="unpublishingGame"
      @back-to-create="backToCreateStart"
      @back-to-edit="backToEdit"
      @regenerate="regenerate"
      @publish="publish"
      @save-publish-info="savePublishInfo"
      @unpublish-game="unpublishGame"
      @copy="copyText"
      @upload-cover="handleCoverUpload"
      @add-tag="addPublishTag"
      @remove-tag="removePublishTag"
    />

    <component
      :is="activeCreateView"
      v-else-if="currentTask"
      :status="currentTask.status"
      :title="terminalStateTitle"
      :message="terminalStateMessage"
      :retrying="retrying"
      @back-to-create="backToCreateStart"
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
import { ElMessage, ElMessageBox, type UploadRequestOptions } from "element-plus";
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
import { referenceImages } from "@/data/showcase";
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
  savingPublishInfo,
  unpublishingGame,
  canceling,
  retrying,
  deletingTaskId,
  error,
} = storeToRefs(createTask);

const idea = ref("");
const uploadedAssets = ref<AssetResponse[]>([]);
const uploadingCount = ref(0);
const previewManifest = ref<GameManifest | null>(null);
const defaultPublishTitle = "迷雾之城：冥歌";
const defaultPublishDescription =
  "在迷雾与诅咒笼罩的古城中探寻真相，你的选择将决定众人的命运。";
const publishTitle = ref(defaultPublishTitle);
const publishDescription = ref(defaultPublishDescription);
const publishCoverUrl = ref(referenceImages.playRunningImage);
const publishTags = ref(["角色扮演", "剧情", "暗黑奇幻", "单机"]);
const coverUploading = ref(false);
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
      value: publishStatusLabel.value,
    },
  ];
});
const isCurrentTaskPublished = computed(() =>
  currentTask.value?.result.gameStatus === "published",
);
const isCurrentTaskArchived = computed(() =>
  currentTask.value?.result.gameStatus === "archived",
);
const publishStatusLabel = computed(() => {
  if (isCurrentTaskPublished.value) return "已发布";
  if (isCurrentTaskArchived.value) return "已下架";
  return "未发布";
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

function canDeleteTask(task: GenerationTaskResponse) {
  return task.status === "succeeded" || task.status === "failed" || task.status === "canceled";
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
  const payload = buildPublishPayload();
  if (!payload) return;
  const task = await createTask.publishCurrentTask(payload);
  if (task?.result.gameId) {
    ElMessage.success("已发布到首页");
  }
}

async function savePublishInfo() {
  const payload = buildPublishPayload();
  if (!payload) return;
  const task = await createTask.saveCurrentGameInfo(payload);
  if (task?.result.gameId) {
    ElMessage.success("发布信息已保存");
  }
}

async function unpublishGame() {
  try {
    await ElMessageBox.confirm(
      "下架后该游戏将从首页移除，玩家也无法继续通过游玩页访问。确定下架吗？",
      "下架游戏",
      {
        confirmButtonText: "下架",
        cancelButtonText: "取消",
        type: "warning",
      },
    );
    const task = await createTask.unpublishCurrentGame();
    if (task?.result.gameId) {
      ElMessage.success("游戏已下架");
    }
  } catch (caught) {
    if (caught === "cancel" || caught === "close") return;
    ElMessage.error(caught instanceof Error ? caught.message : "下架游戏失败");
  }
}

function buildPublishPayload() {
  const title = publishTitle.value.trim();
  const description = publishDescription.value.trim();
  if (!title) {
    ElMessage.warning("请填写游戏标题");
    return null;
  }
  if (!description) {
    ElMessage.warning("请填写游戏描述");
    return null;
  }
  return {
    title,
    description,
    coverUrl: publishCoverUrl.value || null,
    tags: [...new Set(publishTags.value.map((tag) => tag.trim()).filter(Boolean))],
  };
}

async function handleCoverUpload(file: File) {
  coverUploading.value = true;
  try {
    const asset = await uploadAsset(file);
    publishCoverUrl.value = asset.url;
    ElMessage.success("封面已更新");
  } catch (caught) {
    ElMessage.error(caught instanceof Error ? caught.message : "封面上传失败");
  } finally {
    coverUploading.value = false;
  }
}

function addPublishTag(tag: string) {
  const normalized = tag.trim();
  if (!normalized || publishTags.value.includes(normalized)) return;
  publishTags.value = [...publishTags.value, normalized];
}

function removePublishTag(tag: string) {
  publishTags.value = publishTags.value.filter((item) => item !== tag);
}

function backToEdit() {
  if (currentTask.value?.ideaText) idea.value = currentTask.value.ideaText;
  previewManifest.value = null;
  createTask.reset();
}

function backToCreateStart() {
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

async function deleteHistoryTask(task: GenerationTaskResponse) {
  if (!canDeleteTask(task)) {
    ElMessage.warning("运行中的任务不能删除");
    return;
  }
  try {
    await ElMessageBox.confirm(
      "删除后该任务将从历史列表隐藏，生成产物和已发布游戏不会被删除。确定删除吗？",
      "删除任务",
      {
        confirmButtonText: "删除",
        cancelButtonText: "取消",
        type: "warning",
      },
    );
    await createTask.deleteTaskById(task.id);
    previewManifest.value = null;
    ElMessage.success("任务已删除");
  } catch (caught) {
    if (caught === "cancel" || caught === "close") return;
    ElMessage.error(caught instanceof Error ? caught.message : "删除任务失败");
  }
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
  () => currentTask.value?.result,
  (result) => {
    if (!result) return;
    publishTitle.value = result.title || previewManifest.value?.title || defaultPublishTitle;
    publishDescription.value = result.description || defaultPublishDescription;
    publishCoverUrl.value = result.coverUrl || referenceImages.playRunningImage;
    publishTags.value = result.tags?.length ? result.tags : [];
  },
  { immediate: true },
);

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
      if (!currentTask.value?.result.title) publishTitle.value = payload.title;
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
  padding: 26px 46px 34px;
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
  gap: 30px;
  align-items: start;
  min-width: 0;
}

.publish-layout {
  grid-template-columns: minmax(0, 1fr) 488px;
  gap: 30px;
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

.task-main {
  gap: 18px;
  min-width: 0;
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
  display: block;
  height: 242px;
}

.prompt-input .el-textarea__inner {
  display: block;
  min-height: 242px !important;
  height: 242px;
  border: 0 !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  background: transparent !important;
  padding: 16px 16px 58px;
  color: #334155;
  font-size: 13px;
  line-height: 1.8;
}

.prompt-hints {
  position: absolute;
  top: 16px;
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

.prompt-hints__lead {
  display: block !important;
  margin-bottom: 20px !important;
  color: #9aa4b8;
  font-size: 14px;
  line-height: 1.5;
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

.prompt-actions__left .el-button {
  height: 28px;
  padding: 0 8px;
  color: #6b78a4;
  font-size: 12px;
}

.prompt-actions__left .el-button:hover {
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

.generate-button .el-icon {
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

.asset-uploader .el-upload-dragger {
  display: grid;
  min-height: 142px;
  place-items: center;
  border: 1px dashed #9d8cff;
  border-radius: 8px;
  background: #fff;
  padding: 20px;
}

.asset-uploader .el-upload {
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

.recent-task__actions .history-action-button {
  min-width: 58px;
  height: 30px;
  border: 0;
  border-radius: 4px;
  padding: 0 12px;
  font-size: 13px;
  font-weight: 800;
}

.recent-task__actions .history-action-button + .history-action-button {
  margin-left: 0;
}

.recent-task__actions .history-action-button--primary {
  background: #f3f7ff;
  color: #409eff;
}

.recent-task__actions .history-action-button--danger {
  background: #fff5f5;
  color: #ff6b6b;
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

.task-view-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  min-height: 24px;
}

.task-view-head .breadcrumb {
  margin: 0;
}

.task-view-head .el-button {
  color: #4f63ff;
  font-weight: 800;
}

.task-idea-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 538px;
  gap: 32px;
  min-width: 0;
  overflow: hidden;
  padding: 24px;
}

.running-idea-card {
  min-height: 268px;
}

.task-idea-card__content,
.task-assets {
  min-width: 0;
}

.card-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #0f172a;
  font-size: 17px;
  font-weight: 800;
}

.card-label .el-icon {
  color: #6d5dfc;
}

.task-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  margin-top: 24px;
}

.task-idea-card h1 {
  min-width: 0;
  overflow: hidden;
  margin: 0;
  color: #0f172a;
  font-size: 24px;
  font-weight: 800;
  line-height: 1.25;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.edit-icon {
  display: grid;
  width: 26px;
  height: 26px;
  flex: 0 0 auto;
  place-items: center;
  border: 0;
  background: transparent;
  color: #64748b;
  cursor: pointer;
}

.task-idea-card h3 {
  margin: 22px 0 8px;
  color: #1e293b;
  font-size: 14px;
  font-weight: 800;
}

.task-idea-card p {
  display: -webkit-box;
  max-width: 720px;
  min-height: 50px;
  margin: 0;
  overflow: hidden;
  color: #475569;
  font-size: 14px;
  line-height: 1.8;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
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
  padding: 5px 13px;
  color: #475569;
  font-size: 12px;
  font-weight: 700;
}

.task-assets {
  border-left: 1px solid #e2e8f0;
  padding-left: 30px;
}

.task-assets__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.task-assets__head strong {
  color: #0f172a;
  font-size: 14px;
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
  gap: 14px;
  min-width: 0;
}

.task-assets__list article {
  overflow: hidden;
  border: 1px solid #dce4f0;
  border-radius: 9px;
  background: #fff;
  box-shadow: 0 8px 18px rgba(40, 54, 96, 0.04);
}

.task-assets__list img,
.file-preview {
  width: 100%;
  height: 91px;
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
  min-width: 0;
  min-height: 92px;
  place-items: center;
  border: 1px dashed #cbd5e1;
  border-radius: 8px;
  color: #94a3b8;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.workflow-card,
.log-card,
.preview-card,
.result-card {
  min-width: 0;
  padding: 24px;
}

.running-workflow-card {
  overflow: hidden;
  padding: 22px 24px 24px;
}

.running-log-card {
  overflow: hidden;
  padding: 18px 24px 14px;
}

.workflow-card__head,
.log-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  min-width: 0;
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

.workflow-card h2 .el-icon {
  color: #6d5dfc;
}

.workflow-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  min-width: 0;
}

.workflow-stats span {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border-radius: 999px;
  background: #f1f5f9;
  padding: 5px 14px;
  color: #64748b;
  font-size: 12px;
  font-weight: 800;
}

.workflow-stats b {
  font-size: 12px;
}

.workflow-stats .waiting {
  background: #f1f5f9;
  color: #64748b;
}

.workflow-stats .running {
  background: linear-gradient(135deg, #4f63ff, #7a3cff);
  color: #fff;
}
.workflow-stats .done {
  background: #dff7e8;
  color: #078b5a;
}
.workflow-stats .failed {
  background: #fff1f1;
  color: #dc2626;
}

.workflow-steps {
  display: grid;
  grid-template-columns: repeat(8, minmax(112px, 1fr));
  gap: 10px;
  margin-top: 22px;
  min-width: 0;
  overflow-x: auto;
  overflow-y: hidden;
  padding-bottom: 6px;
}

.workflow-step {
  position: relative;
  display: grid;
  justify-items: center;
  gap: 7px;
  min-width: 0;
  text-align: center;
}

.workflow-step i {
  position: absolute;
  top: 18px;
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
  position: relative;
  z-index: 1;
  width: 40px;
  height: 40px;
  place-items: center;
  border-radius: 999px;
  border: 1px solid #dce4f0;
  background: #f3f6fb;
  color: #a3adbf;
  font-size: 18px;
}

.workflow-step.done .workflow-step__icon {
  background: #2fb56f;
  border-color: #2fb56f;
  color: #fff;
}
.workflow-step.running .workflow-step__icon {
  background: linear-gradient(135deg, #3f63ff, #7a3cff);
  border-color: transparent;
  color: #fff;
  box-shadow: 0 10px 24px rgba(79, 99, 255, 0.24);
}
.workflow-step.failed .workflow-step__icon {
  background: #ef4444;
  border-color: #ef4444;
  color: #fff;
}

.workflow-step strong {
  overflow-wrap: anywhere;
  color: #1e293b;
  font-size: 13px;
  line-height: 1.25;
}

.workflow-step span {
  color: #94a3b8;
  font-size: 12px;
  line-height: 1.2;
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
  min-width: 0;
  margin-top: 24px;
}

.workflow-progress .el-progress {
  min-width: 0;
}

.workflow-progress .el-progress-bar__outer {
  height: 8px !important;
  background: #e9eef7;
}

.workflow-progress .el-progress-bar__inner {
  background: linear-gradient(90deg, #3f7cff, #7a3cff);
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
  grid-template-columns: 72px max-content minmax(0, 1fr) auto;
  gap: 16px;
  align-items: center;
  min-width: 0;
  margin-top: 16px;
}

.current-step strong {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #4f63ff;
}

.current-step p {
  min-width: 0;
  overflow: hidden;
  margin: 0;
  color: #64748b;
  font-size: 13px;
  line-height: 1.6;
  text-overflow: ellipsis;
  white-space: nowrap;
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
  grid-template-columns: repeat(6, minmax(188px, 1fr));
  gap: 13px;
  min-width: 0;
  margin-top: 18px;
  overflow-x: auto;
  overflow-y: hidden;
  padding-bottom: 6px;
}

.log-list article {
  border: 1px solid #dce4f0;
  border-radius: 8px;
  background: #fff;
  padding: 14px 14px 13px;
  min-height: 174px;
}

.log-list article.active {
  border-color: #6374ff;
  background: #fbfcff;
  box-shadow: 0 0 0 1px rgba(91, 77, 255, 0.18);
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
  min-width: 0;
  color: #1e293b;
  font-size: 13px;
}

.log-list__top .el-icon {
  color: #12a66a;
}

.log-list article.running .log-list__top .el-icon {
  color: #5b5cff;
}

.log-list article.waiting .log-list__top .el-icon {
  color: #cbd5e1;
}

.log-list__top span {
  color: #64748b;
  font-size: 12px;
}

.log-list p {
  display: -webkit-box;
  min-height: 58px;
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

.log-list article.done .log-list__bottom span {
  background: #eef2ff;
  color: #4f63ff;
}

.log-list article.running .log-list__bottom span {
  background: #f0efff;
  color: #4f63ff;
}

.log-list article.waiting .log-list__bottom span {
  background: transparent;
  padding-inline: 0;
  color: #94a3b8;
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
  margin: 16px auto 0;
  border: 0;
  background: transparent;
  color: #334155;
  cursor: pointer;
  font-weight: 700;
}

.task-side {
  display: grid;
  position: relative;
  z-index: 1;
  gap: 0;
  min-width: 0;
  width: 100%;
  border: 1px solid #dce4f0;
  border-radius: 14px;
  background: #fff;
  padding: 24px 26px;
  box-shadow: 0 8px 22px rgba(31, 42, 68, 0.04);
}

.side-card {
  border: 0;
  border-bottom: 1px solid #e2e8f0;
  border-radius: 0;
  box-shadow: none;
  padding: 0 0 24px;
  margin-bottom: 24px;
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
  gap: 16px;
  margin-top: 22px;
}

.info-list__row {
  display: grid;
  grid-template-columns: 100px minmax(0, 1fr) 22px;
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
  font-size: 14px;
  font-weight: 700;
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
  margin-top: 20px;
}

.artifact-grid div {
  display: grid;
  min-height: 110px;
  place-items: center;
  gap: 7px;
  border: 1px solid #e2e8f0;
  border-radius: 9px;
  background: #fff;
  color: #94a3b8;
  text-align: center;
}

.artifact-grid .el-icon {
  color: #c2cad8;
  font-size: 28px;
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
  margin-top: 4px;
}

.task-side__actions .el-button {
  min-width: 0;
  height: 40px;
  margin-left: 0 !important;
  padding-inline: 10px;
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
  gap: 22px;
  min-height: 92px;
  padding: 18px 22px;
}

.success-banner__content {
  display: flex;
  align-items: center;
  gap: 22px;
  min-width: 0;
}

.success-banner__badge {
  display: inline-flex;
  align-items: center;
  flex: 0 0 auto;
  gap: 10px;
  min-height: 48px;
  justify-content: center;
  border-radius: 999px;
  background: #16a34a;
  padding: 0 18px 0 12px;
  color: #fff;
  font-size: 15px;
  font-weight: 800;
  line-height: 1;
  white-space: nowrap;
}

.success-banner__badge i {
  display: grid;
  width: 30px;
  height: 30px;
  place-items: center;
  border-radius: 999px;
  background: #fff;
  color: #16a34a;
  font-size: 18px;
  font-style: normal;
}

.success-banner__copy {
  min-width: 0;
}

.success-banner h1 {
  overflow: hidden;
  margin: 0;
  color: #0f172a;
  font-size: 18px;
  font-weight: 800;
  line-height: 1.28;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.success-banner p {
  overflow: hidden;
  margin: 7px 0 0;
  color: #64748b;
  font-size: 13px;
  line-height: 1.4;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.success-banner__actions {
  display: flex;
  flex: 0 0 auto;
  gap: 12px;
}

.success-banner__actions .el-button {
  min-width: 88px;
  height: 36px;
  border-color: #d8e0ef;
  border-radius: 7px;
  background: #fff;
  color: #334155;
  font-size: 13px;
  font-weight: 800;
}

.success-banner__actions .publish-button {
  width: 106px;
  margin: 0;
  padding-inline: 18px;
}

.success-banner__actions .unpublish-button {
  border-color: #fecaca;
  background: #fff5f5;
  color: #ef4444;
}

.archived-pill {
  display: inline-flex;
  height: 36px;
  align-items: center;
  border-radius: 7px;
  background: #f8fafc;
  padding: 0 14px;
  color: #64748b;
  font-size: 13px;
  font-weight: 800;
}

.preview-card h2,
.result-card h2 {
  margin-bottom: 16px;
}

.preview-card {
  padding: 30px;
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
  margin-bottom: 16px;
}

.preview-actions h2 {
  margin: 0;
  font-size: 24px;
}

.preview-actions p {
  margin: 0;
  color: #64748b;
  font-size: 15px;
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

.publish-side {
  gap: 20px;
}

.publish-card {
  padding: 30px;
  border-radius: 14px;
}

.publish-form {
  margin-top: 26px;
}

.publish-form .el-form-item {
  margin-bottom: 22px;
}

.publish-form .el-form-item__label {
  color: #334155;
  font-size: 16px;
  line-height: 1.4;
  padding-bottom: 10px;
}

.publish-form .el-input__wrapper {
  min-height: 40px;
}

.publish-form .el-textarea__inner {
  min-height: 118px !important;
  resize: vertical;
}

.cover-field {
  display: flex;
  align-items: flex-start;
  gap: 18px;
}

.cover-field img {
  width: 140px;
  height: 78px;
  border-radius: 7px;
  object-fit: cover;
}

.cover-field p {
  margin: 12px 0 0;
  color: #94a3b8;
  font-size: 12px;
}

.publish-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.publish-tags .el-tag {
  height: 30px;
  border-color: #bfdbfe;
  background: #eff6ff;
  color: #2f63ff;
  font-weight: 700;
}

.publish-tags__input {
  width: 104px;
}

.build-info {
  display: grid;
  gap: 18px;
  margin-top: 24px;
}

.build-info div {
  display: grid;
  grid-template-columns: 132px minmax(0, 1fr) 28px;
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
  font-size: 14px;
  font-weight: 800;
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

.create-page .el-button {
  border-radius: 7px;
  font-weight: 700;
}

.create-page .el-input__wrapper,
.create-page .el-select__wrapper,
.create-page .el-textarea__inner {
  border-radius: 7px !important;
}

@media (max-width: 1600px) and (min-width: 1321px) {
  .create-page {
    padding-right: 36px;
    padding-left: 36px;
  }

  .task-layout {
    grid-template-columns: minmax(0, 1fr) 390px;
    gap: 24px;
  }

  .task-idea-card {
    grid-template-columns: minmax(0, 1fr) minmax(360px, 420px);
  }

  .workflow-steps {
    grid-template-columns: repeat(8, minmax(104px, 1fr));
  }
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

  .workflow-steps,
  .log-list {
    overflow-x: auto;
  }

  .workflow-steps {
    grid-template-columns: repeat(8, minmax(116px, 1fr));
    padding-bottom: 4px;
  }

  .task-side {
    padding: 22px;
  }

  .success-banner {
    align-items: flex-start;
    flex-direction: column;
  }

  .success-banner__actions {
    width: 100%;
    flex-wrap: wrap;
    gap: 12px;
  }

  .success-banner__actions .el-button,
  .success-banner__actions .publish-button {
    flex: 1 1 180px;
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
  .prompt-input .el-textarea__inner {
    min-height: 300px !important;
    height: 300px;
  }

  .asset-layout {
    grid-template-columns: minmax(0, 1fr);
  }

  .asset-list {
    grid-template-columns: minmax(0, 1fr);
  }

  .task-idea-card {
    padding: 20px;
  }

  .task-assets__list,
  .artifact-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .workflow-card__head,
  .log-card__head,
  .current-step {
    align-items: flex-start;
    grid-template-columns: minmax(0, 1fr);
  }

  .workflow-card__head,
  .log-card__head {
    flex-direction: column;
  }

  .workflow-progress {
    grid-template-columns: minmax(0, 1fr);
    gap: 8px;
  }

  .task-side__actions {
    grid-template-columns: minmax(0, 1fr);
  }

  .success-banner,
  .preview-card,
  .publish-card {
    padding: 20px;
  }

  .success-banner__content,
  .cover-field {
    align-items: flex-start;
    flex-direction: column;
  }

  .success-banner h1 {
    font-size: 22px;
  }

  .preview-actions {
    align-items: flex-start;
    flex-direction: column;
  }

  .build-info div {
    grid-template-columns: minmax(0, 1fr) 28px;
  }

  .build-info span {
    grid-column: 1 / -1;
  }
}
</style>
