<template>
  <section class="rounded-2xl border border-emerald-200 bg-emerald-50 p-5">
    <div class="flex flex-wrap items-center justify-between gap-4">
      <div>
        <p class="m-0 text-xs font-black uppercase tracking-[0.24em] text-emerald-600">Ready to publish</p>
        <h3 class="mt-2 text-2xl font-black text-slate-950">{{ task.result.gameId ? '预览已生成' : '生成完成' }}</h3>
        <p class="mt-2 break-all text-sm leading-6 text-slate-600">{{ task.result.manifestUrl }}</p>
      </div>
      <div class="flex flex-wrap gap-3">
        <el-button :loading="publishing" class="agent-gradient-button" type="primary" @click="emit('publish')">发布到首页</el-button>
        <el-button v-if="task.result.gameId" plain @click="emit('play', task.result.gameId)">打开游戏</el-button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { GenerationTaskResponse } from '@/api/tasks'

defineProps<{
  task: GenerationTaskResponse
  publishing: boolean
}>()

const emit = defineEmits<{
  publish: []
  play: [gameId: string]
}>()
</script>
