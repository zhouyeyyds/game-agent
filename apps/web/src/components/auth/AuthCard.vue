<template>
  <section class="auth-card">
    <el-segmented
      v-model="activeMode"
      :options="tabs"
      block
      @change="handleTabChange"
    />

    <el-form class="auth-form" label-position="top" @submit.prevent="submit">
      <el-form-item v-if="isRegister" label="昵称">
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

      <div v-if="!isRegister" class="auth-options">
        <el-checkbox v-model="remember">记住我</el-checkbox>
        <button type="button">忘记密码?</button>
      </div>

      <el-button
        class="auth-submit"
        size="large"
        type="primary"
        :loading="auth.loading"
        @click="submit"
      >
        {{ isRegister ? "注册" : "登录" }}
      </el-button>
    </el-form>

    <div class="auth-divider">
      <span />
      <em>或继续使用</em>
      <span />
    </div>

    <div class="social-buttons">
      <el-button size="large">
        <svg class="social-icon" viewBox="0 0 24 24" aria-hidden="true">
          <path
            fill="#4285F4"
            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
          />
          <path
            fill="#34A853"
            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
          />
          <path
            fill="#FBBC05"
            d="M5.84 14.1c-.22-.66-.35-1.36-.35-2.1s.13-1.44.35-2.1V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l3.66-2.84z"
          />
          <path
            fill="#EA4335"
            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84C6.71 7.3 9.14 5.38 12 5.38z"
          />
        </svg>
        使用 Google 账号{{ isRegister ? "注册" : "登录" }}
      </el-button>
      <el-button size="large">
        <svg
          class="social-icon github-icon"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            fill="currentColor"
            d="M12 1.5C6.2 1.5 1.5 6.3 1.5 12.2c0 4.7 3 8.7 7.2 10.1.5.1.7-.2.7-.5v-1.9c-2.9.6-3.5-1.3-3.5-1.3-.5-1.2-1.1-1.5-1.1-1.5-.9-.6.1-.6.1-.6 1 .1 1.6 1.1 1.6 1.1.9 1.6 2.4 1.1 3 .9.1-.7.4-1.1.7-1.3-2.3-.3-4.8-1.2-4.8-5.3 0-1.2.4-2.1 1.1-2.9-.1-.3-.5-1.4.1-2.9 0 0 .9-.3 2.9 1.1.8-.2 1.7-.3 2.6-.3s1.8.1 2.6.3c2-1.4 2.9-1.1 2.9-1.1.6 1.5.2 2.6.1 2.9.7.8 1.1 1.7 1.1 2.9 0 4.1-2.5 5-4.8 5.3.4.3.7 1 .7 2v3c0 .3.2.6.7.5 4.2-1.4 7.2-5.4 7.2-10.1C22.5 6.3 17.8 1.5 12 1.5z"
          />
        </svg>
        使用 GitHub 账号{{ isRegister ? "注册" : "登录" }}
      </el-button>
    </div>

    <p class="auth-switch">
      {{ isRegister ? "已有账号?" : "没有账号?" }}
      <RouterLink :to="isRegister ? '/login' : '/register'">{{
        isRegister ? "立即登录" : "立即注册"
      }}</RouterLink>
    </p>
  </section>
</template>

<script setup lang="ts">
import { Lock, Message, User } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useAuthStore } from "@/stores/auth";

const props = defineProps<{
  mode: "login" | "register";
}>();

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();

const activeMode = ref(props.mode);
const remember = ref(true);
const displayName = ref("Creator");
const email = ref("");
const password = ref("");

const tabs = [
  { label: "登录", value: "login" },
  { label: "注册", value: "register" },
];

const isRegister = computed(() => activeMode.value === "register");

watch(
  () => props.mode,
  (mode) => {
    activeMode.value = mode;
  },
);

function handleTabChange(value: string | number) {
  const target = value === "register" ? "register" : "login";
  if (target !== props.mode) {
    router.push({ name: target, query: route.query });
  }
}

