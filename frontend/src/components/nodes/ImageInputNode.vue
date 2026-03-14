<template>
  <div class="workflow-node image-input-node">
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
      <span class="node-title">{{ $t('workflow.imageInput') }}</span>
      <div v-if="localData.imageUrl" class="node-status filled"></div>
    </div>
    <div class="node-body">
      <!-- Image Preview -->
      <div v-if="localData.imageUrl" class="image-preview">
        <img :src="localData.imageUrl" alt="Input" />
        <button class="remove-btn" @click="removeImage">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
      
      <!-- Upload Area -->
      <div v-else class="upload-area" @click="triggerUpload" @dragover.prevent @drop.prevent="handleDrop">
        <input type="file" ref="fileInput" @change="handleFileSelect" accept="image/*" hidden />
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="3" y="3" width="18" height="18" rx="2"/>
          <circle cx="8.5" cy="8.5" r="1.5"/>
          <path d="M21 15l-5-5L5 21"/>
        </svg>
        <span class="upload-text">Drop image or click to upload</span>
      </div>
      
      <!-- URL Input -->
      <div class="url-input-wrapper">
        <input
          v-model="imageUrlInput"
          type="text"
          placeholder="Or paste image URL..."
          class="url-input"
          @keyup.enter="loadFromUrl"
        />
        <button class="url-btn" @click="loadFromUrl" :disabled="!imageUrlInput">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        </button>
      </div>
      
      <!-- Quick Actions -->
      <div v-if="localData.imageUrl" class="quick-actions">
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
    <Handle type="source" :position="Position.Right" class="node-handle source" />
  </div>
</template>

<script setup>
import { ref, watch, inject } from 'vue'
import { Handle, Position, useVueFlow } from '@vue-flow/core'

const props = defineProps({
  id: String,
  data: Object
})

const { updateNodeData, removeNodes } = useVueFlow()
const addConnectedNode = inject('addConnectedNode', null)

const fileInput = ref(null)
const imageUrlInput = ref('')

const localData = ref({
  imageUrl: props.data.imageUrl || null,
  imageData: props.data.imageData || null
})

watch(() => props.data, (newData) => {
  localData.value = {
    imageUrl: newData.imageUrl || null,
    imageData: newData.imageData || null
  }
}, { deep: true })

const triggerUpload = () => fileInput.value?.click()

const handleFileSelect = (e) => {
  const file = e.target.files?.[0]
  if (file) processFile(file)
}

const handleDrop = (e) => {
  const file = e.dataTransfer.files?.[0]
  if (file && file.type.startsWith('image/')) processFile(file)
}

const processFile = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    // Store full data URL in both fields for consistency
    localData.value.imageUrl = e.target.result
    localData.value.imageData = e.target.result  // Full data URL, not just base64
    updateData()
  }
  reader.readAsDataURL(file)
}

const loadFromUrl = () => {
  if (imageUrlInput.value) {
    localData.value.imageUrl = imageUrlInput.value
    localData.value.imageData = null
    updateData()
    imageUrlInput.value = ''
  }
}

const removeImage = () => {
  localData.value.imageUrl = null
  localData.value.imageData = null
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
  border-color: rgba(249, 115, 22, 0.4);
  box-shadow: 0 12px 40px rgba(249, 115, 22, 0.15);
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
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.25), rgba(249, 115, 22, 0.1));
  border-radius: 10px;
  color: #FB923C;
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

.image-preview {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 16px;
  background: rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  max-height: 240px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.image-preview img {
  max-width: 100%;
  max-height: 240px;
  display: block;
  border-radius: 10px;
  object-fit: contain;
}

.remove-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
}

.remove-btn:hover {
  background: #EF4444;
  border-color: #EF4444;
}

.remove-btn svg {
  width: 14px;
  height: 14px;
}

.upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 24px;
  background: rgba(255, 255, 255, 0.03);
  border: 2px dashed rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 16px;
}

.upload-area:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(249, 115, 22, 0.4);
}

.upload-area svg {
  width: 40px;
  height: 40px;
  color: rgba(255, 255, 255, 0.2);
}

.upload-text {
  font-size: 0.75rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.4);
  text-align: center;
}

.url-input-wrapper {
  display: flex;
  gap: 8px;
}

.url-input {
  flex: 1;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: #fff;
  font-size: 0.8125rem;
  transition: all 0.2s ease;
}

.url-input:focus {
  outline: none;
  border-color: rgba(249, 115, 22, 0.5);
  background: rgba(255, 255, 255, 0.08);
}

.url-input::placeholder {
  color: #6B7280;
}

.url-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(249, 115, 22, 0.1);
  border: 1px solid rgba(249, 115, 22, 0.2);
  border-radius: 10px;
  color: #FB923C;
  cursor: pointer;
  transition: all 0.2s ease;
}

.url-btn:hover:not(:disabled) {
  background: rgba(249, 115, 22, 0.2);
  border-color: #F97316;
}

.url-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.url-btn svg {
  width: 16px;
  height: 16px;
}

.node-handle {
  width: 10px !important;
  height: 10px !important;
  background: #1A1A1A !important;
  border: 2px solid #F97316 !important;
  transition: all 0.2s ease;
}

.node-handle:hover {
  transform: scale(1.3);
  background: #F97316 !important;
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
  background: rgba(249, 115, 22, 0.15);
  border-color: #F97316;
  color: #F97316;
  transform: translateY(-2px);
}

.quick-action-btn svg {
  width: 16px;
  height: 16px;
}
</style>