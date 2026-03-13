<template>
  <div class="workflow-node image-gen-node" :class="{ processing: isProcessing }">
    <button class="node-delete-btn" @click.stop="deleteNode" title="Delete node">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"/>
        <line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    </button>
    <div class="node-header">
      <div class="node-icon-wrapper">
        <span class="node-icon">🎨</span>
      </div>
      <span class="node-title">{{ $t('workflow.textToImage') }}</span>
      <div v-if="isProcessing" class="node-spinner"></div>
      <div v-else-if="localData.resultUrls && localData.resultUrls.length" class="node-status success"></div>
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
        <select v-model="localData.model" @change="onModelChange" class="form-select">
          <option v-for="m in models" :key="m.id" :value="m.id">{{ m.name }}</option>
        </select>
      </div>
      <div class="form-row">
        <label>{{ $t('settings.aspectRatio') }}</label>
        <select v-model="localData.aspectRatio" @change="onAspectChange" class="form-select">
          <option v-for="ar in aspectRatios" :key="ar.value" :value="ar.value">{{ ar.label }}</option>
        </select>
      </div>
      <div class="form-row">
        <label>{{ $t('settings.numImages') }}</label>
        <div class="batch-selector">
          <button 
            v-for="n in [1, 2, 3, 4]" 
            :key="n"
            class="batch-btn"
            :class="{ active: localData.batchSize === n }"
            @click="setBatchSize(n)"
          >{{ n }}</button>
        </div>
      </div>
      
      <!-- Result Preview -->
      <div v-if="localData.resultUrls && localData.resultUrls.length" class="result-preview">
        <div class="result-grid" :class="{ 'single': localData.resultUrls.length === 1 }">
          <div v-for="(url, idx) in localData.resultUrls" :key="idx" class="result-item">
            <img :src="url" :alt="'Generated ' + (idx + 1)" />
          </div>
        </div>
        <div class="result-badge">{{ localData.resultUrls.length }} image{{ localData.resultUrls.length > 1 ? 's' : '' }}</div>
      </div>
      
      <!-- Quick Actions -->
      <div v-if="localData.resultUrls && localData.resultUrls.length" class="quick-actions">
        <button class="quick-action-btn" @click="addConnected('imageEdit')" title="Edit Image">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
        </button>
        <button class="quick-action-btn" @click="addConnected('imageEnhance')" title="Enhance Image">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
        </button>
        <button class="quick-action-btn" @click="addConnected('img2video')" title="Image to Video">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="23 7 16 12 23 17 23 7"/>
            <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
          </svg>
        </button>
        <button class="quick-action-btn" @click="addConnected('imageAnalysis')" title="Analyze Image (OCR)">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
        </button>
        <button class="quick-action-btn" @click="addConnected('bgRemoval')" title="Remove Background">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
            <circle cx="8.5" cy="8.5" r="1.5"/>
            <polyline points="21 15 16 10 5 21"/>
          </svg>
        </button>
      </div>
    </div>
    <Handle type="target" :position="Position.Left" class="node-handle target" />
    <Handle type="source" :position="Position.Right" class="node-handle source" />
  </div>
</template>

<script setup>
import { ref, watch, computed, inject } from 'vue'
import { Handle, Position, useVueFlow } from '@vue-flow/core'

const props = defineProps({
  id: String,
  data: Object
})

const { updateNodeData, removeNodes } = useVueFlow()
const addConnectedNode = inject('addConnectedNode', null)

// Available models
const models = [
  { id: 'Flux_2_Klein_4B_BF16', name: 'Flux 2 Klein', steps: 4 },
  { id: 'Flux1schnell', name: 'Flux.1 Schnell', steps: 4 },
  { id: 'ZImageTurbo_INT8', name: 'ZImage Turbo', steps: 8 }
]

