<template>
  <section class="runtime-panel">
    <div class="runtime-panel__header">
      <h2>远程资源信息</h2>
      <span class="runtime-panel__status">加载成功</span>
    </div>

    <div class="runtime-panel__rows">
      <div
        v-for="row in copyableRows"
        :key="row.label"
        class="runtime-panel__copy-row"
      >
        <span class="runtime-panel__label">{{ row.label }}</span>
        <span class="runtime-panel__value runtime-panel__value--boxed">{{ row.value }}</span>
        <el-button
          :icon="CopyDocument"
          circle
          size="small"
          class="runtime-panel__copy"
          @click="copyValue(row.value)"
        />
      </div>

      <div
        v-for="row in plainRows"
        :key="row.label"
        class="runtime-panel__plain-row"
      >
        <span class="runtime-panel__label">{{ row.label }}</span>
        <span class="runtime-panel__value">{{ row.value }}</span>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { CopyDocument } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { computed } from 'vue'

import type { PlayDescriptor } from '@/api/types'

const props = defineProps<{
  descriptor: PlayDescriptor
}>()

interface ResourceRow {
  label: string
  value: string
}

const copyableRows = computed<ResourceRow[]>(() => [
  { label: 'Manifest URL', value: props.descriptor.manifestUrl },
  { label: 'Bundle URL', value: deriveBundleUrl(props.descriptor.manifestUrl) },
  { label: 'OSS 路径', value: props.descriptor.storagePrefix },
])

const plainRows = computed<ResourceRow[]>(() => [
  { label: '资源大小', value: '512.4 MB' },
  { label: '加载耗时', value: '2.31 s' },
  { label: '运行环境', value: formatRuntime(props.descriptor.runtime) },
])

function deriveBundleUrl(manifestUrl: string) {
  return manifestUrl
    .replace('/manifests/', '/bundles/')
    .replace(/manifest\.json$/i, 'bundle.zip')
}

function formatRuntime(runtime: PlayDescriptor['runtime']) {
  if (runtime === 'iframe_manifest_v1') return 'AgentPlay Runtime v1.3.2'
  return runtime
}

async function copyValue(value: string) {
  try {
    await navigator.clipboard.writeText(value)
    ElMessage.success('已复制')
  } catch {
    ElMessage.warning('复制失败')
  }
}
</script>

<style scoped>
.runtime-panel {
  border: 1px solid #dce4f0;
  border-radius: 8px;
  background: #fff;
  padding: 20px;
  box-shadow: 0 8px 22px rgba(31, 42, 68, 0.05);
}

.runtime-panel__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}

.runtime-panel__header h2 {
  margin: 0;
  color: #0f172a;
  font-size: 16px;
  font-weight: 700;
}

.runtime-panel__status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-radius: 6px;
  background: #dcfce7;
  padding: 6px 12px;
  color: #16a34a;
  font-size: 12px;
  font-weight: 700;
}

.runtime-panel__status::before {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: currentColor;
  content: "";
}

.runtime-panel__rows {
  display: grid;
  gap: 14px;
  font-size: 13px;
}

.runtime-panel__copy-row {
  display: grid;
  grid-template-columns: 82px minmax(0, 1fr) 28px;
  align-items: center;
  gap: 10px;
}

.runtime-panel__plain-row {
  display: grid;
  grid-template-columns: 82px minmax(0, 1fr);
  align-items: center;
  gap: 10px;
}

.runtime-panel__label {
  color: #64748b;
}

.runtime-panel__value {
  min-width: 0;
  overflow: hidden;
  color: #475569;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.runtime-panel__value--boxed {
  border-radius: 6px;
  background: #f8fafc;
  padding: 8px 10px;
  font-weight: 500;
}

.runtime-panel__copy {
  color: #64748b;
}
</style>
