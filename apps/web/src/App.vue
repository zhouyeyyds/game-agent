<template>
  <NConfigProvider :theme="darkTheme">
    <NMessageProvider>
      <NDialogProvider>
        <NLayout class="min-h-screen bg-ink text-white">
          <NLayoutHeader bordered class="border-white/10 bg-ink/90 backdrop-blur">
            <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
              <RouterLink to="/" class="text-xl font-bold text-white no-underline">
                PromptPlay AI
              </RouterLink>
              <nav class="flex items-center gap-3">
                <RouterLink to="/" class="text-slate-300 no-underline hover:text-white">Home</RouterLink>
                <RouterLink to="/create" class="text-slate-300 no-underline hover:text-white">Create</RouterLink>
                <RouterLink to="/login" class="text-slate-300 no-underline hover:text-white">Login</RouterLink>
              </nav>
            </div>
          </NLayoutHeader>
          <NLayoutContent>
            <RouterView />
          </NLayoutContent>
        </NLayout>
      </NDialogProvider>
    </NMessageProvider>
  </NConfigProvider>
</template>

<script setup lang="ts">
import { darkTheme, NConfigProvider, NDialogProvider, NLayout, NLayoutContent, NLayoutHeader, NMessageProvider } from 'naive-ui'
</script>
