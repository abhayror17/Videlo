<template>
  <div class="workflow-node prompt-enhancer-node video-enhancer" :class="{ processing: isProcessing }">
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
      <span class="node-title">{{ $t('workflow.videoPromptEnhancer') }}</span>
      <div v-if="isProcessing" class="node-spinner"></div>
      <div v-else-if="localData.enhancedPrompt" class="node-status success"></div>
    </div>
    <div class="node-body">
      <div class="form-row">
        <label>{{ $t('workflow.originalPrompt') }}</label>
        <textarea 
          v-model="localData.originalPrompt" 
          @input="updateData"
          class="form-textarea"
          rows="3"
          :placeholder="$t('workflow.enterVideoPromptToEnhance')"
        ></textarea>
      </div>
      
      <!-- Enhanced Result -->
      <div v-if="localData.enhancedPrompt" class="enhanced-result">
        <div class="result-label">{{ $t('workflow.enhancedPrompt') }}</div>
        <div class="result-content">{{ localData.enhancedPrompt }}</div>
        <button class="copy-btn" @click="copyEnhancedPrompt" :class="{ copied: copied }">
          <svg v-if="!copied" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          <span>{{ copied ? $t('workflow.copied') : $t('workflow.copy') }}</span>
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
  originalPrompt: props.data.originalPrompt || '',
  enhancedPrompt: props.data.enhancedPrompt || '',
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

const copyEnhancedPrompt = () => {
  if (localData.value.enhancedPrompt) {
    navigator.clipboard.writeText(localData.value.enhancedPrompt)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
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
  min-width: 280px;
  max-width: 320px;
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
  background: #EF4444;
  color: white;
}

.node-delete-btn svg {
  width: 14px;
  height: 14px;
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
  margin-bottom: 14px;
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

.form-textarea {
  width: 100%;
  padding: 10px 12px;
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 10px;
  color: #fff;
  font-size: 0.8125rem;
  font-family: inherit;
  transition: all 0.2s ease;
  resize: none;
  line-height: 1.5;
}

.form-textarea:focus {
  outline: none;
  border-color: rgba(236, 72, 153, 0.6);
  background: rgba(0, 0, 0, 0.5);
  box-shadow: 0 0 0 3px rgba(236, 72, 153, 0.1);
}

.form-textarea::placeholder {
  color: var(--text-muted);
}

.enhanced-result {
  margin-top: 14px;
  padding: 12px;
  background: rgba(236, 72, 153, 0.1);
  border: 1px solid rgba(236, 72, 153, 0.2);
  border-radius: 10px;
}

.result-label {
  font-size: 0.625rem;
  font-weight: 700;
  color: #F472B6;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
}

.result-content {
  font-size: 0.8125rem;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.5;
  max-height: 120px;
  overflow-y: auto;
  margin-bottom: 10px;
}

.copy-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 8px 12px;
  background: rgba(236, 72, 153, 0.2);
  border: 1px solid rgba(236, 72, 153, 0.3);
  border-radius: 8px;
  color: #F472B6;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.copy-btn:hover {
  background: rgba(236, 72, 153, 0.3);
}

.copy-btn.copied {
  background: rgba(34, 197, 94, 0.2);
  border-color: rgba(34, 197, 94, 0.3);
  color: #22C55E;
}

.copy-btn svg {
  width: 14px;
  height: 14px;
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
