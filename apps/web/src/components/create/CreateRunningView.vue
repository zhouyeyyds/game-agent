<template>
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
          <p>{{ task.ideaText }}</p>
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
            <div v-if="uploadedAssets.length === 0" class="task-assets__empty">
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
              <el-icon v-else-if="step.state === 'running'" class="is-loading"
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
            {{ currentWorkflowStep?.description || "Agent 正在准备生成任务。" }}
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
        <InfoList :rows="taskInfoRows" @copy="emit('copy', $event)" />
      </section>
      <section class="side-card">
        <h2><span class="fire-dot">●</span> 资源消耗</h2>
        <InfoList :rows="resourceRows" @copy="emit('copy', $event)" />
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
          @click="emit('cancel-current')"
          >终止任务</el-button
        >
        <el-button :loading="retrying" @click="emit('regenerate')"
          >重新生成</el-button
        >
        <el-button disabled>预览（不可用）</el-button>
      </div>
      <p class="task-side__note">终止任务会在当前 Agent 步骤结束后停止</p>
    </aside>
  </div>
</template>

<script setup lang="ts">
import {
  ArrowDown,
  ArrowRight,
  Box,
  Check,
  CircleCheckFilled,
  CopyDocument,
  Document,
  EditPen,
  Loading,
  VideoPlay,
} from "@element-plus/icons-vue";
import { defineComponent, h, type Component } from "vue";

import type { AssetResponse } from "@/api/assets";
import type { GenerationTaskResponse } from "@/api/tasks";

interface InfoRow {
  label: string;
  value: string;
  copy?: boolean;
}

interface WorkflowStep {
  key: string;
  title: string;
  icon: Component;
  description: string;
  state: "done" | "running" | "failed" | "waiting";
  label: string;
}

interface WorkflowCounts {
  waiting: number;
  running: number;
  done: number;
  failed: number;
}

interface ExecutionCard {
  key: string;
  title: string;
  duration: string;
  message: string;
  output: string;
  state: string;
}

interface ArtifactCard {
  name: string;
  status: string;
  icon: Component;
}

const realtimeLogs = defineModel<boolean>("realtimeLogs", { default: true });

defineProps<{
  task: GenerationTaskResponse;
  taskTitle: string;
  taskTags: string[];
  uploadedAssets: AssetResponse[];
  workflowSteps: WorkflowStep[];
  workflowCounts: WorkflowCounts;
  currentWorkflowStep?: WorkflowStep;
  taskProgress: number;
  executionCards: ExecutionCard[];
  taskInfoRows: InfoRow[];
  resourceRows: InfoRow[];
  artifactCards: ArtifactCard[];
  canceling: boolean;
  retrying: boolean;
  isImageAsset: (asset: AssetResponse) => boolean;
  formatBytes: (value: number) => string;
}>();

const emit = defineEmits<{
  "cancel-current": [];
  regenerate: [];
  copy: [value: string];
}>();

const InfoList = defineComponent({
  props: {
    rows: { type: Array as () => InfoRow[], required: true },
  },
  emits: {
    copy: (_value: string) => true,
  },
  setup(props, { emit }) {
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
                  { type: "button", onClick: () => emit("copy", row.value) },
                  [h(CopyDocument)],
                )
              : null,
          ]),
        ),
      );
  },
});
</script>
