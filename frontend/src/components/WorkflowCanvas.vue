<template>
  <div class="workflow-canvas" @click="showSavedDropdown = false">
    <!-- Floating Header -->
    <header class="workflow-header">
      <div class="header-left">
        <router-link to="/" class="logo-link">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"/>
            <path d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72l1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
          </svg>
          <span>Videlo</span>
        </router-link>
        <span class="breadcrumb-sep">/</span>
        <span class="breadcrumb-current">{{ $t('nav.workflow') }}</span>
      </div>

      <div class="header-actions">
        <!-- Saved Workflows -->
        <div class="dropdown-wrapper" @click.stop>
          <button class="action-btn secondary" @click.stop="showSavedDropdown = !showSavedDropdown">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
            </svg>
            <span>{{ $t('workflow.myWorkflows') }}</span>
            <span v-if="savedWorkflows.length" class="badge">{{ savedWorkflows.length }}</span>
            <svg class="chevron" :class="{ rotated: showSavedDropdown }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </button>
          <Transition name="dropdown">
            <div v-if="showSavedDropdown" class="dropdown-panel">
              <div v-if="savedWorkflows.length === 0" class="dropdown-empty">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
                  <polyline points="13 2 13 9 20 9"/>
                </svg>
                <span>{{ $t('workflow.noSavedWorkflows') }}</span>
              </div>
              <div 
                v-for="wf in savedWorkflows" 
                :key="wf.id" 
                class="workflow-item"
                @click="loadWorkflow(wf.id)"
              >
                <div class="workflow-item-info">
                  <span class="workflow-item-name">{{ wf.name }}</span>
                  <span class="workflow-item-meta">{{ wf.node_count }} {{ $t('workflow.nodes') }}</span>
                </div>
                <button class="workflow-item-delete" @click.stop="deleteSavedWorkflow(wf.id, $event)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                  </svg>
                </button>
              </div>
            </div>
          </Transition>
        </div>

        <button class="action-btn" @click="showSaveModal = true" :disabled="nodes.length === 0">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
            <polyline points="17 21 17 13 7 13 7 21"/>
            <polyline points="7 3 7 10 15 10"/>
          </svg>
          <span>{{ $t('workflow.saveWorkflow') }}</span>
        </button>

        <button class="action-btn danger" @click="clearCanvas" :disabled="nodes.length === 0">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
          <span>{{ $t('workflow.clear') }}</span>
        </button>

        <button class="action-btn primary run" @click="executeGraph" :disabled="isExecuting || nodes.length === 0">
          <svg v-if="!isExecuting" viewBox="0 0 24 24" fill="currentColor">
            <polygon points="5 3 19 12 5 21 5 3"/>
          </svg>
          <div v-else class="spinner"></div>
          <span>{{ isExecuting ? $t('workflow.running') : $t('workflow.run') }}</span>
        </button>
      </div>
    </header>

    <!-- Main Layout -->
    <div class="workflow-layout">
      <!-- Canvas Area -->
      <main class="canvas-area">
        <div
          class="canvas-wrapper"
          @drop="onDrop"
          @dragover.prevent
          @click="closeContextMenu"
          @contextmenu.prevent="onCanvasContextMenu"
        >
          <VueFlow
            v-model:nodes="nodes"
            v-model:edges="edges"
            :node-types="nodeTypesMap"
            @connect="onConnect"
            @connect-end="onConnectEnd"
            @node-context-menu="onNodeContextMenu"
            :default-viewport="{ zoom: 1, x: 0, y: 0 }"
            :min-zoom="0.1"
            :max-zoom="4"
            :pan-on-drag="true"
            :select-nodes-on-drag="false"
            :delete-key-code="['Delete', 'Backspace']"
            fit-view-on-init
            class="vue-flow-instance"
            @viewport-change="onViewportChange"
          >
            <Background variant="dots" :gap="24" :size="2" pattern-color="rgba(255, 255, 255, 0.08)" />
          </VueFlow>
          
          <!-- Settings Button (BYOK) -->
          <button class="settings-btn" @click="showSettingsModal = true" title="Settings - Bring Your Own Key">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3"/>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
            </svg>
            <span v-if="hasCustomApiKey" class="settings-badge">✓</span>
          </button>
          
          <!-- Zoom Indicator -->
          <div class="zoom-indicator">
            <button class="zoom-btn" @click="zoomOut" title="Zoom Out">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
            </button>
            <span class="zoom-value">{{ zoomLevel }}%</span>
            <button class="zoom-btn" @click="zoomIn" title="Zoom In">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19"/>
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
            </button>
            <button class="zoom-btn" @click="resetZoom" title="Reset Zoom">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
                <path d="M3 3v5h5"/>
              </svg>
            </button>
          </div>

          <!-- Canvas Context Menu (Quick Add) -->
          <Teleport to="body">
            <div
              v-if="canvasContextMenu.show"
              class="canvas-context-menu"
              :style="{ left: canvasContextMenu.x + 'px', top: canvasContextMenu.y + 'px' }"
              @click.stop
            >
              <div class="context-menu-title">Add Node</div>
              <div class="context-menu-grid">
                <button 
                  v-for="nt in nodeTypes" 
                  :key="nt.type" 
                  class="context-node-btn"
                  :style="{ '--node-accent': nt.color }"
                  @click="addNodeAtPosition(nt.type, canvasContextMenu.x, canvasContextMenu.y)"
                >
                  <span class="context-node-icon">{{ nt.icon }}</span>
                  <span class="context-node-label">{{ nt.label }}</span>
                </button>
              </div>
            </div>
          </Teleport>

          <!-- Empty State -->
          <div v-if="nodes.length === 0" class="canvas-empty">
            <div class="empty-visual">
              <div class="empty-circles">
                <div class="empty-circle c1"></div>
                <div class="empty-circle c2"></div>
                <div class="empty-circle c3"></div>
              </div>
              <svg class="empty-illustration" viewBox="0 0 120 120" fill="none">
                <rect x="10" y="40" width="30" height="30" rx="6" stroke="currentColor" stroke-width="2"/>
                <rect x="80" y="40" width="30" height="30" rx="6" stroke="currentColor" stroke-width="2"/>
                <path d="M40 55h40" stroke="currentColor" stroke-width="2" stroke-dasharray="4 4"/>
                <circle cx="25" cy="55" r="4" fill="currentColor"/>
                <circle cx="95" cy="55" r="4" fill="currentColor"/>
              </svg>
            </div>
            <h3>WHY Settle for LESS?</h3>
            <p>Infinite Canvas with BYOK</p>
            <div class="empty-quick-add">
              <span>Quick start:</span>
              <button @click="addNode('textInput')" class="quick-add-btn">+ Text Input</button>
              <button @click="addNode('imageGen')" class="quick-add-btn">+ Image Gen</button>
              <button @click="addNode('img2video')" class="quick-add-btn">+ Image to Video</button>
            </div>
          </div>
        </div>

        <!-- Context Menu -->
        <Teleport to="body">
          <div
            v-if="contextMenu.show"
            class="context-menu"
            :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
            @click.stop
          >
            <button class="context-item" @click="duplicateNode(contextMenu.nodeId)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
              </svg>
              {{ $t('workflow.duplicateNode') }}
            </button>
            <div class="context-divider"></div>
            <button class="context-item danger" @click="deleteNode(contextMenu.nodeId)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3 6 5 6 21 6"/>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
              </svg>
              {{ $t('workflow.deleteNode') }}
            </button>
          </div>
        </Teleport>
      </main>
    </div>

    <!-- Execution Status Toast -->
    <Transition name="toast">
      <div v-if="executionStatus" class="status-toast" :class="executionStatus.type">
        <div class="toast-icon">
          <svg v-if="executionStatus.type === 'success'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          <svg v-else-if="executionStatus.type === 'error'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <circle cx="12" cy="12" r="10"/>
            <line x1="15" y1="9" x2="9" y2="15"/>
            <line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
          <div v-else class="toast-spinner"></div>
        </div>
        <div class="toast-content">
          <span class="toast-message">{{ executionStatus.message }}</span>
          <span v-if="executionStatus.progress" class="toast-progress">{{ executionStatus.progress }}%</span>
        </div>
        <div v-if="executionStatus.progress && executionStatus.type === 'info'" class="toast-bar">
          <div class="toast-bar-fill" :style="{ width: executionStatus.progress + '%' }"></div>
        </div>
      </div>
    </Transition>

    <!-- Save Modal -->
    <Transition name="modal">
      <div v-if="showSaveModal" class="modal-backdrop" @click.self="showSaveModal = false">
        <div class="modal-container">
          <div class="modal-header">
            <div class="modal-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
              </svg>
            </div>
            <h3>{{ $t('workflow.saveWorkflowTitle') }}</h3>
          </div>
          <div class="modal-body">
            <div class="form-field">
              <label>{{ $t('workflow.workflowName') }}</label>
              <input
                v-model="workflowName"
                type="text"
                :placeholder="$t('workflow.enterName')"
                @keyup.enter="saveWorkflow"
                ref="nameInput"
              />
            </div>
            <div class="workflow-stats">
              <div class="stat-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="3" width="7" height="7"/>
                  <rect x="14" y="3" width="7" height="7"/>
                  <rect x="3" y="14" width="7" height="7"/>
                  <rect x="14" y="14" width="7" height="7"/>
                </svg>
                <span>{{ nodes.length }} {{ $t('workflow.nodes') }}</span>
              </div>
              <div class="stat-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                  <polyline points="15 3 21 3 21 9"/>
                  <line x1="10" y1="14" x2="21" y2="3"/>
                </svg>
                <span>{{ edges.length }} {{ $t('workflow.connections') }}</span>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="modal-btn secondary" @click="showSaveModal = false">{{ $t('workflow.cancel') }}</button>
            <button class="modal-btn primary" @click="saveWorkflow" :disabled="!workflowName.trim()">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              {{ $t('workflow.save') }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
    
    <!-- Settings Modal (BYOK) -->
    <Transition name="modal">
      <div v-if="showSettingsModal" class="modal-backdrop" @click.self="showSettingsModal = false">
        <div class="modal-container settings-modal">
          <div class="modal-header">
            <div class="modal-icon settings-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3"/>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
              </svg>
            </div>
            <h3>Settings</h3>
          </div>
          <div class="modal-body">
            <div class="byok-section">
              <div class="byok-header">
                <span class="byok-badge">BYOK</span>
                <h4>Bring Your Own Key</h4>
              </div>
              <p class="byok-desc">Use your own deAPI key to access AI models. Get your key at <a href="https://deapi.ai" target="_blank" rel="noopener">deapi.ai</a></p>
              
              <div class="form-field">
                <label>deAPI Key</label>
                <div class="api-key-input">
                  <input
                    v-model="customApiKey"
                    :type="showApiKey ? 'text' : 'password'"
                    placeholder="sk-..."
                    @keyup.enter="saveApiKey"
                  />
                  <button class="toggle-visibility" @click="showApiKey = !showApiKey" type="button">
                    <svg v-if="showApiKey" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                      <line x1="1" y1="1" x2="23" y2="23"/>
                    </svg>
                    <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                      <circle cx="12" cy="12" r="3"/>
                    </svg>
                  </button>
                </div>
              </div>
              
              <div v-if="apiKeyStatus" class="api-key-status" :class="apiKeyStatus.type">
                <svg v-if="apiKeyStatus.type === 'success'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="15" y1="9" x2="9" y2="15"/>
                  <line x1="9" y1="9" x2="15" y2="15"/>
                </svg>
                <span>{{ apiKeyStatus.message }}</span>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="modal-btn secondary" @click="clearApiKey" :disabled="!hasCustomApiKey">Clear Key</button>
            <button class="modal-btn secondary" @click="showSettingsModal = false">Close</button>
            <button class="modal-btn primary" @click="saveApiKey" :disabled="!customApiKey.trim()">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              Save Key
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, markRaw, computed, onMounted, onUnmounted, watch, nextTick, provide } from 'vue'
import { VueFlow, addEdge, useVueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { useI18n } from 'vue-i18n'

import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'

import TextInputNode from './nodes/TextInputNode.vue'
import ImageInputNode from './nodes/ImageInputNode.vue'
import ImageGenNode from './nodes/ImageGenNode.vue'
import VideoGenNode from './nodes/VideoGenNode.vue'
import ImageEditNode from './nodes/ImageEditNode.vue'
import ImageToVideoNode from './nodes/ImageToVideoNode.vue'
import TextToSpeechNode from './nodes/TextToSpeechNode.vue'
import ImageAnalysisNode from './nodes/ImageAnalysisNode.vue'
import ImageBackgroundRemovalNode from './nodes/ImageBackgroundRemovalNode.vue'
import VideoToTextNode from './nodes/VideoToTextNode.vue'
import ImageEnhanceNode from './nodes/ImageEnhanceNode.vue'
import OutputNode from './nodes/OutputNode.vue'

import api from '../services/api.js'

const { t } = useI18n()

// Node types
const nodeTypesMap = {
  textInput: markRaw(TextInputNode),
  imageInput: markRaw(ImageInputNode),
  imageGen: markRaw(ImageGenNode),
  videoGen: markRaw(VideoGenNode),
  imageEdit: markRaw(ImageEditNode),
  img2video: markRaw(ImageToVideoNode),
  tts: markRaw(TextToSpeechNode),
  imageAnalysis: markRaw(ImageAnalysisNode),
  bgRemoval: markRaw(ImageBackgroundRemovalNode),
  videoToText: markRaw(VideoToTextNode),
  imageEnhance: markRaw(ImageEnhanceNode),
  output: markRaw(OutputNode)
}

// Node definitions
const nodeDefinitions = computed(() => ({
  textInput: { icon: '📝', label: t('workflow.textPrompt'), desc: 'Enter text prompts', color: '#6366F1', section: 'input' },
  imageInput: { icon: '🖼️', label: t('workflow.imageInput'), desc: 'Upload images', color: '#F97316', section: 'input' },
  imageGen: { icon: '🎨', label: t('workflow.textToImage'), desc: 'Generate images from text', color: '#A855F7', section: 'generate' },
  videoGen: { icon: '🎬', label: t('workflow.textToVideo'), desc: 'Generate videos from text', color: '#EC4899', section: 'generate' },
  imageEdit: { icon: '✏️', label: t('workflow.imageEdit'), desc: 'Edit images with AI', color: '#22C55E', section: 'transform' },
  img2video: { icon: '🎥', label: t('workflow.imageToVideo'), desc: 'Animate static images', color: '#0EA5E9', section: 'transform' },
  tts: { icon: '🔊', label: t('workflow.textToSpeech'), desc: 'Convert text to audio', color: '#8B5CF6', section: 'transform' },
  imageAnalysis: { icon: '🔍', label: t('workflow.imageAnalysis'), desc: 'Analyze image content', color: '#06B6D4', section: 'transform' },
  bgRemoval: { icon: '🖼️', label: t('workflow.bgRemoval'), desc: 'Remove image background', color: '#EC4899', section: 'transform' },
  videoToText: { icon: '📹', label: t('workflow.videoToText'), desc: 'Transcribe videos', color: '#22C55E', section: 'transform' },
  imageEnhance: { icon: '✨', label: t('workflow.imageEnhance'), desc: 'Enhance image quality', color: '#FBBF24', section: 'transform' },
  output: { icon: '📤', label: t('workflow.output'), desc: 'Final output node', color: '#F59E0B', section: 'output' }
}))

const nodeTypes = computed(() => 
  Object.entries(nodeDefinitions.value).map(([type, def]) => ({ type, ...def }))
)

// State
const nodes = ref([])
const edges = ref([])
const isExecuting = ref(false)
const executionStatus = ref(null)
const contextMenu = ref({ show: false, x: 0, y: 0, nodeId: null })
const canvasContextMenu = ref({ show: false, x: 0, y: 0 })
const showSaveModal = ref(false)
const workflowName = ref('')
const savedWorkflows = ref([])
const showSavedDropdown = ref(false)
const nameInput = ref(null)
let nodeIdCounter = 0

// Settings modal (BYOK)
const showSettingsModal = ref(false)
const customApiKey = ref('')
const showApiKey = ref(false)
const apiKeyStatus = ref(null)
const hasCustomApiKey = computed(() => !!localStorage.getItem('deapi_key'))

// Load saved API key on mount
const loadSavedApiKey = () => {
  const savedKey = localStorage.getItem('deapi_key')
  if (savedKey) {
    customApiKey.value = savedKey
  }
}

// Save API key
const saveApiKey = () => {
  if (customApiKey.value.trim()) {
    localStorage.setItem('deapi_key', customApiKey.value.trim())
    apiKeyStatus.value = { type: 'success', message: 'API key saved successfully!' }
    setTimeout(() => {
      apiKeyStatus.value = null
    }, 2000)
  }
}

// Clear API key
const clearApiKey = () => {
  localStorage.removeItem('deapi_key')
  customApiKey.value = ''
  apiKeyStatus.value = { type: 'success', message: 'API key cleared' }
  setTimeout(() => {
    apiKeyStatus.value = null
  }, 2000)
}

// Zoom state
const { getViewport, setViewport, zoomIn: vfZoomIn, zoomOut: vfZoomOut, fitView, project, connectionStartHandle } = useVueFlow()
const zoomLevel = ref(100)

const onViewportChange = (viewport) => {
  zoomLevel.value = Math.round(viewport.zoom * 100)
}

const zoomIn = () => {
  vfZoomIn({ duration: 200 })
}

const zoomOut = () => {
  vfZoomOut({ duration: 200 })
}

const resetZoom = () => {
  setViewport({ x: 0, y: 0, zoom: 1 }, { duration: 300 })
  zoomLevel.value = 100
}

// Pending connection (for quick-connect on drop)
const pendingConnection = ref(null)

watch(showSaveModal, (val) => {
  if (val) nextTick(() => nameInput.value?.focus())
})

const onDrop = (event) => {
  const type = event.dataTransfer.getData('application/vueflow')
  if (type) addNode(type)
}

// Connections
const onConnect = (params) => {
  edges.value = addEdge({
    ...params,
    animated: true,
    style: { stroke: '#F59E0B', strokeWidth: 2 }
  }, edges.value)
}

// Handle connection end on empty canvas - show quick-add menu
const onConnectEnd = (event) => {
  // Only show menu if connection didn't complete (dropped on empty canvas)
  const target = event.target
  const isHandle = target.closest('.vue-flow__handle')
  const isNode = target.closest('.vue-flow__node')
  
  // If dropped on a handle or node, let the normal connection happen
  if (isHandle || isNode) {
    return
  }
  
  // Store the source connection info for auto-connecting
  const startHandle = connectionStartHandle.value
  if (startHandle) {
    pendingConnection.value = {
      sourceNodeId: startHandle.nodeId,
      sourceHandleId: startHandle.handleId,
      sourceHandleType: startHandle.type
    }
  }
  
  // Show context menu at mouse position
  const clientX = event.clientX || (event.touches && event.touches[0]?.clientX)
  const clientY = event.clientY || (event.touches && event.touches[0]?.clientY)
  
  if (clientX && clientY) {
    canvasContextMenu.value = {
      show: true,
      x: clientX,
      y: clientY
    }
    contextMenu.value = { show: false, x: 0, y: 0, nodeId: null }
  }
}

// Context Menu
const onNodeContextMenu = (event) => {
  event.event.preventDefault()
  contextMenu.value = {
    show: true,
    x: event.event.clientX,
    y: event.event.clientY,
    nodeId: event.node.id
  }
}

const closeContextMenu = () => {
  contextMenu.value = { show: false, x: 0, y: 0, nodeId: null }
  canvasContextMenu.value = { show: false, x: 0, y: 0 }
  pendingConnection.value = null
}

// Canvas Context Menu (Quick Add)
const onCanvasContextMenu = (event) => {
  canvasContextMenu.value = {
    show: true,
    x: event.clientX,
    y: event.clientY
  }
  contextMenu.value = { show: false, x: 0, y: 0, nodeId: null }
  pendingConnection.value = null // Clear pending connection when opening via right-click
}

// Node Operations
const deleteNode = (nodeId) => {
  nodes.value = nodes.value.filter(n => n.id !== nodeId)
  edges.value = edges.value.filter(e => e.source !== nodeId && e.target !== nodeId)
  contextMenu.value = { show: false, x: 0, y: 0, nodeId: null }
}

const duplicateNode = (nodeId) => {
  const node = nodes.value.find(n => n.id === nodeId)
  if (node) {
    const newId = `${node.type}_${++nodeIdCounter}`
    nodes.value = [...nodes.value, {
      id: newId,
      type: node.type,
      position: { x: node.position.x + 50, y: node.position.y + 50 },
      data: { ...node.data }
    }]
  }
  contextMenu.value = { show: false, x: 0, y: 0, nodeId: null }
}

const addNode = (type) => {
  const id = `${type}_${++nodeIdCounter}`
  const baseX = 300 + (nodes.value.length * 40) % 500
  const baseY = 150 + Math.floor(nodes.value.length / 6) * 150
  
  nodes.value = [...nodes.value, {
    id,
    type,
    position: { x: baseX, y: baseY },
    data: getDefaultData(type)
  }]
}

const addNodeAtPosition = (type, screenX, screenY) => {
  const id = `${type}_${++nodeIdCounter}`
  
  // Convert screen coordinates to canvas coordinates using project
  const canvasRect = document.querySelector('.vue-flow-instance')?.getBoundingClientRect()
  let x, y
  
  if (canvasRect && project) {
    // Use VueFlow's project to convert screen to flow coordinates
    const viewport = getViewport()
    x = (screenX - canvasRect.left - viewport.x) / viewport.zoom - 120
    y = (screenY - canvasRect.top - viewport.y) / viewport.zoom - 50
  } else {
    x = screenX - 400
    y = screenY - 150
  }
  
  nodes.value = [...nodes.value, {
    id,
    type,
    position: { x: Math.max(50, x), y: Math.max(50, y) },
    data: getDefaultData(type)
  }]
  
  // If there's a pending connection, create the edge
  if (pendingConnection.value) {
    const { sourceNodeId, sourceHandleId, sourceHandleType } = pendingConnection.value
    
    // Determine target handle (opposite of source)
    const targetHandle = sourceHandleType === 'source' ? 'target' : 'source'
    
    edges.value = addEdge({
      id: `e_${sourceNodeId}_${id}`,
      source: sourceHandleType === 'source' ? sourceNodeId : id,
      target: sourceHandleType === 'source' ? id : sourceNodeId,
      sourceHandle: sourceHandleId,
      targetHandle: targetHandle,
      animated: true,
      style: { stroke: '#F59E0B', strokeWidth: 2 }
    }, edges.value)
    
    pendingConnection.value = null
  }
  
  canvasContextMenu.value = { show: false, x: 0, y: 0 }
}

const getDefaultData = (type) => {
  const defaults = {
    textInput: { text: '' },
    imageInput: { imageUrl: null, imageData: null },
    imageGen: { prompt: '', model: 'Flux_2_Klein_4B_BF16', aspectRatio: '16:9', width: 1024, height: 576, steps: 4, batchSize: 1, resultUrls: [] },
    videoGen: { prompt: '', model: 'Ltx2_3_22B_Dist_INT8', aspectRatio: '16:9', width: 768, height: 432, frames: 49, fps: 24 },
    imageEdit: { model: 'QwenImageEdit_Plus_NF4', aspectRatio: 'original', width: 768, height: 768, editPrompt: '' },
    img2video: { prompt: '', model: 'Ltx2_3_22B_Dist_INT8', aspectRatio: '16:9', width: 768, height: 432, frames: 49 },
    tts: { model: 'Kokoro', voice: 'af_sky', lang: 'en-us', speed: 1 },
    imageAnalysis: { model: 'Nanonets_Ocr_S_F16', language: 'auto', format: 'text' },
    bgRemoval: { model: 'Ben2' },
    videoToText: { model: 'WhisperLargeV3', includeTs: true, videoUrl: '' },
    imageEnhance: { model: 'Flux_2_Klein_4B_BF16', aspectRatio: 'original', width: 768, height: 768, enhanceType: 'quality', enhancePrompt: 'enhance image quality, improve details, sharp focus, high resolution', strength: 0.5 },
    output: {}
  }
  return { ...defaults[type] }
}

const clearCanvas = () => {
  nodes.value = []
  edges.value = []
  nodeIdCounter = 0
  executionStatus.value = null
}

// Quick action: Add connected node
const addConnectedNode = (sourceNodeId, targetType) => {
  // Find source node
  const sourceNode = nodes.value.find(n => n.id === sourceNodeId)
  if (!sourceNode) return

  // Create new node positioned to the right with proper spacing
  const id = `${targetType}_${++nodeIdCounter}`
  const nodeWidth = 280 // Account for node width + padding
  const baseX = sourceNode.position.x + nodeWidth
  
  // Check if there's already a node at this position and offset further
  let newX = baseX
  let newY = sourceNode.position.y
  
  // Avoid overlapping with existing nodes
  const existingNodesAtX = nodes.value.filter(n => 
    Math.abs(n.position.x - newX) < nodeWidth && 
    Math.abs(n.position.y - newY) < 200
  )
  
  if (existingNodesAtX.length > 0) {
    // Offset vertically if there are nodes at same position
    newY = newY + (existingNodesAtX.length * 180)
  }

  const newPosition = { x: newX, y: newY }

  // Get default data and optionally copy image data from source
  const newData = getDefaultData(targetType)
  if (sourceNode.data.resultUrl) {
    newData.imageUrl = sourceNode.data.resultUrl
    newData.imageData = sourceNode.data.resultUrl
  }

  // Add new node
  const newNode = {
    id,
    type: targetType,
    position: newPosition,
    data: newData
  }
  nodes.value = [...nodes.value, newNode]

  // Create edge from source to new node
  const edgeId = `edge-${sourceNodeId}-${id}`
  edges.value = [...edges.value, {
    id: edgeId,
    source: sourceNodeId,
    target: id,
    animated: true,
    style: { stroke: '#F59E0B', strokeWidth: 2 }
  }]

  return id
}

// Provide the function to child nodes
provide('addConnectedNode', addConnectedNode)

// Workflow Management
const saveWorkflow = async () => {
  if (!workflowName.value.trim() || nodes.value.length === 0) return
  
  try {
    const workflowData = {
      nodes: nodes.value.map(n => ({
        id: n.id, type: n.type, position: n.position, data: n.data
      })),
      edges: edges.value.map(e => ({
        id: e.id, source: e.source, target: e.target,
        sourceHandle: e.sourceHandle, targetHandle: e.targetHandle
      }))
    }
    
    await api.saveWorkflow(workflowName.value.trim(), workflowData.nodes, workflowData.edges)
    showSaveModal.value = false
    workflowName.value = ''
    await loadSavedWorkflows()
  } catch (error) {
    console.error('Failed to save workflow:', error)
    alert(t('workflow.savedError'))
  }
}

const loadSavedWorkflows = async () => {
  try {
    const data = await api.listWorkflows()
    savedWorkflows.value = data || []
  } catch (error) {
    console.error('Failed to load workflows:', error)
    savedWorkflows.value = []
  }
}

const loadWorkflow = async (workflowId) => {
  try {
    const workflow = await api.getWorkflow(workflowId)
    let maxCounter = 0
    workflow.nodes.forEach(node => {
      const match = node.id.match(/_(\d+)$/)
      if (match) maxCounter = Math.max(maxCounter, parseInt(match[1]))
    })
    nodeIdCounter = maxCounter
    nodes.value = workflow.nodes
    edges.value = workflow.edges || []
    showSavedDropdown.value = false
    executionStatus.value = null
  } catch (error) {
    console.error('Failed to load workflow:', error)
    alert(t('workflow.loadError'))
  }
}

const deleteSavedWorkflow = async (workflowId, event) => {
  event.stopPropagation()
  if (!confirm(t('workflow.confirmDelete'))) return
  
  try {
    await api.deleteWorkflow(workflowId)
    await loadSavedWorkflows()
  } catch (error) {
    console.error('Failed to delete workflow:', error)
    alert(t('workflow.deleteError'))
  }
}

// Execution
const executeGraph = async () => {
  if (isExecuting.value) return
  
  isExecuting.value = true
  executionStatus.value = { type: 'info', message: t('workflow.preparing'), progress: 0 }
  
  try {
    const graphData = {
      nodes: nodes.value.map(n => ({ id: n.id, type: n.type, data: n.data })),
      edges: edges.value.map(e => ({
        source: e.source, target: e.target,
        sourceHandle: e.sourceHandle, targetHandle: e.targetHandle
      }))
    }
    
    const result = await api.executeGraph(graphData)
    await pollExecution(result.execution_id)
  } catch (error) {
    console.error('Execution failed:', error)
    executionStatus.value = { type: 'error', message: t('workflow.executionFailed') }
  } finally {
    isExecuting.value = false
  }
}

const pollExecution = async (executionId) => {
  const maxPolls = 180
  let polls = 0
  
  while (polls < maxPolls) {
    try {
      const status = await api.getGraphExecution(executionId)
      
      if (status.node_results) {
        for (const [nodeId, result] of Object.entries(status.node_results)) {
          const idx = nodes.value.findIndex(n => n.id === nodeId)
          if (idx !== -1) {
            nodes.value[idx].data = { ...nodes.value[idx].data, ...result }
            
            // Handle multiple images - auto-create output nodes
            if (result.resultUrls && result.resultUrls.length > 1) {
              const sourceNode = nodes.value[idx]
              const urls = result.resultUrls
              
              // Keep first image in original node
              nodes.value[idx].data.resultUrl = urls[0]
              
              // Create output nodes for additional images
              for (let i = 1; i < urls.length; i++) {
                const outputId = `output_${++nodeIdCounter}`
                const xOffset = 280 * i
                
                nodes.value = [...nodes.value, {
                  id: outputId,
                  type: 'output',
                  position: { 
                    x: sourceNode.position.x + xOffset, 
                    y: sourceNode.position.y + 200 
                  },
                  data: { resultUrl: urls[i] }
                }]
                
                // Connect the output node to the source
                edges.value = [...edges.value, {
                  id: `e_${nodeId}_${outputId}`,
                  source: nodeId,
                  target: outputId,
                  sourceHandle: 'source',
                  targetHandle: 'target',
                  animated: true,
                  style: { stroke: '#F59E0B', strokeWidth: 2 }
                }]
              }
            }
          }
        }
      }
      
      if (status.progress !== undefined) {
        executionStatus.value = {
          type: 'info',
          message: status.message || t('workflow.processing'),
          progress: status.progress
        }
      }
      
      if (status.status === 'completed') {
        executionStatus.value = { type: 'success', message: t('workflow.completed') }
        // Auto-dismiss success message after 1 second
        setTimeout(() => {
          executionStatus.value = null
        }, 1000)
        return
      } else if (status.status === 'failed') {
        executionStatus.value = { type: 'error', message: status.error || t('workflow.executionFailed') }
        return
      }
    } catch (error) {
      console.error('Polling error:', error)
    }
    
    await new Promise(r => setTimeout(r, 1000))
    polls++
  }
  
  executionStatus.value = { type: 'error', message: t('workflow.timeout') }
}

onMounted(() => {
  loadSavedWorkflows()
  loadSavedApiKey()
})
</script>

<style scoped>
.workflow-canvas {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg-base);
  position: relative;
  overflow: hidden;
}

