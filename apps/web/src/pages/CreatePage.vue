<template>
  <main class="mx-auto max-w-7xl px-6 py-10">
    <div class="mb-8">
      <p class="text-sm uppercase tracking-[0.3em] text-neon">Creator Studio</p>
      <h1 class="mt-2 text-4xl font-bold text-white">用 Agent 生成互动游戏</h1>
    </div>

    <div class="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
      <NCard title="创意输入" class="border border-white/10 bg-white/5">
        <NForm>
          <NFormItem label="游戏创意">
            <NInput
              v-model:value="idea"
              type="textarea"
              :autosize="{ minRows: 8 }"
              placeholder="例如：做一个霓虹城市里寻找失踪机器人的互动剧情游戏..."
            />
          </NFormItem>
          <NFormItem label="素材上传">
            <NUpload multiple directory-dnd :max="3">
              <NUploadDragger>
                <div class="py-8 text-center text-slate-300">拖拽图片或素材到这里，或点击选择文件</div>
              </NUploadDragger>
            </NUpload>
          </NFormItem>
          <NButton type="primary" size="large" :disabled="!idea.trim()">生成游戏</NButton>
        </NForm>
      </NCard>

      <div class="space-y-6">
        <NCard title="任务进度" class="border border-white/10 bg-white/5">
          <GenerationTimeline status="idle" />
        </NCard>
        <NCard title="Agent 日志" class="border border-white/10 bg-white/5">
          <NEmpty description="提交任务后，这里会展示 LangGraph 节点日志" />
        </NCard>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { NButton, NCard, NEmpty, NForm, NFormItem, NInput, NUpload, NUploadDragger } from 'naive-ui'
import { ref } from 'vue'

import GenerationTimeline from '@/components/create/GenerationTimeline.vue'

const idea = ref('')
</script>
