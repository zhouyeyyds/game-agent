<template>
  <section class="auth-card">
    <el-segmented
      v-model="activeMode"
      :options="tabs"
      block
      @change="handleTabChange"
    />

    <RegisterForm v-if="isRegister" />
    <LoginForm v-else />

    <div class="auth-divider">
      <span />
      <em>或继续使用</em>
      <span />
    </div>

    <div class="social-buttons">
      <el-button
        size="large"
        :loading="providersLoading"
        @click="startGoogleOAuth"
      >
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
      <el-button
        size="large"
        :loading="providersLoading"
        @click="startGitHubOAuth"
      >
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
import { ElMessage } from "element-plus";
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import {
  fetchOAuthProviders,
  oauthStartUrl,
  type OAuthProviderStatus,
} from "@/api/auth";
import LoginForm from "@/components/auth/LoginForm.vue";
import RegisterForm from "@/components/auth/RegisterForm.vue";

const props = defineProps<{
  mode: "login" | "register";
}>();

const route = useRoute();
const router = useRouter();

const activeMode = ref(props.mode);
const providers = ref<OAuthProviderStatus[]>([]);
const providersLoading = ref(false);

const tabs = [
  { label: "登录", value: "login" },
  { label: "注册", value: "register" },
];

const isRegister = computed(() => activeMode.value === "register");
const githubProvider = computed(() =>
  providers.value.find((provider) => provider.provider === "github"),
);

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

function currentRedirect() {
  const redirect = route.query.redirect;
  if (typeof redirect === "string" && redirect.startsWith("/")) return redirect;
  return "/create";
}

async function loadOAuthProviders() {
  providersLoading.value = true;
  try {
    providers.value = (await fetchOAuthProviders()).providers;
  } catch {
    providers.value = [];
  } finally {
    providersLoading.value = false;
  }
}

function startGitHubOAuth() {
  if (!githubProvider.value?.configured) {
    ElMessage.warning(
      "GitHub OAuth 未配置，请先设置 GitHub OAuth App 的 Client ID 和 Secret",
    );
    return;
  }
  window.location.href = oauthStartUrl("github", currentRedirect());
}

function startGoogleOAuth() {
  ElMessage.info(
    "Google OAuth demo 阶段暂未接入，当前仅 GitHub 支持真实授权登录",
  );
}

onMounted(() => {
  void loadOAuthProviders();
  const oauthError = route.query.oauth_error;
  if (typeof oauthError === "string" && oauthError) {
    ElMessage.error(formatOAuthError(oauthError));
  }
});

function formatOAuthError(value: string) {
  const knownMessages: Record<string, string> = {
    google_not_configured: "Google OAuth demo 阶段暂未接入",
    github_missing_code: "GitHub 授权回调缺少 code，请重新登录",
    "GitHub OAuth is not configured": "GitHub OAuth 未配置",
    "OAuth state mismatch": "GitHub 授权状态校验失败，请重新登录",
    "Invalid OAuth state": "GitHub 授权状态已失效，请重新登录",
    "GitHub account has no verified primary email":
      "GitHub 账号缺少已验证主邮箱",
    "GitHub OAuth request failed": "GitHub 授权请求失败，请稍后重试",
  };
  return knownMessages[value] || `第三方登录失败：${value}`;
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

.auth-tabs {
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