/* Header */
.workflow-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: var(--bg-panel);
  border-bottom: 1px solid var(--border-color);
  z-index: 50;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-link {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  transition: opacity 0.15s ease;
}

.logo-link:hover {
  opacity: 0.8;
}

.logo-link svg {
  width: 28px;
  height: 28px;
  color: #F59E0B;
}

.logo-link span {
  font-size: 1.25rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.02em;
}

.breadcrumb-sep {
  color: #4B5563;
  font-size: 0.875rem;
}

.breadcrumb-current {
  font-size: 0.875rem;
  font-weight: 500;
  color: #9CA3AF;
}

.header-actions {
  display: flex;
  gap: 10px;
}

/* Action Buttons */
.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

.action-btn:hover:not(:disabled) {
  background: var(--bg-elevated);
  border-color: var(--border-hover);
}

.action-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.action-btn.primary {
  background: var(--accent-primary);
  border: none;
  color: #000;
  font-weight: 600;
}

.action-btn.primary:hover:not(:disabled) {
  background: var(--accent-primary-hover);
  transform: translateY(-1px);
}

.action-btn.primary.run {
  padding: 8px 24px;
  border-radius: 8px;
}

.action-btn.danger:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: #EF4444;
}

.action-btn .spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(0, 0, 0, 0.2);
  border-top-color: #000;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.badge {
  background: rgba(245, 158, 11, 0.2);
  color: #F59E0B;
  padding: 2px 8px;
  border-radius: 20px;
  font-size: 0.6875rem;
  font-weight: 700;
}

