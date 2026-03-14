<template>
  <div class="workflow-node output-node" :class="{ 'has-result': hasResult, processing: status === 'processing' }">
    <button class="node-delete-btn" @click.stop="deleteNode" title="Delete node">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"/>
        <line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    </button>
    <div class="node-header">
      <div class="node-icon-wrapper">
        <div class="node-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
        </div>
      </div>
      <span class="node-title">{{ $t('workflow.output') }}</span>
      <div v-if="status === 'processing'" class="node-spinner"></div>
      <div v-else-if="hasResult" class="node-status success"></div>
    </div>
    <div class="node-body">
      <!-- Processing State -->
      <div v-if="status === 'processing'" class="state processing-state">
        <div class="processing-animation">
          <div class="ring r1"></div>
          <div class="ring r2"></div>
          <div class="ring r3"></div>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="5 3 19 12 5 21 5 3"/>
          </svg>
        </div>
        <span>{{ $t('workflow.processing') }}</span>
      </div>
      
      <!-- Empty State -->
      <div v-else-if="!hasResult" class="state empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="3" y="3" width="18" height="18" rx="2"/>
          <circle cx="8.5" cy="8.5" r="1.5"/>
          <path d="M21 15l-5-5L5 21"/>
        </svg>
        <span>{{ $t('workflow.connectInput') }}</span>
      </div>
      
      <!-- Image Result -->
      <div v-else-if="isImage" class="result image-result">
        <img :src="localData.resultUrl" alt="Output" @load="onMediaLoad" />
        <div class="result-overlay">
          <span class="result-type">IMAGE</span>
        </div>
        <div class="result-actions">
          <button class="action-btn" @click="openInNewTab" title="Open in new tab">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
              <polyline points="15 3 21 3 21 9"/>
              <line x1="10" y1="14" x2="21" y2="3"/>
            </svg>
          </button>
          <a :href="localData.resultUrl" :download="downloadFilename" class="action-btn" title="Download">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
          </a>
        </div>
      </div>
      
      <!-- Video Result -->
      <div v-else-if="isVideo" class="result video-result">
        <video :src="localData.resultUrl" controls muted loop @loadeddata="onMediaLoad"></video>
        <div class="result-overlay">
          <span class="result-type">VIDEO</span>
        </div>
      </div>
      
      <!-- Audio Result -->
      <div v-else-if="isAudio" class="result audio-result">
        <div class="audio-visualizer">
          <span class="audio-bars">
            <i></i><i></i><i></i><i></i><i></i>
          </span>
        </div>
        <audio :src="localData.resultUrl" controls @loadeddata="onMediaLoad"></audio>
      </div>
      
      <!-- Text Result -->
      <div v-else-if="localData.text" class="result text-result">
        <div class="text-header">
          <span class="text-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
          </span>
          <span class="text-label">{{ $t('workflow.extractedText') }}</span>
        </div>
        <div class="text-content">{{ localData.text }}</div>
        <button class="copy-btn" @click="copyText">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
          </svg>
          {{ copied ? 'Copied!' : $t('workflow.copy') }}
        </button>
      </div>
    </div>
    <Handle type="target" :position="Position.Left" class="node-handle target" />
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { Handle, Position, useVueFlow } from '@vue-flow/core'

const props = defineProps({
  id: String,
  data: Object
})

const { removeNodes } = useVueFlow()

const emit = defineEmits(['update:data'])

const localData = ref({
  resultUrl: props.data?.resultUrl || null,
  text: props.data?.text || null,
  status: props.data?.status || null
})

const copied = ref(false)

watch(() => props.data, (newData) => {
  if (newData) {
    localData.value = {
      resultUrl: newData.resultUrl || localData.value.resultUrl,
      text: newData.text || localData.value.text,
      status: newData.status || localData.value.status
    }
  }
}, { deep: true, immediate: true })

const status = computed(() => localData.value.status)
const hasResult = computed(() => localData.value.resultUrl || localData.value.text)

const deleteNode = () => {
  removeNodes([props.id])
}

const isImage = computed(() => {
  if (!localData.value.resultUrl) return false
  const url = localData.value.resultUrl.toLowerCase()
  return url.includes('.png') || url.includes('.jpg') || url.includes('.jpeg') || url.includes('.webp') || url.includes('.gif')
})

const isVideo = computed(() => {
  if (!localData.value.resultUrl) return false
  const url = localData.value.resultUrl.toLowerCase()
  return url.includes('.mp4') || url.includes('.webm') || url.includes('.mov')
})

const isAudio = computed(() => {
  if (!localData.value.resultUrl) return false
  const url = localData.value.resultUrl.toLowerCase()
  return url.includes('.flac') || url.includes('.mp3') || url.includes('.wav') || url.includes('.ogg') || url.includes('.m4a')
})

