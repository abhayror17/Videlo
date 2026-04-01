<template>
  <div class="workflow-node video-replace-node" :class="{ processing: isProcessing }">
    <button class="node-delete-btn" @click.stop="deleteNode" title="Delete node">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"/>
        <line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    </button>
    <div class="node-header">
      <div class="node-icon-wrapper">
        <div class="node-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
        </div>
      </div>
      <span class="node-title">{{ $t('workflow.videoReplace') }}</span>
      <div v-if="isProcessing" class="node-spinner"></div>
      <div v-else-if="localData.resultUrl" class="node-status success"></div>
    </div>
    <div class="node-body">
      <!-- Video Input -->
      <div class="form-row">
        <label>{{ $t('workflow.sourceVideo') }}</label>
        <div class="file-upload-area" @click="triggerVideoUpload" :class="{ 'has-file': localData.videoFile }">
          <input 
            type="file" 
            ref="videoInput" 
            @change="onVideoSelect" 
            accept="video/*" 
            class="hidden-input"
          />
          <div v-if="!localData.videoFile && !localData.videoPreview" class="upload-placeholder">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="23 7 16 12 23 17 23 7"/>
              <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
            </svg>
            <span>{{ $t('workflow.clickToUploadVideo') }}</span>
          </div>
          <video 
            v-else-if="localData.videoPreview" 
            :src="localData.videoPreview" 
            class="preview-video"
            muted
            loop
          ></video>
          <div v-else class="file-name">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
            <span>{{ localData.videoFile?.name }}</span>
          </div>
        </div>
      </div>

      <!-- Character Image Input -->
      <div class="form-row">
        <label>{{ $t('workflow.characterImage') }}</label>
        <div class="file-upload-area image-upload" @click="triggerImageUpload" :class="{ 'has-file': localData.characterFile }">
          <input 
            type="file" 
            ref="imageInput" 
            @change="onImageSelect" 
            accept="image/*" 
            class="hidden-input"
          />
          <div v-if="!localData.characterFile && !localData.imagePreview" class="upload-placeholder">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <circle cx="8.5" cy="8.5" r="1.5"/>
              <polyline points="21 15 16 10 5 21"/>
            </svg>
            <span>{{ $t('workflow.clickToUploadImage') }}</span>
          </div>
          <img 
            v-else-if="localData.imagePreview" 
            :src="localData.imagePreview" 
            class="preview-image"
          />
          <div v-else class="file-name">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
            <span>{{ localData.characterFile?.name }}</span>
          </div>
        </div>
      </div>

      <!-- Optional Prompt -->
      <div class="form-row">
        <label>{{ $t('workflow.textPrompt') }} ({{ $t('workflow.optional') }})</label>
        <textarea 
          v-model="localData.prompt" 
          @input="updateData"
          class="form-textarea"
          rows="2"
          :placeholder="$t('workflow.videoReplacePromptPlaceholder')"
        ></textarea>
      </div>

      <!-- Steps -->
      <div class="form-row">
        <label>{{ $t('workflow.steps') }}</label>
        <select v-model.number="localData.steps" @change="updateData" class="form-select">
          <option :value="4">4 (Fast)</option>
          <option :value="8">8 (Balanced)</option>
          <option :value="16">16 (Quality)</option>
          <option :value="32">32 (High Quality)</option>
        </select>
      </div>
      
      <!-- Result Preview -->
      <div v-if="localData.resultUrl" class="result-preview">
        <video :src="localData.resultUrl" controls muted loop></video>
        <div class="result-badge">{{ $t('workflow.result') }}</div>
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

const videoInput = ref(null)
const imageInput = ref(null)

const localData = ref({
  prompt: props.data.prompt || '',
  steps: props.data.steps || 4,
  seed: props.data.seed || -1,
  videoFile: props.data.videoFile || null,
  characterFile: props.data.characterFile || null,
  videoPreview: props.data.videoPreview || null,
  imagePreview: props.data.imagePreview || null,
  resultUrl: props.data.resultUrl || null,
  status: props.data.status || 'idle'
})

watch(() => props.data, (newData) => {
  localData.value = { ...localData.value, ...newData }
}, { deep: true })

const isProcessing = computed(() => localData.value.status === 'processing')

const triggerVideoUpload = () => {
  videoInput.value?.click()
}

const triggerImageUpload = () => {
  imageInput.value?.click()
}

const onVideoSelect = (event) => {
  const file = event.target.files?.[0]
  if (file) {
    localData.value.videoFile = file
    localData.value.videoPreview = URL.createObjectURL(file)
    updateData()
  }
}

const onImageSelect = (event) => {
  const file = event.target.files?.[0]
  if (file) {
    localData.value.characterFile = file
    localData.value.imagePreview = URL.createObjectURL(file)
    updateData()
  }
}

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
  background: rgba(26, 26, 26, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  min-width: 280px;
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

.hidden-input {
  display: none;
}

.file-upload-area {
  width: 100%;
  min-height: 80px;
  background: rgba(0, 0, 0, 0.3);
  border: 2px dashed rgba(255, 255, 255, 0.15);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.file-upload-area:hover {
  border-color: rgba(168, 85, 247, 0.5);
  background: rgba(168, 85, 247, 0.05);
}

.file-upload-area.has-file {
  border-style: solid;
  border-color: rgba(168, 85, 247, 0.3);
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.4);
  padding: 16px;
  text-align: center;
}

.upload-placeholder svg {
  width: 24px;
  height: 24px;
}

.upload-placeholder span {
  font-size: 0.75rem;
}

.file-name {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.8125rem;
}

.file-name svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.file-name span {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.preview-video {
  max-width: 100%;
  max-height: 120px;
  object-fit: contain;
}

.preview-image {
  max-width: 100%;
  max-height: 120px;
  object-fit: contain;
}

.image-upload {
  min-height: 100px;
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
  border-color: rgba(168, 85, 247, 0.6);
  background: rgba(0, 0, 0, 0.5);
  box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.1);
}

.form-textarea::placeholder {
  color: var(--text-muted);
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

.result-preview video {
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
  background: rgba(168, 85, 247, 0.8);
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
</style>