.chevron {
  transition: transform 0.2s ease;
  width: 14px;
  height: 14px;
}

.chevron.rotated {
  transform: rotate(180deg);
}

/* Dropdown */
.dropdown-wrapper {
  position: relative;
}

.dropdown-panel {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 300px;
  background: rgba(18, 18, 26, 0.98);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  padding: 8px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(20px);
  z-index: 100;
}

.dropdown-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 32px;
  color: #6B7280;
}

.dropdown-empty svg {
  width: 40px;
  height: 40px;
  opacity: 0.3;
}

.workflow-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.workflow-item:hover {
  background: rgba(255, 255, 255, 0.04);
}

.workflow-item-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.workflow-item-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: #fff;
}

.workflow-item-meta {
  font-size: 0.6875rem;
  color: #6B7280;
}

.workflow-item-delete {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: #6B7280;
  cursor: pointer;
  transition: all 0.15s ease;
}

.workflow-item-delete:hover {
  background: rgba(239, 68, 68, 0.15);
  color: #EF4444;
}

.workflow-item-delete svg {
  width: 16px;
  height: 16px;
}

/* Layout */
.workflow-layout {
  flex: 1;
  display: flex;
  min-height: 0;
  position: relative;
}

/* Canvas */
.canvas-area {
  flex: 1;
  position: relative;
  min-height: 0;
}

