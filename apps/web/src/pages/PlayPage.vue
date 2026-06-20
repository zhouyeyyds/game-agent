<template>
  <main class="workbench-page">
    <div class="mb-4 flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <el-button text :icon="ArrowLeft" @click="router.push('/')">返回</el-button>
        <div>
          <div class="flex flex-wrap items-center gap-3">
            <h1 class="m-0 text-2xl font-semibold text-slate-950">{{ descriptor?.title || manifest?.title || '远程游戏' }}</h1>
            <el-tag type="primary" round>AI 生成</el-tag>
            <el-tag v-if="manifest" type="success" round>运行中</el-tag>
            <el-tag v-else-if="error" type="danger" round>加载失败</el-tag>
            <el-tag v-else type="info" round>加载中</el-tag>
          </div>
          <p class="mt-1 text-sm text-slate-500">{{ statusLine }}</p>
        </div>
      </div>
      <el-button :icon="Refresh" @click="loadGame">刷新资源</el-button>
    </div>

    <template v-if="loading">
      <div class="grid gap-4 xl:grid-cols-[1fr_360px]">
        <section class="app-card flex min-h-[620px] items-center justify-center overflow-hidden p-5">
          <div class="relative w-full overflow-hidden rounded-lg bg-slate-950 p-10 text-center text-white">
            <img :src="referenceImages.playLoadingImage" alt="" class="absolute inset-0 h-full w-full object-cover object-left-top opacity-45" />
            <div class="relative z-10 mx-auto max-w-xl py-24">
              <el-icon class="is-loading mb-8" size="68"><Loading /></el-icon>
              <h2 class="m-0 text-3xl font-semibold">正在加载游戏...</h2>
              <p class="mt-5 text-white/70">首次加载可能需要一些时间，请稍候。</p>
              <el-progress class="mx-auto mt-8 max-w-lg" :percentage="56" :show-text="false" />
            </div>
          </div>
        </section>
        <GameInfoSide :descriptor="descriptor" :manifest="manifest" />
      </div>
    </template>

    <template v-else-if="error">
      <div class="grid gap-4 xl:grid-cols-[1fr_360px]">
        <section class="app-card overflow-hidden p-5">
          <div class="grid min-h-[520px] gap-8 lg:grid-cols-[0.8fr_1fr]">
            <div class="relative overflow-hidden rounded-lg bg-blue-50">
              <img :src="referenceImages.playErrorImage" alt="" class="h-full w-full object-cover object-left-top opacity-75" />
            </div>
            <div class="flex flex-col justify-center">
              <div class="mb-5 grid h-14 w-14 place-items-center rounded-full bg-red-500 text-white">
                <el-icon size="30"><WarningFilled /></el-icon>
              </div>
              <h2 class="m-0 text-3xl font-semibold text-slate-950">游戏加载失败</h2>
              <p class="mt-5 text-base leading-8 text-slate-600">{{ error }}</p>
              <div class="mt-8 flex flex-wrap gap-3">
                <el-button class="agent-gradient-button" :icon="Refresh" @click="loadGame">重试加载</el-button>
                <el-button :icon="House" @click="router.push('/')">返回首页</el-button>
              </div>
            </div>
          </div>
        </section>
        <GameInfoSide :descriptor="descriptor" :manifest="manifest" failed />
      </div>
    </template>

    <template v-else>
      <div class="grid gap-4 xl:grid-cols-[1fr_360px]">
        <section class="space-y-4">
          <RemoteGameFrame :manifest="manifest" :error="error" />
          <section class="app-card p-5">
            <h2 class="m-0 mb-4 text-lg font-semibold text-slate-950">相关游戏</h2>
            <div class="grid gap-3 md:grid-cols-2 2xl:grid-cols-4">
              <div v-for="title in relatedGames" :key="title" class="flex items-center gap-3 rounded-lg border border-slate-200 bg-white p-3">
                <img :src="referenceImages.playRunningImage" alt="" class="h-16 w-24 rounded object-cover object-left-top" />
                <div class="min-w-0">
                  <p class="m-0 truncate text-sm font-semibold text-slate-900">{{ title }}</p>
                  <p class="m-0 mt-1 text-xs text-slate-400">8.7k 次游玩</p>
                </div>
              </div>
            </div>
          </section>
        </section>

        <aside class="space-y-4">
          <GameInfoSide :descriptor="descriptor" :manifest="manifest" />
          <RuntimeInfoPanel v-if="descriptor" :descriptor="descriptor" />
        </aside>
      </div>
    </template>
  </main>
