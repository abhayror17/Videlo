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
        <div class="node-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3 1.912 5.886h6.19l-5.007 3.638L17.007 18.41 12 14.772l-5.007 3.638 1.912-5.886-5.007-3.638h6.19z"/><path d="M5 3 2 6l3 3"/><path d="m19 3 3 3-3 3"/></svg>
        </div>
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
  border-color: rgba(251, 191, 36, 0.4);
  box-shadow: 0 12px 40px rgba(251, 191, 36, 0.15);
  transform: translateY(-2px);
}

.workflow-node.processing {
  border-color: #FBBF24;
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
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.25), rgba(251, 191, 36, 0.1));
  border-radius: 10px;
  color: #FBBF24;
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
  border: 2px solid rgba(251, 191, 36, 0.2);
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
  border-color: rgba(251, 191, 36, 0.6);
  background: rgba(0, 0, 0, 0.5);
  box-shadow: 0 0 0 3px rgba(251, 191, 36, 0.1);
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
  height: 4px;
  -webkit-appearance: none;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  outline: none;
}

.form-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background: #FBBF24;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 0 10px rgba(251, 191, 36, 0.3);
}

.slider-value {
  font-size: 0.75rem;
  color: #FBBF24;
  font-weight: 700;
  min-width: 24px;
}

.result-preview {
  margin-top: 16px;
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  max-height: 240px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.result-preview img {
  max-width: 100%;
  max-height: 240px;
  display: block;
  border-radius: 10px;
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
  border: 2px solid #FBBF24 !important;
  transition: all 0.2s ease;
}

.node-handle:hover {
  transform: scale(1.3);
  background: #FBBF24 !important;
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
