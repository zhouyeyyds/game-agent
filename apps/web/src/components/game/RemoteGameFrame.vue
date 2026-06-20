<template>
  <div class="remote-game-frame" ref="shellRef">
    <el-alert
      v-if="error"
      type="error"
      title="远程游戏加载失败"
      :closable="false"
      show-icon
    >
      {{ error }}
    </el-alert>

    <div v-else class="remote-game-frame__stage">
      <iframe
        v-if="manifest"
        ref="frameRef"
        class="remote-game-frame__iframe"
        sandbox="allow-scripts"
        :src="manifest.entryUrl"
        :title="manifest.title"
      />
      <div v-else class="remote-game-frame__loading">
        <img
          :src="referenceImages.playLoadingImage"
          alt=""
          class="remote-game-frame__loading-image"
        />
        <div class="remote-game-frame__loading-content">
          <div class="remote-game-frame__spinner">
            <el-icon class="is-loading" size="38"><Loading /></el-icon>
          </div>
          <h3>正在加载游戏...</h3>
          <p>首次加载可能需要一些时间，请稍候。</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Loading } from '@element-plus/icons-vue'
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import type { GameManifest } from '@/api/types'
import { referenceImages } from '@/data/showcase'

const props = defineProps<{
  manifest: GameManifest | null
  error?: string | null
}>()

const shellRef = ref<HTMLDivElement | null>(null)
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

async function requestFullscreen() {
  const target = shellRef.value
  if (!target?.requestFullscreen) return

  try {
    await target.requestFullscreen()
  } catch {
    // Fullscreen can be denied by browser policy; keep the control non-disruptive.
  }
}

defineExpose({
  requestFullscreen,
  restart,
  statusText,
})

onMounted(() => window.addEventListener('message', handleMessage))
onBeforeUnmount(() => window.removeEventListener('message', handleMessage))
</script>

<style scoped>
.remote-game-frame {
  overflow: hidden;
  border: 1px solid #dce4f0;
  border-radius: 8px;
  background: #0f172a;
  box-shadow: 0 8px 22px rgba(31, 42, 68, 0.06);
}

.remote-game-frame__stage {
  min-height: 560px;
  height: min(68vh, 720px);
}

.remote-game-frame__iframe {
  display: block;
  width: 100%;
  height: 100%;
  border: 0;
  background: #0f172a;
}

.remote-game-frame__loading {
  position: relative;
  display: flex;
  height: 100%;
  min-height: 560px;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.remote-game-frame__loading-image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: left top;
  opacity: 0.38;
}

.remote-game-frame__loading-content {
  position: relative;
  z-index: 1;
  color: #fff;
  text-align: center;
}

.remote-game-frame__spinner {
  display: grid;
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
  place-items: center;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(12px);
}

.remote-game-frame__loading h3 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
}

.remote-game-frame__loading p {
  margin: 14px 0 0;
  color: rgba(255, 255, 255, 0.72);
  font-size: 14px;
}
</style>
