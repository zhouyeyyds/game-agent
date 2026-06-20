<template>
  <header class="sticky top-0 z-40 border-b border-slate-200/80 bg-white/90 backdrop-blur-xl">
    <div class="mx-auto flex h-16 max-w-[1800px] items-center gap-8 px-6 lg:px-12">
      <RouterLink to="/" class="flex shrink-0 items-center gap-3 text-slate-950 no-underline">
        <span class="grid h-10 w-10 place-items-center rounded-[14px] bg-gradient-to-br from-blue-500 via-indigo-500 to-violet-600 text-lg font-black text-white shadow-lg shadow-blue-500/20">
          A
        </span>
        <span class="text-2xl font-black tracking-tight">AgentPlay</span>
      </RouterLink>

      <nav class="hidden flex-1 items-center justify-center gap-10 text-sm font-bold text-slate-700 md:flex">
        <RouterLink to="/" class="nav-link" active-class="nav-link-active">首页</RouterLink>
        <button class="nav-link cursor-not-allowed opacity-45" type="button" disabled>发现</button>
        <RouterLink to="/create" class="nav-link create-link" active-class="nav-link-active">Create</RouterLink>
        <button class="nav-link cursor-not-allowed opacity-45" type="button" disabled>我的作品</button>
      </nav>

      <div class="ml-auto flex items-center gap-3">
        <template v-if="auth.isAuthenticated && auth.user">
          <el-button :icon="Bell" circle text />
          <el-dropdown trigger="click" @command="handleCommand">
            <button class="flex items-center gap-2 rounded-full border border-slate-200 bg-white px-2 py-1 text-sm font-bold text-slate-800 shadow-sm" type="button">
              <span class="grid h-8 w-8 place-items-center rounded-full bg-gradient-to-br from-slate-900 to-indigo-600 text-xs text-white">
                {{ auth.user.displayName.slice(0, 1).toUpperCase() }}
              </span>
              <span class="hidden max-w-28 truncate sm:inline">{{ auth.user.displayName }}</span>
              <el-icon><ArrowDown /></el-icon>
            </button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item disabled>{{ auth.user.email }}</el-dropdown-item>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <RouterLink to="/login" class="hidden sm:inline-flex">
            <el-button>登录</el-button>
          </RouterLink>
          <RouterLink to="/register">
            <el-button type="primary">注册</el-button>
          </RouterLink>
        </template>
        <el-button circle text>中</el-button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ArrowDown, Bell } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

async function handleCommand(command: string) {
  if (command !== 'logout') return
  try {
    await auth.logout()
    ElMessage.success('已退出登录')
    await router.push('/')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '退出登录失败')
  }
}
</script>
