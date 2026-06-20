<template>
  <div class="space-y-4">
    <el-alert v-if="error" type="error" title="远程游戏加载失败" :closable="false" show-icon>
      {{ error }}
    </el-alert>

    <div v-else class="relative overflow-hidden rounded-lg border border-slate-200 bg-slate-950 shadow-sm">
      <div class="absolute inset-x-0 top-0 z-10 flex items-center justify-between bg-black/35 px-5 py-3 text-xs font-semibold uppercase tracking-[0.16em] text-white/80 backdrop-blur">
        <span>AgentPlay Runtime</span>
        <span>{{ statusText }}</span>
      </div>
      <iframe
        v-if="manifest"
        ref="frameRef"
        class="h-[68vh] min-h-[560px] w-full border-0 pt-10"
        sandbox="allow-scripts"
        :src="manifest.entryUrl"
        :title="manifest.title"
      />
      <div v-else class="relative flex h-[68vh] min-h-[560px] flex-col items-center justify-center gap-5 overflow-hidden">
        <img :src="referenceImages.playLoadingImage" alt="" class="absolute inset-0 h-full w-full object-cover object-left-top opacity-35" />
        <div class="relative z-10 text-center text-white">
          <div class="mx-auto mb-6 grid h-20 w-20 place-items-center rounded-full bg-white/10 backdrop-blur">
            <el-icon class="is-loading" size="38"><Loading /></el-icon>
          </div>
          <h3 class="m-0 text-3xl font-semibold">正在加载游戏...</h3>
          <p class="mt-4 text-sm text-white/70">首次加载可能需要一些时间，请稍候。</p>
        </div>
      </div>
    </div>

    <div class="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-600">
      <span>运行状态：<strong>{{ statusText }}</strong></span>
      <div class="flex gap-2">
        <el-button size="small" :icon="Refresh" @click="restart">重新开始</el-button>
        <el-button size="small" :icon="FullScreen">全屏</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { FullScreen, Loading, Refresh } from '@element-plus/icons-vue'
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import type { GameManifest } from '@/api/types'
import { referenceImages } from '@/data/showcase'

const props = defineProps<{
  manifest: GameManifest | null
  error?: string | null
}>()

const frameRef = ref<HTMLIFrameElement | null>(null)
const gameStatus = ref<'loading' | 'ready' | 'completed' | 'error'>('loading')

const statusText = computed(() => {
  if (props.error) return '加载失败'
  if (gameStatus.value === 'ready') return '就绪'
  if (gameStatus.value === 'completed') return '已完成'
  if (gameStatus.value === 'error') return '运行错误'
  return '加载中'
})

watch(() => props.manifest?.entryUrl, () => {
  gameStatus.value = 'loading'
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
