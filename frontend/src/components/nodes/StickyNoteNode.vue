<template>
  <div 
    class="sticky-note-node" 
    :class="{ 
      editing: isEditing, 
      'color-yellow': localData.color === 'yellow', 
      'color-blue': localData.color === 'blue', 
      'color-green': localData.color === 'green', 
      'color-pink': localData.color === 'pink', 
      'color-purple': localData.color === 'purple' 
    }"
    :style="noteStyle"
  >
    <button class="note-delete-btn" @click.stop="deleteNode" title="Delete note">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"/>
        <line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    </button>
    
    <div class="note-header">
      <div class="note-drag-handle">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="9" cy="12" r="1"/>
          <circle cx="9" cy="5" r="1"/>
          <circle cx="9" cy="19" r="1"/>
          <circle cx="15" cy="12" r="1"/>
          <circle cx="15" cy="5" r="1"/>
          <circle cx="15" cy="19" r="1"/>
        </svg>
      </div>
      <div class="note-color-picker">
        <button 
          v-for="color in colors" 
          :key="color.id"
          class="color-dot"
          :class="{ active: localData.color === color.id, [color.id]: true }"
          @click.stop="setColor(color.id)"
          :title="color.label"
        />
      </div>
    </div>
    
    <div class="note-content" @dblclick="startEditing">
      <textarea
        v-if="isEditing"
        v-model="localData.text"
        @blur="stopEditing"
        @keydown.enter.prevent="stopEditing"
        @keydown.esc="cancelEditing"
        class="note-textarea"
        :placeholder="$t('workflow.stickyNotePlaceholder')"
        ref="textareaRef"
        :style="{ minHeight: (localData.height || 100) - 80 + 'px' }"
      ></textarea>
      <div v-else class="note-text-display" :class="{ empty: !localData.text }">
        {{ displayText }}
      </div>
    </div>
    
    <div class="note-footer">
      <span class="note-hint">{{ isEditing ? $t('workflow.pressEnterToSave') : $t('workflow.doubleClickToEdit') }}</span>
      <span v-if="localData.text" class="char-count">{{ localData.text.length }}</span>
    </div>

    <!-- Resize Handle -->
    <div 
      class="resize-handle" 
      @mousedown.stop.prevent="startResize"
      @touchstart.stop.prevent="startResize"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 21L12 21M21 21L21 12M21 21L14 14"/>
      </svg>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, nextTick } from 'vue'
import { useVueFlow } from '@vue-flow/core'

const props = defineProps({
  id: String,
  data: Object
})

const { updateNodeData, removeNodes } = useVueFlow()

const colors = [
  { id: 'yellow', label: 'Yellow' },
  { id: 'blue', label: 'Blue' },
  { id: 'green', label: 'Green' },
  { id: 'pink', label: 'Pink' },
  { id: 'purple', label: 'Purple' }
]

const localData = ref({
  text: props.data.text || '',
  color: props.data.color || 'yellow',
  width: props.data.width || 220,
  height: props.data.height || 140
})

const isEditing = ref(false)
const textareaRef = ref(null)
const originalText = ref('')
const isResizing = ref(false)
const startPos = ref({ x: 0, y: 0 })
const startSize = ref({ width: 0, height: 0 })

watch(() => props.data, (newData) => {
  if (newData) {
    if (newData.text !== undefined) localData.value.text = newData.text
    if (newData.color !== undefined) localData.value.color = newData.color
    if (newData.width !== undefined) localData.value.width = newData.width
    if (newData.height !== undefined) localData.value.height = newData.height
  }
}, { immediate: true, deep: true })

const noteStyle = computed(() => ({
  width: `${localData.value.width}px`,
  minHeight: `${localData.value.height}px`
}))

const displayText = computed(() => {
  return localData.value.text || 'Double-click to add note...'
})

const updateData = () => {
  updateNodeData(props.id, { 
    text: localData.value.text,
    color: localData.value.color,
    width: localData.value.width,
    height: localData.value.height
  })
}

const setColor = (color) => {
  localData.value.color = color
  updateData()
}

const startEditing = () => {
  originalText.value = localData.value.text
  isEditing.value = true
  nextTick(() => {
    textareaRef.value?.focus()
    textareaRef.value?.select()
  })
}

const stopEditing = () => {
  isEditing.value = false
  updateData()
}

const cancelEditing = () => {
  localData.value.text = originalText.value
  isEditing.value = false
}

const deleteNode = () => {
  removeNodes([props.id])
}

// Resize functionality
const startResize = (e) => {
  isResizing.value = true
  
  const clientX = e.type === 'touchstart' ? e.touches[0].clientX : e.clientX
  const clientY = e.type === 'touchstart' ? e.touches[0].clientY : e.clientY
  
  startPos.value = { x: clientX, y: clientY }
  startSize.value = { 
    width: localData.value.width, 
    height: localData.value.height 
  }

  document.addEventListener('mousemove', onResize)
  document.addEventListener('mouseup', stopResize)
  document.addEventListener('touchmove', onResize)
  document.addEventListener('touchend', stopResize)
}

