<template>
  <main class="create-page">
    <template v-if="!currentTask">
      <!-- 顶部 -->
      <section class="create-hero">
        <div>
          <h1>AI 游戏创作</h1>
          <p>
            用自然语言描述你的游戏想法，上传参考素材，Agent
            将为你生成可玩的互动游戏。
          </p>
        </div>
        <el-button plain :icon="Guide" class="guide-button">创作指南</el-button>
      </section>

      <div class="create-grid">
        <section class="create-main">
          <!-- 输入框 -->
          <section class="creator-card prompt-card">
            <StepTitle :index="1" title="说出你的游戏想法" />
            <div class="prompt-box">
              <el-input
                v-model="idea"
                type="textarea"
                maxlength="3000"
                resize="none"
                class="prompt-input"
                placeholder="尽可能详细地描述你的游戏创意，Agent 会理解并生成完整的游戏内容。"
              />
              <div v-if="!idea" class="prompt-hints">
                <p>
                  <el-icon><Compass /></el-icon>
                  游戏概念：例如世界观、背景故事、核心玩法
                </p>
                <p>
                  <el-icon><Tools /></el-icon>
                  玩法机制：例如操作方式、任务目标、系统规则
                </p>
                <p>
                  <el-icon><Flag /></el-icon>
                  关卡风格：例如卡通、像素风、写实、赛博朋克
                </p>
                <p>
                  <el-icon><User /></el-icon>
                  角色与设定：例如主角、NPC、敌人、道具等
                </p>
                <p>
                  <el-icon><Aim /></el-icon> 胜利 /
                  失败条件：例如通关条件、失败判定
                </p>
                <p>
                  <el-icon><Picture /></el-icon>
                  参考素材：可描述如何使用上传的图片 / 文件 / 视频作为参考
                </p>
              </div>
              <div class="prompt-actions">
                <div class="prompt-actions__left">
                  <el-button text :icon="Link">插入参考</el-button>
                  <el-button text :icon="MagicStick" @click="fillInspiration"
                    >AI 优化描述</el-button
                  >
                </div>

                <el-button
                  class="generate-button"
                  size="large"
                  type="primary"
                  :loading="loading"
                  :disabled="!canGenerate"
                  @click="generate"
                >
                  <el-icon><MagicStick /></el-icon>
                  开始生成
                </el-button>
              </div>
            </div>
          </section>

          <!-- 上传参考素材 -->
          <section class="creator-card assets-card">
            <div class="section-head">
              <StepTitle
                :index="2"
                title="上传参考素材"
                note="（选填） 支持图片、视频、文档等格式，Agent 将参考这些素材生成游戏内容。"
              />
              <div class="asset-count">
                已上传 {{ uploadedAssets.length }}/20
                <button type="button" @click="uploadedAssets = []">清空</button>
              </div>
            </div>
            <div class="asset-layout">
              <el-upload
                drag
                multiple
                :limit="20"
                :show-file-list="false"
                :http-request="handleUpload"
                class="asset-uploader"
              >
                <div class="upload-drop">
                  <el-icon><Plus /></el-icon>
                  <strong>点击上传或拖拽到此处</strong>
                  <span
                    >支持 JPG / PNG / GIF / MP4 / WebM / PDF /
                    DOCX，单个文件不超过 100MB</span
                  >
                </div>
              </el-upload>

              <div v-if="uploadedAssets.length" class="asset-list">
                <article
                  v-for="asset in uploadedAssets"
                  :key="asset.id"
                  class="asset-card"
                >
                  <div class="asset-card__preview">
                    <img
                      v-if="isImageAsset(asset)"
                      :src="asset.url"
                      :alt="asset.filename"
                    />
                    <el-icon v-else><Document /></el-icon>
                  </div>
                  <div class="asset-card__meta">
                    <strong>{{ asset.filename }}</strong>
                    <span>{{ formatBytes(asset.sizeBytes) }}</span>
                  </div>
                  <button
                    type="button"
                    class="asset-card__remove"
                    @click="removeAsset(asset.id)"
                  >
                    <el-icon><Close /></el-icon>
                  </button>
                </article>
              </div>
            </div>
          </section>

          <!-- 任务历史 -->
          <section class="recent-task">
            <div class="recent-task__head">
              <h2>任务历史</h2>
              <el-button text :loading="historyLoading" @click="loadTaskHistory"
                >刷新</el-button
              >
            </div>
            <el-empty
              v-if="!historyLoading && tasks.length === 0"
              description="暂无生成任务"
              class="recent-task__empty"
            />
            <div v-else class="recent-task__list" v-loading="historyLoading">
              <div
                v-for="task in tasks"
                :key="task.id"
                class="recent-task__row"
              >
                <img
                  :src="
                    task.result.manifestUrl
                      ? referenceImages.playRunningImage
                      : referenceImages.createTaskImage
                  "
                  alt=""
                />
                <div class="recent-task__name">
                  <strong>{{ formatTaskTitle(task) }}</strong>
                  <span>{{ formatTaskTime(task.createdAt) }}</span>
                </div>
                <div class="recent-task__progress">
                  <span>{{ taskStatusLabel(task.status) }}</span>
                  <el-progress
                    :percentage="taskProgressFor(task)"
                    :show-text="false"
                  />
                </div>
                <div class="recent-task__model">
                  <span>结果</span>
                  <strong>{{ taskResultSummary(task) }}</strong>
                </div>
                <div class="recent-task__actions">
                  <el-button size="small" @click="viewHistoryTask(task)"
                    >查看</el-button
                  >
                  <el-button
                    v-if="canCancelTask(task)"
                    size="small"
                    type="danger"
                    plain
                    :loading="canceling"
                    @click="cancelHistoryTask(task)"
                  >
                    取消
                  </el-button>
                  <el-button
                    v-if="canRetryTask(task)"
                    size="small"
                    :loading="retrying"
                    @click="retryHistoryTask(task)"
                  >
                    重试
                  </el-button>
                </div>
              </div>
            </div>
          </section>
        </section>
      </div>
    </template>

    <!-- 生成中 -->
    <template
      v-else-if="
        currentTask.status === 'pending' || currentTask.status === 'running'
      "
    >
      <div class="task-layout">
        <section class="task-main">
          <p class="breadcrumb">Create / 生成任务</p>

          <section class="task-idea-card">
            <div class="task-idea-card__content">
              <div class="card-label">
                <el-icon><VideoPlay /></el-icon> 我的游戏创意
              </div>
              <h1>{{ taskTitle }}</h1>
              <button type="button" class="edit-icon">
                <el-icon><EditPen /></el-icon>
              </button>
              <h3>创意描述</h3>
              <p>{{ currentTask.ideaText }}</p>
              <h3>玩法类型</h3>
              <div class="tag-row">
                <span v-for="tag in taskTags" :key="tag">{{ tag }}</span>
              </div>
            </div>
            <div class="task-assets">
              <div class="task-assets__head">
                <strong>上传的素材（{{ uploadedAssets.length }}）</strong>
                <button type="button">
                  查看全部 <el-icon><ArrowRight /></el-icon>
                </button>
              </div>
              <div class="task-assets__list">
                <article v-for="asset in uploadedAssets" :key="asset.id">
                  <img
                    v-if="isImageAsset(asset)"
                    :src="asset.url"
                    :alt="asset.filename"
                  />
                  <div v-else class="file-preview">
                    <el-icon><Document /></el-icon>
                  </div>
                  <strong>{{ asset.filename }}</strong>
                  <span>{{ formatBytes(asset.sizeBytes) }}</span>
                </article>
                <div
                  v-if="uploadedAssets.length === 0"
                  class="task-assets__empty"
                >
                  未上传参考素材
                </div>
              </div>
            </div>
          </section>

          <section class="workflow-card">
            <div class="workflow-card__head">
              <h2>
                <el-icon><Box /></el-icon> AI 多智能体工作流
              </h2>
              <div class="workflow-stats">
                <span>等待中 {{ workflowCounts.waiting }}</span>
                <span class="running">运行中 {{ workflowCounts.running }}</span>
                <span class="done">已完成 {{ workflowCounts.done }}</span>
                <span class="failed">失败 {{ workflowCounts.failed }}</span>
              </div>
            </div>
            <div class="workflow-steps">
              <div
                v-for="(step, index) in workflowSteps"
                :key="step.key"
                class="workflow-step"
                :class="step.state"
              >
                <div class="workflow-step__icon">
                  <el-icon v-if="step.state === 'done'"><Check /></el-icon>
                  <el-icon
                    v-else-if="step.state === 'running'"
                    class="is-loading"
                    ><Loading
                  /></el-icon>
                  <el-icon v-else><component :is="step.icon" /></el-icon>
                </div>
                <strong>{{ step.title }}</strong>
                <span>{{ step.label }}</span>
                <i v-if="index < workflowSteps.length - 1" />
              </div>
            </div>
            <div class="workflow-progress">
              <span>总体进度</span>
              <el-progress :percentage="taskProgress" :show-text="false" />
              <strong>{{ taskProgress }}%</strong>
            </div>
            <div class="current-step">
              <span>当前步骤</span>
              <strong
                ><el-icon><VideoPlay /></el-icon>
                {{ currentWorkflowStep?.title || "准备中" }}</strong
              >
              <p>
                {{
                  currentWorkflowStep?.description || "Agent 正在准备生成任务。"
                }}
              </p>
              <em>预计剩余时间 8 分钟</em>
            </div>
          </section>

          <section class="log-card">
            <div class="log-card__head">
              <h2>智能体执行日志</h2>
              <div>
                <span>实时日志</span><el-switch v-model="realtimeLogs" />
              </div>
            </div>
            <div class="log-list">
              <article
                v-for="item in executionCards"
                :key="item.key"
                :class="{ active: item.state === 'running' }"
              >
                <div class="log-list__top">
                  <strong
                    ><el-icon><CircleCheckFilled /></el-icon>
                    {{ item.title }}</strong
                  >
                  <span>{{ item.duration }}</span>
                </div>
                <p>{{ item.message }}</p>
                <div class="log-list__bottom">
                  <span>{{ item.output }}</span>
                  <button type="button">查看详情</button>
                </div>
              </article>
            </div>
            <button type="button" class="expand-logs">
              展开实时日志 <el-icon><ArrowDown /></el-icon>
            </button>
          </section>
        </section>

        <aside class="task-side">
          <section class="side-card">
            <h2>任务信息</h2>
            <InfoList :rows="taskInfoRows" />
          </section>
          <section class="side-card">
            <h2><span class="fire-dot">●</span> 资源消耗</h2>
            <InfoList :rows="resourceRows" />
          </section>
          <section class="side-card">
            <h2>生成产物（预测）</h2>
            <div class="artifact-grid">
              <div v-for="artifact in artifactCards" :key="artifact.name">
                <el-icon><component :is="artifact.icon" /></el-icon>
                <strong>{{ artifact.name }}</strong>
                <span>{{ artifact.status }}</span>
              </div>
            </div>
          </section>
          <div class="task-side__actions">
            <el-button
              type="danger"
              plain
              :loading="canceling"
              @click="cancelCurrent"
              >终止任务</el-button
            >
            <el-button :loading="retrying" @click="regenerate"
              >重新生成</el-button
            >
            <el-button disabled>预览（不可用）</el-button>
          </div>
          <p class="task-side__note">终止任务会在当前 Agent 步骤结束后停止</p>
        </aside>
      </div>
    </template>

    <!-- 生成成功 -->
    <template v-else-if="currentTask.status === 'succeeded'">
      <div class="publish-layout">
        <section class="publish-main">
          <section class="success-banner">
            <div>
              <span>生成完成</span>
              <div>
                <h1>恭喜！你的游戏已生成完成</h1>
                <p>
                  预览游戏效果，完善信息后即可发布，让更多玩家体验你的作品。
                </p>
              </div>
            </div>
            <div class="success-banner__actions">
              <el-button @click="backToEdit">再次编辑</el-button>
              <el-button @click="regenerate">重新生成</el-button>
              <el-button
                class="publish-button"
                :loading="publishing"
                @click="publish"
                >发布到首页</el-button
              >
            </div>
          </section>

          <section class="preview-card">
            <div class="preview-actions">
              <h2>游戏预览</h2>
              <p>预览为实时运行版本，部分效果可能因设备性能有所差异。</p>
            </div>
            <RemoteGameFrame
              v-if="previewManifest"
              :manifest="previewManifest"
            />
            <div v-else class="preview-loading">
              <el-icon class="is-loading"><Loading /></el-icon>
              正在加载预览...
            </div>
          </section>
        </section>

        <!-- 侧边栏 -->
        <aside class="publish-side">
          <section class="publish-card">
            <h2>发布信息</h2>
            <el-form label-position="top" class="publish-form">
              <el-form-item label="游戏标题">
                <el-input
                  v-model="publishTitle"
                  maxlength="60"
                  show-word-limit
                />
              </el-form-item>
              <el-form-item label="封面">
                <div class="cover-field">
                  <img :src="referenceImages.playRunningImage" alt="" />
                  <div>
                    <el-button>更换封面</el-button>
                    <p>建议尺寸：16:9，JPG/PNG，≤5MB</p>
                  </div>
                </div>
              </el-form-item>
              <el-form-item label="游戏描述">
                <el-input
                  v-model="publishDescription"
                  type="textarea"
                  :rows="4"
                  maxlength="300"
                  show-word-limit
                />
              </el-form-item>
              <el-form-item label="标签">
                <div class="publish-tags">
                  <el-tag v-for="tag in publishTags" :key="tag" closable>{{
                    tag
                  }}</el-tag>
                  <el-button size="small" :icon="Plus">添加标签</el-button>
                </div>
              </el-form-item>
            </el-form>
          </section>

          <section class="publish-card">
            <h2>版本与构建信息</h2>
            <div class="build-info">
              <div v-for="row in buildInfoRows" :key="row.label">
                <span>{{ row.label }}</span>
                <strong>{{ row.value }}</strong>
                <el-button
                  v-if="row.copy"
                  :icon="CopyDocument"
                  circle
                  size="small"
                  @click="copyText(row.value)"
                />
              </div>
            </div>
          </section>
        </aside>
      </div>
    </template>

    <!-- 生成失败 -->
    <template v-else>
      <section class="creator-card error-state">
        <el-alert
          :type="currentTask.status === 'canceled' ? 'warning' : 'error'"
          :title="terminalStateTitle"
          :closable="false"
          show-icon
        >
          {{ terminalStateMessage }}
        </el-alert>
        <div class="terminal-actions">
          <el-button type="primary" :loading="retrying" @click="regenerate"
            >重试任务</el-button
          >
          <el-button @click="backToEdit">返回编辑</el-button>
        </div>
      </section>
    </template>
  </main>
