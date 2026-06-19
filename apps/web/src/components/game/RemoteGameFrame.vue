<template>
  <div class="space-y-4">
    <NAlert v-if="error" type="error" title="游戏加载失败">
      {{ error }}
    </NAlert>

    <div v-else class="overflow-hidden rounded-2xl border border-white/10 bg-black shadow-2xl">
      <iframe
        v-if="manifest"
        ref="frameRef"
        class="h-[640px] w-full border-0"
        sandbox="allow-scripts"
        :src="manifest.entryUrl"
        :title="manifest.title"
      />
      <div v-else class="flex h-[640px] items-center justify-center">
        <NSpin size="large" />
      </div>
    </div>

    <div class="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-300">
      <span>状态：{{ statusText }}</span>
      <NButton size="small" @click="restart">重新开始</NButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { NAlert, NButton, NSpin } from 'naive-ui'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

import type { GameManifest } from '@/api/types'

const props = defineProps<{
  manifest: GameManifest | null
  error?: string | null
}>()

const frameRef = ref<HTMLIFrameElement | null>(null)
const gameStatus = ref<'loading' | 'ready' | 'completed' | 'error'>('loading')

const statusText = computed(() => {
  if (props.error) return '加载失败'
  if (gameStatus.value === 'ready') return '游戏已就绪'
  if (gameStatus.value === 'completed') return '游戏已结束'
  if (gameStatus.value === 'error') return '游戏运行错误'
  return '加载中'
})

function handleMessage(event: MessageEvent) {
  const data = event.data as { type?: string }
  if (!data || typeof data.type !== 'string') return

  if (data.type === 'game.ready') {
    gameStatus.value = 'ready'
  }

  if (data.type === 'game.completed') {
    gameStatus.value = 'completed'
  }

  if (data.type === 'game.error') {
    gameStatus.value = 'error'
  }
}

function restart() {
  frameRef.value?.contentWindow?.postMessage({ type: 'game.restart' }, '*')
  gameStatus.value = 'loading'
}

onMounted(() => window.addEventListener('message', handleMessage))
onBeforeUnmount(() => window.removeEventListener('message', handleMessage))
</script>
