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

        <button class="action-btn" @click="exportWorkflow" :disabled="nodes.length === 0">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          <span>{{ $t('workflow.export') }}</span>
        </button>

        <button class="action-btn" @click="triggerImport">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
          <span>{{ $t('workflow.import') }}</span>
        </button>

        <input
          ref="importFileInput"
          type="file"
          accept=".json"
          style="display: none"
          @change="handleImport"
        />

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
            @edge-click="onEdgeClick"
            @nodes-change="onNodesChange"
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
            <Background variant="dots" :gap="24" :size="2" pattern-color="rgba(255, 255, 255, 0.3)" />
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

          <!-- Add Node Floating Button (Mobile Friendly) -->
          <button class="fab-btn" @click.stop="toggleCanvasMenu" title="Add Node">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
          </button>

          <!-- Canvas Context Menu (Quick Add) -->
          <Teleport to="body">
            <div
              v-if="canvasContextMenu.show"
              class="canvas-context-menu"
              :style="{ left: canvasContextMenu.x + 'px', top: canvasContextMenu.y + 'px' }"
              @click.stop
            >
              <div class="context-menu-header">
                <div class="context-menu-title">Add Node</div>
                <button class="context-close-btn" @click="closeContextMenu">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
              </div>
              <div class="context-menu-scroll">
                <div v-for="section in ['input', 'generate', 'transform', 'annotation', 'output']" :key="section" class="context-section">
                  <div class="section-label" :style="{ '--section-color': getSectionColor(section) }">{{ section }}</div>
                  <div class="context-menu-grid">
                    <button 
                      v-for="nt in nodeTypes.filter(n => n.section === section)" 
                      :key="nt.type" 
                      class="context-node-btn"
                      :style="{ '--node-accent': nt.color, '--node-accent-rgb': hexToRgb(nt.color) }"
                      @click="addNodeAtPosition(nt.type, canvasContextMenu.x, canvasContextMenu.y)"
                      :title="nt.label"
                    >
                      <span class="context-node-icon" v-html="nt.icon"></span>
                      <span class="context-node-label">{{ nt.label }}</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </Teleport>

          <!-- Empty State - Shortcuts Guide -->
          <div v-if="nodes.length === 0" class="canvas-empty">
            <div class="shortcuts-guide">
              <h3 class="guide-title">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="16" x2="12" y2="12"/>
                  <line x1="12" y1="8" x2="12.01" y2="8"/>
                </svg>
                {{ $t('workflow.gettingStarted') }}
              </h3>
              
              <div class="shortcuts-grid">
                <div class="shortcut-item">
                  <div class="shortcut-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <circle cx="11" cy="11" r="8"/>
                      <line x1="21" y1="21" x2="16.65" y2="16.65"/>
                    </svg>
                  </div>
                  <div class="shortcut-info">
                    <span class="shortcut-key">{{ $t('workflow.scrollToZoom') }}</span>
                    <span class="shortcut-desc">{{ $t('workflow.infiniteZoom') }}</span>
                  </div>
                </div>

                <div class="shortcut-item">
                  <div class="shortcut-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <rect x="3" y="3" width="18" height="18" rx="2"/>
                      <circle cx="8.5" cy="8.5" r="1.5"/>
                      <path d="M21 15l-5-5L5 21"/>
                    </svg>
                  </div>
                  <div class="shortcut-info">
                    <span class="shortcut-key">{{ $t('workflow.rightClickForMenu') }}</span>
                    <span class="shortcut-desc">{{ $t('workflow.addNode') }}</span>
                  </div>
                </div>

                <div class="shortcut-item">
                  <div class="shortcut-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
                    </svg>
                  </div>
                  <div class="shortcut-info">
                    <span class="shortcut-key">Ctrl + Z</span>
                    <span class="shortcut-desc">{{ $t('workflow.undo') }}</span>
                  </div>
                </div>

                <div class="shortcut-item">
                  <div class="shortcut-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <circle cx="12" cy="12" r="3"/>
                      <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82V9a1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/>
                    </svg>
                  </div>
                  <div class="shortcut-info">
                    <span class="shortcut-key">{{ $t('header.settings') }}</span>
                    <span class="shortcut-desc">{{ $t('workflow.settingsForKey') }}</span>
                  </div>
                </div>

                <div class="shortcut-item">
                  <div class="shortcut-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/>
                      <polyline points="15 3 21 3 21 9"/>
                      <line x1="10" y1="14" x2="21" y2="3"/>
                    </svg>
                  </div>
                  <div class="shortcut-info">
                    <span class="shortcut-key">{{ $t('workflow.dragToConnect') }}</span>
                    <span class="shortcut-desc">{{ $t('workflow.connections') }}</span>
                  </div>
                </div>

                <div class="shortcut-item">
                  <div class="shortcut-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <line x1="18" y1="6" x2="6" y2="18"/>
                      <line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                  </div>
                  <div class="shortcut-info">
                    <span class="shortcut-key">{{ $t('workflow.selectAndClickX') }}</span>
                    <span class="shortcut-desc">{{ $t('workflow.cutConnection') }}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="empty-quick-add">
              <span>{{ $t('workflow.quickStart') }}:</span>
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
            <h3>{{ $t('workflow.settings') }}</h3>
          </div>
          <div class="modal-body">
            <div class="byok-section">
              <div class="byok-header">
                <span class="byok-badge">BYOK</span>
                <h4>{{ $t('workflow.bringYourOwnKey') }}</h4>
              </div>
              <p class="byok-desc">{{ $t('workflow.byokDesc') }}</p>
              
              <div class="form-field">
                <label>{{ $t('workflow.deapiKey') }}</label>
                <div class="api-key-input">
                  <input
                    v-model="customApiKey"
                    :type="showApiKey ? 'text' : 'password'"
                    :placeholder="$t('workflow.enterApiKey')"
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
              
              <div class="byok-divider"></div>

              <p class="byok-desc">{{ $t('workflow.iflowDesc') }} <a href="https://iflow.cn" target="_blank" rel="noopener">iflow.cn</a></p>

              <div class="form-field">
                <label>{{ $t('workflow.iflowKey') }}</label>
                <div class="api-key-input">
                  <input
                    v-model="customiFlowKey"
                    :type="showiFlowKey ? 'text' : 'password'"
                    :placeholder="$t('workflow.enterIflowKey')"
                    @keyup.enter="saveiFlowKey"
                  />
                  <button class="toggle-visibility" @click="showiFlowKey = !showiFlowKey" type="button">
                    <svg v-if="showiFlowKey" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
              
              <div v-if="iFlowKeyStatus" class="api-key-status" :class="iFlowKeyStatus.type">
                <svg v-if="iFlowKeyStatus.type === 'success'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="15" y1="9" x2="9" y2="15"/>
                  <line x1="9" y1="9" x2="15" y2="15"/>
                </svg>
                <span>{{ iFlowKeyStatus.message }}</span>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="modal-btn secondary" @click="clearApiKey" :disabled="!hasCustomApiKey">{{ $t('workflow.clearKey') }} (deAPI)</button>
            <button class="modal-btn secondary" @click="cleariFlowKey" :disabled="!hasCustomiFlowKey">{{ $t('workflow.clearKey') }} (iFlow)</button>
            <button class="modal-btn secondary" @click="showSettingsModal = false">{{ $t('workflow.cancel') }}</button>
            <button class="modal-btn primary" @click="saveApiKey" :disabled="!customApiKey.trim()">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              {{ $t('workflow.saveKey') }}
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
import VideoReplaceNode from './nodes/VideoReplaceNode.vue'
import TextToSpeechNode from './nodes/TextToSpeechNode.vue'
import ImageAnalysisNode from './nodes/ImageAnalysisNode.vue'
import ImageBackgroundRemovalNode from './nodes/ImageBackgroundRemovalNode.vue'
import VideoToTextNode from './nodes/VideoToTextNode.vue'
import ImageEnhanceNode from './nodes/ImageEnhanceNode.vue'
import AIAssistantNode from './nodes/AIAssistantNode.vue'
import ImagePromptEnhancerNode from './nodes/ImagePromptEnhancerNode.vue'
import VideoPromptEnhancerNode from './nodes/VideoPromptEnhancerNode.vue'
import StickyNoteNode from './nodes/StickyNoteNode.vue'
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
  videoReplace: markRaw(VideoReplaceNode),
  tts: markRaw(TextToSpeechNode),
  imageAnalysis: markRaw(ImageAnalysisNode),
  bgRemoval: markRaw(ImageBackgroundRemovalNode),
  videoToText: markRaw(VideoToTextNode),
  imageEnhance: markRaw(ImageEnhanceNode),
  aiAssistant: markRaw(AIAssistantNode),
  imagePromptEnhancer: markRaw(ImagePromptEnhancerNode),
  videoPromptEnhancer: markRaw(VideoPromptEnhancerNode),
  stickyNote: markRaw(StickyNoteNode),
  output: markRaw(OutputNode)
}

