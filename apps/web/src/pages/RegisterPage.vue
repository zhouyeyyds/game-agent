<template>
  <AuthShell>
    <section class="login-card">
      <el-segmented
        v-model="activeTab"
        :options="tabs"
        block
        class="login-tabs"
        @change="handleTabChange"
      />

      <el-form
        class="login-form register-form"
        label-position="top"
        @submit.prevent="submit"
      >
        <el-form-item label="昵称">
          <el-input
            v-model="displayName"
            :prefix-icon="User"
            placeholder="Creator"
            size="large"
          />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input
            v-model="email"
            :prefix-icon="Message"
            placeholder="请输入邮箱地址"
            size="large"
          />
        </el-form-item>
        <el-form-item label="密码">
          <el-input
            v-model="password"
            :prefix-icon="Lock"
            type="password"
            show-password
            placeholder="请输入密码"
            size="large"
          />
        </el-form-item>

        <el-button
          class="login-submit"
          size="large"
          type="primary"
          :loading="auth.loading"
          @click="submit"
        >
          创建账号
        </el-button>
      </el-form>

      <div class="login-divider">
        <span />
        <em>或继续使用</em>
        <span />
      </div>

      <div class="social-buttons">
        <el-button size="large">
          <span class="google-dot">G</span>
          使用 Google 账号注册
        </el-button>
        <el-button size="large">
          <span class="github-dot">●</span>
          使用 GitHub 账号注册
        </el-button>
      </div>

      <p class="register-tip">
        已有账号？
        <RouterLink to="/login">立即登录</RouterLink>
      </p>
    </section>
  </AuthShell>
</template>

<script setup lang="ts">
import { Lock, Message, User } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { ref } from "vue";
import { useRouter } from "vue-router";

import AuthShell from "@/components/auth/AuthShell.vue";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const router = useRouter();

const activeTab = ref("register");
const displayName = ref("Creator");
const email = ref("");
const password = ref("");
const tabs = [
  { label: "登录", value: "login" },
  { label: "注册", value: "register" },
];

function handleTabChange(value: string | number) {
  if (value === "login") router.push("/login");
}

async function submit() {
  try {
    await auth.register({
      displayName: displayName.value || "Creator",
      email: email.value || "creator@example.com",
      password: password.value || "password123",
    });
    await router.push("/create");
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "注册失败");
  }
}
</script>

<style scoped>
.login-card {
  flex: 0 0 auto;
  box-sizing: border-box;
  max-height: calc(100vh - 108px);
  overflow: hidden;
  padding: 28px 48px 30px;
  border: 1px solid rgba(224, 229, 239, 0.9);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 24px 50px rgba(15, 23, 42, 0.1);
}

.login-brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #0b1020;
  font-size: 24px;
  font-weight: 900;
}

.mini-logo {
  position: relative;
  display: grid;
  width: 29px;
  height: 29px;
  place-items: center;
  border-radius: 9px;
  background: linear-gradient(135deg, #2563eb, #7657ff);
}

.mini-logo::before,
.mini-logo::after {
  position: absolute;
  width: 17px;
  height: 17px;
  border-radius: 6px;
  background: rgba(113, 225, 255, 0.66);
  content: "";
}

.mini-logo::before {
  left: -3px;
  top: 6px;
}

.mini-logo::after {
  right: -3px;
  bottom: 6px;
}

.mini-logo span {
  position: relative;
  z-index: 2;
  width: 0;
  height: 0;
  border-bottom: 7px solid transparent;
  border-left: 11px solid white;
  border-top: 7px solid transparent;
}

.login-tabs {
  margin-top: 24px;
}

.login-tabs :deep(.el-segmented) {
  --el-segmented-item-selected-bg-color: #ffffff;
  height: 46px;
  padding: 4px;
  border: 1px solid #e1e6f0;
  border-radius: 9px;
  background: #f7f9fc;
}

.login-tabs :deep(.el-segmented__item) {
  height: 38px;
  border-radius: 7px;
  color: #4b5563;
  font-size: 15px;
  font-weight: 700;
}

.login-tabs :deep(.is-selected) {
  color: #5b55ff;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
}

.login-form {
  margin-top: 22px;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 18px;
}

.login-form :deep(.el-form-item__label) {
  margin-bottom: 8px;
  color: #0f172a;
  font-size: 14px;
  font-weight: 800;
}

.login-form :deep(.el-input__wrapper) {
  height: 43px;
  border-radius: 8px;
  box-shadow: 0 0 0 1px #dce3ef inset;
}

.login-submit {
  width: 100%;
  height: 47px;
  border: 0;
  border-radius: 8px;
  background: linear-gradient(135deg, #2f63ff, #7c3aed);
  font-size: 16px;
  font-weight: 800;
}

.login-divider {
  display: flex;
  align-items: center;
  gap: 24px;
  margin: 22px 0 18px;
  color: #8a94a6;
  font-size: 13px;
  font-style: normal;
}

.login-divider span {
  height: 1px;
  flex: 1;
  background: #e2e7f0;
}

.login-divider em {
  font-style: normal;
}

.social-buttons {
  display: grid;
  gap: 12px;
}

.social-buttons :deep(.el-button) {
  height: 47px;
  margin-left: 0;
  border-color: #dce3ef;
  border-radius: 8px;
  color: #1f2937;
  font-size: 15px;
  font-weight: 700;
}

.google-dot {
  margin-right: 12px;
  color: #4285f4;
  font-size: 19px;
  font-weight: 900;
}

.github-dot {
  margin-right: 12px;
  color: #0f172a;
  font-size: 19px;
}

.register-tip {
  margin: 16px 0 0;
  color: #8a94a6;
  text-align: center;
  font-size: 14px;
}

.register-tip a {
  color: #6555ff;
  font-weight: 900;
  text-decoration: none;
}

@media (max-height: 850px) {
  .login-card {
    max-height: calc(100vh - 44px);
    padding-top: 18px;
    padding-bottom: 18px;
  }

  .login-tabs {
    margin-top: 18px;
  }

  .login-form {
    margin-top: 16px;
  }

  .login-form :deep(.el-form-item) {
    margin-bottom: 12px;
  }

  .login-divider {
    margin: 14px 0 12px;
  }

  .social-buttons {
    gap: 9px;
  }

  .safe-note {
    margin-top: 12px;
    padding-top: 12px;
  }
}
</style>
