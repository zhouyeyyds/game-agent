<template>
  <main class="auth-page">
    <section class="auth-hero">
      <div class="auth-brand">
        <span class="auth-logo">
          <span class="auth-logo-triangle" />
        </span>
        <span>AgentPlay</span>
      </div>

      <div class="auth-hero-content">
        <div class="auth-pill">
          <el-icon><MagicStick /></el-icon>
          <span>AI 驱动的互动游戏创作与体验社区</span>
        </div>

        <h1 class="auth-title">
          在 AgentPlay，<br />
          人人都是游戏<span>创作者</span>，<br />
          人人都是<span>玩家</span>
        </h1>

        <p class="auth-desc">
          通过 AI Agent 让想象力变成互动世界，<br />
          开启自由创作者发布的互动游戏，<br />
          或使用 Create 打造你的专属作品并发布到世界。
        </p>

        <div class="auth-features">
          <div v-for="item in featureItems" :key="item.title" class="auth-feature">
            <span class="auth-feature-icon">
              <el-icon><component :is="item.icon" /></el-icon>
            </span>
            <div>
              <h3>{{ item.title }}</h3>
              <p>{{ item.text }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="auth-illustration" aria-hidden="true" />
    </section>

    <section class="auth-form-zone">
      <div class="auth-form-stack">
        <slot />
        <footer class="auth-footer">
          <div>
            <span>帮助中心</span>
            <i />
            <span>用户协议</span>
            <i />
            <span>隐私政策</span>
          </div>
          <p>© 2024 AgentPlay. 保留所有权利。</p>
        </footer>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { Connection, MagicStick, Promotion } from '@element-plus/icons-vue'

import { referenceImages } from '@/data/showcase'

const featureItems = [
  {
    title: 'AI 生成，创意无限',
    text: '用自然语言生成剧情、角色与世界设定，AI 帮你快速落地创意。',
    icon: MagicStick,
  },
  {
    title: '沉浸体验，互动随心',
    text: '多分支剧情、角色记忆、实时反馈，每一次选择都影响叙事走向。',
    icon: Connection,
  },
  {
    title: '创作发布，连接世界',
    text: '一键发布你的作品，收获玩家反馈，与全球创作者共同成长。',
    icon: Promotion,
  },
]

const showcaseImage = `url("${referenceImages.authShowcase}")`
</script>

<style scoped>
.auth-page {
  display: flex;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: #fff;
}

.auth-hero {
  position: relative;
  flex: 0 0 clamp(700px, 41.65vw, 780px);
  height: calc(100vh - 28px);
  margin: 14px 0 14px 14px;
  overflow: hidden;
  border-radius: 16px 0 0 16px;
  background:
    radial-gradient(circle at 84% 82%, rgba(139, 92, 246, 0.24), transparent 33%),
    radial-gradient(circle at 72% 52%, rgba(96, 165, 250, 0.16), transparent 36%),
    linear-gradient(142deg, #f8fbff 0%, #eef6ff 48%, #ddd8ff 100%);
}

.auth-brand {
  position: absolute;
  top: 38px;
  left: 44px;
  z-index: 3;
  display: flex;
  align-items: center;
  gap: 14px;
  color: #070b16;
  font-size: 28px;
  font-weight: 900;
  letter-spacing: -0.03em;
}

.auth-logo {
  position: relative;
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  border-radius: 12px;
  background: linear-gradient(135deg, #2563eb, #7657ff);
  box-shadow: 0 12px 28px rgba(79, 70, 229, 0.24);
}

.auth-logo::before,
.auth-logo::after {
  position: absolute;
  width: 22px;
  height: 22px;
  border-radius: 8px;
  background: rgba(113, 225, 255, 0.68);
  content: "";
}

.auth-logo::before {
  left: -4px;
  top: 8px;
}

.auth-logo::after {
  right: -4px;
  bottom: 8px;
}

.auth-logo-triangle {
  position: relative;
  z-index: 2;
  width: 0;
  height: 0;
  border-bottom: 10px solid transparent;
  border-left: 15px solid #fff;
  border-top: 10px solid transparent;
  filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.14));
}

.auth-hero-content {
  position: relative;
  z-index: 2;
  padding: 124px 46px 0;
}

.auth-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 28px;
  padding: 0 13px;
  border: 1px solid rgba(124, 92, 255, 0.28);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.78);
  box-shadow: 0 8px 18px rgba(79, 70, 229, 0.08);
  color: #6555ff;
  font-size: 14px;
  font-weight: 800;
}

