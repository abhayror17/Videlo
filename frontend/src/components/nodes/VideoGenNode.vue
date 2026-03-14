<template>
  <div class="workflow-node video-gen-node" :class="{ processing: isProcessing }">
    <button class="node-delete-btn" @click.stop="deleteNode" title="Delete node">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"/>
        <line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    </button>
    <div class="node-header">
      <div class="node-icon-wrapper">
        <div class="node-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="2" x2="22" y1="10" y2="10"/><line x1="2" x2="2" y1="7" y2="13"/><line x1="22" x2="22" y1="7" y2="13"/><path d="m9 21 3-3 3 3"/></svg>
        </div>
      </div>
      <span class="node-title">{{ $t('workflow.textToVideo') }}</span>
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
  fps: props.data.fps || 24,
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
  background: rgba(26, 26, 26, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  min-width: 260px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.workflow-node:hover {
  border-color: rgba(236, 72, 153, 0.4);
  box-shadow: 0 12px 40px rgba(236, 72, 153, 0.15);
  transform: translateY(-2px);
}

.workflow-node.processing {
  border-color: #EC4899;
  box-shadow: 0 0 20px rgba(236, 72, 153, 0.2);
}

.node-delete-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #EF4444;
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s ease;
  z-index: 10;
}

.workflow-node:hover .node-delete-btn {
  opacity: 1;
}

.node-delete-btn:hover {
  background: rgba(239, 68, 68, 0.2);
  transform: scale(1.1);
}

.node-delete-btn svg {
  width: 12px;
  height: 12px;
}

.node-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.node-icon-wrapper {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(236, 72, 153, 0.25), rgba(236, 72, 153, 0.1));
  border-radius: 10px;
  color: #F472B6;
}

.node-icon svg {
  width: 20px;
  height: 20px;
}

.node-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: #fff;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  flex: 1;
  opacity: 0.9;
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
  width: 18px;
  height: 18px;
  border: 2px solid rgba(236, 72, 153, 0.2);
  border-top-color: #EC4899;
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
  margin-bottom: 16px;
}

.form-row:last-child {
  margin-bottom: 0;
}

.form-row label {
  display: block;
  font-size: 0.625rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.4);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
}

.form-select,
.form-textarea {
  width: 100%;
  padding: 10px 32px 10px 12px;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  color: #fff;
  font-size: 0.8125rem;
  font-family: inherit;
  transition: all 0.2s ease;
  cursor: pointer;
}

.form-select {
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23FFFFFF' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 16px;
}

.form-select option {
  background: #1a1a2e;
  color: #fff;
  padding: 12px;
  font-size: 0.875rem;
  font-weight: 500;
}

.form-select option:hover,
.form-select option:focus,
.form-select option:checked {
  background: rgba(236, 72, 153, 0.3);
  color: #fff;
}

.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: rgba(236, 72, 153, 0.8);
  background: rgba(0, 0, 0, 0.6);
  box-shadow: 0 0 0 3px rgba(236, 72, 153, 0.15);
}

.form-textarea::placeholder {
  color: var(--text-muted);
}

.result-preview {
  margin-top: 16px;
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  max-height: 240px;
  border: 1px solid rgba(255, 255, 255, 0.05);
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
  padding: 4px 8px;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  border-radius: 6px;
  font-size: 0.625rem;
  font-weight: 700;
  color: #fff;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.node-handle {
  width: 10px !important;
  height: 10px !important;
  background: #1A1A1A !important;
  border: 2px solid #EC4899 !important;
  transition: all 0.2s ease;
}

.node-handle:hover {
  transform: scale(1.3);
  background: #EC4899 !important;
}
</style>
