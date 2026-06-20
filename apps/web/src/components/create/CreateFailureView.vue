<template>
  <section class="creator-card error-state">
    <el-alert
      :type="status === 'canceled' ? 'warning' : 'error'"
      :title="title"
      :closable="false"
      show-icon
    >
      {{ message }}
    </el-alert>
    <div class="terminal-actions">
      <el-button type="primary" :loading="retrying" @click="emit('regenerate')"
        >重试任务</el-button
      >
      <el-button @click="emit('back-to-edit')">返回编辑</el-button>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { GenerationTaskResponse } from "@/api/tasks";

defineProps<{
  status: GenerationTaskResponse["status"];
  title: string;
  message: string;
  retrying: boolean;
}>();

const emit = defineEmits<{
  regenerate: [];
  "back-to-edit": [];
}>();
</script>
