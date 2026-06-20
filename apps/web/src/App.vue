<template>
  <el-container class="app-shell" :class="{ 'app-shell--auth': hideHeader }">
    <el-header v-if="!hideHeader" class="app-shell__header">
      <AppHeader />
    </el-header>
    <el-main class="app-shell__main" :class="{ 'app-shell__main--auth': hideHeader }">
      <RouterView />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import AppHeader from '@/components/layout/AppHeader.vue'

const route = useRoute()
const hideHeader = computed(() => route.meta.hideHeader === true)
</script>