.canvas-wrapper {
  position: absolute;
  inset: 0;
}

.vue-flow-instance {
  width: 100%;
  height: 100%;
}

/* Zoom Indicator */
.zoom-indicator {
  position: absolute;
  bottom: 20px;
  right: 20px;
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(11, 11, 11, 0.9);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 4px;
  z-index: 10;
}

.zoom-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: #9CA3AF;
  cursor: pointer;
  transition: all 0.15s ease;
}

.zoom-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.zoom-btn svg {
  width: 16px;
  height: 16px;
}

.zoom-value {
  min-width: 48px;
  text-align: center;
  font-size: 0.75rem;
  font-weight: 600;
  color: #fff;
  padding: 0 4px;
}

/* Settings Button (BYOK) */
.settings-btn {
  position: absolute;
  bottom: 20px;
  left: 20px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(11, 11, 11, 0.9);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  color: #9CA3AF;
  cursor: pointer;
  transition: all 0.2s ease;
  z-index: 10;
}

.settings-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  border-color: rgba(245, 158, 11, 0.3);
}

.settings-btn svg {
  width: 20px;
  height: 20px;
}

.settings-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #22C55E;
  border-radius: 50%;
  font-size: 0.625rem;
  color: #fff;
  font-weight: 700;
}

/* Settings Modal */
.settings-modal {
  max-width: 440px;
}

