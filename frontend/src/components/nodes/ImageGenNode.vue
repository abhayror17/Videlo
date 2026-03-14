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
        <div class="node-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
        </div>
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
  border-color: rgba(168, 85, 247, 0.4);
  box-shadow: 0 12px 40px rgba(168, 85, 247, 0.15);
  transform: translateY(-2px);
}

.workflow-node.processing {
  border-color: #A855F7;
  box-shadow: 0 0 20px rgba(168, 85, 247, 0.2);
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
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.25), rgba(168, 85, 247, 0.1));
  border-radius: 10px;
  color: #C084FC;
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
.form-input,
.form-textarea {
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

/* Custom select arrow */
.form-select {
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%239CA3AF' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 16px;
}

/* Dropdown options styling */
.form-select option {
  background: #1a1a2e;
  color: #fff;
  padding: 10px;
  font-size: 0.875rem;
}

.form-select option:hover,
.form-select option:focus {
  background: rgba(168, 85, 247, 0.3);
}

.form-select:focus,
.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: rgba(168, 85, 247, 0.6);
  background: rgba(0, 0, 0, 0.5);
  box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.1);
}

.form-textarea {
  width: 100%;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: #fff;
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
  gap: 6px;
}

.batch-btn {
  flex: 1;
  padding: 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.batch-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.batch-btn.active {
  background: rgba(168, 85, 247, 0.2);
  border-color: rgba(168, 85, 247, 0.4);
  color: #C084FC;
}

.result-preview {
  margin-top: 16px;
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.result-grid {
  display: grid;
  gap: 2px;
  padding: 2px;
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
  max-height: 180px;
}

.result-grid.single .result-item img {
  max-height: 200px;
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
  border: 2px solid #A855F7 !important;
  transition: all 0.2s ease;
}

.node-handle:hover {
  transform: scale(1.3);
  background: #A855F7 !important;
}

.quick-actions {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.quick-action-btn {
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.2s ease;
}

.quick-action-btn:hover {
  background: rgba(168, 85, 247, 0.2);
  border-color: rgba(168, 85, 247, 0.4);
  color: #C084FC;
  transform: translateY(-2px);
}

.quick-action-btn svg {
  width: 16px;
  height: 16px;
}
</style>
