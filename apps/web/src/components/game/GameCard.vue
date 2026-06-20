<template>
  <article
    class="game-card"
    role="button"
    tabindex="0"
    @click="emit('play', game.id)"
    @keydown.enter="emit('play', game.id)"
    @keydown.space.prevent="emit('play', game.id)"
  >
    <div class="game-card__inner">
      <div class="game-card__cover" aria-hidden="true">
        <img v-if="game.coverUrl" :src="game.coverUrl" :alt="game.title" />
        <img v-else :src="fallbackImage" :alt="game.title" />
        <span class="game-card__badge" :class="{ 'game-card__badge--published': game.publishedAt }">
          {{ game.publishedAt ? '已发布' : 'AI 生成' }}
        </span>
      </div>

      <div class="game-card__body">
        <h3>{{ game.title }}</h3>
        <p>{{ game.description }}</p>

        <div class="game-card__author">
          <span>{{ game.author.displayName.slice(0, 1) }}</span>
          <em>{{ game.author.displayName }}</em>
        </div>

        <div class="game-card__meta">
          <div class="game-card__tags">
            <span v-for="tag in game.tags.slice(0, 3)" :key="tag">{{ tag }}</span>
          </div>
          <el-button type="primary" size="small" plain @click.stop="emit('play', game.id)">
            <el-icon><VideoPlay /></el-icon>
            Play
          </el-button>
        </div>

        <time>{{ displayDate }}</time>
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
import { VideoPlay } from '@element-plus/icons-vue'
import { computed } from 'vue'

import type { GameListItem } from '@/api/types'
import { referenceImages } from '@/data/showcase'

const props = defineProps<{
  game: GameListItem
  index: number
}>()

const emit = defineEmits<{
  play: [gameId: string]
}>()

const fallbackImages = [
  referenceImages.playErrorImage,
  referenceImages.homeShowcase,
  referenceImages.playRunningImage,
  referenceImages.createPublishImage,
  referenceImages.createTaskImage,
  referenceImages.createFormImage,
  referenceImages.playLoadingImage,
  referenceImages.authShowcase,
]

const fallbackImage = computed(() => fallbackImages[props.index % fallbackImages.length])

const fallbackDates = ['2024-05-09', '2024-05-10', '2024-05-11', '2024-05-12']
const displayDate = computed(() => props.game.publishedAt?.slice(0, 10) || fallbackDates[props.index % fallbackDates.length])
</script>

<style scoped>
.game-card {
  overflow: hidden;
  border: 1px solid #dfe6f3;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 10px 24px rgba(31, 42, 68, 0.04);
  cursor: pointer;
  outline: none;
  transition: border-color 160ms ease, box-shadow 160ms ease, transform 160ms ease;
}

.game-card:hover,
.game-card:focus-visible {
  border-color: #cfd9ec;
  box-shadow: 0 16px 34px rgba(31, 42, 68, 0.1);
  transform: translateY(-1px);
}

.game-card__inner {
  display: block;
  width: 100%;
}

.game-card__cover {
  position: relative;
  height: 166px;
  overflow: hidden;
  background: linear-gradient(135deg, #eef2f7, #e8edf6);
}

.game-card__cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 220ms ease;
}

.game-card:hover .game-card__cover img {
  transform: scale(1.03);
}

.game-card__badge {
  position: absolute;
  top: 12px;
  left: 12px;
  border-radius: 7px;
  background: linear-gradient(135deg, #6f5cff, #9d55f7);
  box-shadow: 0 8px 18px rgba(101, 74, 255, 0.24);
  color: #fff;
  font-size: 12px;
  font-weight: 800;
  line-height: 1;
  padding: 7px 11px;
}

.game-card__badge--published {
  background: #21bf73;
  box-shadow: 0 8px 18px rgba(33, 191, 115, 0.2);
  color: #fff;
}

.game-card__body {
  padding: 14px 14px 12px;
}

.game-card__body h3 {
  margin: 0;
  overflow: hidden;
  color: #172033;
  font-size: 16px;
  font-weight: 800;
  line-height: 1.38;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.game-card__body p {
  display: -webkit-box;
  min-height: 42px;
  margin: 8px 0 0;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  color: #6d7788;
  font-size: 13px;
  line-height: 1.6;
}

.game-card__author {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-top: 11px;
}

.game-card__author span {
  display: grid;
  width: 24px;
  height: 24px;
  place-items: center;
  border-radius: 999px;
  background: linear-gradient(135deg, #151c2f, #38445d);
  color: #fff;
  font-size: 11px;
  font-weight: 800;
}

.game-card__author em {
  overflow: hidden;
  color: #4c596c;
  font-size: 12px;
  font-style: normal;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.game-card__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-top: 12px;
}

.game-card__tags {
  display: flex;
  min-width: 0;
  gap: 6px;
  overflow: hidden;
}

.game-card__tags span {
  flex: 0 0 auto;
  max-width: 86px;
  overflow: hidden;
  border-radius: 7px;
  background: #f2efff;
  color: #7657ff;
  font-size: 12px;
  font-weight: 700;
  line-height: 1;
  padding: 6px 8px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.game-card__meta :deep(.el-button) {
  flex: 0 0 auto;
  height: 30px;
  border-color: #b8a6ff;
  border-radius: 7px;
  background: #fff;
  color: #6d55ff;
  font-size: 13px;
  font-weight: 800;
  padding: 0 11px;
}

.game-card__meta :deep(.el-button:hover) {
  border-color: #7657ff;
  background: #f5f2ff;
  color: #5f46ef;
}

.game-card__meta :deep(.el-icon) {
  font-size: 14px;
}

.game-card__body time {
  display: block;
  margin-top: 8px;
  color: #9aa5b5;
  font-size: 12px;
  line-height: 1;
}
</style>
