<template>
  <main class="auth-page">
    <AuthShell />
    <section class="auth-form-zone">
      <div class="auth-form-stack">
        <AuthCard mode="register" />
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
import AuthCard from '@/components/auth/AuthCard.vue'
import AuthShell from '@/components/auth/AuthShell.vue'
</script>

<style scoped>
.auth-page {
  display: flex;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background: radial-gradient(circle at 50% 50%, rgba(148, 163, 184, 0.1), transparent 34%), #fff;
}

.auth-form-zone {
  display: flex;
  height: 100vh;
  min-width: 0;
  flex: 1 1 auto;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  padding: 0 72px 0 48px;
}

.auth-form-stack {
  display: flex;
  width: min(738px, 100%);
  min-height: 0;
  flex: 0 1 738px;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}

.auth-footer {
  flex: 0 0 auto;
  margin-top: 20px;
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

@media (max-width: 1180px) {
  .auth-form-zone {
    padding: 0 24px;
  }
}

@media (max-height: 820px) {
  .auth-form-zone {
    align-items: flex-start;
    padding-top: 20px;
    padding-bottom: 16px;
  }
}
</style>
