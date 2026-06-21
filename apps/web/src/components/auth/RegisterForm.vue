<template>
  <el-form class="auth-form" label-position="top" @submit.prevent="submit">
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
      class="auth-submit"
      size="large"
      type="primary"
      native-type="submit"
      :loading="auth.loading"
    >
      注册
    </el-button>
  </el-form>
</template>

<script setup lang="ts">
import { Lock, Message, User } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { ref } from "vue";
import { useRouter } from "vue-router";

import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const router = useRouter();

const displayName = ref("Creator");
const email = ref("");
const password = ref("");

async function submit() {
  try {
    await auth.register({
      displayName: displayName.value,
      email: email.value,
      password: password.value,
    });
    await router.push("/");
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : "注册失败");
  }
}
</script>

<style scoped>
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

.auth-submit {
  width: 100%;
  height: 58px;
  border: 0;
  border-radius: 8px;
  background: linear-gradient(135deg, #2f63ff, #7c3aed);
  font-size: 18px;
  font-weight: 900;
}

@media (max-height: 850px) {
  .auth-form {
    margin-top: 18px;
  }

  .auth-form :deep(.el-form-item) {
    margin-bottom: 12px;
  }

  .auth-form :deep(.el-input__wrapper),
  .auth-submit {
    height: 48px;
  }
}
</style>