.settings-icon {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(139, 92, 246, 0.1)) !important;
}

.byok-section {
  padding: 4px 0;
}

.byok-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.byok-badge {
  padding: 4px 10px;
  background: linear-gradient(135deg, #8B5CF6, #6366F1);
  border-radius: 6px;
  font-size: 0.625rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.5px;
}

.byok-header h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.byok-desc {
  font-size: 0.8125rem;
  color: #9CA3AF;
  margin-bottom: 20px;
  line-height: 1.5;
}

.byok-desc a {
  color: #8B5CF6;
  text-decoration: none;
}

.byok-desc a:hover {
  text-decoration: underline;
}

.api-key-input {
  position: relative;
  display: flex;
  align-items: center;
}

.api-key-input input {
  flex: 1;
  padding-right: 40px;
}

.toggle-visibility {
  position: absolute;
  right: 8px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: #6B7280;
  cursor: pointer;
  transition: color 0.15s ease;
}

.toggle-visibility:hover {
  color: #fff;
}

.toggle-visibility svg {
  width: 16px;
  height: 16px;
}

.api-key-status {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 0.8125rem;
}

.api-key-status.success {
  background: rgba(34, 197, 94, 0.1);
  color: #22C55E;
}

.api-key-status.error {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

.api-key-status svg {
  width: 16px;
  height: 16px;
}

/* Empty State */
.canvas-empty {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  pointer-events: none;
  z-index: 5;
}

.empty-visual {
  position: relative;
  width: 160px;
  height: 160px;
  margin-bottom: 24px;
}

.empty-circles {
  position: absolute;
  inset: 0;
}

.empty-circle {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(245, 158, 11, 0.1);
}

.empty-circle.c1 {
  inset: 0;
  animation: pulse 3s ease-in-out infinite;
}

.empty-circle.c2 {
  inset: 20px;
  animation: pulse 3s ease-in-out infinite 0.5s;
}

.empty-circle.c3 {
  inset: 40px;
  animation: pulse 3s ease-in-out infinite 1s;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.05); opacity: 1; }
}

