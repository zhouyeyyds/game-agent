<template>
  <main class="mx-auto max-w-6xl px-6 py-10">
    <div class="mb-6 flex items-center justify-between">
      <div>
        <p class="text-sm uppercase tracking-[0.3em] text-neon">Remote Runtime</p>
        <h1 class="mt-2 text-3xl font-bold text-white">{{ descriptor?.title || 'Loading game...' }}</h1>
      </div>
      <NButton @click="$router.push('/')">返回首页</NButton>
    </div>

    <NSpin :show="loading">
      <RemoteGameFrame :manifest="manifest" :error="error" />
    </NSpin>

    <NCollapse v-if="descriptor" class="mt-6 rounded-2xl border border-white/10 bg-white/5 p-4">
      <NCollapseItem title="Runtime Info" name="runtime">
        <div class="space-y-2 break-all text-sm text-slate-300">
          <p>Runtime: {{ descriptor.runtime }}</p>
          <p>Manifest: {{ descriptor.manifestUrl }}</p>
          <p>Storage: {{ descriptor.storagePrefix }}</p>
        </div>
      </NCollapseItem>
    </NCollapse>
  </main>
</template>

<script setup lang="ts">
import { NButton, NCollapse, NCollapseItem, NSpin } from 'naive-ui'
import { onMounted, ref } from 'vue'

import { fetchPlayDescriptor } from '@/api/games'
import type { GameManifest, PlayDescriptor } from '@/api/types'
import RemoteGameFrame from '@/components/game/RemoteGameFrame.vue'

const props = defineProps<{
  gameId: string
}>()

const loading = ref(false)
const descriptor = ref<PlayDescriptor | null>(null)
const manifest = ref<GameManifest | null>(null)
const error = ref<string | null>(null)

function isGameManifest(value: unknown): value is GameManifest {
  if (!value || typeof value !== 'object') return false
  const candidate = value as Partial<GameManifest>
  return candidate.schemaVersion === 'game-manifest-v1'
    && typeof candidate.entryUrl === 'string'
    && typeof candidate.title === 'string'
}

onMounted(async () => {
  loading.value = true
  try {
    descriptor.value = await fetchPlayDescriptor(props.gameId)
    const response = await fetch(descriptor.value.manifestUrl)
    if (!response.ok) throw new Error(`Manifest 请求失败：${response.status}`)
    const payload = await response.json()
    if (!isGameManifest(payload)) throw new Error('Manifest 协议不合法')
    manifest.value = payload
  } catch (caught) {
    error.value = caught instanceof Error ? caught.message : '加载失败'
  } finally {
    loading.value = false
  }
})
</script>
