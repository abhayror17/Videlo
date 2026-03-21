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
        <div class="node-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>
        </div>
      </div>
      <span class="node-title">{{ $t('workflow.textToSpeech') }}</span>
      <div v-if="isProcessing" class="node-spinner"></div>
      <div v-else-if="localData.resultUrl" class="node-status success"></div>
    </div>
    <div class="node-body">
      <div class="form-row">
        <label>{{ $t('settings.model') }}</label>
        <select v-model="localData.model" @change="onModelChange" class="form-select">
          <option value="Kokoro">Kokoro</option>
          <option value="Chatterbox">Chatterbox</option>
          <option value="Qwen3_TTS_12Hz_1_7B_CustomVoice">Qwen3 TTS</option>
          <option value="Qwen3_TTS_12Hz_1_7B_Base">Qwen3 Voice Clone</option>
          <option value="Qwen3_TTS_12Hz_1_7B_VoiceDesign">Qwen3 Voice Design</option>
        </select>
      </div>
      
      <!-- Language Selection -->
      <div class="form-row">
        <label>{{ $t('settings.language') }}</label>
        <select v-model="localData.lang" @change="onLangChange" class="form-select">
          <option v-for="lang in availableLanguages" :key="lang.code" :value="lang.code">
            {{ lang.name }}
          </option>
        </select>
      </div>
      
      <!-- Voice Selection (for custom_voice mode) -->
      <div v-if="localData.model !== 'Qwen3_TTS_12Hz_1_7B_VoiceDesign'" class="form-row">
        <label>{{ $t('settings.voice') }}</label>
        <select v-model="localData.voice" @change="updateData" class="form-select">
          <option v-for="voice in availableVoices" :key="voice.id" :value="voice.id">
            {{ voice.name }}
          </option>
        </select>
      </div>
      
      <!-- Voice Design Instructions (for voice_design mode) -->
      <div v-if="localData.model === 'Qwen3_TTS_12Hz_1_7B_VoiceDesign'" class="form-row">
        <label>{{ $t('settings.voiceDesign') }}</label>
        <textarea 
          v-model="localData.instruct" 
          @change="updateData" 
          class="form-textarea"
          :placeholder="$t('settings.voiceDesignPlaceholder')"
          rows="2"
        ></textarea>
      </div>
      
      <div class="form-row">
        <label>{{ $t('settings.speed') }}</label>
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

