<template>
  <main class="play-page">
    <header class="play-page__titlebar">
      <div class="play-page__title-left">
        <el-button
          text
          :icon="ArrowLeft"
          class="play-page__back"
          @click="router.push('/')"
        >
          返回
        </el-button>

        <div class="play-page__title-copy">
          <div class="play-page__heading-row">
            <h1>{{ gameTitle }}</h1>

            <span class="play-page__badge" :class="statusBadgeClass">{{
              statusLabel
            }}</span>
            <span class="play-page__status-line">{{ statusLine }}</span>
          </div>
        </div>
      </div>
      <el-button :icon="Refresh" class="play-page__refresh" @click="loadGame">
        刷新资源
      </el-button>
    </header>

    <div class="play-page__layout">
      <section class="play-page__main-column">
        <template v-if="loading">
          <section class="play-loading-card">
            <img :src="referenceImages.playLoadingImage" alt="" />
            <div class="play-loading-card__content">
              <el-icon class="is-loading" size="64"><Loading /></el-icon>
              <h2>正在加载游戏...</h2>
              <p>首次加载可能需要一些时间，请稍候。</p>
              <el-progress :percentage="56" :show-text="false" />
            </div>
          </section>
        </template>

        <template v-else-if="error">
          <section class="play-error-card">
            <div class="play-error-card__image">
              <img :src="referenceImages.playErrorImage" alt="" />
            </div>
            <div class="play-error-card__content">
              <div class="play-error-card__icon">
                <el-icon size="30"><WarningFilled /></el-icon>
              </div>
              <h2>游戏加载失败</h2>
              <p>{{ error }}</p>
              <div class="play-error-card__actions">
                <el-button
                  class="agent-gradient-button"
                  :icon="Refresh"
                  @click="loadGame"
                >
                  重试加载
                </el-button>
                <el-button :icon="House" @click="router.push('/')"
                  >返回首页</el-button
                >
              </div>
            </div>
          </section>
        </template>

        <template v-else>
          <RemoteGameFrame
            ref="gameFrameRef"
            :manifest="manifest"
            :error="error"
          />
        </template>

        <section class="play-toolbar">
          <div class="play-toolbar__left">
            <el-button :icon="Refresh" @click="restartGame">重新开始</el-button>
            <el-button :icon="Setting">设置</el-button>
          </div>
          <div class="play-toolbar__right">
            <el-button :icon="FullScreen" @click="requestGameFullscreen"
              >全屏</el-button
            >
            <el-button
              type="danger"
              plain
              :icon="Close"
              @click="router.push('/')"
            >
              退出游戏
            </el-button>
          </div>
        </section>

        <section class="related-panel">
          <h2>相关游戏</h2>
          <div class="related-panel__grid">
            <article
              v-for="game in relatedGames"
              :key="game.title"
              class="related-card"
            >
              <img :src="game.image" alt="" />
              <div>
                <h3>{{ game.title }}</h3>
                <span>{{ game.tag }}</span>
                <p>{{ game.plays }} 次游玩</p>
              </div>
            </article>
          </div>
        </section>
      </section>

      <aside class="play-page__side-column">
        <section class="game-info-card">
          <div class="game-info-card__hero">
            <img :src="coverImage" alt="" />
            <div>
              <h2>{{ gameTitle }}</h2>
              <div class="game-info-card__author">
                <span>墨染江南</span>
                <el-icon color="#4f63ff" size="14"
                  ><CircleCheckFilled
                /></el-icon>
              </div>
              <p class="game-info-card__hot">{{ playCountLabel }} 次游玩</p>
            </div>
          </div>

          <p class="game-info-card__description">
            {{ gameDescription }}
          </p>

          <div class="game-info-card__tags">
            <span v-for="tag in gameTags" :key="tag">{{ tag }}</span>
          </div>

          <div class="game-info-card__stats">
            <div>
              <strong>{{ playCountLabel }}</strong>
              <span>游玩次数</span>
            </div>
            <div>
              <strong>92%</strong>
              <span>好评率</span>
            </div>
          </div>

          <dl class="game-info-card__meta">
            <div v-for="item in gameMeta" :key="item.label">
              <dt>{{ item.label }}</dt>
              <dd>{{ item.value }}</dd>
            </div>
          </dl>
        </section>

        <RuntimeInfoPanel v-if="descriptor" :descriptor="descriptor" />
      </aside>
    </div>
  </main>