.empty-illustration {
  position: absolute;
  inset: 30px;
  color: rgba(255, 255, 255, 0.3);
}

.canvas-empty h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.canvas-empty p {
  font-size: 0.8125rem;
  color: var(--text-muted);
  max-width: 280px;
  margin-bottom: 24px;
}

.empty-quick-add {
  display: flex;
  align-items: center;
  gap: 10px;
  pointer-events: auto;
}

.empty-quick-add span {
  font-size: 0.75rem;
  color: #6B7280;
}

.quick-add-btn {
  padding: 8px 14px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.quick-add-btn:hover {
  background: rgba(245, 158, 11, 0.1);
  border-color: rgba(245, 158, 11, 0.3);
  color: #F59E0B;
}

/* Context Menu */
.context-menu {
  position: fixed;
  z-index: 1001;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 6px;
  min-width: 180px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5);
}

.context-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 14px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: #D1D5DB;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.context-item:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
}

.context-item.danger:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

.context-item svg {
  width: 16px;
  height: 16px;
}

.context-divider {
  height: 1px;
  background: var(--border-color);
  margin: 4px 0;
}

/* Canvas Context Menu (Quick Add) */
.canvas-context-menu {
  position: fixed;
  z-index: 1001;
  background: rgba(18, 18, 26, 0.98);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 12px;
  min-width: 280px;
  max-width: 320px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(20px);
}

