<template>
  <span :class="['status-badge', status]">
    {{ statusText }}
  </span>
</template>

<script>
export default {
  name: 'StatusBadge',
  props: {
    status: {
      type: String,
      required: true
    }
  },
  computed: {
    statusText() {
      const texts = {
        pending: 'Pending',
        processing: 'Processing',
        completed: 'Done',
        failed: 'Failed'
      }
      return texts[this.status] || this.status
    }
  }
}
</script>

<style scoped>
.status-badge {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.status-badge.pending {
  background: rgba(251, 191, 36, 0.15);
  color: #fbbf24;
}

.status-badge.processing {
  background: rgba(245, 158, 11, 0.15);
  color: var(--accent-primary);
  animation: pulse 1.5s ease-in-out infinite;
}

.status-badge.completed {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.status-badge.failed {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
</style>