</template>

<script setup lang="ts">
import { ArrowLeft, House, Loading, Refresh, WarningFilled } from '@element-plus/icons-vue'
import { computed, defineComponent, h, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { fetchPlayDescriptor } from '@/api/games'
import type { GameManifest, PlayDescriptor } from '@/api/types'
import RemoteGameFrame from '@/components/game/RemoteGameFrame.vue'
import RuntimeInfoPanel from '@/components/game/RuntimeInfoPanel.vue'
import { referenceImages } from '@/data/showcase'

const props = defineProps<{
  gameId: string
}>()

const router = useRouter()
const loading = ref(false)
const descriptor = ref<PlayDescriptor | null>(null)
const manifest = ref<GameManifest | null>(null)
const error = ref<string | null>(null)
const relatedGames = ['星露谷的夏天', '赛博纪元 2077：重启', '心动信号', '遗落的文明']

const statusLine = computed(() => {
  if (loading.value) return '正在加载运行资源，请稍候'
  if (error.value) return '加载失败，请检查远程资源'
  return '加载成功，可正常游玩'
})

function isGameManifest(value: unknown): value is GameManifest {
  if (!value || typeof value !== 'object') return false
  const candidate = value as Partial<GameManifest>
  return candidate.schemaVersion === 'game-manifest-v1'
    && typeof candidate.entryUrl === 'string'
    && typeof candidate.title === 'string'
}

async function loadGame() {
  loading.value = true
  error.value = null
  manifest.value = null
  try {
    descriptor.value = await fetchPlayDescriptor(props.gameId)
    const response = await fetch(descriptor.value.manifestUrl)
    if (!response.ok) throw new Error(`Manifest 请求失败: ${response.status}`)
    const payload = await response.json()
    if (!isGameManifest(payload)) throw new Error('Manifest 协议不合法')
    manifest.value = payload
  } catch (caught) {
    error.value = caught instanceof Error ? caught.message : '加载失败'
  } finally {
    loading.value = false
  }
}

const GameInfoSide = defineComponent({
  props: {
    descriptor: { type: Object as () => PlayDescriptor | null, default: null },
    manifest: { type: Object as () => GameManifest | null, default: null },
    failed: { type: Boolean, default: false },
  },
  setup(sideProps) {
    return () => h('section', { class: 'agent-card p-5' }, [
      h('img', { src: sideProps.failed ? referenceImages.playErrorImage : referenceImages.playRunningImage, class: 'h-44 w-full rounded-lg object-cover object-left-top', alt: '' }),
      h('h2', { class: 'mt-5 text-2xl font-semibold text-slate-950' }, sideProps.manifest?.title || sideProps.descriptor?.title || '迷雾之城：钟声'),
      h('p', { class: 'mt-3 text-sm leading-7 text-slate-600' }, '在迷雾与诅咒交织的城市中探寻真相，你的选择将决定众人的命运。'),
      h('div', { class: 'mt-4 flex flex-wrap gap-2' }, ['冒险', '解谜', '角色扮演', '剧情'].map((tag) => h('span', { class: 'rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-600' }, tag))),
      h('div', { class: 'mt-5 grid grid-cols-2 gap-3 rounded-lg border border-slate-200 p-4 text-center' }, [
        h('div', [h('p', { class: 'm-0 text-xl font-semibold text-slate-950' }, '12.4k'), h('p', { class: 'm-0 text-xs text-slate-500' }, '游玩次数')]),
        h('div', [h('p', { class: 'm-0 text-xl font-semibold text-slate-950' }, '92%'), h('p', { class: 'm-0 text-xs text-slate-500' }, '好评率')]),
      ]),
    ])
  },
})

onMounted(loadGame)
</script>
