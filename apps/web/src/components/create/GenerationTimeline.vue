<template>
  <NTimeline>
    <NTimelineItem
      v-for="item in items"
      :key="item.key"
      :type="item.type"
      :title="item.title"
      :content="item.content"
    />
  </NTimeline>
</template>

<script setup lang="ts">
import { NTimeline, NTimelineItem } from 'naive-ui'
import { computed } from 'vue'

const props = defineProps<{
  status: 'idle' | 'pending' | 'running' | 'succeeded' | 'failed'
  currentStep?: string | null
}>()

const steps = [
  ['idea', '创意分析'],
  ['spec', 'GameSpec 生成'],
  ['render', '模板渲染'],
  ['upload', '上传产物'],
  ['ready', '预览发布'],
] as const

const items = computed(() => steps.map(([key, title]) => ({
  key,
  title,
  content: props.currentStep === key ? '进行中' : '',
  type: props.status === 'failed' && props.currentStep === key ? 'error' : props.status === 'succeeded' ? 'success' : 'info',
})))
</script>