.context-menu-title {
  font-size: 0.6875rem;
  font-weight: 600;
  color: #6B7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 0 8px 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  margin-bottom: 10px;
}

.context-menu-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 6px;
}

.context-node-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 12px 8px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid transparent;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.context-node-btn:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: var(--node-accent, rgba(99, 102, 241, 0.3));
}

.context-node-icon {
  font-size: 1.25rem;
}

.context-node-label {
  font-size: 0.6875rem;
  font-weight: 500;
  color: #D1D5DB;
  text-align: center;
  line-height: 1.2;
}


/* Status Toast */
.status-toast {
  position: fixed;
  bottom: 32px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 24px;
  background: rgba(18, 18, 26, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(20px);
  z-index: 100;
  min-width: 300px;
}

.status-toast.success {
  border-color: rgba(34, 197, 94, 0.3);
  box-shadow: 0 16px 48px rgba(34, 197, 94, 0.1);
}

.status-toast.error {
  border-color: rgba(239, 68, 68, 0.3);
  box-shadow: 0 16px 48px rgba(239, 68, 68, 0.1);
}

.toast-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toast-icon svg {
  width: 22px;
  height: 22px;
}

.status-toast.success .toast-icon svg {
  color: #22C55E;
}

.status-toast.error .toast-icon svg {
  color: #EF4444;
}

.toast-spinner {
  width: 22px;
  height: 22px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-top-color: #F59E0B;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.toast-content {
  flex: 1;
}

.toast-message {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #fff;
}

.toast-progress {
  display: block;
  font-size: 0.6875rem;
  color: #6B7280;
  margin-top: 2px;
}

.toast-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 0 0 14px 14px;
  overflow: hidden;
}

