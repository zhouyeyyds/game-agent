<template>
  <main class="mx-auto grid max-w-[1800px] gap-6 px-6 py-7 lg:grid-cols-[1fr_390px] lg:px-12">
    <section class="min-w-0 space-y-6">
      <section class="agent-card grid overflow-hidden p-8 lg:grid-cols-[1fr_0.9fr] lg:p-10">
        <div class="relative z-10">
          <div class="inline-flex items-center rounded-xl bg-white px-3 py-2 text-sm font-bold text-indigo-600 shadow-sm">
            AI 驱动的互动游戏创作与体验社区
          </div>
          <h1 class="mt-6 max-w-2xl text-4xl font-black leading-tight tracking-tight text-slate-950 md:text-5xl">
            在 AgentPlay，人人都是游戏<span class="text-indigo-600">创作者</span>，人人都是<span class="text-blue-600">玩家</span>
          </h1>
          <p class="mt-5 max-w-2xl text-base leading-8 text-slate-600">
            通过 AI Agent 让想象力变成可玩世界。探索由创作者发布的互动游戏，或使用 Create 打造你的专属作品并发布给世界。
          </p>
          <div class="mt-7 flex flex-wrap gap-3">
            <el-button class="agent-gradient-button" size="large" type="primary" :icon="VideoPlay" @click="scrollToGallery">开始探索</el-button>
            <el-button size="large" :icon="MagicStick" @click="router.push('/create')">Create 游戏</el-button>
          </div>
        </div>
        <div class="relative mt-8 min-h-56 overflow-hidden rounded-3xl lg:mt-0">
          <img :src="referenceImages.homeShowcase" alt="" class="absolute inset-0 h-full w-full object-cover object-right-top" />
        </div>
      </section>

      <div class="grid gap-3 md:grid-cols-[1fr_210px]">
        <el-input v-model="searchText" :prefix-icon="Search" size="large" placeholder="搜索游戏名称、作者或标签，例如：科幻、悬疑、冒险..." />
        <el-select v-model="sortMode" size="large">
          <el-option label="排序：最新发布" value="newest" />
          <el-option label="排序：最多游玩" value="plays" />
        </el-select>
      </div>

      <el-tabs v-model="activeCategory" class="category-tabs">
        <el-tab-pane v-for="category in categories" :key="category" :label="category" :name="category" />
      </el-tabs>

      <div id="gallery" v-loading="loading" element-loading-background="rgba(247, 249, 255, 0.72)" class="min-h-80">
        <el-empty v-if="!loading && filteredGames.length === 0" description="暂无已发布游戏" class="agent-card py-20" />
        <div v-else class="grid gap-5 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
          <GameCard v-for="(game, index) in filteredGames" :key="game.id" :game="game" :index="index" @play="goPlay" />
        </div>
      </div>
    </section>

    <aside class="space-y-5">
      <section class="agent-card p-5">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="m-0 text-lg font-black text-slate-950">热门标签</h2>
          <button class="border-0 bg-transparent text-sm font-bold text-slate-400" type="button">查看更多</button>
        </div>
        <div class="flex flex-wrap gap-3">
          <el-tag v-for="[tag, count] in hotTags" :key="tag" round size="large">{{ tag }} <span class="ml-1 text-slate-400">{{ count }}</span></el-tag>
        </div>
      </section>

      <section class="agent-card p-5">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="m-0 text-lg font-black text-slate-950">推荐创作者</h2>
          <button class="border-0 bg-transparent text-sm font-bold text-slate-400" type="button">查看更多</button>
        </div>
        <div class="space-y-4">
          <div v-for="creator in creators" :key="creator[0]" class="flex items-center gap-3">
            <span class="grid h-11 w-11 place-items-center rounded-full bg-gradient-to-br from-slate-900 to-indigo-500 text-sm font-bold text-white">{{ creator[0].slice(0, 1) }}</span>
            <div class="min-w-0 flex-1">
              <p class="m-0 truncate text-sm font-black text-slate-900">{{ creator[0] }}</p>
              <p class="m-0 truncate text-xs text-slate-500">{{ creator[1] }}</p>
              <p class="m-0 text-xs text-orange-500">{{ creator[2] }}</p>
            </div>
            <el-button size="small" plain>关注</el-button>
          </div>
        </div>
      </section>

      <section class="agent-card p-5">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="m-0 text-lg font-black text-slate-950">平台数据</h2>
          <span class="text-xs font-bold text-emerald-500">实时更新</span>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div v-for="[value, label] in platformStats" :key="label" class="rounded-2xl bg-slate-50 p-4">
            <p class="m-0 text-xl font-black text-indigo-600">{{ value }}</p>
            <p class="m-0 mt-1 text-xs text-slate-500">{{ label }}</p>
          </div>
        </div>
      </section>
    </aside>
  </main>
</template>

<script setup lang="ts">
import { MagicStick, Search, VideoPlay } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { fetchPublishedGames } from '@/api/games'
import type { GameListItem } from '@/api/types'
import GameCard from '@/components/game/GameCard.vue'
import { creators, hotTags, platformStats, referenceImages } from '@/data/showcase'

const router = useRouter()
const loading = ref(false)
const games = ref<GameListItem[]>([])
const searchText = ref('')
const sortMode = ref('newest')
const activeCategory = ref('全部')
const categories = ['全部', '角色扮演', '冒险', '解谜', '模拟', '恋爱', '科幻', '悬疑', '奇幻']

const filteredGames = computed(() => {
  const keyword = searchText.value.trim().toLowerCase()
  const filtered = games.value.filter((game) => {
    const matchesKeyword = !keyword
      || game.title.toLowerCase().includes(keyword)
      || game.description.toLowerCase().includes(keyword)
      || game.author.displayName.toLowerCase().includes(keyword)
      || game.tags.some((tag) => tag.toLowerCase().includes(keyword))
    const matchesCategory = activeCategory.value === '全部' || game.tags.includes(activeCategory.value)
    return matchesKeyword && matchesCategory
  })

  return [...filtered].sort((a, b) => {
    if (sortMode.value === 'plays') return b.playCount - a.playCount
    return String(b.publishedAt || '').localeCompare(String(a.publishedAt || ''))
  })
})

function goPlay(gameId: string) {
  router.push(`/play/${gameId}`)
}

function scrollToGallery() {
  document.querySelector('#gallery')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

onMounted(async () => {
  loading.value = true
  try {
    games.value = await fetchPublishedGames()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '加载游戏列表失败')
  } finally {
    loading.value = false
  }
})
</script>