const onResize = (e) => {
  if (!isResizing.value) return
  
  const clientX = e.type === 'touchmove' ? e.touches[0].clientX : e.clientX
  const clientY = e.type === 'touchmove' ? e.touches[0].clientY : e.clientY
  
  const deltaX = clientX - startPos.value.x
  const deltaY = clientY - startPos.value.y
  
  // Minimum and maximum sizes
  const minWidth = 180
  const maxWidth = 400
  const minHeight = 100
  const maxHeight = 400
  
  localData.value.width = Math.min(maxWidth, Math.max(minWidth, startSize.value.width + deltaX))
  localData.value.height = Math.min(maxHeight, Math.max(minHeight, startSize.value.height + deltaY))
}

const stopResize = () => {
  if (isResizing.value) {
    isResizing.value = false
    updateData()
  }
  
  document.removeEventListener('mousemove', onResize)
  document.removeEventListener('mouseup', stopResize)
  document.removeEventListener('touchmove', onResize)
  document.removeEventListener('touchend', stopResize)
}
</script>

<style scoped>
.sticky-note-node {
  position: relative;
  min-width: 180px;
  border-radius: 12px;
  padding: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15), 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
  cursor: grab;
  user-select: none;
  box-sizing: border-box;
}

.sticky-note-node:active {
  cursor: grabbing;
}

.sticky-note-node:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2), 0 4px 8px rgba(0, 0, 0, 0.15);
}

/* Color variants */
.color-yellow {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border: 1px solid #fbbf24;
}

.color-blue {
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  border: 1px solid #60a5fa;
}

.color-green {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  border: 1px solid #34d399;
}

.color-pink {
  background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%);
  border: 1px solid #f472b6;
}

.color-purple {
  background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%);
  border: 1px solid #a78bfa;
}

.note-delete-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.1);
  border: none;
  border-radius: 50%;
  color: #666;
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s ease;
  z-index: 10;
}

.sticky-note-node:hover .note-delete-btn {
  opacity: 1;
}

.note-delete-btn:hover {
  background: #ef4444;
  color: white;
}

.note-delete-btn svg {
  width: 12px;
  height: 12px;
}

.note-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  padding-right: 28px;
}

.note-drag-handle {
  color: rgba(0, 0, 0, 0.3);
  cursor: grab;
}

.note-drag-handle svg {
  width: 16px;
  height: 16px;
}

.note-drag-handle:active {
  cursor: grabbing;
}

.note-color-picker {
  display: flex;
  gap: 4px;
}

.color-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.color-dot:hover {
  transform: scale(1.2);
}

.color-dot.active {
  border-color: rgba(0, 0, 0, 0.4);
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.5);
}

.color-dot.yellow { background: #fbbf24; }
.color-dot.blue { background: #60a5fa; }
.color-dot.green { background: #34d399; }
.color-dot.pink { background: #f472b6; }
.color-dot.purple { background: #a78bfa; }

.note-content {
  min-height: 40px;
  flex: 1;
}

.note-text-display {
  font-size: 0.875rem;
  line-height: 1.5;
  color: #1f2937;
  white-space: pre-wrap;
  word-break: break-word;
  padding: 4px;
  border-radius: 6px;
  transition: background 0.2s ease;
}

.note-text-display:hover {
  background: rgba(0, 0, 0, 0.03);
}

.note-text-display.empty {
  color: #9ca3af;
  font-style: italic;
}

.note-textarea {
  width: 100%;
  padding: 4px;
  background: rgba(255, 255, 255, 0.8);
  border: 2px solid rgba(0, 0, 0, 0.2);
  border-radius: 6px;
  font-size: 0.875rem;
  line-height: 1.5;
  color: #1f2937;
  resize: none;
  font-family: inherit;
  outline: none;
  box-sizing: border-box;
}

.note-textarea:focus {
  border-color: rgba(0, 0, 0, 0.4);
  background: white;
}

.note-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.note-hint {
  font-size: 0.625rem;
  color: rgba(0, 0, 0, 0.4);
  font-weight: 500;
}

.char-count {
  font-size: 0.625rem;
  color: rgba(0, 0, 0, 0.4);
  font-weight: 600;
}

/* Resize Handle */
.resize-handle {
  position: absolute;
  bottom: 4px;
  right: 4px;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: se-resize;
  opacity: 0;
  transition: opacity 0.2s ease;
  color: rgba(0, 0, 0, 0.3);
}

.sticky-note-node:hover .resize-handle {
  opacity: 1;
}

.resize-handle:hover {
  color: rgba(0, 0, 0, 0.6);
}

.resize-handle svg {
  width: 14px;
  height: 14px;
}
</style>