// Node definitions
const nodeDefinitions = computed(() => ({
  textInput: { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>', label: t('workflow.textPrompt'), desc: 'Enter text prompts', color: '#6366F1', section: 'input', sectionColor: '#6366F1' },
  imageInput: { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>', label: t('workflow.imageInput'), desc: 'Upload images', color: '#F97316', section: 'input', sectionColor: '#6366F1' },
  imageGen: { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3 1.912 5.886h6.19l-5.007 3.638L17.007 18.41 12 14.772l-5.007 3.638 1.912-5.886-5.007-3.638h6.19z"/></svg>', label: t('workflow.textToImage'), desc: 'Generate images from text', color: '#A855F7', section: 'generate', sectionColor: '#EC4899' },
  videoGen: { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="2" x2="22" y1="10" y2="10"/><line x1="2" x2="2" y1="7" y2="13"/><line x1="22" x2="22" y1="7" y2="13"/><path d="m9 21 3-3 3 3"/></svg>', label: t('workflow.textToVideo'), desc: 'Generate videos from text', color: '#EC4899', section: 'generate', sectionColor: '#EC4899' },
  imageEdit: { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>', label: t('workflow.imageEdit'), desc: 'Edit images with AI', color: '#22C55E', section: 'transform', sectionColor: '#0EA5E9' },
  img2video: { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/><path d="m16 2 6 6-6 6"/></svg>', label: t('workflow.imageToVideo'), desc: 'Animate static images', color: '#0EA5E9', section: 'transform', sectionColor: '#0EA5E9' },
  videoReplace: { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>', label: t('workflow.videoReplace'), desc: 'Replace character in video', color: '#A855F7', section: 'transform', sectionColor: '#0EA5E9' },
  tts: { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>', label: t('workflow.textToSpeech'), desc: 'Convert text to audio', color: '#8B5CF6', section: 'transform', sectionColor: '#0EA5E9' },
  imageAnalysis: { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/><line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/></svg>', label: t('workflow.imageAnalysis'), desc: 'Analyze image content', color: '#06B6D4', section: 'transform', sectionColor: '#0EA5E9' },
  bgRemoval: { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></svg>', label: t('workflow.bgRemoval'), desc: 'Remove image background', color: '#EC4899', section: 'transform', sectionColor: '#0EA5E9' },
  videoToText: { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><path d="M7 21h10"/><path d="M12 17v4"/><path d="M9 8h6"/><path d="M9 12h6"/></svg>', label: t('workflow.videoToText'), desc: 'Transcribe videos', color: '#22C55E', section: 'transform', sectionColor: '#0EA5E9' },
  imageEnhance: { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3 1.912 5.886h6.19l-5.007 3.638L17.007 18.41 12 14.772l-5.007 3.638 1.912-5.886-5.007-3.638h6.19z"/><path d="M5 3 2 6l3 3"/><path d="m19 3 3 3-3 3"/></svg>', label: t('workflow.imageEnhance'), desc: 'Enhance image quality', color: '#FBBF24', section: 'transform', sectionColor: '#0EA5E9' },
  aiAssistant: { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>', label: t('workflow.aiAssistant'), desc: 'AI Assistant for text processing', color: '#6366F1', section: 'transform', sectionColor: '#0EA5E9' },
  imagePromptEnhancer: { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3 1.912 5.886h6.19l-5.007 3.638L17.007 18.41 12 14.772l-5.007 3.638 1.912-5.886-5.007-3.638h6.19z"/><path d="M5 3 2 6l3 3"/><path d="m19 3 3 3-3 3"/></svg>', label: t('workflow.imagePromptEnhancer'), desc: 'Enhance prompts for image generation', color: '#A855F7', section: 'transform', sectionColor: '#0EA5E9' },
  videoPromptEnhancer: { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="2" x2="22" y1="10" y2="10"/><line x1="2" x2="2" y1="7" y2="13"/><line x1="22" x2="22" y1="7" y2="13"/><path d="m9 21 3-3 3 3"/></svg>', label: t('workflow.videoPromptEnhancer'), desc: 'Enhance prompts for video generation', color: '#EC4899', section: 'transform', sectionColor: '#0EA5E9' },
  stickyNote: { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>', label: t('workflow.stickyNote'), desc: 'Add text notes to canvas', color: '#FBBF24', section: 'annotation', sectionColor: '#F59E0B' },
  output: { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>', label: t('workflow.output'), desc: 'Final output node', color: '#F59E0B', section: 'output', sectionColor: '#F59E0B' }
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

// Undo/Redo History
const history = ref([])
const historyIndex = ref(-1)
const maxHistorySize = 50

// Save current state to history
const saveHistory = () => {
  // Remove any future states if we're in the middle of the history
  if (historyIndex.value < history.value.length - 1) {
    history.value = history.value.slice(0, historyIndex.value + 1)
  }
  
  // Add new state
  history.value.push({
    nodes: JSON.parse(JSON.stringify(nodes.value)),
    edges: JSON.parse(JSON.stringify(edges.value)),
    nodeIdCounter
  })
  
  // Limit history size
  if (history.value.length > maxHistorySize) {
    history.value.shift()
  } else {
    historyIndex.value++
  }
}

// Undo last action
const undo = () => {
  if (historyIndex.value > 0) {
    historyIndex.value--
    const state = history.value[historyIndex.value]
    nodes.value = JSON.parse(JSON.stringify(state.nodes))
    edges.value = JSON.parse(JSON.stringify(state.edges))
    nodeIdCounter = state.nodeIdCounter
  }
}

// Redo last undone action
const redo = () => {
  if (historyIndex.value < history.value.length - 1) {
    historyIndex.value++
    const state = history.value[historyIndex.value]
    nodes.value = JSON.parse(JSON.stringify(state.nodes))
    edges.value = JSON.parse(JSON.stringify(state.edges))
    nodeIdCounter = state.nodeIdCounter
  }
}

// Initialize history with empty state
saveHistory()

// Parameter change detection for workflow nodes
// This tracks executed parameters and clears stale results when parameters change

// Get relevant parameters for each node type that affect the output
const getNodeParams = (nodeType, data) => {
  const params = {}
  
  // Common parameters that affect output
  switch (nodeType) {
    case 'imageGen':
      return {
        model: data.model,
        width: data.width,
        height: data.height,
        steps: data.steps,
        guidance: data.guidance,
        seed: data.seed,
        batchSize: data.batchSize
      }
    case 'videoGen':
      return {
        model: data.model,
        width: data.width,
        height: data.height,
        frames: data.frames,
        fps: data.fps,
        steps: data.steps,
        guidance: data.guidance,
        seed: data.seed
      }
    case 'img2video':
      return {
        model: data.model,
        frames: data.frames,
        fps: data.fps,
        prompt: data.prompt,
        seed: data.seed
      }
    case 'videoReplace':
      return {
        model: data.model,
        prompt: data.prompt,
        steps: data.steps,
        seed: data.seed,
        hasVideo: !!data.videoFile,
        hasCharacter: !!data.characterFile
      }
    case 'imageEdit':
      return {
        model: data.model,
        editPrompt: data.editPrompt,
        steps: data.steps,
        guidance: data.guidance,
        seed: data.seed
      }
    case 'tts':
      return {
        model: data.model,
        voice: data.voice,
        lang: data.lang,
        speed: data.speed
      }
    case 'imageAnalysis':
      return {
        model: data.model,
        language: data.language
      }
    case 'bgRemoval':
      return {
        model: data.model
      }
    case 'imageEnhance':
      return {
        model: data.model,
        enhanceType: data.enhanceType,
        enhancePrompt: data.enhancePrompt,
        strength: data.strength,
        width: data.width,
        height: data.height
      }
    case 'videoToText':
      return {
        model: data.model,
        videoUrl: data.videoUrl,
        includeTs: data.includeTs
      }
    case 'aiAssistant':
      return {
        systemPrompt: data.systemPrompt,
        model: data.model
      }
    case 'imagePromptEnhancer':
    case 'videoPromptEnhancer':
      return {
        style: data.style
      }
    case 'textInput':
      return {
        text: data.text
      }
    case 'imageInput':
      return {
        imageData: data.imageData ? data.imageData.substring(0, 100) : null // Just use prefix for comparison
      }
    default:
      return {}
  }
}

// Simple hash function for parameters
const hashParams = (params) => {
  return JSON.stringify(params)
}

// Store for tracking last executed parameters per node
const lastExecutedParams = ref({})

// Check if node parameters have changed since last execution
const haveParamsChanged = (nodeId, nodeType, data) => {
  const currentParams = getNodeParams(nodeType, data)
  const currentHash = hashParams(currentParams)
  const lastHash = lastExecutedParams.value[nodeId]
  
  return lastHash !== undefined && lastHash !== currentHash
}

// Clear stale results from a node and its downstream nodes
const clearStaleResults = (nodeId) => {
  const nodeIdx = nodes.value.findIndex(n => n.id === nodeId)
  if (nodeIdx === -1) return
  
  const node = nodes.value[nodeIdx]
  
  // Clear the node's result
  if (node.data.resultUrl || node.data.status === 'completed') {
    node.data.resultUrl = null
    node.data.resultUrls = null
    node.data.status = 'idle'
    delete node.data.cached
  }
  
  // Find and clear downstream nodes (nodes connected from this node)
  const downstreamNodeIds = new Set()
  const findDownstream = (nId) => {
    edges.value.forEach(edge => {
      if (edge.source === nId && !downstreamNodeIds.has(edge.target)) {
        downstreamNodeIds.add(edge.target)
        findDownstream(edge.target)
      }
    })
  }
  findDownstream(nodeId)
  
  // Clear results from downstream nodes
  downstreamNodeIds.forEach(dNodeId => {
    const dIdx = nodes.value.findIndex(n => n.id === dNodeId)
    if (dIdx !== -1) {
      const dNode = nodes.value[dIdx]
      if (dNode.data.resultUrl || dNode.data.status === 'completed') {
        dNode.data.resultUrl = null
        dNode.data.resultUrls = null
        dNode.data.status = 'idle'
        dNode.data.text = null
        delete dNode.data.cached
      }
      // Also clear the last executed params for downstream nodes
      delete lastExecutedParams.value[dNodeId]
    }
  })
}

// Watch for node data changes and clear stale results
watch(
  () => nodes.value.map(n => ({ id: n.id, type: n.type, data: n.data })),
  (newNodes, oldNodes) => {
    if (!oldNodes || isExecuting.value) return
    
    newNodes.forEach((newNode, idx) => {
      const oldNode = oldNodes[idx]
      if (!oldNode || newNode.id !== oldNode.id) return
      
      // Check if this node has been executed before
      if (lastExecutedParams.value[newNode.id]) {
        const paramsChanged = haveParamsChanged(newNode.id, newNode.type, newNode.data)
        
        if (paramsChanged) {
          console.log(`[Workflow] Parameters changed for node ${newNode.id}, clearing stale results`)
          clearStaleResults(newNode.id)
          delete lastExecutedParams.value[newNode.id]
        }
      }
    })
  },
  { deep: true }
)

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

// Save API keys (both deAPI and iFlow)
const saveApiKey = () => {
  if (customApiKey.value.trim()) {
    localStorage.setItem('deapi_key', customApiKey.value.trim())
    apiKeyStatus.value = { type: 'success', message: t('workflow.keySaved') }
    setTimeout(() => {
      apiKeyStatus.value = null
    }, 2000)
  }

  if (customiFlowKey.value.trim()) {
    localStorage.setItem('iflow_key', customiFlowKey.value.trim())
    iFlowKeyStatus.value = { type: 'success', message: t('workflow.keySaved') }
    setTimeout(() => {
      iFlowKeyStatus.value = null
    }, 2000)
  }
}

// Clear API key
const clearApiKey = () => {
  localStorage.removeItem('deapi_key')
  customApiKey.value = ''
  apiKeyStatus.value = { type: 'success', message: t('workflow.keyCleared') }
  setTimeout(() => {
    apiKeyStatus.value = null
  }, 2000)
}

// iFlow API Key (for AI Assistant)
const customiFlowKey = ref('')
const showiFlowKey = ref(false)
const iFlowKeyStatus = ref(null)
const hasCustomiFlowKey = computed(() => !!localStorage.getItem('iflow_key'))

// Load saved iFlow key on mount
const loadSavediFlowKey = () => {
  const savedKey = localStorage.getItem('iflow_key')
  if (savedKey) {
    customiFlowKey.value = savedKey
  }
}

// Save iFlow key
const saveiFlowKey = () => {
  if (customiFlowKey.value.trim()) {
    localStorage.setItem('iflow_key', customiFlowKey.value.trim())
    iFlowKeyStatus.value = { type: 'success', message: t('workflow.keySaved') }
    setTimeout(() => {
      iFlowKeyStatus.value = null
    }, 2000)
  }
}

// Clear iFlow key
const cleariFlowKey = () => {
  localStorage.removeItem('iflow_key')
  customiFlowKey.value = ''
  iFlowKeyStatus.value = { type: 'success', message: t('workflow.keyCleared') }
  setTimeout(() => {
    iFlowKeyStatus.value = null
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
  const edgeId = `e_${params.source}_${params.target}_${Date.now()}`
  edges.value = addEdge({
    ...params,
    id: edgeId,
    animated: true,
    style: { stroke: '#F59E0B', strokeWidth: 2 },
    label: '✕',
    labelStyle: { fill: '#EF4444', fontWeight: 'bold', fontSize: '14px' },
    labelBgStyle: { fill: 'rgba(0,0,0,0.8)', stroke: '#EF4444', strokeWidth: 1, rx: 10, ry: 10 },
    labelBgPadding: [6, 6],
    labelBgBorderRadius: 10,
    class: selectedNodes.value.has(params.source) || selectedNodes.value.has(params.target) 
      ? 'cuttable-edge selected' 
      : 'cuttable-edge'
  }, edges.value)
}

// Delete edge by ID
const deleteEdge = (edgeId) => {
  edges.value = edges.value.filter(e => e.id !== edgeId)
  saveHistory()
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

// Edge Click - Delete connection
const onEdgeClick = (event) => {
  const edge = event.edge
  if (edge && edge.id) {
    deleteEdge(edge.id)
  }
}

// Track selected nodes and update connected edges
const selectedNodes = ref(new Set())

const onNodesChange = (changes) => {
  changes.forEach(change => {
    if (change.type === 'select') {
      if (change.selected) {
        selectedNodes.value.add(change.id)
      } else {
        selectedNodes.value.delete(change.id)
      }
    }
  })
  
  // Update edges to show/hide cut buttons based on connected node selection
  updateEdgeSelection()
}

const updateEdgeSelection = () => {
  edges.value = edges.value.map(edge => {
    const isConnected = selectedNodes.value.has(edge.source) || selectedNodes.value.has(edge.target)
    return {
      ...edge,
      class: isConnected ? 'cuttable-edge selected' : 'cuttable-edge'
    }
  })
}

const closeContextMenu = () => {
  contextMenu.value = { show: false, x: 0, y: 0, nodeId: null }
  canvasContextMenu.value = { show: false, x: 0, y: 0 }
  pendingConnection.value = null
}

const toggleCanvasMenu = (event) => {
  if (canvasContextMenu.value.show) {
    closeContextMenu()
  } else {
    // If it's a click from the FAB, center it or put it in a reasonable place
    const x = event.clientX || window.innerWidth / 2 - 140
    const y = event.clientY || window.innerHeight / 2 - 200
    
    canvasContextMenu.value = {
      show: true,
      x: Math.max(20, Math.min(x, window.innerWidth - 300)),
      y: Math.max(20, Math.min(y, window.innerHeight - 400))
    }
  }
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
  saveHistory()
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
    saveHistory()
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
  
  saveHistory()
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
  
  saveHistory()
  
  // If there's a pending connection, create the edge
  if (pendingConnection.value) {
    const { sourceNodeId, sourceHandleId, sourceHandleType } = pendingConnection.value
    
    // Determine target handle (opposite of source)
    const targetHandle = sourceHandleType === 'source' ? 'target' : 'source'
    
    const sourceId = sourceHandleType === 'source' ? sourceNodeId : id
    const targetId = sourceHandleType === 'source' ? id : sourceNodeId
    edges.value = addEdge({
      id: `e_${sourceNodeId}_${id}_${Date.now()}`,
      source: sourceId,
      target: targetId,
      sourceHandle: sourceHandleId,
      targetHandle: targetHandle,
      animated: true,
      style: { stroke: '#F59E0B', strokeWidth: 2 },
      label: '✕',
      labelStyle: { fill: '#EF4444', fontWeight: 'bold', fontSize: '14px' },
      labelBgStyle: { fill: 'rgba(0,0,0,0.8)', stroke: '#EF4444', strokeWidth: 1, rx: 10, ry: 10 },
      labelBgPadding: [6, 6],
      labelBgBorderRadius: 10,
      class: selectedNodes.value.has(sourceId) || selectedNodes.value.has(targetId)
        ? 'cuttable-edge selected'
        : 'cuttable-edge'
    }, edges.value)
    
    pendingConnection.value = null
    saveHistory()
  }
  
  canvasContextMenu.value = { show: false, x: 0, y: 0 }
}

// Helper function to get section color
const getSectionColor = (section) => {
  const colors = {
    input: '#6366F1',
    generate: '#EC4899',
    transform: '#0EA5E9',
    annotation: '#F59E0B',
    output: '#10B981'
  }
  return colors[section] || '#6366F1'
}

// Helper function to convert hex to RGB for CSS variables
const hexToRgb = (hex) => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  return result 
    ? `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}`
    : '99, 102, 241'
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
    aiAssistant: { systemPrompt: 'You are a helpful AI assistant.', userPrompt: '', model: 'gpt-4o-mini', response: '' },
    imagePromptEnhancer: { originalPrompt: '', enhancedPrompt: '' },
    videoPromptEnhancer: { originalPrompt: '', enhancedPrompt: '' },
    stickyNote: { text: '', color: 'yellow' },
    output: {}
  }
  return { ...defaults[type] }
}

const clearCanvas = () => {
  nodes.value = []
  edges.value = []
  nodeIdCounter = 0
  executionStatus.value = null
  saveHistory()
}

// Export/Import functionality
const importFileInput = ref(null)

const exportWorkflow = () => {
  if (nodes.value.length === 0) return
  
  const workflowData = {
    version: '1.0',
    exportedAt: new Date().toISOString(),
    nodes: nodes.value,
    edges: edges.value
  }
  
  const blob = new Blob([JSON.stringify(workflowData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `videlo-workflow-${Date.now()}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  executionStatus.value = {
    type: 'success',
    message: t('workflow.exportSuccess')
  }
  setTimeout(() => {
    executionStatus.value = null
  }, 2000)
}

const triggerImport = () => {
  importFileInput.value?.click()
}

const handleImport = (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  
  if (file.type !== 'application/json' && !file.name.endsWith('.json')) {
    executionStatus.value = {
      type: 'error',
      message: t('workflow.importErrorInvalidFile')
    }
    setTimeout(() => {
      executionStatus.value = null
    }, 3000)
    return
  }
  
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const workflowData = JSON.parse(e.target.result)
      
      // Validate workflow data
      if (!workflowData.nodes || !Array.isArray(workflowData.nodes)) {
        throw new Error('Invalid workflow: missing nodes')
      }
      if (!workflowData.edges || !Array.isArray(workflowData.edges)) {
        throw new Error('Invalid workflow: missing edges')
      }
      
      // Clear current canvas and load imported workflow
      nodes.value = workflowData.nodes
      edges.value = workflowData.edges
      
      // Update node counter to be higher than any existing node
      const maxCounter = workflowData.nodes.reduce((max, node) => {
        const match = node.id?.match(/_(\d+)$/)
        const num = match ? parseInt(match[1]) : 0
        return Math.max(max, num)
      }, 0)
      nodeIdCounter = maxCounter
      
      saveHistory()
      
      executionStatus.value = {
        type: 'success',
        message: t('workflow.importSuccess')
      }
      setTimeout(() => {
        executionStatus.value = null
      }, 2000)
      
    } catch (err) {
      executionStatus.value = {
        type: 'error',
        message: t('workflow.importErrorParse') + ': ' + err.message
      }
      setTimeout(() => {
        executionStatus.value = null
      }, 3000)
    }
  }
  reader.onerror = () => {
    executionStatus.value = {
      type: 'error',
      message: t('workflow.importErrorRead')
    }
    setTimeout(() => {
      executionStatus.value = null
    }, 3000)
  }
  reader.readAsText(file)
  
  // Reset input so same file can be selected again
  event.target.value = ''
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
  const edgeId = `edge-${sourceNodeId}-${id}-${Date.now()}`
  edges.value = [...edges.value, {
    id: edgeId,
    source: sourceNodeId,
    target: id,
    animated: true,
    style: { stroke: '#F59E0B', strokeWidth: 2 },
    label: '✕',
    labelStyle: { fill: '#EF4444', fontWeight: 'bold', fontSize: '14px' },
    labelBgStyle: { fill: 'rgba(0,0,0,0.8)', stroke: '#EF4444', strokeWidth: 1, rx: 10, ry: 10 },
    labelBgPadding: [6, 6],
    labelBgBorderRadius: 10,
    class: selectedNodes.value.has(sourceNodeId) || selectedNodes.value.has(id)
      ? 'cuttable-edge selected'
      : 'cuttable-edge'
  }]

  saveHistory()
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
  // Reduced from 180 polls at 1s to 30 polls with exponential backoff
  // Total ~10 minutes max instead of 3 minutes with 180 requests
  const maxPolls = 30
  let polls = 0
  const minDelay = 5000  // Start at 5 seconds
  const maxDelay = 20000 // Max 20 seconds
  
  while (polls < maxPolls) {
    try {
      const status = await api.getGraphExecution(executionId)
      
      if (status.node_results) {
        for (const [nodeId, result] of Object.entries(status.node_results)) {
          const idx = nodes.value.findIndex(n => n.id === nodeId)
          if (idx !== -1) {
            nodes.value[idx].data = { ...nodes.value[idx].data, ...result }
            
            // Store the executed parameters hash for this node
            if (result.status === 'completed' || result.resultUrl) {
              const node = nodes.value[idx]
              const params = getNodeParams(node.type, node.data)
              lastExecutedParams.value[nodeId] = hashParams(params)
            }
            
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
                  id: `e_${nodeId}_${outputId}_${Date.now()}`,
                  source: nodeId,
                  target: outputId,
                  sourceHandle: 'source',
                  targetHandle: 'target',
                  animated: true,
                  style: { stroke: '#F59E0B', strokeWidth: 2 },
                  label: '✕',
                  labelStyle: { fill: '#EF4444', fontWeight: 'bold', fontSize: '14px' },
                  labelBgStyle: { fill: 'rgba(0,0,0,0.8)', stroke: '#EF4444', strokeWidth: 1, rx: 10, ry: 10 },
                  labelBgPadding: [6, 6],
                  labelBgBorderRadius: 10,
                  class: 'cuttable-edge'
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
    
    // Exponential backoff: 5s -> 7s -> 9s -> ... -> 20s max
    const delay = Math.min(minDelay + (polls * 2000), maxDelay)
    await new Promise(r => setTimeout(r, delay))
    polls++
  }
  
  executionStatus.value = { type: 'error', message: t('workflow.timeout') }
}

// Keyboard event handler
const handleKeydown = (e) => {
  // Undo: Ctrl+Z
  if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
    e.preventDefault()
    undo()
  }
  // Redo: Ctrl+Y or Ctrl+Shift+Z
  else if ((e.ctrlKey || e.metaKey) && (e.key === 'y' || (e.key === 'z' && e.shiftKey))) {
    e.preventDefault()
    redo()
  }
}

onMounted(() => {
  loadSavedWorkflows()
  loadSavedApiKey()
  loadSavediFlowKey()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
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
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.action-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
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

/* Empty State - Shortcuts Guide */
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
  width: 100%;
  max-width: 480px;
  padding: 0 20px;
}

.shortcuts-guide {
  background: rgba(18, 18, 26, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 28px 32px;
  margin-bottom: 28px;
  box-shadow: 
    0 32px 64px rgba(0, 0, 0, 0.4),
    0 0 0 1px rgba(255, 255, 255, 0.02);
  pointer-events: auto;
  width: 100%;
}

.guide-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 1.25rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 24px;
  letter-spacing: -0.02em;
}

.guide-title svg {
  width: 24px;
  height: 24px;
  color: #F59E0B;
}

.shortcuts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  text-align: left;
}

.shortcut-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  transition: all 0.2s ease;
}

.shortcut-item:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(245, 158, 11, 0.3);
  transform: translateY(-2px);
}

.shortcut-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(245, 158, 11, 0.05));
  border-radius: 10px;
  color: #F59E0B;
  flex-shrink: 0;
}

.shortcut-icon svg {
  width: 18px;
  height: 18px;
}

.shortcut-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.shortcut-key {
  font-size: 0.8rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.3px;
}

.shortcut-desc {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.4);
  font-weight: 500;
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

/* Canvas Context Menu (Quick Add) - Compact Icon-First Design */
.canvas-context-menu {
  position: fixed;
  z-index: 1001;
  background: rgba(18, 18, 26, 0.98);
  backdrop-filter: blur(32px);
  -webkit-backdrop-filter: blur(32px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  padding: 0;
  width: auto;
  min-width: 280px;
  max-width: 340px;
  max-height: 70vh;
  display: flex;
  flex-direction: column;
  box-shadow: 
    0 32px 64px rgba(0, 0, 0, 0.7),
    0 0 0 1px rgba(255, 255, 255, 0.05),
    0 0 40px rgba(245, 158, 11, 0.1);
  overflow: hidden;
  animation: menuAppear 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes menuAppear {
  from { opacity: 0; transform: scale(0.9) translateY(20px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

.context-menu-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.03), transparent);
}

.context-menu-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: #fff;
  text-transform: uppercase;
  letter-spacing: 1.5px;
}

.context-close-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.2s ease;
}

.context-close-btn:hover {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.3);
  color: #EF4444;
}

.context-close-btn svg {
  width: 14px;
  height: 14px;
}

.context-menu-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.1) transparent;
}

.context-menu-scroll::-webkit-scrollbar {
  width: 4px;
}

.context-menu-scroll::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

.context-section {
  margin-bottom: 14px;
}

.context-section:last-child {
  margin-bottom: 0;
}

.section-label {
  font-size: 0.6rem;
  font-weight: 800;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 8px;
  margin-left: 4px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.section-label::before {
  content: '';
  width: 12px;
  height: 3px;
  background: var(--section-color, rgba(255, 255, 255, 0.3));
  border-radius: 2px;
  box-shadow: 0 0 8px var(--section-color, rgba(255, 255, 255, 0.2));
  transition: all 0.2s ease;
}

.context-section:hover .section-label::before {
  width: 16px;
  box-shadow: 0 0 12px var(--section-color, rgba(255, 255, 255, 0.4));
}

/* 4-column compact grid */
.context-menu-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px;
}

/* Compact icon-only buttons */
.context-node-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 10px 4px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.context-node-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, var(--node-accent, #6366F1), transparent);
  opacity: 0;
  transition: opacity 0.2s ease;
}

.context-node-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: var(--node-accent, #6366F1);
  transform: translateY(-2px) scale(1.02);
  box-shadow: 
    0 4px 12px rgba(0, 0, 0, 0.3),
    0 0 20px rgba(var(--node-accent-rgb, 99, 102, 241), 0.2);
}

.context-node-btn:hover::before {
  opacity: 0.1;
}

.context-node-btn:active {
  transform: translateY(0) scale(0.98);
}

.context-node-icon {
  width: 22px;
  height: 22px;
  color: var(--node-accent, #fff);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.95;
  position: relative;
  z-index: 1;
  transition: transform 0.2s ease;
}

.context-node-btn:hover .context-node-icon {
  transform: scale(1.15);
}

.context-node-icon :deep(svg) {
  width: 18px;
  height: 18px;
  stroke-width: 2px;
}

/* Minimal text - single line, truncated */
.context-node-label {
  font-size: 0.6rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.65);
  text-align: center;
  line-height: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  padding: 0 2px;
  position: relative;
  z-index: 1;
}

.context-node-btn:hover .context-node-label {
  color: rgba(255, 255, 255, 0.9);
}

/* FAB Button */
.fab-btn {
  position: absolute;
  bottom: 80px;
  right: 20px;
  width: 56px;
  height: 56px;
  border-radius: 28px;
  background: linear-gradient(135deg, #F59E0B, #D97706);
  border: none;
  color: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(245, 158, 11, 0.3);
  cursor: pointer;
  z-index: 60;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.fab-btn:hover {
  transform: scale(1.1) rotate(90deg);
  box-shadow: 0 12px 32px rgba(245, 158, 11, 0.4);
}

.fab-btn svg {
  width: 24px;
  height: 24px;
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
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.15);
}

/* Enhanced focus states for accessibility */
.action-btn:focus-visible,
.zoom-btn:focus-visible,
.settings-btn:focus-visible,
.fab-btn:focus-visible,
.context-node-btn:focus-visible,
.quick-add-btn:focus-visible {
  outline: 2px solid var(--accent-primary);
  outline-offset: 2px;
}

/* Smooth scrolling for the whole page */
html {
  scroll-behavior: smooth;
}

/* Better text rendering */
.workflow-canvas {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
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

/* Cuttable Edge Styles - Show only when edge or connected node is selected */
:deep(.cuttable-edge) {
  cursor: pointer;
}

:deep(.cuttable-edge .vue-flow__edge-label) {
  cursor: pointer;
  pointer-events: all;
  opacity: 0;
  transition: all 0.2s ease;
  transform: scale(0.8);
}

/* Show cut button when edge is selected */
:deep(.cuttable-edge.selected .vue-flow__edge-label) {
  opacity: 1;
  transform: scale(1);
}

:deep(.cuttable-edge .vue-flow__edge-label > div) {
  background: rgba(239, 68, 68, 0.15) !important;
  border: 1px solid rgba(239, 68, 68, 0.5) !important;
  border-radius: 50% !important;
  width: 28px !important;
  height: 28px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  backdrop-filter: blur(4px);
  transition: all 0.2s ease;
}

:deep(.cuttable-edge.selected .vue-flow__edge-label > div) {
  background: rgba(239, 68, 68, 0.9) !important;
  border-color: #EF4444 !important;
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.5);
}

:deep(.cuttable-edge .vue-flow__edge-label span) {
  color: #EF4444 !important;
  font-size: 16px !important;
  font-weight: bold !important;
  line-height: 1 !important;
  transition: color 0.2s ease;
}

:deep(.cuttable-edge.selected .vue-flow__edge-label span) {
  color: #fff !important;
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
  fill: rgba(255, 255, 255, 0.3) !important;
}

/* Mobile Responsiveness - Comprehensive */
@media (max-width: 1024px) {
  .workflow-header {
    padding: 12px 16px;
  }

  .header-actions {
    gap: 8px;
  }

  .action-btn {
    padding: 8px 14px;
  }

  .action-btn span {
    font-size: 0.8rem;
  }
}

@media (max-width: 768px) {
  .workflow-header {
    padding: 10px 12px;
    flex-wrap: nowrap;
    gap: 8px;
  }

  .header-left {
    flex-shrink: 0;
  }

  .logo-link span {
    display: none; /* Hide logo text on mobile */
  }

  .logo-link svg {
    width: 24px;
    height: 24px;
  }

  .breadcrumb-sep,
  .breadcrumb-current {
    display: none;
  }

  .header-actions {
    flex: 1;
    display: flex;
    gap: 6px;
    overflow-x: auto;
    scrollbar-width: none; /* Firefox */
    -ms-overflow-style: none; /* IE/Edge */
    padding-bottom: 0;
  }

  .header-actions::-webkit-scrollbar {
    display: none; /* Chrome/Safari */
  }

  .action-btn {
    padding: 8px;
    min-width: 36px;
    min-height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .action-btn span:not(.badge) {
    display: none; /* Hide button text on mobile, keep icons */
  }

  .action-btn svg {
    width: 18px;
    height: 18px;
  }

  .action-btn.primary.run {
    padding: 8px 16px;
  }

  .action-btn.primary.run span {
    display: block;
    font-size: 0.8rem;
  }

  /* Reposition controls for mobile */
  .zoom-indicator {
    bottom: 16px;
    left: 16px;
    right: auto;
    padding: 3px;
  }

  .zoom-btn {
    width: 32px;
    height: 32px;
  }

  .zoom-value {
    font-size: 0.7rem;
    min-width: 40px;
  }

  .settings-btn {
    bottom: 16px;
    right: 16px;
    left: auto;
    width: 44px;
    height: 44px;
  }

  .settings-btn svg {
    width: 22px;
    height: 22px;
  }

  .fab-btn {
    bottom: 76px;
    right: 16px;
    width: 60px;
    height: 60px;
  }

  .fab-btn svg {
    width: 28px;
    height: 28px;
  }

  /* Context menu improvements - Mobile */
  .canvas-context-menu {
    width: calc(100vw - 24px);
    max-width: 360px;
    left: 50% !important;
    top: 50% !important;
    transform: translate(-50%, -50%) !important;
    max-height: 80vh;
    border-radius: 14px;
  }

  .context-menu-header {
    padding: 10px 14px;
  }

  .context-menu-title {
    font-size: 0.7rem;
  }

  .context-menu-scroll {
    padding: 8px;
  }

  /* 3-column on mobile for better fit */
  .context-menu-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 5px;
  }

  .context-node-btn {
    padding: 8px 3px;
    gap: 3px;
  }

  .context-node-icon {
    width: 20px;
    height: 20px;
  }

  .context-node-icon :deep(svg) {
    width: 16px;
    height: 16px;
  }

  .context-node-label {
    font-size: 0.55rem;
    letter-spacing: 0.3px;
  }

  .section-label {
    font-size: 0.55rem;
    margin-bottom: 6px;
  }

  /* Empty state improvements */
  .canvas-empty {
    padding: 20px;
    width: 100%;
    max-width: 100%;
  }

  .shortcuts-guide {
    padding: 20px;
    margin-bottom: 20px;
  }

  .guide-title {
    font-size: 1.1rem;
    margin-bottom: 20px;
  }

  .shortcuts-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .shortcut-item {
    padding: 10px;
  }

  .shortcut-icon {
    width: 32px;
    height: 32px;
  }

  .shortcut-key {
    font-size: 0.75rem;
  }

  .shortcut-desc {
    font-size: 0.65rem;
  }

  .empty-quick-add {
    flex-wrap: wrap;
    justify-content: center;
    gap: 8px;
  }

  .empty-quick-add span {
    width: 100%;
    text-align: center;
    margin-bottom: 4px;
  }

  .quick-add-btn {
    padding: 8px 12px;
    font-size: 0.75rem;
  }

  /* Status toast improvements */
  .status-toast {
    left: 16px;
    right: 16px;
    transform: none;
    min-width: auto;
    padding: 12px 16px;
    border-radius: 12px;
  }

  /* Modal improvements */
  .modal-container {
    margin: 16px;
    max-width: calc(100vw - 32px);
  }

  .modal-header {
    padding: 20px;
  }

  .modal-body {
    padding: 20px;
  }

  .modal-footer {
    padding: 16px 20px;
  }

  /* Dropdown improvements */
  .dropdown-panel {
    position: fixed;
    top: auto;
    bottom: 80px;
    left: 16px;
    right: 16px;
    min-width: auto;
    max-height: 60vh;
  }
}

@media (max-width: 480px) {
  .workflow-header {
    padding: 8px 10px;
  }

  .action-btn.primary.run {
    padding: 8px 12px;
  }

  .action-btn.primary.run span {
    font-size: 0.75rem;
  }

  /* Context menu - 3 columns on small screens */
  .context-menu-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 4px;
  }

  .canvas-context-menu {
    width: calc(100vw - 20px);
    max-height: 85vh;
  }

  .context-menu-scroll {
    padding: 6px;
  }

  .context-node-btn {
    padding: 6px 2px;
    min-height: 56px;
  }

  .context-node-icon {
    width: 18px;
    height: 18px;
  }

  .context-node-icon :deep(svg) {
    width: 15px;
    height: 15px;
  }

  .context-node-label {
    font-size: 0.5rem;
    letter-spacing: 0;
  }

  /* Shortcuts guide mobile */
  .shortcuts-guide {
    padding: 16px;
  }

  .guide-title {
    font-size: 1rem;
  }

  .shortcut-item {
    padding: 8px;
  }

  /* Touch improvements */
  .context-node-btn,
  .quick-add-btn,
  .action-btn,
  .zoom-btn {
    min-height: 44px; /* iOS touch target */
  }
}
</style>