// Voice definitions per model and language
const VOICES = {
  Kokoro: {
    'en-us': [
      { id: 'af_sky', name: 'Sky (Female)' },
      { id: 'af_bella', name: 'Bella (Female)' },
      { id: 'af_nicole', name: 'Nicole (Female)' },
      { id: 'af_sarah', name: 'Sarah (Female)' },
      { id: 'af_rose', name: 'Rose (Female)' },
      { id: 'am_michael', name: 'Michael (Male)' },
      { id: 'am_adam', name: 'Adam (Male)' },
      { id: 'am_eric', name: 'Eric (Male)' }
    ],
    'en-gb': [
      { id: 'bf_emma', name: 'Emma (Female)' },
      { id: 'bf_isabella', name: 'Isabella (Female)' },
      { id: 'bm_george', name: 'George (Male)' },
      { id: 'bm_lewis', name: 'Lewis (Male)' }
    ],
    'es': [
      { id: 'ef_dora', name: 'Dora (Female)' },
      { id: 'em_alex', name: 'Alex (Male)' }
    ],
    'fr-fr': [
      { id: 'ff_sihane', name: 'Sihane (Female)' }
    ],
    'hi': [
      { id: 'hf_alpha', name: 'Alpha (Female)' },
      { id: 'hf_beta', name: 'Beta (Female)' },
      { id: 'hm_omega', name: 'Omega (Male)' }
    ],
    'it': [
      { id: 'if_sara', name: 'Sara (Female)' },
      { id: 'im_nicola', name: 'Nicola (Male)' }
    ],
    'pt-br': [
      { id: 'pf_dora', name: 'Dora (Female)' },
      { id: 'pm_alex', name: 'Alex (Male)' }
    ]
  },
  Chatterbox: {
    'en': [{ id: 'default', name: 'Default' }],
    'zh': [{ id: 'default', name: 'Default' }],
    'ja': [{ id: 'default', name: 'Default' }],
    'ko': [{ id: 'default', name: 'Default' }],
    'de': [{ id: 'default', name: 'Default' }],
    'fr': [{ id: 'default', name: 'Default' }],
    'es': [{ id: 'default', name: 'Default' }],
    'it': [{ id: 'default', name: 'Default' }],
    'pt': [{ id: 'default', name: 'Default' }],
    'ru': [{ id: 'default', name: 'Default' }],
    'ar': [{ id: 'default', name: 'Default' }],
    'hi': [{ id: 'default', name: 'Default' }]
  },
  Qwen3_TTS_12Hz_1_7B_CustomVoice: {
    'English': [
      { id: 'Vivian', name: 'Vivian (Female)' },
      { id: 'Serena', name: 'Serena (Female)' },
      { id: 'Dylan', name: 'Dylan (Male)' },
      { id: 'Eric', name: 'Eric (Male)' },
      { id: 'Aiden', name: 'Aiden (Male)' },
      { id: 'Ryan', name: 'Ryan (Male)' }
    ],
    'Chinese': [
      { id: 'Vivian', name: 'Vivian (Female)' },
      { id: 'Uncle_Fu', name: 'Uncle Fu (Male)' }
    ],
    'Japanese': [
      { id: 'Ono_Anna', name: 'Anna (Female)' },
      { id: 'Ryan', name: 'Ryan (Male)' }
    ],
    'Korean': [
      { id: 'Sohee', name: 'Sohee (Female)' },
      { id: 'Ryan', name: 'Ryan (Male)' }
    ]
  },
  Qwen3_TTS_12Hz_1_7B_Base: {
    'English': [{ id: 'default', name: 'Clone from Audio' }],
    'Chinese': [{ id: 'default', name: 'Clone from Audio' }],
    'Japanese': [{ id: 'default', name: 'Clone from Audio' }],
    'Korean': [{ id: 'default', name: 'Clone from Audio' }]
  },
  Qwen3_TTS_12Hz_1_7B_VoiceDesign: {
    'English': [{ id: 'designed', name: 'AI Designed Voice' }],
    'Chinese': [{ id: 'designed', name: 'AI Designed Voice' }],
    'Japanese': [{ id: 'designed', name: 'AI Designed Voice' }],
    'Korean': [{ id: 'designed', name: 'AI Designed Voice' }]
  }
}

const LANGUAGES = {
  Kokoro: [
    { code: 'en-us', name: 'English (US)' },
    { code: 'en-gb', name: 'English (UK)' },
    { code: 'es', name: 'Spanish' },
    { code: 'fr-fr', name: 'French' },
    { code: 'hi', name: 'Hindi' },
    { code: 'it', name: 'Italian' },
    { code: 'pt-br', name: 'Portuguese (BR)' }
  ],
  Chatterbox: [
    { code: 'en', name: 'English' },
    { code: 'zh', name: 'Chinese' },
    { code: 'ja', name: 'Japanese' },
    { code: 'ko', name: 'Korean' },
    { code: 'de', name: 'German' },
    { code: 'fr', name: 'French' },
    { code: 'es', name: 'Spanish' },
    { code: 'it', name: 'Italian' },
    { code: 'pt', name: 'Portuguese' },
    { code: 'ru', name: 'Russian' },
    { code: 'ar', name: 'Arabic' },
    { code: 'hi', name: 'Hindi' }
  ],
  Qwen3_TTS_12Hz_1_7B_CustomVoice: [
    { code: 'English', name: 'English' },
    { code: 'Chinese', name: 'Chinese' },
    { code: 'Japanese', name: 'Japanese' },
    { code: 'Korean', name: 'Korean' },
    { code: 'German', name: 'German' },
    { code: 'French', name: 'French' },
    { code: 'Spanish', name: 'Spanish' },
    { code: 'Portuguese', name: 'Portuguese' },
    { code: 'Italian', name: 'Italian' },
    { code: 'Russian', name: 'Russian' }
  ],
  Qwen3_TTS_12Hz_1_7B_Base: [
    { code: 'English', name: 'English' },
    { code: 'Chinese', name: 'Chinese' },
    { code: 'Japanese', name: 'Japanese' },
    { code: 'Korean', name: 'Korean' },
    { code: 'German', name: 'German' },
    { code: 'French', name: 'French' },
    { code: 'Spanish', name: 'Spanish' },
    { code: 'Portuguese', name: 'Portuguese' },
    { code: 'Italian', name: 'Italian' },
    { code: 'Russian', name: 'Russian' }
  ],
  Qwen3_TTS_12Hz_1_7B_VoiceDesign: [
    { code: 'English', name: 'English' },
    { code: 'Chinese', name: 'Chinese' },
    { code: 'Japanese', name: 'Japanese' },
    { code: 'Korean', name: 'Korean' },
    { code: 'German', name: 'German' },
    { code: 'French', name: 'French' },
    { code: 'Spanish', name: 'Spanish' },
    { code: 'Portuguese', name: 'Portuguese' },
    { code: 'Italian', name: 'Italian' },
    { code: 'Russian', name: 'Russian' }
  ]
}

