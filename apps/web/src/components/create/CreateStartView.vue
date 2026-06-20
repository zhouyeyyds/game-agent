<template>
  <div class="create-grid">
    <section class="create-main">
      <section class="creator-card prompt-card">
        <StepTitle :index="1" title="说出你的游戏想法" />
        <div class="prompt-box">
          <el-input
            v-model="idea"
            type="textarea"
            maxlength="3000"
            resize="none"
            class="prompt-input"
          />
          <div v-if="!idea" class="prompt-hints mb-10">
            <p class="prompt-hints__lead">
              尽可能详细地描述你的游戏创意，Agent 会理解并生成完整的游戏内容。
            </p>
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
              <el-icon><Aim /></el-icon> 胜利 / 失败条件：例如通关条件、失败判定
            </p>
            <p>
              <el-icon><Picture /></el-icon>
              参考素材：可描述如何使用上传的图片 / 文件 / 视频作为参考
            </p>
          </div>
          <div class="prompt-actions mt-sm">
            <div class="prompt-actions__left">
              <el-button
                text
                :icon="MagicStick"
                class="prompt-ai-button"
                @click="emit('optimize-description')"
              >
                AI 优化描述
              </el-button>
            </div>

            <div class="prompt-actions__right">
              <span>{{ idea.length }}/3000</span>
              <el-button
                class="generate-button"
                type="primary"
                :loading="loading"
                :disabled="!canGenerate"
                @click="emit('generate')"
              >
                <el-icon><Promotion /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </section>

      <section class="creator-card assets-card">
        <div class="section-head">
          <StepTitle
            :index="2"
            title="上传参考素材"
            note="（选填） 支持图片、视频、文档等格式，Agent 将参考这些素材生成游戏内容。"
          />
          <div class="asset-count">
            已上传 {{ uploadedAssets.length }}/20
            <button type="button" @click="emit('clear-assets')">清空</button>
          </div>
        </div>
        <div class="asset-layout">
          <el-upload
            drag
            multiple
            accept="image/png,image/jpeg,image/webp,image/gif,video/mp4,video/webm,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain,application/json"
            :limit="20"
            :show-file-list="false"
            :http-request="handleUpload"
            class="asset-uploader"
          >
            <div class="upload-drop">
              <el-icon><Plus /></el-icon>
              <strong>点击上传或拖拽到此处</strong>
              <span
                >支持 JPG / PNG / GIF / MP4 / WebM / PDF / DOCX，单个文件不超过
                100MB</span
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
                @click="emit('remove-asset', asset.id)"
              >
                <el-icon><Close /></el-icon>
              </button>
            </article>
          </div>
        </div>
      </section>

      <section class="recent-task">
        <div class="recent-task__head">
          <h2>任务历史</h2>
          <el-button
            text
            :loading="historyLoading"
            @click="emit('load-history')"
            >刷新</el-button
          >
        </div>
        <el-empty
          v-if="!historyLoading && tasks.length === 0"
          description="暂无生成任务"
          class="recent-task__empty"
        />
        <div v-else class="recent-task__list" v-loading="historyLoading">
          <div v-for="task in tasks" :key="task.id" class="recent-task__row">
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
              <el-button
                size="small"
                class="history-action-button history-action-button--primary"
                @click="emit('view-history-task', task)"
                >详情</el-button
              >
              <el-button
                v-if="canRetryTask(task)"
                size="small"
                class="history-action-button history-action-button--primary"
                :loading="retrying"
                @click="emit('retry-history-task', task)"
              >
                重新生成
              </el-button>
              <el-button
                v-if="canDeleteTask(task)"
                size="small"
                class="history-action-button history-action-button--danger"
                :loading="deletingTaskId === task.id"
                @click="emit('delete-history-task', task)"
              >
                删除
              </el-button>
            </div>
          </div>
        </div>
      </section>
    </section>
  </div>
</template>

<script setup lang="ts">
import {
  Aim,
  CircleCheckFilled,
  Close,
  Compass,
  Document,
  Flag,
  MagicStick,
  Picture,
  Plus,
  Promotion,
  Tools,
  User,
} from "@element-plus/icons-vue";
import type { UploadRequestOptions } from "element-plus";
import { defineComponent, h } from "vue";

import type { AssetResponse } from "@/api/assets";
import type { GenerationTaskResponse } from "@/api/tasks";
import { referenceImages } from "@/data/showcase";

const idea = defineModel<string>("idea", { default: "" });

defineProps<{
  uploadedAssets: AssetResponse[];
  tasks: GenerationTaskResponse[];
  loading: boolean;
  historyLoading: boolean;
  retrying: boolean;
  deletingTaskId: string | null;
  canGenerate: boolean;
  isImageAsset: (asset: AssetResponse) => boolean;
  formatBytes: (value: number) => string;
  formatTaskTitle: (task: GenerationTaskResponse) => string;
  formatTaskTime: (value: string | null) => string;
  taskStatusLabel: (status: GenerationTaskResponse["status"]) => string;
  taskProgressFor: (task: GenerationTaskResponse) => number;
  taskResultSummary: (task: GenerationTaskResponse) => string;
  canRetryTask: (task: GenerationTaskResponse) => boolean;
  canDeleteTask: (task: GenerationTaskResponse) => boolean;
}>();

const emit = defineEmits<{
  "optimize-description": [];
  generate: [];
  upload: [options: UploadRequestOptions];
  "clear-assets": [];
  "remove-asset": [assetId: string];
  "load-history": [];
  "view-history-task": [task: GenerationTaskResponse];
  "cancel-history-task": [task: GenerationTaskResponse];
  "retry-history-task": [task: GenerationTaskResponse];
  "delete-history-task": [task: GenerationTaskResponse];
}>();

function handleUpload(options: UploadRequestOptions) {
  emit("upload", options);
}

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
</script>
