<template>
  <div class="workflow-node image-analysis-node" :class="{ processing: isProcessing }">
    <button class="node-delete-btn" @click.stop="deleteNode" title="Delete node">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"/>
        <line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    </button>
    <div class="node-header">
      <div class="node-icon-wrapper">
        <span class="node-icon">🔍</span>
      </div>
      <span class="node-title">{{ $t('workflow.imageAnalysis') }}</span>
      <div v-if="isProcessing" class="node-spinner"></div>
      <div v-else-if="localData.text" class="node-status success"></div>
    </div>
    <div class="node-body">
      <div class="form-row">
        <label>{{ $t('settings.model') }}</label>
        <select v-model="localData.model" @change="updateData" class="form-select">
          <option value="Nanonets_Ocr_S_F16">Nanonets OCR</option>
        </select>
      </div>
      <div class="form-row">
        <label>Language</label>
        <select v-model="localData.language" @change="updateData" class="form-select">
          <option value="auto">Auto Detect</option>
          <option value="en">English</option>
          <option value="zh">Chinese</option>
          <option value="ja">Japanese</option>
        </select>
      </div>
      
      <!-- Result Preview -->
      <div v-if="localData.text" class="result-preview">
        <div class="result-header">
          <span class="result-icon">📝</span>
          <span class="result-label">Extracted Text</span>
        </div>
        <div class="result-text">{{ localData.text }}</div>
        <button class="copy-btn" @click="copyText">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
          </svg>
          {{ copied ? 'Copied!' : $t('workflow.copy') }}
        </button>
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

const localData = ref({
  model: props.data.model || 'Nanonets_Ocr_S_F16',
  language: props.data.language || 'auto',
  format: props.data.format || 'text',
  text: props.data.text || null,
  status: props.data.status || 'idle'
})

const copied = ref(false)

watch(() => props.data, (newData) => {
  localData.value = { ...localData.value, ...newData }
}, { deep: true })

const isProcessing = computed(() => localData.value.status === 'processing')

const updateData = () => {
  updateNodeData(props.id, { ...localData.value })
}

const deleteNode = () => {
  removeNodes([props.id])
}

const copyText = async () => {
  if (localData.value.text) {
    await navigator.clipboard.writeText(localData.value.text)
    copied.value = true
    setTimeout(() => copied.value = false, 2000)
  }
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
  border-color: rgba(6, 182, 212, 0.3);
  box-shadow: 0 8px 32px rgba(6, 182, 212, 0.15);
}

.workflow-node.processing {
  border-color: rgba(6, 182, 212, 0.5);
  box-shadow: 0 0 30px rgba(6, 182, 212, 0.2);
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
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.3), rgba(6, 182, 212, 0.1));
  border-radius: 8px;
}

.node-icon {
  font-size: 1rem;
}

.node-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: #22D3EE;
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
  border: 2px solid rgba(6, 182, 212, 0.2);
  border-top-color: #06B6D4;
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

.form-select:focus {
  outline: none;
  border-color: #06B6D4;
  background: var(--bg-elevated);
}

.result-preview {
  margin-top: 14px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-radius: 10px;
  padding: 14px;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.result-icon {
  font-size: 0.875rem;
}

.result-label {
  font-size: 0.6875rem;
  font-weight: 600;
  color: #6B7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.result-text {
  font-size: 0.8125rem;
  color: #E5E5E5;
  line-height: 1.5;
  max-height: 100px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.copy-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 12px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 6px;
  color: #9CA3AF;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.copy-btn:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(6, 182, 212, 0.3);
  color: #22D3EE;
}

.copy-btn svg {
  width: 14px;
  height: 14px;
}

.node-handle {
  width: 14px !important;
  height: 14px !important;
  background: #06B6D4 !important;
  border: 2px solid var(--bg-panel) !important;
}
</style>