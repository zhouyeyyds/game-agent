<template>
  <div class="space-y-5">
    <div class="grid grid-cols-2 gap-4 md:grid-cols-4 xl:grid-cols-8">
      <div v-for="(item, index) in items" :key="item.key" class="text-center">
        <div
          class="mx-auto grid h-11 w-11 place-items-center rounded-full border text-sm font-black"
          :class="itemClasses(item)"
        >
          <el-icon v-if="item.state === 'done'"><Check /></el-icon>
          <el-icon v-else-if="item.state === 'running'" class="is-loading"><Loading /></el-icon>
          <span v-else>{{ index + 1 }}</span>
        </div>
        <p class="mt-2 text-xs font-black" :class="item.state === 'running' ? 'text-indigo-600' : 'text-slate-700'">{{ item.title }}</p>
        <p class="m-0 text-xs text-slate-400">{{ item.label }}</p>
      </div>
    </div>
    <div class="flex items-center gap-4">
      <span class="text-sm text-slate-500">总体进度</span>
      <el-progress class="flex-1" :percentage="progress" :show-text="false" />
      <span class="text-sm font-black text-slate-700">{{ progress }}%</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Check, Loading } from '@element-plus/icons-vue'
import { computed } from 'vue'

import { generationSteps } from '@/data/showcase'

const props = defineProps<{
  status: 'idle' | 'pending' | 'running' | 'succeeded' | 'failed'
  currentStep?: string | null
}>()

const stepKeys = ['idea', 'spec', 'render', 'upload', 'ready', 'build', 'storage', 'db']

const currentIndex = computed(() => {
  const index = stepKeys.indexOf(props.currentStep || '')
  if (props.status === 'succeeded') return generationSteps.length - 1
  return index >= 0 ? index : props.status === 'pending' ? 0 : 3
})

const progress = computed(() => {
  if (props.status === 'succeeded') return 100
  if (props.status === 'failed') return Math.max(12, Math.round(((currentIndex.value + 1) / generationSteps.length) * 100))
  return Math.round(((currentIndex.value + 1) / generationSteps.length) * 100)
})

const items = computed(() => generationSteps.map((title, index) => ({
  key: stepKeys[index] || title,
  title,
  label: index < currentIndex.value || props.status === 'succeeded' ? '已完成' : index === currentIndex.value ? '运行中' : '等待中',
  state: index < currentIndex.value || props.status === 'succeeded' ? 'done' : index === currentIndex.value ? 'running' : 'waiting',
})))

function itemClasses(item: { state: string }) {
  if (item.state === 'done') return 'border-emerald-400 bg-emerald-500 text-white'
  if (item.state === 'running') return 'border-indigo-500 bg-indigo-600 text-white shadow-lg shadow-indigo-500/25'
  return 'border-slate-200 bg-slate-100 text-slate-400'
}
</script>