</template>

<script setup lang="ts">
import {
  Aim,
  ArrowDown,
  ArrowRight,
  Box,
  Check,
  CircleCheckFilled,
  Close,
  Cloudy,
  Compass,
  CopyDocument,
  DataLine,
  Document,
  EditPen,
  Finished,
  Flag,
  FullScreen,
  Guide,
  Link,
  Loading,
  MagicStick,
  MoreFilled,
  Open,
  Picture,
  Plus,
  Promotion,
  Refresh,
  Setting,
  Tools,
  User,
  VideoPlay,
  View,
  Wallet,
} from "@element-plus/icons-vue";
import { ElMessage, type UploadRequestOptions } from "element-plus";
import { storeToRefs } from "pinia";
import {
  computed,
  defineComponent,
  h,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
  type Component,
} from "vue";

import { uploadAsset, type AssetResponse } from "@/api/assets";
import type { AgentLogResponse, GenerationTaskResponse } from "@/api/tasks";
import type { GameManifest } from "@/api/types";
import RemoteGameFrame from "@/components/game/RemoteGameFrame.vue";
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
const gameType = ref("RPG 角色扮演");
const duration = ref("short");
const artStyle = ref("realistic");
const language = ref("zh-CN");
const model = ref("game-v1");
const workflow = ref("standard");
const publishTitle = ref("迷雾之城：冥歌");
const publishDescription = ref(
  "在迷雾与诅咒笼罩的古城中探寻真相，你的选择将决定众人的命运。",
);
const publishTags = ref(["角色扮演", "剧情", "暗黑奇幻", "单机"]);
const publishMode = ref("now");
const visibility = ref("public");
const inspirationOffset = ref(0);
const realtimeLogs = ref(true);