.toast-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #F59E0B, #FBBF24);
  transition: width 0.3s ease;
}

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  width: 100%;
  max-width: 420px;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.modal-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(99, 102, 241, 0.05));
  border-radius: 12px;
}

.modal-icon svg {
  width: 22px;
  height: 22px;
  color: #818CF8;
}

.modal-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #fff;
}

.modal-body {
  padding: 24px;
}

.form-field {
  margin-bottom: 20px;
}

.form-field label {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  color: #9CA3AF;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-field input {
  width: 100%;
  padding: 12px 16px;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 0.9375rem;
  transition: all 0.2s ease;
}

.form-field input:focus {
  outline: none;
  border-color: var(--accent-primary);
  background: var(--bg-elevated);
}

.form-field input::placeholder {
  color: #6B7280;
}

.workflow-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 10px;
}

.stat-item svg {
  width: 18px;
  height: 18px;
  color: #6B7280;
}

.stat-item span {
  font-size: 0.8125rem;
  color: #9CA3AF;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.04);
}

.modal-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  border-radius: 10px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.modal-btn.secondary {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #9CA3AF;
}

.modal-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.06);
  color: #fff;
}

.modal-btn.primary {
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  border: none;
  color: #fff;
}

.modal-btn.primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.3);
}

.modal-btn.primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-btn svg {
  width: 16px;
  height: 16px;
}

:deep(.vue-flow__node) {
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
  box-shadow: none !important;
  border-radius: 0 !important;
}

:deep(.vue-flow__edge-path) {
  stroke-width: 2 !important;
  stroke: rgba(255, 255, 255, 0.6) !important;
}

/* Animated edge (connected) */
:deep(.vue-flow__edge.animated path) {
  stroke: rgba(255, 255, 255, 0.6) !important;
  stroke-width: 2 !important;
}

:deep(.vue-flow__edge.selected .vue-flow__edge-path) {
  stroke: #F59E0B !important;
}

/* Connection line while dragging (yellow dotted) */
:deep(.vue-flow__connection-line) {
  stroke: #FBBF24 !important;
  stroke-width: 2 !important;
}

:deep(.vue-flow__connection-line-path) {
  stroke: #FBBF24 !important;
  stroke-width: 2 !important;
  stroke-dasharray: 6 4 !important;
  fill: none !important;
}

:deep(.vue-flow__connection-line svg) {
  overflow: visible;
}

:deep(.vue-flow__handle) {
  width: 12px;
  height: 12px;
  background: var(--accent-primary);
  border: 2px solid var(--bg-panel);
  transition: transform 0.15s ease;
}

:deep(.vue-flow__handle:hover) {
  transform: scale(1.3);
}

:deep(.vue-flow__controls) {
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

:deep(.vue-flow__controls-button) {
  background: transparent;
  border: none;
  color: #9CA3AF;
  width: 32px;
  height: 32px;
}

:deep(.vue-flow__controls-button:hover) {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

/* Scrollbar */
.palette-sections::-webkit-scrollbar {
  width: 4px;
}

.palette-sections::-webkit-scrollbar-track {
  background: transparent;
}

.palette-sections::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 2px;
}

/* Animations */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.toast-enter-active {
  transition: all 0.2s ease-out;
}

.toast-leave-active {
  transition: all 0.15s ease-in;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(10px);
}

.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95);
}

/* Selection rectangle (drag to select) */
:deep(.vue-flow__selection) {
  background: rgba(74, 222, 128, 0.15) !important;
  border: 1px dashed #4ade80 !important;
  border-radius: 4px;
}

/* Selected nodes - glowing effect */
:deep(.vue-flow__node.selected) {
  z-index: 10;
}

:deep(.vue-flow__node.selected .workflow-node) {
  box-shadow: 
    0 0 0 2px rgba(74, 222, 128, 0.8),
    0 0 20px rgba(74, 222, 128, 0.4),
    0 8px 32px rgba(0, 0, 0, 0.5) !important;
  border-color: #4ade80 !important;
}

/* Selection box during drag */
:deep(.vue-flow__pane) {
  cursor: default;
}

:deep(.vue-flow__pane.dragging) {
  cursor: crosshair;
}

/* Pan cursor when space is held */
.vue-flow-panning :deep(.vue-flow__pane) {
  cursor: grab !important;
}

.vue-flow-panning :deep(.vue-flow__pane:active) {
  cursor: grabbing !important;
}

/* Dotted grid background enhancement */
:deep(.vue-flow__background) {
  background-color: #0b0b0b !important;
}

:deep(.vue-flow__background pattern circle) {
  fill: rgba(255, 255, 255, 0.06) !important;
}
</style>