const downloadFilename = computed(() => {
  let ext = '.png'
  if (isVideo.value) ext = '.mp4'
  else if (isAudio.value) ext = '.flac'
  return `workflow-output${ext}`
})

const onMediaLoad = () => {
  localData.value.status = 'completed'
}

const openInNewTab = () => {
  if (localData.value.resultUrl) {
    window.open(localData.value.resultUrl, '_blank')
  }
}

const copyText = async () => {
  if (localData.value.text) {
    await navigator.clipboard.writeText(localData.value.text)
    copied.value = true
    setTimeout(() => copied.value = false, 2000)
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
  border-color: rgba(245, 158, 11, 0.4);
  box-shadow: 0 12px 40px rgba(245, 158, 11, 0.15);
  transform: translateY(-2px);
}

.workflow-node.has-result {
  border-color: rgba(245, 158, 11, 0.5);
}

.workflow-node.processing {
  border-color: #F59E0B;
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
  background: rgba(239, 68, 68, 0.9);
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
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.25), rgba(245, 158, 11, 0.1));
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
  border: 2px solid rgba(245, 158, 11, 0.2);
  border-top-color: #F59E0B;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.node-body {
  padding: 16px;
  min-height: 160px;
}

/* States */
.state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 140px;
  gap: 14px;
  color: rgba(255, 255, 255, 0.3);
}

.state svg {
  width: 48px;
  height: 48px;
  opacity: 0.5;
}

.state span {
  font-size: 0.8125rem;
  font-weight: 500;
}

/* Processing Animation */
.processing-state {
  color: #FBBF24;
}

.processing-animation {
  position: relative;
  width: 60px;
  height: 60px;
}

.processing-animation svg {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 24px;
  height: 24px;
  color: #F59E0B;
  opacity: 1;
}

.processing-animation .ring {
  position: absolute;
  inset: 0;
  border: 2px solid transparent;
  border-top-color: rgba(245, 158, 11, 0.4);
  border-radius: 50%;
  animation: ringPulse 1.5s ease-in-out infinite;
}

.processing-animation .r1 { animation-delay: 0s; }
.processing-animation .r2 { animation-delay: 0.3s; }
.processing-animation .r3 { animation-delay: 0.6s; }

@keyframes ringPulse {
  0% { transform: scale(0.8); opacity: 1; }
  100% { transform: scale(1.4); opacity: 0; }
}

/* Results */
.result {
  border-radius: 12px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.image-result,
.video-result {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  max-height: 300px;
}

.image-result img,
.video-result video {
  max-width: 100%;
  max-height: 300px;
  display: block;
  object-fit: contain;
}

.result-overlay {
  position: absolute;
  top: 8px;
  left: 8px;
}

.result-type {
  font-size: 0.625rem;
  padding: 4px 10px;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  border-radius: 6px;
  color: #fff;
  font-weight: 700;
  letter-spacing: 0.05em;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.result-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  gap: 6px;
}

.action-btn {
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  border-radius: 10px;
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.action-btn:hover {
  background: #F59E0B;
  color: #000;
  border-color: #F59E0B;
}

.action-btn svg {
  width: 18px;
  height: 18px;
}

/* Audio Result */
.audio-result {
  padding: 24px;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(245, 158, 11, 0.05));
  text-align: center;
}

.audio-visualizer {
  margin-bottom: 20px;
}

.audio-bars {
  display: inline-flex;
  align-items: flex-end;
  gap: 4px;
  height: 40px;
}

.audio-bars i {
  width: 6px;
  background: linear-gradient(to top, #F59E0B, #FBBF24);
  border-radius: 3px;
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

.audio-result audio {
  width: 100%;
  height: 40px;
  border-radius: 10px;
}

/* Text Result */
.text-result {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 16px;
}

.text-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.text-icon {
  font-size: 0.875rem;
}

.text-label {
  font-size: 0.625rem;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.4);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.text-content {
  font-size: 0.8125rem;
  color: #fff;
  line-height: 1.6;
  max-height: 150px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
  opacity: 0.9;
}

.copy-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.copy-btn:hover {
  background: rgba(245, 158, 11, 0.1);
  border-color: rgba(245, 158, 11, 0.4);
  color: #FBBF24;
}

.copy-btn svg {
  width: 14px;
  height: 14px;
}

/* Handle */
.node-handle {
  width: 10px !important;
  height: 10px !important;
  background: #1A1A1A !important;
  border: 2px solid #F59E0B !important;
  transition: all 0.2s ease;
}

.node-handle:hover {
  transform: scale(1.3);
  background: #F59E0B !important;
}
</style>