const gameTypeOptions = [
  "RPG 角色扮演",
  "ACT 动作",
  "AVG 冒险解谜",
  "SLG 策略",
  "SIM 模拟经营",
  "RAC 竞速",
  "PUZ 益智",
  "其它",
];
const durationOptions = [
  { label: "短（15-15 分钟）", value: "short" },
  { label: "中（15-60 分钟）", value: "medium" },
  { label: "长（60 分钟以上）", value: "long" },
];
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
const resultSteps = [
  { title: "预览可用", summary: "游戏已成功运行，可完整预览体验" },
  { title: "资源已上传 OSS", summary: "资源包已安全上传，访问正常" },
  { title: "元数据已就绪", summary: "元数据已准备，等待写入数据库" },
];

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
    const state =
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

function rotateInspirations() {
  inspirationOffset.value = (inspirationOffset.value + 1) % inspirations.length;
}

function removeAsset(assetId: string) {
  uploadedAssets.value = uploadedAssets.value.filter(
    (asset) => asset.id !== assetId,
  );
}

function resetForm() {
  idea.value = "";
  uploadedAssets.value = [];
  gameType.value = "RPG 角色扮演";
  duration.value = "short";
  artStyle.value = "realistic";
  language.value = "zh-CN";
  model.value = "game-v1";
  workflow.value = "standard";
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

function resetAll() {
  resetForm();
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

const StepTitle = defineComponent({
  props: {
    index: { type: Number, required: true },
    title: { type: String, required: true },
    note: { type: String, default: "" },
  },
  setup(props) {
    return () =>
      h("div", { class: "step-title" }, [
        h("span", { class: "step-title__index" }, props.index),
        h("div", [
          h("h2", props.title),
          props.note ? h("p", props.note) : null,
        ]),
      ]);
  },
});

const InfoList = defineComponent({
  props: {
    rows: { type: Array as () => InfoRow[], required: true },
  },
  setup(props) {
    return () =>
      h(
        "div",
        { class: "info-list" },
        props.rows.map((row) =>
          h("div", { class: "info-list__row" }, [
            h("span", row.label),
            h("strong", row.value),
            row.copy
              ? h(
                  "button",
                  { type: "button", onClick: () => copyText(row.value) },
                  [h(CopyDocument)],
                )
              : null,
          ]),
        ),
      );
  },
});

onBeforeUnmount(() => createTask.stopPolling());
</script>

<style scoped>
.create-page {
  max-width: 1800px;
  margin: 0 auto;
  padding: 28px 44px 34px;
  color: #1e293b;
}

.create-hero,
.create-grid,
.task-layout,
.publish-layout {
  position: relative;
}

.create-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 22px;
}

.create-hero h1 {
  margin: 0;
  color: #0f172a;
  font-size: 32px;
  font-weight: 800;
}

.create-hero p {
  margin: 10px 0 0;
  color: #64748b;
  font-size: 15px;
}

.guide-button {
  border-color: #c4b5fd;
  color: #5b4dff;
  font-weight: 700;
}

.create-grid,
.task-layout,
.publish-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 390px;
  gap: 24px;
  align-items: start;
}