</template>

<script setup lang="ts">
import {
  ArrowLeft,
  CircleCheckFilled,
  Close,
  Connection,
  FullScreen,
  House,
  Loading,
  Microphone,
  Mute,
  Refresh,
  Setting,
  WarningFilled,
} from "@element-plus/icons-vue";
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

import { fetchPlayDescriptor } from "@/api/games";
import type { GameManifest, PlayDescriptor } from "@/api/types";
import RemoteGameFrame from "@/components/game/RemoteGameFrame.vue";
import RuntimeInfoPanel from "@/components/game/RuntimeInfoPanel.vue";
import { referenceImages } from "@/data/showcase";

const props = defineProps<{
  gameId: string;
}>();

type RemoteGameFrameInstance = InstanceType<typeof RemoteGameFrame>;

const router = useRouter();
const loading = ref(false);
const descriptor = ref<PlayDescriptor | null>(null);
const manifest = ref<GameManifest | null>(null);
const error = ref<string | null>(null);
const isMuted = ref(false);
const gameFrameRef = ref<RemoteGameFrameInstance | null>(null);

const relatedGames = [
  {
    title: "星露谷的夏天",
    tag: "冒险",
    plays: "8.7k",
    image: referenceImages.homeShowcase,
  },
  {
    title: "赛博纪元 2077：重启",
    tag: "科幻",
    plays: "12.1k",
    image: referenceImages.createPublishImage,
  },
  {
    title: "心动信号",
    tag: "恋爱",
    plays: "6.2k",
    image: referenceImages.authShowcase,
  },
  {
    title: "遗落的文明",
    tag: "解谜",
    plays: "9.3k",
    image: referenceImages.playErrorImage,
  },
];

const gameTitle = computed(
  () => descriptor.value?.title || manifest.value?.title || "迷雾之城：哀歌",
);
const gameDescription = computed(
  () =>
    descriptor.value?.description ||
    "在蒸汽与迷雾交织的维多利亚时代，你将扮演侦探艾登，调查一系列离奇的失踪案，揭开这座城市背后的黑暗秘密。",
);
const coverImage = computed(() =>
  descriptor.value?.coverUrl ||
  (error.value
    ? referenceImages.playErrorImage
    : referenceImages.playRunningImage),
);
const gameTags = computed(() =>
  descriptor.value?.tags?.length
    ? descriptor.value.tags
    : ["冒险", "解谜", "角色扮演", "剧情", "悬疑", "维多利亚"],
);
const playCountLabel = computed(() => formatPlayCount(descriptor.value?.playCount ?? 0));

const statusLabel = computed(() => {
  if (loading.value) return "加载中";
  if (error.value) return "加载失败";
  return "运行中";
});

const statusBadgeClass = computed(() => ({
  "play-page__badge--success": !loading.value && !error.value,
  "play-page__badge--danger": Boolean(error.value),
  "play-page__badge--info": loading.value,
}));

const statusLine = computed(() => {
  if (loading.value) return "正在加载运行资源，请稍候";
  if (error.value) return "加载失败，请检查远程资源";
  return "加载成功，可正常游戏";
});

const gameMeta = computed(() => [
  {
    label: "发布时间",
    value: descriptor.value?.publishedAt
      ? new Date(descriptor.value.publishedAt).toLocaleString()
      : "-",
  },
  { label: "最后更新", value: "2024-05-20 09:15" },
  { label: "作品类型", value: "AI 生成游戏" },
  { label: "使用模型", value: "GPT-4o + AgentPlay Runtime" },
  { label: "画面风格", value: "写实 / 暗黑 / 蒸汽朋克" },
]);

function isGameManifest(value: unknown): value is GameManifest {
  if (!value || typeof value !== "object") return false;
  const candidate = value as Partial<GameManifest>;
  return (
    candidate.schemaVersion === "game-manifest-v1" &&
    typeof candidate.entryUrl === "string" &&
    typeof candidate.title === "string"
  );
}

