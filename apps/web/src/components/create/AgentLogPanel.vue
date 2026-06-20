<template>
  <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
    <el-empty v-if="logs.length === 0" description="Agent logs will appear after generation starts" class="md:col-span-2 xl:col-span-4" />
    <article v-for="log in logs" :key="log.id" class="rounded-2xl border border-slate-200 bg-white p-4">
      <div class="mb-3 flex items-center justify-between gap-3">
        <el-tag :type="tagType(log.level)" size="small" round>{{ log.nodeName }}</el-tag>
        <span class="text-xs text-slate-400">{{ formatTime(log.createdAt) }}</span>
      </div>
      <p class="m-0 line-clamp-3 text-sm leading-6 text-slate-600">{{ log.message }}</p>
    </article>
  </div>
</template>

<script setup lang="ts">
import type { AgentLogResponse } from '@/api/tasks'

defineProps<{
  logs: AgentLogResponse[]
}>()

function tagType(level: AgentLogResponse['level']) {
  if (level === 'error') return 'danger'
  if (level === 'warning') return 'warning'
  if (level === 'debug') return 'info'
  return 'success'
}

function formatTime(value: string) {
  return new Date(value).toLocaleTimeString()
}
</script>
