<template>
  <main class="workbench-page">
    <template v-if="!currentTask">
      <section class="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 class="m-0 text-2xl font-semibold text-slate-950">创作中心</h1>
          <p class="m-0 mt-1 text-sm text-slate-500">描述创意、上传参考素材，然后交给智能体生成可运行的 HTML5 游戏。</p>
        </div>
        <el-button plain :icon="Guide">创作指南</el-button>
      </section>

      <div class="grid gap-4 xl:grid-cols-[1fr_360px]">
        <section class="space-y-4">
          <section class="app-card p-5">
            <div class="mb-4 flex items-center gap-3">
              <span class="step-dot">1</span>
              <div>
                <h2 class="m-0 text-lg font-semibold text-slate-950">说出你的游戏想法</h2>
                <p class="m-0 mt-1 text-sm text-slate-500">包含玩法、世界观、角色、胜利条件和希望参考的视觉风格。</p>
              </div>
            </div>
            <el-input
              v-model="idea"
              class="prompt-input"
              type="textarea"
              :autosize="{ minRows: 9 }"
              maxlength="3000"
              show-word-limit
              placeholder="例如：做一个赛博都市跑酷游戏，玩家需要躲避巡逻无人机、收集能量芯片，并在 3 分钟内抵达屋顶撤离点。"
            />
            <div class="mt-4 flex flex-wrap gap-3">
              <el-button size="small" :icon="Plus">插入参考</el-button>
              <el-button size="small" :icon="MagicStick" @click="idea = quickIdeas[0] ?? ''">填入灵感</el-button>
            </div>
          </section>

          <section class="app-card p-5">
            <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
              <div class="flex items-center gap-3">
                <span class="step-dot">2</span>
                <div>
                  <h2 class="m-0 text-lg font-semibold text-slate-950">上传参考素材</h2>
                  <p class="m-0 mt-1 text-sm text-slate-500">支持图片、文本和 JSON 设定文件。</p>
                </div>
              </div>
              <span class="text-sm text-slate-400">已上传 {{ uploadedAssets.length }}/20</span>
            </div>
            <div class="grid gap-4 lg:grid-cols-[320px_1fr]">
              <el-upload drag multiple :limit="4" :http-request="handleUpload">
                <div class="py-8 text-center">
                  <el-icon class="text-4xl text-blue-500"><Plus /></el-icon>
                  <p class="mt-3 font-semibold text-slate-600">点击上传或拖拽到此处</p>
                  <p class="text-xs text-slate-400">JPG / PNG / GIF / TXT / JSON，单个文件不超过 10MB</p>
                </div>
              </el-upload>
              <div class="grid gap-3 md:grid-cols-3">
                <div v-for="asset in uploadedAssets" :key="asset.id" class="overflow-hidden rounded-lg border border-slate-200 bg-white p-3">
                  <div class="h-24 rounded bg-slate-100" />
                  <p class="mt-2 truncate text-sm font-semibold text-slate-700">{{ asset.filename }}</p>
                </div>
                <div v-for="index in Math.max(0, 3 - uploadedAssets.length)" :key="index" class="overflow-hidden rounded-lg border border-slate-200 bg-white">
                  <img :src="referenceImages.createFormImage" alt="" class="h-32 w-full object-cover object-left-top opacity-80" />
                </div>
              </div>
            </div>
          </section>

          <section class="app-card p-5">
            <div class="mb-4 flex items-center gap-3">
              <span class="step-dot">3</span>
              <h2 class="m-0 text-lg font-semibold text-slate-950">快速灵感</h2>
            </div>
            <div class="grid gap-3 md:grid-cols-3 xl:grid-cols-5">
              <button v-for="tip in quickIdeas" :key="tip" class="rounded-lg border border-slate-200 bg-white p-4 text-left text-sm font-semibold text-slate-700 transition hover:border-blue-300 hover:text-blue-600" type="button" @click="idea = tip">
                {{ tip }}
              </button>
            </div>
          </section>
        </section>

        <aside class="app-card h-fit p-5">
          <div class="mb-5 flex items-center justify-between">
            <h2 class="m-0 text-lg font-semibold text-slate-950">生成配置</h2>
            <el-button text size="small" @click="resetAll">重置</el-button>
          </div>
          <el-form label-position="top">
            <el-form-item label="游戏类型">
              <el-segmented v-model="gameType" :options="gameTypeOptions" />
            </el-form-item>
            <el-form-item label="目标时长">
              <el-radio-group v-model="duration">
                <el-radio-button label="短" />
                <el-radio-button label="中" />
                <el-radio-button label="长" />
              </el-radio-group>
            </el-form-item>
            <el-form-item label="美术风格">
              <el-select v-model="artStyle">
                <el-option label="写实风格" value="realistic" />
                <el-option label="像素风格" value="pixel" />
                <el-option label="二次元" value="anime" />
              </el-select>
            </el-form-item>
            <el-form-item label="语言设置">
              <el-select v-model="language">
                <el-option label="简体中文" value="zh-CN" />
                <el-option label="English" value="en" />
              </el-select>
            </el-form-item>
            <el-form-item label="生成模型">
              <el-select v-model="model">
                <el-option label="AgentPlay Game v1.0" value="game-v1" />
              </el-select>
            </el-form-item>
          </el-form>
          <el-button class="agent-gradient-button w-full" size="large" type="primary" :loading="loading" :disabled="!canGenerate" @click="generate">
            开始生成
          </el-button>
          <p class="mt-4 text-xs leading-5 text-slate-400">素材仅用于本次生成，不会用于公开展示或模型训练。</p>
        </aside>
      </div>
    </template>

    <template v-else-if="currentTask.status === 'pending' || currentTask.status === 'running'">
      <div class="grid gap-4 xl:grid-cols-[1fr_360px]">
        <section class="space-y-4">
          <section class="app-card p-5">
            <p class="m-0 text-sm text-slate-500">Create / 生成任务</p>
            <h1 class="mt-3 text-2xl font-semibold text-slate-950">{{ currentTask.ideaText.slice(0, 32) || 'AI 游戏生成任务' }}</h1>
            <p class="mt-3 line-clamp-3 text-sm leading-7 text-slate-600">{{ currentTask.ideaText }}</p>
            <div class="mt-4 flex flex-wrap gap-2">
              <el-tag v-for="tag in ['开放世界', '生存建造', '太空探索']" :key="tag" round>{{ tag }}</el-tag>
            </div>
          </section>

          <section class="app-card p-5">
            <div class="mb-5 flex flex-wrap items-center justify-between gap-3">
              <h2 class="m-0 text-lg font-semibold text-slate-950">AI 多智能体工作流</h2>
              <div class="flex gap-2">
                <el-tag type="info" round>等待中</el-tag>
                <el-tag type="primary" round>运行中</el-tag>
                <el-tag type="success" round>已完成</el-tag>
              </div>
            </div>
            <GenerationTimeline :status="timelineStatus" :current-step="currentTask.currentStep" />
          </section>

          <section class="app-card p-5">
            <div class="mb-5 flex items-center justify-between">
              <h2 class="m-0 text-lg font-semibold text-slate-950">智能体执行日志</h2>
              <el-switch model-value active-text="实时日志" />
            </div>
            <AgentLogPanel :logs="logs" />
          </section>
        </section>

        <TaskAside :task="currentTask" :publishing="publishing" @reset="resetAll" @publish="publish" />
      </div>
    </template>

    <template v-else-if="currentTask.status === 'succeeded' && previewManifest">
      <div class="grid gap-4 xl:grid-cols-[1fr_420px]">
        <section class="space-y-4">
          <section class="app-card flex flex-wrap items-center justify-between gap-4 p-5">
            <div class="flex items-center gap-4">
              <span class="grid h-12 w-12 place-items-center rounded-full bg-emerald-500 text-white"><el-icon size="24"><Check /></el-icon></span>
              <div>
                <h1 class="m-0 text-xl font-semibold text-slate-950">游戏已生成完成</h1>
                <p class="mt-1 text-sm text-slate-500">预览效果并完善发布信息后即可上线。</p>
              </div>
            </div>
            <div class="flex flex-wrap gap-3">
              <el-button @click="resetAll">再次编辑</el-button>
              <el-button @click="generate">重新生成</el-button>
              <el-button class="agent-gradient-button" :loading="publishing" @click="publish">发布到首页</el-button>
            </div>
          </section>

          <section class="app-card p-5">
            <h2 class="m-0 mb-4 text-lg font-semibold text-slate-950">游戏预览</h2>
            <RemoteGameFrame :manifest="previewManifest" />
          </section>

          <PublishPanel :task="currentTask" :publishing="publishing" @publish="publish" @play="openPlay" />
        </section>

        <aside class="space-y-4">
          <section class="app-card p-5">
            <h2 class="m-0 text-lg font-semibold text-slate-950">发布信息</h2>
            <el-form class="mt-5" label-position="top">
              <el-form-item label="游戏标题">
                <el-input v-model="publishTitle" maxlength="60" show-word-limit />
              </el-form-item>
              <el-form-item label="封面图">
                <div class="flex items-center gap-4">
                  <img :src="referenceImages.createPublishImage" alt="" class="h-20 w-32 rounded-lg object-cover object-left-top" />
                  <el-button>更换封面</el-button>
                </div>
              </el-form-item>
              <el-form-item label="游戏描述">
                <el-input v-model="publishDescription" type="textarea" :rows="4" maxlength="300" show-word-limit />
              </el-form-item>
              <el-form-item label="标签">
                <div class="flex flex-wrap gap-2">
                  <el-tag v-for="tag in publishTags" :key="tag" closable round>{{ tag }}</el-tag>
                  <el-button size="small">添加标签</el-button>
                </div>
              </el-form-item>
              <el-form-item label="发布状态">
                <el-radio-group v-model="publishMode">
                  <el-radio value="now">立即发布</el-radio>
                  <el-radio value="later">定时发布</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-form>
          </section>

          <section class="app-card p-5">
            <h2 class="m-0 text-lg font-semibold text-slate-950">版本与构建信息</h2>
            <InfoRows :rows="buildRows" />
          </section>
        </aside>
      </div>
    </template>

    <template v-else>
      <section class="app-card p-6">
        <el-alert type="error" title="Create workflow error" :closable="false" show-icon>
          {{ error || currentTask.errorMessage || '任务失败，请重试。' }}
        </el-alert>
        <el-button class="mt-5" type="primary" @click="resetAll">返回创作表单</el-button>
      </section>
    </template>
  </main>