async function loadGame() {
  loading.value = true;
  error.value = null;
  manifest.value = null;
  try {
    descriptor.value = await fetchPlayDescriptor(props.gameId);
    const response = await fetch(descriptor.value.manifestUrl);
    if (!response.ok) throw new Error(`Manifest 请求失败: ${response.status}`);
    const payload = await response.json();
    if (!isGameManifest(payload)) throw new Error("Manifest 协议不合法");
    manifest.value = payload;
  } catch (caught) {
    error.value = caught instanceof Error ? caught.message : "加载失败";
  } finally {
    loading.value = false;
  }
}

function restartGame() {
  gameFrameRef.value?.restart();
}

function requestGameFullscreen() {
  gameFrameRef.value?.requestFullscreen();
}

function formatPlayCount(count: number) {
  if (count >= 10000) return `${(count / 10000).toFixed(1)}万`;
  if (count >= 1000) return `${(count / 1000).toFixed(1)}k`;
  return String(count);
}

onMounted(loadGame);
</script>

<style scoped>
.play-page {
  max-width: 1760px;
  margin: 0 auto;
  padding: 28px 32px 24px;
  color: #1e293b;
}

.play-page__titlebar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 18px;
}

.play-page__title-left {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 14px;
}

.play-page__back {
  color: #334155;
  font-weight: 600;
}

.play-page__cover {
  width: 40px;
  height: 40px;
  flex: 0 0 auto;
  border-radius: 8px;
  object-fit: cover;
  object-position: left top;
}

.play-page__title-copy {
  min-width: 0;
}

.play-page__heading-row {
  display: flex;
  min-width: 0;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.play-page__heading-row h1 {
  margin: 0;
  color: #0f172a;
  font-size: 26px;
  font-weight: 800;
  line-height: 1.2;
}

.play-page__badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-radius: 6px;
  padding: 5px 10px;
  font-size: 12px;
  font-weight: 700;
  line-height: 1;
}

.play-page__badge--ai {
  border: 1px solid #c7d2fe;
  background: #eef2ff;
  color: #4f46e5;
}

.play-page__badge--success {
  background: #dcfce7;
  color: #16a34a;
}

.play-page__badge--danger {
  background: #fee2e2;
  color: #dc2626;
}

.play-page__badge--info {
  background: #f1f5f9;
  color: #64748b;
}

.play-page__badge--success::before,
.play-page__badge--danger::before,
.play-page__badge--info::before {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: currentColor;
  content: "";
}

.play-page__status-line {
  color: #64748b;
  font-size: 13px;
  font-weight: 600;
}

.play-page__refresh {
  flex: 0 0 auto;
}

.play-page__layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 16px;
  align-items: start;
}

.play-page__main-column,
.play-page__side-column {
  display: grid;
  gap: 16px;
}

.play-loading-card,
.play-error-card,
.related-panel,
.game-info-card {
  border: 1px solid #dce4f0;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 8px 22px rgba(31, 42, 68, 0.05);
}

.play-loading-card {
  position: relative;
  display: grid;
  min-height: 620px;
  place-items: center;
  overflow: hidden;
  background: #0f172a;
  color: #fff;
}

.play-loading-card > img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: left top;
  opacity: 0.45;
}

.play-loading-card__content {
  position: relative;
  z-index: 1;
  width: min(520px, 80%);
  text-align: center;
}

.play-loading-card__content h2,
.play-error-card__content h2 {
  margin: 22px 0 0;
  font-size: 30px;
  font-weight: 800;
}

.play-loading-card__content p {
  margin: 14px 0 24px;
  color: rgba(255, 255, 255, 0.72);
}

.play-error-card {
  display: grid;
  min-height: 560px;
  grid-template-columns: 0.85fr 1fr;
  gap: 32px;
  overflow: hidden;
  padding: 20px;
}

.play-error-card__image {
  overflow: hidden;
  border-radius: 8px;
  background: #eff6ff;
}

.play-error-card__image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: left top;
  opacity: 0.78;
}

