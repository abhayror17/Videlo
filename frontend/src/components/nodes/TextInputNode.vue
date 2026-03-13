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
        <span class="node-icon">📝</span>
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
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  min-width: 240px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  transition: all 0.2s ease;
}

.workflow-node:hover {
  border-color: rgba(99, 102, 241, 0.3);
  box-shadow: 0 8px 32px rgba(99, 102, 241, 0.15);
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
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(99, 102, 241, 0.1));
  border-radius: 8px;
}

.node-icon {
  font-size: 1rem;
}

.node-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: #A5B4FC;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  flex: 1;
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
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 0.8125rem;
  line-height: 1.5;
  resize: none;
  font-family: inherit;
  transition: all 0.2s ease;
}

.node-textarea:focus {
  outline: none;
  border-color: #6366F1;
  background: var(--bg-elevated);
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
  font-size: 0.6875rem;
  color: #4B5563;
  transition: color 0.2s ease;
}

.char-count.has-content {
  color: #6B7280;
}

.node-handle {
  width: 14px !important;
  height: 14px !important;
  background: #6366F1 !important;
  border: 2px solid var(--bg-panel) !important;
}

.node-handle:hover {
  transform: scale(1.2);
}
</style>