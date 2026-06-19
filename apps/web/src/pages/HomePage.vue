<template>
  <main class="mx-auto max-w-7xl px-6 py-10">
    <section class="rounded-3xl border border-white/10 bg-white/5 p-8 shadow-2xl backdrop-blur">
      <p class="text-sm font-semibold uppercase tracking-[0.3em] text-neon">AI Native Arcade</p>
      <h1 class="mt-4 max-w-3xl text-4xl font-bold tracking-tight text-white md:text-6xl">
        用自然语言生成、发布并游玩互动小游戏
      </h1>
      <p class="mt-5 max-w-2xl text-base leading-7 text-slate-300">
        PromptPlay AI 通过 LangGraph Agent 将创意和素材转成可发布的远端 HTML5 游戏产物。
      </p>
    </section>

    <section class="mt-10">
      <div class="mb-5 flex items-center justify-between">
        <h2 class="text-2xl font-semibold text-white">Published Games</h2>
        <NButton type="primary" @click="$router.push('/create')">Start Creating</NButton>
      </div>

      <NSpin :show="loading">
        <NEmpty v-if="!loading && games.length === 0" description="暂无已发布游戏" />
        <div v-else class="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          <NCard v-for="game in games" :key="game.id" class="overflow-hidden border border-white/10 bg-white/5">
            <template #cover>
              <div class="flex h-40 items-center justify-center bg-gradient-to-br from-cyan-500/25 to-fuchsia-500/25 text-5xl">
                🎮
              </div>
            </template>
            <div class="space-y-3">
              <div>
                <h3 class="text-xl font-semibold text-white">{{ game.title }}</h3>
                <p class="mt-2 line-clamp-3 text-sm leading-6 text-slate-300">{{ game.description }}</p>
              </div>
              <div class="flex flex-wrap gap-2">
                <NTag v-for="tag in game.tags" :key="tag" size="small" type="info">{{ tag }}</NTag>
              </div>
              <div class="flex items-center justify-between text-xs text-slate-400">
                <span>by {{ game.author.displayName }}</span>
                <span>{{ game.playCount }} plays</span>
              </div>
              <NButton block type="primary" @click="$router.push(`/play/${game.id}`)">Play</NButton>
            </div>
          </NCard>
        </div>
      </NSpin>
    </section>
  </main>
</template>

<script setup lang="ts">
import { NButton, NCard, NEmpty, NSpin, NTag, useMessage } from 'naive-ui'
import { onMounted, ref } from 'vue'

import { fetchPublishedGames } from '@/api/games'
import type { GameListItem } from '@/api/types'

const message = useMessage()
const loading = ref(false)
const games = ref<GameListItem[]>([])

onMounted(async () => {
  loading.value = true
  try {
    games.value = await fetchPublishedGames()
  } catch (error) {
    message.error(error instanceof Error ? error.message : '加载游戏列表失败')
  } finally {
    loading.value = false
  }
})
</script>
