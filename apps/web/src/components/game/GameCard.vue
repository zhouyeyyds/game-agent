<template>
  <article class="agent-card group overflow-hidden transition duration-200 hover:-translate-y-0.5 hover:shadow-lg">
    <button class="block w-full border-0 bg-transparent p-0 text-left" type="button" @click="emit('play', game.id)">
      <div class="relative aspect-[16/9] overflow-hidden bg-slate-100">
        <img v-if="game.coverUrl" :src="game.coverUrl" :alt="game.title" class="h-full w-full object-cover transition duration-300 group-hover:scale-105" />
        <img v-else :src="referenceImages.playRunningImage" :alt="game.title" class="h-full w-full object-cover object-left-top transition duration-300 group-hover:scale-105" />
        <el-tag class="absolute left-3 top-3" type="primary" effect="dark">AI 生成</el-tag>
      </div>
      <div class="space-y-3 p-4">
        <h3 class="m-0 line-clamp-1 text-lg font-semibold text-slate-950">{{ game.title }}</h3>
        <p class="m-0 line-clamp-2 min-h-10 text-sm leading-5 text-slate-600">{{ game.description }}</p>
        <div class="flex items-center gap-2 text-sm text-slate-500">
          <span class="grid h-6 w-6 place-items-center rounded-full bg-blue-50 text-xs font-semibold text-blue-600">{{ game.author.displayName.slice(0, 1) }}</span>
          <span>{{ game.author.displayName }}</span>
        </div>
        <div class="flex flex-wrap gap-2">
          <el-tag v-for="tag in game.tags.slice(0, 3)" :key="tag" round size="small">{{ tag }}</el-tag>
        </div>
        <div class="flex items-center justify-between text-xs text-slate-400">
          <span>{{ game.publishedAt?.slice(0, 10) || '未发布' }}</span>
          <el-button type="primary" size="small" round>
            <el-icon><VideoPlay /></el-icon>
            游玩
          </el-button>
        </div>
      </div>
    </button>
  </article>
</template>

<script setup lang="ts">
import { VideoPlay } from '@element-plus/icons-vue'

import type { GameListItem } from '@/api/types'
import { referenceImages } from '@/data/showcase'

defineProps<{
  game: GameListItem
  index: number
}>()

const emit = defineEmits<{
  play: [gameId: string]
}>()
</script>
