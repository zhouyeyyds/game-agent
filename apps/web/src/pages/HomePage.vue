<template>
  <main class="workbench-page">
    <div class="xl:grid-cols-[1fr_360px]">
      <section class="space-y-4">
        <section class="home-hero">
          <div class="home-hero__content">
            <div class="home-hero__eyebrow">
              <el-icon><MagicStick /></el-icon>
              <span>AI 驱动的互动游戏创作与体验社区</span>
            </div>
            <h1>
              在 AgentPlay，人人都是<br />
              游戏<span>创作者</span>，人人都是<span>玩家</span>
            </h1>
            <p>
              通过 AI Agent
              让想象力变成可玩世界。探索由创作者发布的互动游戏，<br
                class="home-hero__break"
              />
              或使用 Create 打造你的专属作品并发布给世界。
            </p>
            <div class="home-hero__actions">
              <el-button
                class="home-hero__primary"
                type="primary"
                :icon="VideoPlay"
                @click="scrollToGallery"
                >开始探索</el-button
              >
              <el-button
                class="home-hero__secondary"
                :icon="MagicStick"
                @click="router.push('/create')"
                >Create 游戏</el-button
              >
            </div>
          </div>
          <div class="home-hero__visual" aria-hidden="true">
            <img :src="referenceImages.homeHeroVisual" alt="" />
          </div>
        </section>

        <section id="gallery" class="game-plaza">
          <div class="plaza-toolbar">
            <el-input
              v-model="searchText"
              :prefix-icon="Search"
              placeholder="搜索游戏名称、作者或标签，例如：科幻、悬疑、冒险..."
              clearable
            />
            <el-select v-model="sortMode" class="plaza-sort">
              <el-option label="排序：最新发布" value="newest" />
              <el-option label="排序：最多游玩" value="plays" />
            </el-select>
          </div>

          <div class="category-row">
            <button
              v-for="category in visibleCategories"
              :key="category"
              class="category-pill"
              :class="{ active: activeCategory === category }"
              type="button"
              @click="activeCategory = category"
            >
              {{ category }}
            </button>
            <button class="category-pill more" type="button">
              更多
              <el-icon><ArrowDown /></el-icon>
            </button>
          </div>

          <div
            v-loading="loading"
            element-loading-background="rgba(248, 250, 252, 0.72)"
            class="plaza-grid-wrap"
          >
            <el-empty
              v-if="!loading && displayGames.length === 0"
              description="暂无已发布游戏"
              class="py-16"
            />
            <div v-else class="plaza-grid">
              <GameCard
                v-for="(game, index) in displayGames"
                :key="game.id"
                :game="game"
                :index="index"
                @play="goPlay"
              />
            </div>
          </div>
        </section>
      </section>
    </div>
  </main>
</template>

<script setup lang="ts">
import {
  ArrowDown,
  MagicStick,
  Search,
  VideoPlay,
} from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import { fetchPublishedGames } from "@/api/games";
import type { GameListItem } from "@/api/types";
import GameCard from "@/components/game/GameCard.vue";
import { referenceImages } from "@/data/showcase";

const router = useRouter();
const loading = ref(false);
const games = ref<GameListItem[]>([]);
const searchText = ref("");
const sortMode = ref("newest");
const activeCategory = ref("全部");

const visibleCategories = [
  "全部",
  "角色扮演",
  "冒险",
  "解谜",
  "模拟",
  "恋爱",
  "科幻",
  "悬疑",
  "奇幻",
];

const displayGames = computed(() => {
  const keyword = searchText.value.trim().toLowerCase();
  const filtered = games.value.filter((game) => {
    const matchesKeyword =
      !keyword ||
      game.title.toLowerCase().includes(keyword) ||
      game.description.toLowerCase().includes(keyword) ||
      game.author.displayName.toLowerCase().includes(keyword) ||
      game.tags.some((tag) => tag.toLowerCase().includes(keyword));
    const matchesCategory =
      activeCategory.value === "全部" ||
      game.tags.includes(activeCategory.value);
    return matchesKeyword && matchesCategory;
  });

  return [...filtered].sort((a, b) => {
    if (sortMode.value === "plays") return b.playCount - a.playCount;
    return String(b.publishedAt || "").localeCompare(
      String(a.publishedAt || ""),
    );
  });
});

function goPlay(gameId: string) {
  router.push(`/play/${gameId}`);
}

function scrollToGallery() {
  document
    .querySelector("#gallery")
    ?.scrollIntoView({ behavior: "smooth", block: "start" });
}