.auth-title {
  margin: 28px 0 0;
  color: #070b16;
  font-size: clamp(36px, 3.15vw, 46px);
  font-weight: 950;
  letter-spacing: -0.055em;
  line-height: 1.14;
}

.auth-title span {
  color: #4f63ff;
}

.auth-desc {
  margin: 26px 0 0;
  color: #475569;
  font-size: 15px;
  font-weight: 500;
  line-height: 1.78;
}

.auth-features {
  display: flex;
  flex-direction: column;
  gap: 22px;
  margin-top: 30px;
  padding-bottom: 270px;
}

.auth-feature {
  display: flex;
  max-width: 520px;
  align-items: center;
  gap: 20px;
}

.auth-feature-icon {
  display: grid;
  width: 50px;
  height: 50px;
  flex: 0 0 50px;
  place-items: center;
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 14px 30px rgba(72, 89, 143, 0.16);
  color: #6857ff;
  font-size: 24px;
}

.auth-feature h3 {
  margin: 0;
  color: #0b1020;
  font-size: 16px;
  font-weight: 900;
}

.auth-feature p {
  margin: 5px 0 0;
  color: #475569;
  font-size: 13px;
  font-weight: 500;
  line-height: 1.45;
}

.auth-illustration {
  position: absolute;
  right: 0;
  bottom: 0;
  width: min(520px, 74%);
  height: 286px;
  background-image: v-bind(showcaseImage);
  background-position: 43% 100%;
  background-repeat: no-repeat;
  background-size: 1060px auto;
  opacity: 0.74;
  mix-blend-mode: multiply;
  mask-image: linear-gradient(90deg, transparent 0%, #000 18%, #000 100%);
}

.auth-form-zone {
  display: flex;
  height: 100vh;
  min-width: 0;
  flex: 1 1 auto;
  align-items: stretch;
  justify-content: center;
  overflow: hidden;
  padding: 0 72px 0 48px;
  background:
    radial-gradient(circle at 52% 50%, rgba(148, 163, 184, 0.12), transparent 32%),
    #fff;
}

.auth-form-stack {
  display: flex;
  width: min(506px, 100%);
  height: 100%;
  min-height: 0;
  flex: 0 1 506px;
  flex-direction: column;
  justify-content: center;
  padding: 36px 0;
  box-sizing: border-box;
}

.auth-footer {
  flex: 0 0 auto;
  margin-top: 18px;
  color: #8a94a6;
  text-align: center;
  font-size: 13px;
  font-weight: 500;
}

.auth-footer div {
  display: flex;
  justify-content: center;
  gap: 18px;
}

.auth-footer i {
  width: 1px;
  height: 13px;
  background: #d8dde8;
}

.auth-footer p {
  margin: 10px 0 0;
}

@media (max-width: 1023px) {
  .auth-hero {
    display: none;
  }

  .auth-form-zone {
    padding: 0 24px;
  }
}

@media (max-height: 860px) {
  .auth-form-stack {
    justify-content: flex-start;
    padding-top: 20px;
    padding-bottom: 16px;
  }

  .auth-footer {
    margin-top: 10px;
  }
}

@media (max-height: 820px) {
  .auth-brand {
    top: 30px;
  }

  .auth-hero-content {
    padding-top: 102px;
  }

  .auth-features {
    gap: 15px;
    margin-top: 22px;
    padding-bottom: 220px;
  }

  .auth-illustration {
    height: 238px;
  }
}
</style>
