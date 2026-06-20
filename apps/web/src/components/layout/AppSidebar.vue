<template>
  <aside class="fixed inset-y-0 left-0 z-30 hidden w-72 border-r border-white/10 bg-[#07010f]/95 px-5 py-6 text-white shadow-2xl backdrop-blur xl:flex xl:flex-col">
    <RouterLink to="/" class="flex items-center gap-3 no-underline">
      <div class="grid h-12 w-12 place-items-center rounded-2xl bg-gradient-to-br from-cyan-300 via-fuchsia-400 to-violet-600 text-2xl font-black shadow-lg shadow-fuchsia-500/25">
        P
      </div>
      <div>
        <p class="m-0 text-2xl font-black tracking-tight text-white">PromptPlay</p>
        <p class="m-0 text-xs font-semibold uppercase tracking-[0.25em] text-cyan-200/80">AI Arcade</p>
      </div>
    </RouterLink>

    <RouterLink
      to="/"
      class="mt-10 flex items-center justify-center gap-3 rounded-full bg-gradient-to-r from-fuchsia-500 to-violet-600 px-6 py-4 text-xl font-black text-white no-underline shadow-xl shadow-fuchsia-500/30 transition hover:scale-[1.02]"
    >
      <span>Play</span>
    </RouterLink>

    <nav class="mt-8 space-y-2 border-t border-white/10 pt-8">
      <RouterLink v-for="item in navItems" :key="item.to" :to="item.to" class="sidebar-link" active-class="sidebar-link-active">
        <span class="text-lg">{{ item.icon }}</span>
        <span>{{ item.label }}</span>
      </RouterLink>
    </nav>

    <div class="mt-auto space-y-5 border-t border-white/10 pt-6">
      <div v-if="auth.isAuthenticated && auth.user" class="rounded-3xl border border-white/10 bg-white/[0.06] p-4">
        <p class="m-0 text-xs font-black uppercase tracking-[0.25em] text-slate-400">Signed in</p>
        <p class="mt-2 truncate text-base font-black text-white">{{ auth.user.displayName }}</p>
        <p class="m-0 truncate text-xs font-semibold text-slate-400">{{ auth.user.email }}</p>
        <button
          type="button"
          class="mt-4 w-full rounded-full border border-white/10 bg-white/10 px-4 py-2 text-sm font-black text-white transition hover:bg-white/15 disabled:cursor-not-allowed disabled:opacity-60"
          :disabled="auth.loading"
          @click="handleLogout"
        >
          退出登录
        </button>
      </div>
      <div v-else class="grid gap-2">
        <RouterLink to="/login" class="sidebar-link">
          <span class="text-lg">IN</span>
          <span>Sign In</span>
        </RouterLink>
        <RouterLink to="/register" class="sidebar-link">
          <span class="text-lg">+</span>
          <span>Create Account</span>
        </RouterLink>
      </div>
      <div class="rounded-3xl border border-cyan-300/20 bg-cyan-300/10 p-4">
        <p class="m-0 text-sm font-bold text-cyan-100">Creator Mode</p>
        <p class="mt-1 text-xs leading-5 text-slate-300">用一句话和素材生成可发布的远程 HTML5 游戏。</p>
      </div>
      <div class="flex justify-around text-xl text-slate-400">
        <span>AI</span>
        <span>3D</span>
        <span>JS</span>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const navItems = [
  { to: '/', label: 'Home', icon: 'H' },
  { to: '/create', label: 'Create', icon: '+' },
]

async function handleLogout() {
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
.sidebar-link {
  display: flex;
  align-items: center;
  gap: 1rem;
  border-radius: 1rem;
  padding: 0.95rem 1rem;
  color: rgb(226 232 240);
  font-weight: 800;
  text-decoration: none;
  transition: background-color 160ms ease, color 160ms ease, transform 160ms ease;
}

.sidebar-link:hover,
.sidebar-link-active {
  background: rgba(255, 255, 255, 0.08);
  color: white;
  transform: translateX(2px);
}
</style>
