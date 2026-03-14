<template>
  <div class="workflow-node video-to-text-node" :class="{ processing: isProcessing }">
    <button class="node-delete-btn" @click.stop="deleteNode" title="Delete node">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"/>
        <line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    </button>
    <div class="node-header">
      <div class="node-icon-wrapper">
        <div class="node-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><path d="M7 21h10"/><path d="M12 17v4"/><path d="M9 8h6"/><path d="M9 12h6"/></svg>
        </div>
      </div>
      <span class="node-title">{{ $t('workflow.videoToText') }}</span>
      <div v-if="isProcessing" class="node-spinner"></div>
      <div v-else-if="localData.text" class="node-status success"></div>
    </div>
    <div class="node-body">
      <div class="form-row">
        <label>{{ $t('settings.model') }}</label>
        <select v-model="localData.model" @change="updateData" class="form-select">
          <option value="WhisperLargeV3">Whisper Large V3</option>
        </select>
      </div>
      
      <div class="form-row">
        <label>Include Timestamps</label>
        <select v-model="localData.includeTs" @change="updateData" class="form-select">
          <option :value="true">Yes</option>
          <option :value="false">No</option>
        </select>
      </div>
      
      <!-- Video URL Input -->
      <div class="form-row">
        <label>Video URL (YouTube, X, Twitch)</label>
        <input 
          v-model="localData.videoUrl" 
          @change="updateData"
          type="text" 
          class="form-input" 
          placeholder="https://youtube.com/watch?v=..."
        />
      </div>
      
      <!-- Result Preview -->
      <div v-if="localData.text" class="result-preview">
        <div class="text-result">{{ truncatedText }}</div>
        <button class="copy-btn" @click="copyText">
          {{ copied ? 'Copied!' : 'Copy' }}
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
  model: props.data.model || 'WhisperLargeV3',
  includeTs: props.data.includeTs ?? true,
  videoUrl: props.data.videoUrl || '',
  text: props.data.text || null,
  status: props.data.status || 'idle'
})

const copied = ref(false)

watch(() => props.data, (newData) => {
  localData.value = { ...localData.value, ...newData }
}, { deep: true })

const isProcessing = computed(() => localData.value.status === 'processing')

const truncatedText = computed(() => {
  const text = localData.value.text
  if (!text) return ''
  return text.length > 300 ? text.substring(0, 300) + '...' : text
})

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
  border-color: rgba(34, 197, 94, 0.4);
  box-shadow: 0 12px 40px rgba(34, 197, 94, 0.15);
  transform: translateY(-2px);
}

.workflow-node.processing {
  border-color: #22C55E;
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
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.25), rgba(34, 197, 94, 0.1));
  border-radius: 10px;
  color: #4ADE80;
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
  border: 2px solid rgba(34, 197, 94, 0.2);
  border-top-color: #22C55E;
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
.form-input {
  width: 100%;
  padding: 10px 32px 10px 12px;
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.15);
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
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%239CA3AF' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 16px;
}

.form-select option {
  background: #1a1a2e;
  color: #fff;
  padding: 10px;
  font-size: 0.875rem;
}

.form-select:focus,
.form-input:focus {
  outline: none;
  border-color: rgba(34, 197, 94, 0.6);
  background: rgba(0, 0, 0, 0.5);
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.1);
}

.form-input::placeholder {
  color: var(--text-muted);
}

.result-preview {
  position: relative;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 16px;
}

.text-result {
  font-size: 0.8125rem;
  color: #fff;
  line-height: 1.6;
  white-space: pre-wrap;
  max-height: 150px;
  overflow-y: auto;
  opacity: 0.9;
}

.copy-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 8px 16px;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.2);
  border-radius: 8px;
  color: #4ADE80;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.copy-btn:hover {
  background: rgba(34, 197, 94, 0.2);
  border-color: #22C55E;
}

.node-handle {
  width: 10px !important;
  height: 10px !important;
  background: #1A1A1A !important;
  border: 2px solid #22C55E !important;
  transition: all 0.2s ease;
}

.node-handle:hover {
  transform: scale(1.3);
  background: #22C55E !important;
}
</style>