const localData = ref({
  model: props.data.model || 'Kokoro',
  voice: props.data.voice || 'af_sky',
  lang: props.data.lang || 'en-us',
  speed: props.data.speed || 1,
  instruct: props.data.instruct || '',
  resultUrl: props.data.resultUrl || null,
  status: props.data.status || 'idle'
})

watch(() => props.data, (newData) => {
  localData.value = { ...localData.value, ...newData }
}, { deep: true })

const isProcessing = computed(() => localData.value.status === 'processing')

const availableLanguages = computed(() => {
  return LANGUAGES[localData.value.model] || LANGUAGES['Kokoro']
})

const availableVoices = computed(() => {
  const modelVoices = VOICES[localData.value.model]
  if (!modelVoices) return VOICES['Kokoro']['en-us']
  return modelVoices[localData.value.lang] || Object.values(modelVoices)[0] || []
})

const onModelChange = () => {
  // Reset to first available language for the new model
  const langs = LANGUAGES[localData.value.model]
  if (langs && langs.length > 0) {
    localData.value.lang = langs[0].code
  }
  // Reset to first available voice
  const voices = VOICES[localData.value.model]
  if (voices) {
    const langVoices = voices[localData.value.lang] || Object.values(voices)[0]
    if (langVoices && langVoices.length > 0) {
      localData.value.voice = langVoices[0].id
    }
  }
  updateData()
}

const onLangChange = () => {
  // Reset to first available voice for the new language
  const voices = VOICES[localData.value.model]
  if (voices) {
    const langVoices = voices[localData.value.lang]
    if (langVoices && langVoices.length > 0) {
      localData.value.voice = langVoices[0].id
    }
  }
  updateData()
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
  min-width: 260px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.workflow-node:hover {
  border-color: rgba(139, 92, 246, 0.4);
  box-shadow: 0 12px 40px rgba(139, 92, 246, 0.15);
  transform: translateY(-2px);
}

.workflow-node.processing {
  border-color: #8B5CF6;
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
  transform: scale(1.05);
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
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.25), rgba(139, 92, 246, 0.1));
  border-radius: 10px;
  color: #A78BFA;
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

.form-select {
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

.form-select:focus {
  outline: none;
  border-color: rgba(139, 92, 246, 0.6);
  background: rgba(0, 0, 0, 0.5);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.form-textarea {
  width: 100%;
  padding: 10px 12px;
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 10px;
  color: #fff;
  font-size: 0.8125rem;
  font-family: inherit;
  resize: vertical;
  min-height: 60px;
  transition: all 0.2s ease;
}

.form-textarea:focus {
  outline: none;
  border-color: rgba(139, 92, 246, 0.6);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.form-textarea::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.slider-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.form-slider {
  flex: 1;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
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
  box-shadow: 0 0 10px rgba(139, 92, 246, 0.3);
}

.slider-value {
  min-width: 36px;
  font-size: 0.75rem;
  font-weight: 700;
  color: #A78BFA;
  text-align: right;
}

.result-preview.audio {
  margin-top: 16px;
  padding: 16px;
  background: rgba(139, 92, 246, 0.05);
  border: 1px solid rgba(139, 92, 246, 0.1);
  border-radius: 12px;
  text-align: center;
}

.audio-visualizer {
  margin-bottom: 16px;
}

.audio-bars {
  display: inline-flex;
  align-items: flex-end;
  gap: 3px;
  height: 32px;
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
  50% { transform: scaleY(0.4); }
}

.result-preview.audio audio {
  width: 100%;
  height: 40px;
  border-radius: 10px;
  filter: invert(1) hue-rotate(180deg);
}

.node-handle {
  width: 10px !important;
  height: 10px !important;
  background: #1A1A1A !important;
  border: 2px solid #8B5CF6 !important;
  transition: all 0.2s ease;
}

.node-handle:hover {
  transform: scale(1.3);
  background: #8B5CF6 !important;
}
</style>