</template>

<script setup lang="ts">
import { Check, Guide, MagicStick, Plus } from '@element-plus/icons-vue'
import { ElMessage, type UploadRequestOptions } from 'element-plus'
import { storeToRefs } from 'pinia'
import { computed, defineComponent, h, onBeforeUnmount, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { uploadAsset, type AssetResponse } from '@/api/assets'
import type { GenerationTaskResponse } from '@/api/tasks'
import type { GameManifest } from '@/api/types'
import AgentLogPanel from '@/components/create/AgentLogPanel.vue'
import GenerationTimeline from '@/components/create/GenerationTimeline.vue'
import PublishPanel from '@/components/create/PublishPanel.vue'
import RemoteGameFrame from '@/components/game/RemoteGameFrame.vue'
import { generatedArtifacts, quickIdeas, referenceImages } from '@/data/showcase'
import { useCreateTaskStore } from '@/stores/createTask'

const router = useRouter()
const createTask = useCreateTaskStore()
const { currentTask, logs, loading, publishing, error } = storeToRefs(createTask)

const idea = ref('')
const uploadedAssets = ref<AssetResponse[]>([])
const uploadingCount = ref(0)
const previewManifest = ref<GameManifest | null>(null)
const gameType = ref('RPG 角色扮演')
const duration = ref('短')
const artStyle = ref('realistic')
const language = ref('zh-CN')
const model = ref('game-v1')
const publishTitle = ref('迷雾之城：钟声')
const publishDescription = ref('在迷雾与诅咒交织的古城中探寻真相，你的选择将决定众人的命运。')
const publishTags = ref(['角色扮演', '剧情向', '暗黑奇幻', '单机'])
const publishMode = ref('now')
const gameTypeOptions = ['RPG 角色扮演', 'ACT 动作', 'AVG 冒险解谜', 'SLG 策略', 'SIM 模拟经营', 'RAC 竞速']

const canGenerate = computed(() => idea.value.trim().length > 0 && uploadingCount.value === 0 && !loading.value)
const timelineStatus = computed(() => currentTask.value?.status ?? 'idle')
const buildRows = computed(() => [
  ['版本号', 'v1.0.0'],
  ['任务 ID', currentTask.value?.id || '-'],
  ['游戏地址', currentTask.value?.result.gameId ? `/play/${currentTask.value.result.gameId}` : '-'],
  ['Manifest URL', currentTask.value?.result.manifestUrl || '-'],
  ['发布状态', currentTask.value?.result.gameId ? '已发布' : '未发布'],
])

function isGameManifest(value: unknown): value is GameManifest {
  if (!value || typeof value !== 'object') return false
  const candidate = value as Partial<GameManifest>
  return candidate.schemaVersion === 'game-manifest-v1'
    && typeof candidate.entryUrl === 'string'
    && typeof candidate.title === 'string'
}

async function handleUpload(options: UploadRequestOptions) {
  uploadingCount.value += 1
  try {
    const asset = await uploadAsset(options.file)
    uploadedAssets.value.push(asset)
    options.onSuccess(asset)
    ElMessage.success(`已上传 ${asset.filename}`)
  } catch (caught) {
    const uploadError = caught instanceof Error ? caught : new Error('上传失败')
    options.onError(uploadError as Parameters<UploadRequestOptions['onError']>[0])
    ElMessage.error(uploadError.message)
  } finally {
    uploadingCount.value -= 1
  }
}

async function generate() {
  previewManifest.value = null
  await createTask.startTask({
    ideaText: idea.value.trim(),
    assetIds: uploadedAssets.value.map((asset) => asset.id),
  })
}

async function publish() {
  const task = await createTask.publishCurrentTask()
  if (task?.result.gameId) {
    ElMessage.success('已发布到首页')
  }
}

function openPlay(gameId: string) {
  router.push(`/play/${gameId}`)
}

function resetAll() {
  idea.value = ''
  uploadedAssets.value = []
  previewManifest.value = null
  createTask.reset()
}

watch(
  () => currentTask.value?.result.manifestUrl,
  async (manifestUrl) => {
    if (!manifestUrl) return
    try {
      const response = await fetch(manifestUrl)
      if (!response.ok) throw new Error(`Manifest 请求失败: ${response.status}`)
      const payload = await response.json()
      if (!isGameManifest(payload)) throw new Error('Manifest 协议不合法')
      previewManifest.value = payload
      publishTitle.value = payload.title
    } catch (caught) {
      ElMessage.error(caught instanceof Error ? caught.message : '预览加载失败')
    }
  },
)

const InfoRows = defineComponent({
  props: {
    rows: { type: Array as () => string[][], required: true },
  },
  setup(props) {
    return () => h('div', { class: 'mt-4 space-y-3' }, props.rows.map(([label, value]) => h('div', { class: 'flex gap-4 text-sm' }, [
      h('span', { class: 'w-24 shrink-0 text-slate-400' }, label),
      h('span', { class: 'min-w-0 flex-1 break-all font-medium text-slate-700' }, value),
    ])))
  },
})

const TaskAside = defineComponent({
  props: {
    task: { type: Object as () => GenerationTaskResponse, required: true },
    publishing: { type: Boolean, required: true },
  },
  emits: ['reset', 'publish'],
  setup(props, { emit }) {
    return () => h('aside', { class: 'space-y-4' }, [
      h('section', { class: 'app-card p-5' }, [
        h('h2', { class: 'm-0 text-lg font-semibold text-slate-950' }, '任务信息'),
        h(InfoRows, { rows: [
          ['任务状态', props.task.status],
          ['任务 ID', props.task.id],
          ['当前步骤', props.task.currentStep],
          ['预计完成', '约 8 分钟后'],
          ['运行时长', '00:06:48'],
        ] }),
      ]),
      h('section', { class: 'app-card p-5' }, [
        h('h2', { class: 'm-0 mb-4 text-lg font-semibold text-slate-950' }, '生成产物'),
        h('div', { class: 'grid grid-cols-2 gap-3' }, generatedArtifacts.map((artifact) => h('div', { class: 'rounded-lg border border-slate-200 bg-slate-50 p-4 text-center text-sm font-semibold text-slate-500' }, artifact))),
      ]),
      h('section', { class: 'app-card p-5' }, [
        h('h2', { class: 'm-0 mb-4 text-lg font-semibold text-slate-950' }, '资源消耗'),
        h(InfoRows, { rows: [
          ['总消耗', '1,240 积分'],
          ['Tokens', '3,245,678'],
          ['模型调用', '18 次'],
          ['智能体调用', '24 次'],
        ] }),
      ]),
      h('div', { class: 'flex gap-3' }, [
        h('button', { class: 'flex-1 rounded-lg border border-red-200 bg-white px-4 py-3 font-semibold text-red-500', onClick: () => emit('reset') }, '终止任务'),
        h('button', { class: 'flex-1 rounded-lg border border-slate-200 bg-slate-100 px-4 py-3 font-semibold text-slate-400', disabled: true }, '预览'),
      ]),
    ])
  },
})

onBeforeUnmount(() => createTask.stopPolling())
</script>

<style scoped>
.step-dot {
  display: grid;
  width: 28px;
  height: 28px;
  place-items: center;
  border-radius: 999px;
  background: #2f63ff;
  color: #fff;
  font-size: 14px;
  font-weight: 700;
}

.prompt-input :deep(textarea) {
  border-radius: 8px;
  font-size: 1rem;
  line-height: 1.8;
}
</style>
