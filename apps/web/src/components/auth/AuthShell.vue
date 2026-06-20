<template>
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

      <h2 class="auth-title">
        在 AgentPlay，<br />
        人人都是游戏<span>创作者</span>，<br />
        人人都是<span>玩家</span>
      </h2>

      <p class="auth-desc">
        通过 AI Agent 让想象力变成互动世界，<br />
        开启由创作者发布的互动游戏，<br />
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

    <div class="auth-illustration" aria-hidden="true">
      <div class="orbit orbit-one" />
      <div class="orbit orbit-two" />
      <div class="bot">
        <span class="bot-eye left" />
        <span class="bot-eye right" />
      </div>
      <div class="float-card card-game">GAME</div>
      <div class="float-card card-list" />
      <div class="float-card card-image" />
      <div class="float-card card-like" />
    </div>
  </section>
</template>

<script setup lang="ts">
import { Connection, MagicStick, Promotion } from '@element-plus/icons-vue'

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
</script>

<style scoped>
.auth-hero {
  position: relative;
  flex: 0 0 min(41.7vw, 720px);
  min-width: 620px;
  height: calc(100vh - 28px);
  margin: 14px 0 14px 14px;
  overflow: hidden;
  border-radius: 16px 0 0 16px;
  background:
    radial-gradient(circle at 82% 84%, rgba(131, 97, 255, 0.3), transparent 36%),
    radial-gradient(circle at 70% 54%, rgba(96, 165, 250, 0.18), transparent 38%),
    linear-gradient(145deg, #f8fbff 0%, #eef6ff 48%, #ddd8ff 100%);
}

.auth-brand {
  position: absolute;
  top: 42px;
  left: 48px;
  z-index: 3;
  display: flex;
  align-items: center;
  gap: 14px;
  color: #050816;
  font-size: 29px;
  font-weight: 900;
  letter-spacing: -0.03em;
}

.auth-logo {
  position: relative;
  display: grid;
  width: 40px;
  height: 40px;
  place-items: center;
  border-radius: 12px;
  background: linear-gradient(135deg, #2563eb, #7657ff);
  box-shadow: 0 12px 28px rgba(79, 70, 229, 0.24);
}

.auth-logo::before,
.auth-logo::after {
  position: absolute;
  width: 23px;
  height: 23px;
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
  border-left: 16px solid #fff;
  border-top: 10px solid transparent;
  filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.14));
}

.auth-hero-content {
  position: relative;
  z-index: 2;
  padding: 136px 48px 0;
}

.auth-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 28px;
  padding: 0 13px;
  border: 1px solid rgba(124, 92, 255, 0.3);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.78);
  box-shadow: 0 8px 18px rgba(79, 70, 229, 0.08);
  color: #6555ff;
  font-size: 14px;
  font-weight: 800;
}

.auth-title {
  margin: 28px 0 0;
  color: #050816;
  font-size: 35px;
  font-weight: 600;
  letter-spacing: -0.055em;
  line-height: 1.5;
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
  right: 22px;
  bottom: 30px;
  width: 500px;
  height: 290px;
}

.orbit {
  position: absolute;
  left: 84px;
  bottom: 18px;
  border: 1px solid rgba(255, 255, 255, 0.86);
  border-radius: 50%;
  box-shadow: 0 0 16px rgba(255, 255, 255, 0.85);
  transform: rotate(-7deg);
}

.orbit-one {
  width: 320px;
  height: 96px;
}

.orbit-two {
  left: 118px;
  bottom: 34px;
  width: 240px;
  height: 72px;
}

.bot {
  position: absolute;
  left: 206px;
  bottom: 42px;
  width: 92px;
  height: 104px;
  border-radius: 50% 50% 44% 44%;
  background: linear-gradient(180deg, #fff 0%, #d8d8ff 100%);
  box-shadow: 0 18px 42px rgba(86, 76, 215, 0.28);
}

.bot::before {
  position: absolute;
  top: 30px;
  left: 18px;
  width: 56px;
  height: 34px;
  border-radius: 18px;
  background: #20275d;
  box-shadow: inset 0 0 15px rgba(74, 222, 255, 0.32);
  content: "";
}

.bot::after {
  position: absolute;
  right: 24px;
  bottom: -26px;
  left: 24px;
  height: 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 0 18px rgba(255, 255, 255, 0.9);
  content: "";
}

.bot-eye {
  position: absolute;
  z-index: 2;
  top: 44px;
  width: 9px;
  height: 13px;
  border-radius: 999px;
  background: #68e8ff;
  box-shadow: 0 0 10px #68e8ff;
}

.bot-eye.left {
  left: 35px;
}

.bot-eye.right {
  left: 55px;
}

.float-card {
  position: absolute;
  display: grid;
  place-items: center;
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.48);
  box-shadow: 0 18px 36px rgba(92, 82, 204, 0.18);
  backdrop-filter: blur(8px);
}

.card-game {
  left: 86px;
  top: 38px;
  width: 124px;
  height: 76px;
  color: #6a5cff;
  font-size: 18px;
  font-weight: 900;
  transform: rotate(-10deg);
}

.card-list {
  right: 42px;
  top: 40px;
  width: 120px;
  height: 74px;
  transform: rotate(10deg);
}

.card-list::before {
  width: 62px;
  height: 30px;
  border-top: 4px solid #fff;
  border-bottom: 4px solid #fff;
  content: "";
}

.card-image {
  left: 100px;
  bottom: 30px;
  width: 76px;
  height: 58px;
  transform: rotate(-12deg);
}

.card-image::before {
  width: 32px;
  height: 24px;
  border-radius: 4px;
  background: linear-gradient(135deg, #9cc2ff, #7b65ff);
  content: "";
}

.card-like {
  right: 10px;
  bottom: 92px;
  width: 72px;
  height: 54px;
  transform: rotate(11deg);
}

.card-like::before {
  color: #ef5cc8;
  content: "LIKE";
  font-size: 13px;
  font-weight: 900;
}

@media (max-width: 1180px) {
  .auth-hero {
    display: none;
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
    bottom: 18px;
    transform: scale(0.88);
    transform-origin: right bottom;
  }
}
</style>
