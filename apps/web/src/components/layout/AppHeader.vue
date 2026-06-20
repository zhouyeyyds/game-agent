<template>
  <header class="fixed inset-x-0 top-0 z-50 h-16 border-b border-slate-200 bg-white">
    <div class="flex h-full items-center gap-3 px-4 lg:px-6">
      <RouterLink to="/" class="flex shrink-0 items-center gap-3 text-slate-800 no-underline">
        <span class="brand-mark">A</span>
        <span class="hidden text-xl font-semibold tracking-normal sm:inline">AgentPlay</span>
      </RouterLink>

      <el-button class="hidden lg:inline-flex" :icon="Refresh" circle text @click="reloadPage" />

      <nav class="hidden h-full items-center gap-7 md:flex">
        <RouterLink v-for="item in navItems" :key="item.to" :to="item.to" class="nav-link" active-class="nav-link-active">
          <el-icon>
            <component :is="item.icon" />
          </el-icon>
          <span>{{ item.label }}</span>
        </RouterLink>
        <el-dropdown trigger="click">
          <button class="nav-link" type="button">
            <el-icon><Grid /></el-icon>
            <span>更多</span>
            <el-icon><ArrowDown /></el-icon>
          </button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item disabled>我的作品</el-dropdown-item>
              <el-dropdown-item disabled>数据面板</el-dropdown-item>
              <el-dropdown-item disabled>素材库</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </nav>

      <div class="ml-auto hidden w-[260px] xl:block">
        <el-input v-model="keyword" :prefix-icon="Search" placeholder="搜索" clearable>
          <template #suffix>
            <span class="rounded border border-slate-200 px-2 py-0.5 text-xs text-slate-400">Ctrl K</span>
          </template>
        </el-input>
      </div>

      <div class="ml-auto flex items-center gap-1 xl:ml-0">
        <el-button class="hidden sm:inline-flex" :icon="FullScreen" circle text />
        <el-button class="hidden sm:inline-flex" :icon="Bell" circle text />
        <el-button class="hidden sm:inline-flex" :icon="Sunny" circle text />

        <template v-if="auth.isAuthenticated && auth.user">
          <el-dropdown trigger="click" @command="handleCommand">
            <button class="user-button" type="button">
              <span class="user-avatar">{{ auth.user.displayName.slice(0, 1).toUpperCase() }}</span>
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
            <el-button text>登录</el-button>
          </RouterLink>
          <RouterLink to="/register">
            <el-button type="primary">注册</el-button>
          </RouterLink>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import {
  ArrowDown,
  Bell,
  Compass,
  FullScreen,
  Grid,
  MagicStick,
  Refresh,
  Search,
  Sunny,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const keyword = ref('')

const navItems = [
  { to: '/', label: '工作台', icon: Compass },
  { to: '/create', label: '创作中心', icon: MagicStick },
]

function reloadPage() {
  window.location.reload()
}

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

<style scoped>
.brand-mark {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  border-radius: 8px;
  background: linear-gradient(135deg, #11c5d9, #2f63ff);
  color: #fff;
  font-weight: 800;
}

.user-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 38px;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: #334155;
  cursor: pointer;
}

.user-avatar {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  border-radius: 999px;
  background: #e8efff;
  color: #2f63ff;
  font-size: 13px;
  font-weight: 800;
}
</style>
