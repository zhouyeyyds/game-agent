<template>
  <div class="publish-layout">
    <section class="publish-main">
      <div class="task-view-head">
        <p class="breadcrumb">Create / 生成完成</p>
        <el-button text @click="emit('back-to-create')">返回创建中心</el-button>
      </div>

      <section class="success-banner">
        <div class="success-banner__content">
          <span class="success-banner__badge">
            <i><el-icon><Check /></el-icon></i>
            生成完成
          </span>
          <div class="success-banner__copy">
            <h1>恭喜！你的游戏已生成完成</h1>
            <p>预览游戏效果，完善信息后即可发布，让更多玩家体验你的作品。</p>
          </div>
        </div>
        <div class="success-banner__actions">
          <el-button @click="emit('back-to-edit')">再次编辑</el-button>
          <el-button @click="emit('regenerate')">重新生成</el-button>
          <el-button
            class="publish-button"
            :loading="publishing"
            @click="emit('publish')"
            >发布到首页</el-button
          >
        </div>
      </section>

      <section class="preview-card">
        <div class="preview-actions">
          <h2>游戏预览</h2>
          <p>预览为实时运行版本，部分效果可能因设备性能有所差异。</p>
        </div>
        <RemoteGameFrame v-if="previewManifest" :manifest="previewManifest" />
        <div v-else class="preview-loading">
          <el-icon class="is-loading"><Loading /></el-icon>
          正在加载预览...
        </div>
      </section>
    </section>

    <aside class="publish-side">
      <section class="publish-card">
        <h2>发布信息</h2>
        <el-form label-position="top" class="publish-form">
          <el-form-item label="游戏标题">
            <el-input v-model="publishTitle" maxlength="60" show-word-limit />
          </el-form-item>
          <el-form-item label="封面">
            <div class="cover-field">
              <img :src="coverUrl" alt="" />
              <div>
                <el-upload
                  accept="image/*"
                  :auto-upload="false"
                  :show-file-list="false"
                  :on-change="handleCoverChange"
                >
                  <el-button :loading="coverUploading">更换封面</el-button>
                </el-upload>
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
              <el-tag
                v-for="tag in publishTags"
                :key="tag"
                closable
                @close="emit('remove-tag', tag)"
              >
                {{ tag }}
              </el-tag>
              <el-input
                v-if="addingTag"
                ref="tagInputRef"
                v-model="draftTag"
                class="publish-tags__input"
                size="small"
                maxlength="12"
                @keyup.enter="submitTag"
                @blur="submitTag"
              />
              <el-button
                v-else
                size="small"
                :icon="Plus"
                @click="showTagInput"
              >
                添加标签
              </el-button>
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
              @click="emit('copy', row.value)"
            />
          </div>
        </div>
      </section>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { Check, CopyDocument, Loading, Plus } from "@element-plus/icons-vue";
import type { UploadFile } from "element-plus";
import { nextTick, ref } from "vue";

import type { GameManifest } from "@/api/types";
import RemoteGameFrame from "@/components/game/RemoteGameFrame.vue";

interface InfoRow {
  label: string;
  value: string;
  copy?: boolean;
}

const publishTitle = defineModel<string>("publishTitle", { default: "" });
const publishDescription = defineModel<string>("publishDescription", {
  default: "",
});

defineProps<{
  previewManifest: GameManifest | null;
  coverUrl: string;
  coverUploading: boolean;
  publishTags: string[];
  buildInfoRows: InfoRow[];
  publishing: boolean;
}>();

const emit = defineEmits<{
  "back-to-create": [];
  "back-to-edit": [];
  regenerate: [];
  publish: [];
  copy: [value: string];
  "upload-cover": [file: File];
  "add-tag": [tag: string];
  "remove-tag": [tag: string];
}>();

const addingTag = ref(false);
const draftTag = ref("");
const tagInputRef = ref<HTMLInputElement | null>(null);

function handleCoverChange(uploadFile: UploadFile) {
  const file = uploadFile.raw;
  if (!file || !file.type.startsWith("image/")) return;
  emit("upload-cover", file);
}

async function showTagInput() {
  addingTag.value = true;
  await nextTick();
  tagInputRef.value?.focus?.();
}

function submitTag() {
  const tag = draftTag.value.trim();
  if (tag) emit("add-tag", tag);
  draftTag.value = "";
  addingTag.value = false;
}
</script>
