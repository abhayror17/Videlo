<template>
  <div class="workflow-node image-to-video-node" :class="{ processing: isProcessing }">
    <button class="node-delete-btn" @click.stop="deleteNode" title="Delete node">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"/>
        <line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    </button>
    <div class="node-header">
      <div class="node-icon-wrapper">
        <span class="node-icon">🎥</span>
      </div>
      <span class="node-title">{{ $t('workflow.imageToVideo') }}</span>
      <div v-if="isProcessing" class="node-spinner"></div>
      <div v-else-if="localData.resultUrl" class="node-status success"></div>
    </div>
    <div class="node-body">
      <div class="form-row">
        <label>{{ $t('workflow.textPrompt') }}</label>
        <textarea 
          v-model="localData.prompt" 
          @input="updateData"
          class="form-textarea"
          rows="2"
          :placeholder="$t('workflow.enterPrompt')"
        ></textarea>
      </div>
      <div class="form-row">
        <label>{{ $t('settings.model') }}</label>
        <select v-model="localData.model" @change="updateData" class="form-select">
          <option value="Ltx2_3_22B_Dist_INT8">LTX-2.3 22B (Best)</option>
          <option value="Ltx2_19B_Dist_FP8">LTX-2 19B</option>
          <option value="Ltxv_13B_0_9_8_Distilled_FP8">LTX-Video 13B</option>
        </select>
      </div>
      <div class="form-row">
        <label>{{ $t('settings.aspectRatio') }}</label>
        <select v-model="localData.aspectRatio" @change="onAspectChange" class="form-select">
          <option v-for="ar in aspectRatios" :key="ar.value" :value="ar.value">{{ ar.label }}</option>
        </select>
      </div>
      <div class="form-row">
        <label>{{ $t('settings.duration') }}</label>
        <select v-model.number="localData.frames" @change="updateData" class="form-select">
          <option :value="49">~2 {{ $t('settings.seconds') }}</option>
          <option :value="120">~5 {{ $t('settings.seconds') }}</option>
          <option :value="241">~10 {{ $t('settings.seconds') }}</option>
        </select>
      </div>
      
      <!-- Result Preview -->
      <div v-if="localData.resultUrl" class="result-preview">
        <video :src="localData.resultUrl" controls muted loop></video>
        <div class="result-badge">Video</div>
      </div>
    </div>
    <Handle type="target" :position="Position.Left" class="node-handle target" />
    <Handle type="source" :position="Position.Right" class="node-handle source" />
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { Handle, Position, useVueFlow } from '@vue-flow/core'

const props = defineProps({
  id: String,
  data: Object
})

const { updateNodeData, removeNodes } = useVueFlow()

// Aspect ratios for video
const aspectRatios = [
  { value: '16:9', label: '16:9 (Landscape)', width: 768, height: 432 },
  { value: '9:16', label: '9:16 (Portrait)', width: 432, height: 768 },
  { value: '1:1', label: '1:1 (Square)', width: 512, height: 512 },
  { value: '4:3', label: '4:3', width: 640, height: 480 },
  { value: '3:4', label: '3:4', width: 480, height: 640 }
]

const localData = ref({
  prompt: props.data.prompt || '',
  model: props.data.model || 'Ltx2_3_22B_Dist_INT8',
  aspectRatio: props.data.aspectRatio || '16:9',
  width: props.data.width || 768,
  height: props.data.height || 432,
  frames: props.data.frames || 49,
  resultUrl: props.data.resultUrl || null,
  status: props.data.status || 'idle'
})

watch(() => props.data, (newData) => {
  localData.value = { ...localData.value, ...newData }
}, { deep: true })

const isProcessing = computed(() => localData.value.status === 'processing')

const onAspectChange = () => {
  const ar = aspectRatios.find(a => a.value === localData.value.aspectRatio)
  if (ar) {
    localData.value.width = ar.width
    localData.value.height = ar.height
  }
  updateData()
}

const updateData = () => {
  updateNodeData(props.id, { ...localData.value })
}

const deleteNode = () => {
  removeNodes([props.id])
}
</script>

<style scoped>
.workflow-node {
  position: relative;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  min-width: 240px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  transition: all 0.2s ease;
}

.workflow-node:hover {
  border-color: rgba(14, 165, 233, 0.3);
  box-shadow: 0 8px 32px rgba(14, 165, 233, 0.15);
}

.workflow-node.processing {
  border-color: rgba(14, 165, 233, 0.5);
  box-shadow: 0 0 30px rgba(14, 165, 233, 0.2);
}

.node-delete-btn {
  position: absolute;
  top: -8px;
  left: -8px;
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(239, 68, 68, 0.9);
  border: 2px solid var(--bg-panel);
  border-radius: 50%;
  color: white;
  cursor: pointer;
  opacity: 0;
  transform: scale(0.8);
  transition: all 0.15s ease;
  z-index: 10;
}

.workflow-node:hover .node-delete-btn {
  opacity: 1;
  transform: scale(1);
}

.node-delete-btn:hover {
  background: #EF4444;
  transform: scale(1.1);
}

.node-delete-btn svg {
  width: 12px;
  height: 12px;
}

.node-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: var(--bg-elevated);
  border-bottom: 1px solid var(--border-color);
  border-radius: 12px 12px 0 0;
}

.node-icon-wrapper {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.3), rgba(14, 165, 233, 0.1));
  border-radius: 8px;
}

.node-icon {
  font-size: 1rem;
}

.node-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: #38BDF8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  flex: 1;
}

.node-status {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.node-status.success {
  background: #22C55E;
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.5);
}

.node-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(14, 165, 233, 0.2);
  border-top-color: #0EA5E9;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.node-body {
  padding: 16px;
}

.form-row {
  margin-bottom: 14px;
}

.form-row:last-child {
  margin-bottom: 0;
}

.form-row label {
  display: block;
  font-size: 0.6875rem;
  font-weight: 600;
  color: #6B7280;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  margin-bottom: 6px;
}

.form-select {
  width: 100%;
  padding: 12px;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 0.8125rem;
  transition: all 0.2s ease;
}

.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #0EA5E9;
  background: var(--bg-elevated);
}

.form-textarea {
  width: 100%;
  padding: 10px 12px;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.8125rem;
  resize: none;
  font-family: inherit;
  transition: all 0.2s ease;
}

.form-textarea::placeholder {
  color: var(--text-muted);
}

.result-preview {
  margin-top: 14px;
  position: relative;
  border-radius: 10px;
  overflow: hidden;
  background: var(--bg-elevated);
  display: flex;
  align-items: center;
  justify-content: center;
  max-height: 240px;
}

.result-preview video {
  max-width: 100%;
  max-height: 240px;
  display: block;
  border-radius: 10px;
  object-fit: contain;
}

.result-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  padding: 4px 10px;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  border-radius: 6px;
  font-size: 0.625rem;
  font-weight: 600;
  color: #fff;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.node-handle {
  width: 14px !important;
  height: 14px !important;
  background: #0EA5E9 !important;
  border: 2px solid var(--bg-panel) !important;
}
</style>