.play-error-card__content {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.play-error-card__icon {
  display: grid;
  width: 56px;
  height: 56px;
  place-items: center;
  border-radius: 999px;
  background: #ef4444;
  color: #fff;
}

.play-error-card__content p {
  margin: 18px 0 0;
  color: #64748b;
  font-size: 15px;
  line-height: 1.8;
}

.play-error-card__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 28px;
}

.play-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  border: 1px solid #dce4f0;
  border-radius: 8px;
  background: #fff;
  padding: 14px 16px;
}

.play-toolbar__left,
.play-toolbar__right {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.latency-pill {
  display: inline-flex;
  height: 32px;
  align-items: center;
  gap: 7px;
  border: 1px solid #dce4f0;
  border-radius: 6px;
  background: #fff;
  padding: 0 14px;
  color: #059669;
  font-size: 13px;
  font-weight: 700;
}

.related-panel {
  padding: 18px;
}

.related-panel h2 {
  margin: 0 0 14px;
  color: #0f172a;
  font-size: 16px;
  font-weight: 800;
}

.related-panel__grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.related-card {
  display: grid;
  grid-template-columns: 108px minmax(0, 1fr);
  gap: 12px;
  align-items: center;
  min-width: 0;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
  padding: 10px;
}

.related-card img {
  width: 108px;
  height: 70px;
  border-radius: 6px;
  object-fit: cover;
  object-position: left top;
}

.related-card h3 {
  overflow: hidden;
  margin: 0;
  color: #0f172a;
  font-size: 14px;
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.related-card span {
  display: inline-flex;
  margin-top: 8px;
  border-radius: 5px;
  background: #eef2ff;
  padding: 4px 8px;
  color: #4f46e5;
  font-size: 12px;
  font-weight: 700;
}

.related-card p {
  margin: 8px 0 0;
  color: #64748b;
  font-size: 12px;
}

.game-info-card {
  padding: 20px;
}

.game-info-card__hero {
  display: grid;
  grid-template-columns: 88px minmax(0, 1fr);
  gap: 14px;
  align-items: start;
}

.game-info-card__hero img {
  width: 88px;
  height: 88px;
  border-radius: 7px;
  object-fit: cover;
  object-position: left top;
}

.game-info-card__hero h2 {
  margin: 2px 0 8px;
  color: #0f172a;
  font-size: 20px;
  font-weight: 800;
  line-height: 1.25;
}

.game-info-card__author {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #475569;
  font-size: 13px;
  font-weight: 700;
}

.game-info-card__hot {
  margin: 8px 0 0;
  color: #64748b;
  font-size: 12px;
}

.game-info-card__description {
  margin: 18px 0 0;
  color: #64748b;
  font-size: 13px;
  line-height: 1.85;
}

.game-info-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
}

.game-info-card__tags span {
  border: 1px solid #ddd6fe;
  border-radius: 5px;
  background: #f5f3ff;
  padding: 5px 9px;
  color: #635bff;
  font-size: 12px;
  font-weight: 700;
}

.game-info-card__stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-top: 18px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 14px 0;
}

.game-info-card__stats div {
  display: grid;
  gap: 4px;
  place-items: center;
}

.game-info-card__stats div + div {
  border-left: 1px solid #e2e8f0;
}

.game-info-card__stats strong {
  color: #0f172a;
  font-size: 20px;
  line-height: 1;
}

.game-info-card__stats span {
  color: #64748b;
  font-size: 12px;
}

.game-info-card__meta {
  display: grid;
  gap: 12px;
  margin: 18px 0 0;
  font-size: 13px;
}

.game-info-card__meta div {
  display: grid;
  grid-template-columns: 82px minmax(0, 1fr);
  gap: 12px;
}

.game-info-card__meta dt {
  color: #64748b;
}

.game-info-card__meta dd {
  overflow: hidden;
  margin: 0;
  color: #475569;
  font-weight: 600;
  text-align: right;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.el-button) {
  border-radius: 6px;
  font-weight: 600;
}

@media (max-width: 1280px) {
  .play-page__layout {
    grid-template-columns: minmax(0, 1fr);
  }

  .play-page__side-column {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .related-panel__grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
