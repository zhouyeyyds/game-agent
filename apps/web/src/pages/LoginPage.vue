<template>
  <main class="mx-auto flex min-h-[calc(100vh-80px)] max-w-md items-center px-6 py-10">
    <NCard title="登录创作者账号" class="w-full border border-white/10 bg-white/5">
      <NForm @submit.prevent="submit">
        <NFormItem label="邮箱">
          <NInput v-model:value="email" placeholder="demo@example.com" />
        </NFormItem>
        <NFormItem label="密码">
          <NInput v-model:value="password" type="password" show-password-on="click" />
        </NFormItem>
        <NButton block type="primary" :loading="auth.loading" @click="submit">登录</NButton>
      </NForm>
      <p class="mt-4 text-center text-sm text-slate-400">
        还没有账号？<RouterLink class="text-neon" to="/register">立即注册</RouterLink>
      </p>
    </NCard>
  </main>
</template>

<script setup lang="ts">
import { NButton, NCard, NForm, NFormItem, NInput, useMessage } from 'naive-ui'
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const message = useMessage()

const email = ref('demo@example.com')
const password = ref('password123')

async function submit() {
  try {
    await auth.login({ email: email.value, password: password.value })
    await router.push(String(route.query.redirect || '/create'))
  } catch (error) {
    message.error(error instanceof Error ? error.message : '登录失败')
  }
}
</script>
