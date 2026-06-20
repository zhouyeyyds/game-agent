<template>
  <main class="workbench-page">
    <div class="grid gap-4 xl:grid-cols-[1fr_360px]">
      <section class="space-y-4">
        <section class="app-card overflow-hidden">
          <div class="grid gap-5 p-5 lg:grid-cols-[1fr_320px]">
            <div>
              <div class="mb-4 flex flex-wrap items-center gap-2">
                <el-tag type="primary" effect="plain">工作台</el-tag>
                <span class="text-sm text-slate-500">AI 游戏创作与体验平台</span>
              </div>
              <h1 class="m-0 text-2xl font-semibold text-slate-900 lg:text-3xl">发现、创建并运行 AI 生成游戏</h1>
              <p class="mt-3 max-w-3xl text-sm leading-6 text-slate-500">
                浏览社区发布的互动游戏，按题材快速筛选，也可以进入创作中心用自然语言生成自己的游戏作品。
              </p>
              <div class="mt-5 flex flex-wrap gap-3">
                <el-button type="primary" :icon="VideoPlay" @click="scrollToGallery">查看游戏</el-button>
                <el-button :icon="MagicStick" @click="router.push('/create')">创建游戏</el-button>
              </div>
            </div>
            <div class="hidden overflow-hidden rounded-lg border border-slate-200 bg-slate-50 lg:block">
              <img :src="referenceImages.homeShowcase" alt="" class="h-full min-h-44 w-full object-cover object-right-top" />
            </div>
          </div>
        </section>

        <section class="grid gap-4 md:grid-cols-4">
          <article v-for="[value, label] in platformStats" :key="label" class="app-card p-4">
            <p class="m-0 text-2xl font-semibold text-blue-600">{{ value }}</p>
            <p class="m-0 mt-1 text-sm text-slate-500">{{ label }}</p>
          </article>
        </section>

        <section id="gallery" class="app-card p-4">
          <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 class="m-0 text-lg font-semibold text-slate-900">游戏广场</h2>
              <p class="m-0 mt-1 text-sm text-slate-500">按题材、热度和发布时间浏览已发布作品</p>
            </div>
            <el-button text type="primary" :icon="Plus" @click="router.push('/create')">发布新作品</el-button>
          </div>

          <div class="grid gap-3 lg:grid-cols-[1fr_200px]">
            <el-input v-model="searchText" :prefix-icon="Search" placeholder="搜索游戏名称、作者或标签" clearable />
            <el-select v-model="sortMode">
              <el-option label="最新发布" value="newest" />
              <el-option label="最多游玩" value="plays" />
            </el-select>
          </div>

          <el-tabs v-model="activeCategory" class="mt-2">
            <el-tab-pane v-for="category in categories" :key="category" :label="category" :name="category" />
          </el-tabs>

          <div v-loading="loading" element-loading-background="rgba(248, 250, 252, 0.72)" class="min-h-80">
            <el-empty v-if="!loading && filteredGames.length === 0" description="暂无已发布游戏" class="py-16" />
            <div v-else class="grid gap-4 sm:grid-cols-2 2xl:grid-cols-3">
              <GameCard v-for="(game, index) in filteredGames" :key="game.id" :game="game" :index="index" @play="goPlay" />
            </div>
          </div>
        </section>
      </section>

      <aside class="space-y-4">
        <section class="app-card p-4">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="m-0 text-lg font-semibold text-slate-900">热门标签</h2>
            <el-button text size="small">更多</el-button>
          </div>
          <div class="flex flex-wrap gap-2">
            <el-tag v-for="[tag, count] in hotTags" :key="tag" round>
              {{ tag }} <span class="ml-1 text-slate-400">{{ count }}</span>
            </el-tag>
          </div>
        </section>

        <section class="app-card p-4">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="m-0 text-lg font-semibold text-slate-900">推荐创作者</h2>
            <el-button text size="small">查看</el-button>
          </div>
          <div class="space-y-4">
            <div v-for="creator in creators" :key="creator[0]" class="flex items-center gap-3">
              <span class="grid h-10 w-10 place-items-center rounded-full bg-blue-50 text-sm font-semibold text-blue-600">
                {{ creator[0].slice(0, 1) }}
              </span>
              <div class="min-w-0 flex-1">
                <p class="m-0 truncate text-sm font-semibold text-slate-800">{{ creator[0] }}</p>
                <p class="m-0 truncate text-xs text-slate-500">{{ creator[1] }}</p>
                <p class="m-0 text-xs text-orange-500">{{ creator[2] }}</p>
              </div>
              <el-button size="small" plain>关注</el-button>
            </div>
          </div>
        </section>

        <section class="app-card p-4">
          <h2 class="m-0 text-lg font-semibold text-slate-900">快捷入口</h2>
          <div class="mt-4 grid gap-2">
            <el-button :icon="MagicStick" @click="router.push('/create')">进入创作中心</el-button>
            <el-button :icon="Search" @click="scrollToGallery">浏览游戏广场</el-button>
          </div>
        </section>
      </aside>
    </div>
  </main>
</template>

<script setup lang="ts">
import { MagicStick, Plus, Search, VideoPlay } from '@element-plus/icons-vue'
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
