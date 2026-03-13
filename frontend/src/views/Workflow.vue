<template>
  <div class="workflow-view">
    <WorkflowCanvas />
  </div>
</template>

<script setup>
import WorkflowCanvas from '../components/WorkflowCanvas.vue'
</script>

<style scoped>
.workflow-view {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
</style>
