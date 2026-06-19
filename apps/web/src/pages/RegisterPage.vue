<template>
  <main class="mx-auto flex min-h-[calc(100vh-80px)] max-w-md items-center px-6 py-10">
    <NCard title="注册创作者账号" class="w-full border border-white/10 bg-white/5">
      <NForm @submit.prevent="submit">
        <NFormItem label="昵称">
          <NInput v-model:value="displayName" placeholder="Creator" />
        </NFormItem>
        <NFormItem label="邮箱">
          <NInput v-model:value="email" placeholder="creator@example.com" />
        </NFormItem>
        <NFormItem label="密码">
          <NInput v-model:value="password" type="password" show-password-on="click" />
        </NFormItem>
        <NButton block type="primary" :loading="auth.loading" @click="submit">注册</NButton>
      </NForm>
    </NCard>
  </main>
</template>

<script setup lang="ts">
import { NButton, NCard, NForm, NFormItem, NInput, useMessage } from 'naive-ui'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const message = useMessage()

const displayName = ref('Creator')
const email = ref('creator@example.com')
const password = ref('password123')

async function submit() {
  try {
    await auth.register({ displayName: displayName.value, email: email.value, password: password.value })
    await router.push('/create')
  } catch (error) {
    message.error(error instanceof Error ? error.message : '注册失败')
  }
}
</script>
