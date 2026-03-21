<template>
  <div class="workflow-node ai-assistant-node" :class="{ processing: isProcessing }">
    <button class="node-delete-btn" @click.stop="deleteNode" title="Delete node">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"/>
        <line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    </button>
    <div class="node-header">
      <div class="node-icon-wrapper">
        <div class="node-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
        </div>
      </div>
      <span class="node-title">{{ $t('workflow.aiAssistant') }}</span>
      <div v-if="isProcessing" class="node-spinner"></div>
      <div v-else-if="localData.response" class="node-status success"></div>
    </div>
    <div class="node-body">
      <div class="form-row">
        <label>{{ $t('workflow.userPrompt') }}</label>
        <textarea 
          v-model="localData.userPrompt" 
          @input="updateData"
          class="form-textarea"
          rows="3"
          :placeholder="$t('workflow.userPromptPlaceholder')"
        ></textarea>
      </div>
      <div class="form-row">
        <label>{{ $t('workflow.model') }}</label>
        <select v-model="localData.model" @change="updateData" class="form-select">
          <option v-for="m in models" :key="m.id" :value="m.id">{{ m.name }}</option>
        </select>
      </div>
      
      <!-- Response Preview -->
      <div v-if="localData.response" class="response-preview">
        <div class="response-label">{{ $t('workflow.aiResponse') }}</div>
        <div class="response-content">{{ localData.response }}</div>
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

// Available models for AI Assistant (iFlow compatible)
const models = [
  { id: 'kimi-k2', name: 'Kimi K2' },
  { id: 'gpt-4o', name: 'GPT-4o' },
  { id: 'gpt-4o-mini', name: 'GPT-4o Mini' },
  { id: 'claude-3-sonnet', name: 'Claude 3 Sonnet' },
  { id: 'claude-3-haiku', name: 'Claude 3 Haiku' }
]

// Default system prompt (hidden from user)
const DEFAULT_SYSTEM_PROMPT = "You are a helpful AI assistant."

const localData = ref({
  userPrompt: '',
  model: 'kimi-k2',
  response: '',
  status: 'idle'
})

// Initialize from props and watch for changes
watch(() => props.data, (newData) => {
  if (newData) {
    // Update each field individually to maintain reactivity
    if (newData.userPrompt !== undefined) localData.value.userPrompt = newData.userPrompt
    if (newData.model !== undefined) localData.value.model = newData.model
    if (newData.response !== undefined) localData.value.response = newData.response
    if (newData.status !== undefined) localData.value.status = newData.status
    if (newData.text !== undefined) localData.value.response = newData.text
  }
}, { immediate: true, deep: true })

const isProcessing = computed(() => localData.value.status === 'processing')

const updateData = () => {
  updateNodeData(props.id, { 
    systemPrompt: DEFAULT_SYSTEM_PROMPT,
    userPrompt: localData.value.userPrompt,
    model: localData.value.model,
    response: localData.value.response,
    status: localData.value.status
  })
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
  min-width: 280px;
  max-width: 320px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.workflow-node:hover {
  border-color: rgba(99, 102, 241, 0.4);
  box-shadow: 0 12px 40px rgba(99, 102, 241, 0.15);
  transform: translateY(-2px);
}

.workflow-node.processing {
  border-color: #6366F1;
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.2);
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
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.25), rgba(99, 102, 241, 0.1));
  border-radius: 10px;
  color: #A5B4FC;
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
  border: 2px solid rgba(99, 102, 241, 0.2);
  border-top-color: #6366F1;
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

.form-select,
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
.form-textarea:focus {
  outline: none;
  border-color: rgba(99, 102, 241, 0.6);
  background: rgba(0, 0, 0, 0.5);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.form-textarea {
  resize: none;
  line-height: 1.5;
}

.form-textarea::placeholder {
  color: var(--text-muted);
}

.response-preview {
  margin-top: 14px;
  padding: 12px;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.2);
  border-radius: 10px;
}

.response-label {
  font-size: 0.625rem;
  font-weight: 700;
  color: #22C55E;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
}

.response-content {
  font-size: 0.8125rem;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.5;
  max-height: 120px;
  overflow-y: auto;
}

.node-handle {
  width: 10px !important;
  height: 10px !important;
  background: #1A1A1A !important;
  border: 2px solid #6366F1 !important;
  transition: all 0.2s ease;
}

.node-handle:hover {
  transform: scale(1.3);
  background: #6366F1 !important;
}
</style>
