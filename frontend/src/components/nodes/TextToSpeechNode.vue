<template>
  <div class="workflow-node tts-node" :class="{ processing: isProcessing }">
    <button class="node-delete-btn" @click.stop="deleteNode" title="Delete node">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"/>
        <line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    </button>
    <div class="node-header">
      <div class="node-icon-wrapper">
        <span class="node-icon">🔊</span>
      </div>
      <span class="node-title">{{ $t('workflow.textToSpeech') }}</span>
      <div v-if="isProcessing" class="node-spinner"></div>
      <div v-else-if="localData.resultUrl" class="node-status success"></div>
    </div>
    <div class="node-body">
      <div class="form-row">
        <label>{{ $t('settings.model') }}</label>
        <select v-model="localData.model" @change="updateData" class="form-select">
          <option value="Kokoro">Kokoro</option>
        </select>
      </div>
      <div class="form-row">
        <label>Voice</label>
        <select v-model="localData.voice" @change="updateData" class="form-select">
          <option value="af_sky">Sky (Female)</option>
          <option value="af_bella">Bella (Female)</option>
          <option value="am_michael">Michael (Male)</option>
        </select>
      </div>
      <div class="form-row">
        <label>Speed</label>
        <div class="slider-wrapper">
          <input type="range" v-model.number="localData.speed" @change="updateData" min="0.5" max="2" step="0.1" class="form-slider" />
          <span class="slider-value">{{ localData.speed }}x</span>
        </div>
      </div>
      
      <!-- Result Preview -->
      <div v-if="localData.resultUrl" class="result-preview audio">
        <div class="audio-visualizer">
          <span class="audio-bars">
            <i></i><i></i><i></i><i></i><i></i>
          </span>
        </div>
        <audio :src="localData.resultUrl" controls></audio>
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
  model: props.data.model || 'Kokoro',
  voice: props.data.voice || 'af_sky',
  lang: props.data.lang || 'en-us',
  speed: props.data.speed || 1,
  resultUrl: props.data.resultUrl || null,
  status: props.data.status || 'idle'
})

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
  border-color: rgba(139, 92, 246, 0.3);
  box-shadow: 0 8px 32px rgba(139, 92, 246, 0.15);
}

.workflow-node.processing {
  border-color: rgba(139, 92, 246, 0.5);
  box-shadow: 0 0 30px rgba(139, 92, 246, 0.2);
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
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.3), rgba(139, 92, 246, 0.1));
  border-radius: 8px;
}

.node-icon {
  font-size: 1rem;
}

.node-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: #A78BFA;
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
  border: 2px solid rgba(139, 92, 246, 0.2);
  border-top-color: #8B5CF6;
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
  border-color: #8B5CF6;
  background: var(--bg-elevated);
}

.slider-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.form-slider {
  flex: 1;
  height: 4px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 2px;
  appearance: none;
  cursor: pointer;
}

.form-slider::-webkit-slider-thumb {
  appearance: none;
  width: 16px;
  height: 16px;
  background: linear-gradient(135deg, #8B5CF6, #A78BFA);
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 0 8px rgba(139, 92, 246, 0.4);
}

.slider-value {
  min-width: 36px;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #A78BFA;
  text-align: right;
}

.result-preview.audio {
  margin-top: 14px;
  padding: 16px;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(139, 92, 246, 0.05));
  border-radius: 10px;
  text-align: center;
}

.audio-visualizer {
  margin-bottom: 12px;
}

.audio-bars {
  display: inline-flex;
  align-items: flex-end;
  gap: 3px;
  height: 28px;
}

.audio-bars i {
  width: 4px;
  background: linear-gradient(to top, #8b5cf6, #a78bfa);
  border-radius: 2px;
  animation: audioBar 0.8s ease-in-out infinite;
}

.audio-bars i:nth-child(1) { height: 40%; animation-delay: 0s; }
.audio-bars i:nth-child(2) { height: 70%; animation-delay: 0.1s; }
.audio-bars i:nth-child(3) { height: 100%; animation-delay: 0.2s; }
.audio-bars i:nth-child(4) { height: 60%; animation-delay: 0.3s; }
.audio-bars i:nth-child(5) { height: 30%; animation-delay: 0.4s; }

@keyframes audioBar {
  0%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(0.5); }
}

.result-preview.audio audio {
  width: 100%;
  height: 40px;
  border-radius: 8px;
}

.node-handle {
  width: 14px !important;
  height: 14px !important;
  background: #8B5CF6 !important;
  border: 2px solid var(--bg-panel) !important;
}
</style>