// Aspect ratios with dimensions
const aspectRatios = [
  { value: '1:1', label: '1:1 (Square)', width: 1024, height: 1024 },
  { value: '16:9', label: '16:9 (Landscape)', width: 1024, height: 576 },
  { value: '9:16', label: '9:16 (Portrait)', width: 576, height: 1024 },
  { value: '4:3', label: '4:3', width: 1024, height: 768 },
  { value: '3:4', label: '3:4', width: 768, height: 1024 },
  { value: '21:9', label: '21:9 (Ultrawide)', width: 1024, height: 440 },
  { value: '9:21', label: '9:21 (Vertical)', width: 440, height: 1024 }
]

const localData = ref({
  prompt: props.data.prompt || '',
  model: props.data.model || 'Flux_2_Klein_4B_BF16',
  aspectRatio: props.data.aspectRatio || '16:9',
  width: props.data.width || 1024,
  height: props.data.height || 576,
  steps: props.data.steps || 4,
  batchSize: props.data.batchSize || 1,
  resultUrl: props.data.resultUrl || null,
  resultUrls: props.data.resultUrls || [],
  status: props.data.status || 'idle'
})

watch(() => props.data, (newData) => {
  localData.value = { ...localData.value, ...newData }
}, { deep: true })

const isProcessing = computed(() => localData.value.status === 'processing')

const updateData = () => {
  updateNodeData(props.id, { ...localData.value })
}

const onModelChange = () => {
  const model = models.find(m => m.id === localData.value.model)
  if (model) {
    localData.value.steps = model.steps
  }
  updateData()
}

const onAspectChange = () => {
  const ar = aspectRatios.find(a => a.value === localData.value.aspectRatio)
  if (ar) {
    localData.value.width = ar.width
    localData.value.height = ar.height
  }
  updateData()
}

const setBatchSize = (n) => {
  localData.value.batchSize = n
  updateData()
}

const deleteNode = () => {
  removeNodes([props.id])
}

const addConnected = (nodeType) => {
  if (addConnectedNode) {
    addConnectedNode(props.id, nodeType)
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
  border-color: rgba(168, 85, 247, 0.3);
  box-shadow: 0 8px 32px rgba(168, 85, 247, 0.15);
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
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.3), rgba(168, 85, 247, 0.1));
  border-radius: 8px;
}

.node-icon {
  font-size: 1rem;
}

.node-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: #C084FC;
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
  border: 2px solid rgba(168, 85, 247, 0.2);
  border-top-color: #A855F7;
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

.form-select,
.form-input {
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
.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #A855F7;
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

.batch-selector {
  display: flex;
  gap: 8px;
}

.batch-btn {
  flex: 1;
  padding: 10px;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-muted);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.batch-btn:hover {
  border-color: #A855F7;
  color: #A855F7;
}

.batch-btn.active {
  background: rgba(168, 85, 247, 0.15);
  border-color: #A855F7;
  color: #A855F7;
}

.result-preview {
  margin-top: 14px;
  position: relative;
  border-radius: 10px;
  overflow: hidden;
  background: var(--bg-elevated);
}

.result-grid {
  display: grid;
  gap: 4px;
  padding: 4px;
}

.result-grid.single {
  display: flex;
  justify-content: center;
}

.result-grid:not(.single) {
  grid-template-columns: repeat(2, 1fr);
}

.result-item {
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-input);
}

.result-item img {
  width: 100%;
  height: auto;
  display: block;
  object-fit: cover;
  max-height: 150px;
}

.result-grid.single .result-item img {
  max-height: 200px;
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
  background: #A855F7 !important;
  border: 2px solid var(--bg-panel) !important;
}

.quick-actions {
  display: flex;
  justify-content: center;
  gap: 6px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

.quick-action-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: #9CA3AF;
  cursor: pointer;
  transition: all 0.15s ease;
}

.quick-action-btn:hover {
  background: rgba(168, 85, 247, 0.15);
  border-color: #A855F7;
  color: #A855F7;
  transform: translateY(-2px);
}

.quick-action-btn svg {
  width: 16px;
  height: 16px;
}
</style>
