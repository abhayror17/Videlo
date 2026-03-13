<template>
  <div class="workflow-node image-enhance-node" :class="{ processing: isProcessing }">
    <button class="node-delete-btn" @click.stop="deleteNode" title="Delete node">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"/>
        <line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    </button>
    <div class="node-header">
      <div class="node-icon-wrapper">
        <span class="node-icon">✨</span>
      </div>
      <span class="node-title">{{ $t('workflow.imageEnhance') }}</span>
      <div v-if="isProcessing" class="node-spinner"></div>
      <div v-else-if="localData.resultUrl" class="node-status success"></div>
    </div>
    <div class="node-body">
      <div class="form-row">
        <label>{{ $t('settings.model') }}</label>
        <select v-model="localData.model" @change="updateData" class="form-select">
          <option value="Flux_2_Klein_4B_BF16">Flux 2 Klein</option>
          <option value="QwenImageEdit_Plus_NF4">Qwen Image Edit</option>
        </select>
      </div>
      <div class="form-row">
        <label>{{ $t('settings.aspectRatio') }}</label>
        <select v-model="localData.aspectRatio" @change="onAspectChange" class="form-select">
          <option v-for="ar in aspectRatios" :key="ar.value" :value="ar.value">{{ ar.label }}</option>
        </select>
      </div>
      
      <div class="form-row">
        <label>Enhancement</label>
        <select v-model="localData.enhanceType" @change="updateEnhancePrompt" class="form-select">
          <option value="quality">Improve Quality</option>
          <option value="upscale">Upscale & Sharpen</option>
          <option value="denoise">Remove Noise</option>
          <option value="color">Enhance Colors</option>
          <option value="custom">Custom Prompt</option>
        </select>
      </div>
      
      <div v-if="localData.enhanceType === 'custom'" class="form-row">
        <label>Custom Prompt</label>
        <textarea 
          v-model="localData.enhancePrompt" 
          @input="updateData"
          class="form-textarea"
          rows="2"
          placeholder="Describe the enhancement..."
        ></textarea>
      </div>
      
      <div class="form-row">
        <label>Strength</label>
        <div class="slider-wrapper">
          <input 
            type="range" 
            v-model.number="localData.strength" 
            @change="updateData" 
            min="0.1" 
            max="1" 
            step="0.1" 
            class="form-slider" 
          />
          <span class="slider-value">{{ localData.strength }}</span>
        </div>
      </div>
      
      <!-- Result Preview -->
      <div v-if="localData.resultUrl" class="result-preview">
        <img :src="localData.resultUrl" alt="Enhanced" />
        <div class="result-badge">Enhanced</div>
      </div>
      
      <!-- Quick Actions -->
      <div v-if="localData.resultUrl" class="quick-actions">
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

// Aspect ratios
const aspectRatios = [
  { value: 'original', label: 'Original Size', width: 768, height: 768 },
  { value: '1:1', label: '1:1 (Square)', width: 768, height: 768 },
  { value: '16:9', label: '16:9 (Landscape)', width: 1024, height: 576 },
  { value: '9:16', label: '9:16 (Portrait)', width: 576, height: 1024 },
  { value: '4:3', label: '4:3', width: 768, height: 576 },
  { value: '3:4', label: '3:4', width: 576, height: 768 }
]

const enhancePrompts = {
  quality: 'enhance image quality, improve details, sharp focus, high resolution, professional photography',
  upscale: 'upscale image, increase resolution, add fine details, 4k quality, sharp edges',
  denoise: 'remove noise, clean image, smooth gradients, reduce grain, clear details',
  color: 'enhance colors, vibrant tones, improve contrast, better lighting, vivid colors'
}

const localData = ref({
  model: props.data.model || 'Flux_2_Klein_4B_BF16',
  aspectRatio: props.data.aspectRatio || 'original',
  width: props.data.width || 768,
  height: props.data.height || 768,
  enhanceType: props.data.enhanceType || 'quality',
  enhancePrompt: props.data.enhancePrompt || enhancePrompts.quality,
  strength: props.data.strength || 0.5,
  resultUrl: props.data.resultUrl || null,
  status: props.data.status || 'idle'
})

watch(() => props.data, (newData) => {
  localData.value = { ...localData.value, ...newData }
}, { deep: true })

const isProcessing = computed(() => localData.value.status === 'processing')

const updateEnhancePrompt = () => {
  if (localData.value.enhanceType !== 'custom') {
    localData.value.enhancePrompt = enhancePrompts[localData.value.enhanceType] || enhancePrompts.quality
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

const updateData = () => {
  updateNodeData(props.id, { ...localData.value })
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
  border-color: rgba(251, 191, 36, 0.3);
  box-shadow: 0 8px 32px rgba(251, 191, 36, 0.15);
}

.workflow-node.processing {
  border-color: rgba(251, 191, 36, 0.5);
  box-shadow: 0 0 30px rgba(251, 191, 36, 0.2);
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
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.3), rgba(251, 191, 36, 0.1));
  border-radius: 8px;
}

.node-icon {
  font-size: 1rem;
}

.node-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: #FBBF24;
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
  border: 2px solid rgba(251, 191, 36, 0.3);
  border-top-color: #FBBF24;
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
  font-weight: 500;
  color: #9CA3AF;
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-select,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.8125rem;
  transition: all 0.2s ease;
}

.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #FBBF24;
  background: var(--bg-elevated);
}

.form-textarea {
  resize: none;
  font-family: inherit;
}

.slider-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.form-slider {
  flex: 1;
  height: 6px;
  -webkit-appearance: none;
  background: var(--bg-input);
  border-radius: 3px;
  outline: none;
}

.form-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background: #FBBF24;
  border-radius: 50%;
  cursor: pointer;
}

.slider-value {
  font-size: 0.75rem;
  color: #FBBF24;
  font-weight: 500;
  min-width: 24px;
}

.result-preview {
  position: relative;
  border-radius: 10px;
  overflow: hidden;
  max-height: 150px;
  display: flex;
  justify-content: center;
  background: var(--bg-input);
}

.result-preview img {
  max-width: 100%;
  max-height: 150px;
  object-fit: contain;
  border-radius: 10px;
}

.result-badge {
  position: absolute;
  bottom: 8px;
  right: 8px;
  padding: 4px 10px;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 6px;
  font-size: 0.625rem;
  font-weight: 600;
  color: #FBBF24;
  text-transform: uppercase;
}

.node-handle {
  width: 14px !important;
  height: 14px !important;
  background: #FBBF24 !important;
  border: 2px solid var(--bg-panel) !important;
}

.node-handle:hover {
  transform: scale(1.2);
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
  background: rgba(251, 191, 36, 0.15);
  border-color: #FBBF24;
  color: #FBBF24;
  transform: translateY(-2px);
}

.quick-action-btn svg {
  width: 16px;
  height: 16px;
}
</style>
