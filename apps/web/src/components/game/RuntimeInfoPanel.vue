<template>
  <section class="agent-card p-5">
    <div class="mb-4 flex items-center justify-between">
      <h2 class="m-0 text-lg font-black text-slate-950">远程资源信息</h2>
      <el-tag type="success" round>加载成功</el-tag>
    </div>
    <div class="space-y-4 text-sm">
      <div class="grid grid-cols-[110px_1fr_auto] items-center gap-3">
        <span class="text-slate-500">Manifest URL</span>
        <span class="truncate rounded-lg bg-slate-50 px-3 py-2 font-medium text-slate-700">{{ descriptor.manifestUrl }}</span>
        <el-button :icon="CopyDocument" circle size="small" />
      </div>
      <div class="grid grid-cols-[110px_1fr] gap-3">
        <span class="text-slate-500">Runtime</span>
        <span class="font-medium text-slate-700">{{ descriptor.runtime }}</span>
      </div>
      <div class="grid grid-cols-[110px_1fr] gap-3">
        <span class="text-slate-500">Storage</span>
        <span class="break-all font-medium text-slate-700">{{ descriptor.storagePrefix }}</span>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { CopyDocument } from '@element-plus/icons-vue'

import type { PlayDescriptor } from '@/api/types'

defineProps<{
  descriptor: PlayDescriptor
}>()
</script>