onMounted(async () => {
  loading.value = true;
  try {
    games.value = await fetchPublishedGames();
  } catch (error) {
    ElMessage.error(
      error instanceof Error ? error.message : "加载游戏列表失败",
    );
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.home-hero {
  position: relative;
  min-height: 286px;
  overflow: hidden;
  border: 1px solid #dce6f6;
  border-radius: 14px;
  background:
    radial-gradient(
      circle at 66% 40%,
      rgba(255, 255, 255, 0.8) 0 7%,
      transparent 26%
    ),
    linear-gradient(105deg, #eef6ff 0%, #eef4ff 43%, #eee8ff 72%, #f0d9ff 100%);
  box-shadow: 0 12px 28px rgba(65, 88, 135, 0.08);
}

.home-hero__content {
  position: relative;
  z-index: 2;
  width: min(58%, 650px);
  padding: 32px 40px;
}

.home-hero__eyebrow {
  display: inline-flex;
  height: 32px;
  align-items: center;
  gap: 7px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.78);
  color: #635bff;
  font-size: 14px;
  font-weight: 800;
  padding: 0 12px;
  box-shadow: 0 8px 20px rgba(99, 91, 255, 0.08);
}

.home-hero__eyebrow :deep(.el-icon) {
  font-size: 16px;
}

.home-hero h1 {
  margin: 14px 0 0;
  color: #07090f;
  font-size: 40px;
  font-weight: 900;
  letter-spacing: 0;
  line-height: 1.18;
}

.home-hero h1 span {
  color: #6957ff;
}

.home-hero p {
  margin: 16px 0 0;
  color: #626b7d;
  font-size: 15px;
  font-weight: 500;
  line-height: 1.65;
}

.home-hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 18px;
}

.home-hero__actions :deep(.el-button) {
  height: 42px;
  border-radius: 7px;
  font-size: 15px;
  font-weight: 800;
  padding: 0 28px;
}

.home-hero__primary {
  border: 0 !important;
  background: linear-gradient(135deg, #4167ff, #7d3cff) !important;
  box-shadow: 0 10px 22px rgba(89, 82, 255, 0.28);
}

.home-hero__secondary {
  border-color: #d5dcea !important;
  background: rgba(255, 255, 255, 0.9) !important;
  color: #111827 !important;
  box-shadow: 0 8px 18px rgba(31, 42, 68, 0.06);
}

.home-hero__visual {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 50%;
  overflow: hidden;
}

.home-hero__visual::before {
  position: absolute;
  inset: 0 auto 0 0;
  z-index: 1;
  width: 28%;
  background: linear-gradient(
    90deg,
    #eef6ff 0%,
    rgba(238, 246, 255, 0.76) 35%,
    rgba(238, 246, 255, 0) 100%
  );
  content: "";
}

.home-hero__visual img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center right;
}

.game-plaza {
  margin-top: 18px;
}

.plaza-toolbar {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 210px;
  gap: 14px;
}

.plaza-toolbar :deep(.el-input__wrapper),
.plaza-toolbar :deep(.el-select__wrapper) {
  height: 46px;
  border-radius: 9px !important;
  background: #fff;
  box-shadow:
    0 0 0 1px #dfe7f4 inset,
    0 10px 24px rgba(31, 42, 68, 0.07);
}

.plaza-toolbar :deep(.el-input__inner),
.plaza-toolbar :deep(.el-select__selected-item) {
  color: #4b5563;
  font-size: 14px;
  font-weight: 600;
}

.plaza-sort {
  width: 210px;
}

.category-row {
  display: flex;
  gap: 14px;
  margin-top: 14px;
  overflow: hidden;
  white-space: nowrap;
}

.category-pill {
  display: inline-flex;
  height: 34px;
  align-items: center;
  gap: 6px;
  border: 1px solid #dfe7f4;
  border-radius: 10px;
  background: #fff;
  color: #5f6b7a;
  cursor: pointer;
  font-size: 14px;
  font-weight: 700;
  padding: 0 18px;
}

.category-pill.active {
  border-color: transparent;
  background: linear-gradient(135deg, #4b6fff, #7c3aed);
  color: #fff;
}

.category-pill.more {
  padding-right: 14px;
}

.plaza-grid-wrap {
  margin-top: 18px;
  min-height: 540px;
}

.plaza-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;
}

@media (max-width: 1500px) {
  .plaza-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 1180px) {
  .home-hero {
    min-height: auto;
  }

  .home-hero__content {
    width: 68%;
    padding: 28px 30px;
  }

  .home-hero h1 {
    font-size: 34px;
  }

  .home-hero__visual {
    width: 48%;
  }

  .plaza-toolbar {
    grid-template-columns: 1fr;
  }

  .plaza-sort {
    width: 100%;
  }

  .plaza-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .home-hero__content {
    width: 100%;
    padding: 24px 20px;
  }

  .home-hero__visual {
    display: none;
  }

  .home-hero h1 {
    font-size: 30px;
  }

  .home-hero p {
    font-size: 14px;
  }

  .home-hero__break {
    display: none;
  }

  .home-hero__actions :deep(.el-button) {
    flex: 1 1 150px;
    padding: 0 14px;
  }
}
</style>
