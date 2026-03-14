<template>
  <div class="workflow-node text-input-node">
    <button class="node-delete-btn" @click.stop="deleteNode" title="Delete node">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"/>
        <line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    </button>
    <div class="node-header">
      <div class="node-icon-wrapper">
        <div class="node-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
        </div>
      </div>
      <span class="node-title">{{ $t('workflow.textPrompt') }}</span>
      <div v-if="localText" class="node-status filled"></div>
    </div>
    <div class="node-body">
      <textarea
        v-model="localText"
        :placeholder="$t('workflow.enterPrompt')"
        @input="updateData"
        rows="4"
        class="node-textarea"
      ></textarea>
      <div class="node-footer">
        <span class="char-count" :class="{ 'has-content': localText.length > 0 }">
          {{ localText.length }} chars
        </span>
      </div>
    </div>
    <Handle type="source" :position="Position.Right" class="node-handle source" />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Handle, Position, useVueFlow } from '@vue-flow/core'

const props = defineProps({
  id: String,
  data: Object
})

const { updateNodeData, removeNodes } = useVueFlow()

const localText = ref(props.data.text || '')

watch(() => props.data.text, (newVal) => {
  localText.value = newVal || ''
})

const updateData = () => {
  updateNodeData(props.id, { ...props.data, text: localText.value })
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
  min-width: 240px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.workflow-node:hover {
  border-color: rgba(99, 102, 241, 0.4);
  box-shadow: 0 12px 40px rgba(99, 102, 241, 0.15);
  transform: translateY(-2px);
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
  background: rgba(239, 68, 68, 0.1);
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
  background: #4B5563;
  transition: all 0.2s ease;
}

.node-status.filled {
  background: #22C55E;
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.5);
}

.node-body {
  padding: 16px;
}

.node-textarea {
  width: 100%;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: #fff;
  font-size: 0.8125rem;
  line-height: 1.5;
  resize: none;
  font-family: inherit;
  transition: all 0.2s ease;
}

.node-textarea:focus {
  outline: none;
  border-color: rgba(99, 102, 241, 0.5);
  background: rgba(255, 255, 255, 0.08);
}

.node-textarea::placeholder {
  color: var(--text-muted);
}

.node-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}

.char-count {
  font-size: 0.625rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.2);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.char-count.has-content {
  color: rgba(255, 255, 255, 0.4);
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