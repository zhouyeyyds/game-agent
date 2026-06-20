<template>
  <section class="space-y-4">
    <div class="flex items-end justify-between gap-4">
      <div>
        <h2 class="m-0 text-2xl font-black tracking-tight text-white md:text-3xl">{{ title }}</h2>
        <p v-if="subtitle" class="mt-1 text-sm font-medium text-slate-400">{{ subtitle }}</p>
      </div>
      <span class="hidden text-xs font-bold uppercase tracking-[0.25em] text-cyan-200/70 md:inline">Remote Bundles</span>
    </div>
    <div class="flex gap-5 overflow-x-auto pb-4 pr-8 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
      <GameCard v-for="(game, index) in games" :key="`${title}-${game.id}`" :game="game" :index="index" @play="emit('play', $event)" />
    </div>
  </section>
</template>

<script setup lang="ts">
import type { GameListItem } from '@/api/types'
import GameCard from '@/components/game/GameCard.vue'

defineProps<{
  title: string
  subtitle?: string
  games: GameListItem[]
}>()

const emit = defineEmits<{
  play: [gameId: string]
}>()
</script>