async function submit() {
  try {
    if (isRegister.value) {
      await auth.register({
        displayName: displayName.value || "Creator",
        email: email.value || "creator@example.com",
        password: password.value || "password123",
      });
      await router.push("/create");
      return;
    }

    await auth.login({
      email: email.value || "demo@example.com",
      password: password.value || "password123",
    });
    await router.push(String(route.query.redirect || "/create"));
  } catch (error) {
    ElMessage.error(
      error instanceof Error
        ? error.message
        : isRegister.value
          ? "注册失败"
          : "登录失败",
    );
  }
}
</script>

<style scoped>
.auth-card {
  flex: 0 0 auto;
  box-sizing: border-box;
  width: 80%;
  max-height: calc(100vh - 120px);
  overflow: hidden;
  padding: 52px 60px 34px;
  border: 1px solid rgba(224, 229, 239, 0.95);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 24px 50px rgba(15, 23, 42, 0.1);
}

/* .auth-tabs {
  margin: 0;
}

.auth-tabs :deep(.el-segmented) {
  --el-segmented-item-selected-bg-color: #3f9df5;
  --el-segmented-item-selected-color: #ffffff;
  --el-segmented-item-hover-color: #2f63ff;
  height: 50px;
  padding: 4px;
  border: 0;
  border-radius: 4px;
  background: #f3f6fb;
}

.auth-tabs :deep(.el-segmented__item) {
  height: 42px;
  border-radius: 3px;
  color: #1f2a44;
  font-size: 16px;
  font-weight: 800;
}

.auth-tabs :deep(.el-segmented__item-selected) {
  background: #3f9df5;
  color: #5d49ff;
  box-shadow: 0 6px 14px rgba(47, 99, 255, 0.16);
} */

.auth-form {
  margin-top: 26px;
}

.auth-form :deep(.el-form-item) {
  margin-bottom: 18px;
}

.auth-form :deep(.el-form-item__label) {
  margin-bottom: 8px;
  color: #0f172a;
  font-size: 14px;
  font-weight: 800;
}

.auth-form :deep(.el-input__wrapper) {
  height: 56px;
  border-radius: 8px !important;
  box-shadow: 0 0 0 1px #dce3ef inset;
}

.auth-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: -1px 0 24px;
}

.auth-options button {
  border: 0;
  background: transparent;
  color: #6555ff;
  cursor: pointer;
  font-size: 13px;
  font-weight: 800;
}

.auth-submit {
  width: 100%;
  height: 58px;
  border: 0;
  border-radius: 8px;
  background: linear-gradient(135deg, #2f63ff, #7c3aed);
  font-size: 18px;
  font-weight: 900;
}

.auth-divider {
  display: flex;
  align-items: center;
  gap: 28px;
  margin: 22px 0 18px;
  color: #8a94a6;
  font-size: 13px;
  font-style: normal;
}

.auth-divider span {
  height: 1px;
  flex: 1;
  background: #e2e7f0;
}

.auth-divider em {
  font-style: normal;
}

.social-buttons {
  display: grid;
  gap: 12px;
}

.social-buttons :deep(.el-button) {
  height: 58px;
  margin-left: 0;
  border-color: #dce3ef;
  border-radius: 8px;
  color: #0f172a;
  font-size: 17px;
  font-weight: 800;
}

.social-icon {
  width: 22px;
  height: 22px;
  margin-right: 14px;
}

.github-icon {
  color: #0f172a;
}

.auth-switch {
  margin: 18px 0 0;
  color: #8a94a6;
  text-align: center;
  font-size: 14px;
}

.auth-switch a {
  color: #6555ff;
  font-weight: 900;
  text-decoration: none;
}

@media (max-height: 850px) {
  .auth-card {
    max-height: calc(100vh - 44px);
    padding: 32px 48px 24px;
  }

  .auth-form {
    margin-top: 18px;
  }

  .auth-form :deep(.el-form-item) {
    margin-bottom: 12px;
  }

  .auth-form :deep(.el-input__wrapper),
  .auth-submit,
  .social-buttons :deep(.el-button) {
    height: 48px;
  }

  .auth-divider {
    margin: 14px 0 12px;
  }

  .social-buttons {
    gap: 9px;
  }
}
</style>