.create-main,
.task-main,
.publish-main,
.publish-side {
  display: grid;
  gap: 16px;
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
  padding: 20px;
}

.step-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.step-title__index {
  display: grid;
  width: 26px;
  height: 26px;
  flex: 0 0 auto;
  place-items: center;
  border-radius: 999px;
  background: linear-gradient(135deg, #4664ff, #7d4cff);
  color: #fff;
  font-size: 14px;
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

.prompt-box {
  position: relative;
  margin-top: 16px;
  border: 1px solid #d7dfec;
  border-radius: 10px;
  background: #fff;
  min-height: 260px;
  overflow: hidden;
}

.prompt-input {
  height: 260px;
}

.prompt-input :deep(.el-textarea__inner) {
  min-height: 260px !important;
  border: 0 !important;
  box-shadow: none !important;
  padding: 18px 20px 54px;
  color: #334155;
  font-size: 14px;
  line-height: 1.8;
}

.prompt-hints {
  position: absolute;
  top: 52px;
  left: 20px;
  display: grid;
  gap: 10px;
  pointer-events: none;
  color: #94a3b8;
  font-size: 13px;
}

.prompt-hints p {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}

.prompt-actions {
  position: absolute;
  right: 14px;
  bottom: 12px;
  left: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  border-top: 1px solid transparent;
}

.prompt-actions__left,
.prompt-actions__right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.prompt-actions__right span {
  color: #94a3b8;
  font-size: 12px;
}

.prompt-send {
  border: 0;
  background: linear-gradient(135deg, #6674ff, #8a4dff);
  color: #fff;
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
  grid-template-columns: 420px minmax(0, 1fr);
  gap: 16px;
  margin-top: 16px;
}

.asset-uploader :deep(.el-upload-dragger) {
  display: grid;
  min-height: 156px;
  place-items: center;
  border: 1px dashed #9f8cff;
  border-radius: 10px;
  background: #fff;
}

.upload-drop {
  display: grid;
  place-items: center;
  gap: 10px;
  color: #64748b;
}

.upload-drop .el-icon {
  color: #694cff;
  font-size: 30px;
}

.upload-drop span {
  color: #94a3b8;
  font-size: 12px;
}

.asset-list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.asset-card {
  position: relative;
  overflow: hidden;
  border: 1px solid #dce4f0;
  border-radius: 9px;
  background: #fff;
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
  padding: 10px 34px 12px 12px;
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

.generate-button,
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
</style>
