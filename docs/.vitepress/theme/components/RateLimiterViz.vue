<script setup lang="ts">
import { ref, onUnmounted } from 'vue';

const capacity = 8;
const refillRate = 2;
const tokens = ref(capacity);
const requestLog = ref<{ time: number; accepted: boolean }[]>([]);
const message = ref('Click "Send Request" to consume tokens');
const autoRefillId = ref<ReturnType<typeof setInterval> | null>(null);
const running = ref(false);

function startRefill() {
  if (autoRefillId.value) return;
  running.value = true;
  autoRefillId.value = setInterval(() => {
    if (tokens.value < capacity) {
      tokens.value = Math.min(capacity, tokens.value + 1);
    }
  }, 1000 / refillRate);
  message.value = `Auto-refilling at ${refillRate} tokens/sec`;
}

function stopRefill() {
  if (autoRefillId.value) {
    clearInterval(autoRefillId.value);
    autoRefillId.value = null;
  }
  running.value = false;
  message.value = 'Auto-refill stopped';
}

function sendRequest() {
  const now = Date.now();
  if (tokens.value > 0) {
    tokens.value--;
    requestLog.value.push({ time: now, accepted: true });
    message.value = `Request accepted (${tokens.value} tokens left)`;
  } else {
    requestLog.value.push({ time: now, accepted: false });
    message.value = 'Request REJECTED — bucket empty!';
  }
  if (requestLog.value.length > 20) {
    requestLog.value = requestLog.value.slice(-20);
  }
}

function sendBurst() {
  for (let i = 0; i < 5; i++) {
    setTimeout(() => sendRequest(), i * 80);
  }
}

function reset() {
  stopRefill();
  tokens.value = capacity;
  requestLog.value = [];
  message.value = 'Bucket refilled to capacity';
}

onUnmounted(() => {
  if (autoRefillId.value) clearInterval(autoRefillId.value);
});

function tokenColor(i: number) {
  if (i < tokens.value) return 'var(--viz-primary)';
  return 'var(--viz-cell-empty)';
}
</script>

<template>
  <div class="viz-container">
    <div class="viz-title">Interactive Token Bucket Rate Limiter</div>

    <!-- Bucket visualization -->
    <div class="rl-bucket-wrap">
      <div class="rl-bucket-label">{{ tokens }}/{{ capacity }} tokens</div>
      <svg :viewBox="`0 0 ${capacity * 32 + 16} 48`" class="rl-svg">
        <rect
          v-for="i in capacity"
          :key="i"
          :x="(i - 1) * 32 + 8"
          y="8"
          width="26"
          height="32"
          rx="4"
          :fill="tokenColor(i - 1)"
          stroke="var(--viz-border)"
          stroke-width="1"
          :class="{ 'rl-token-active': i - 1 < tokens }"
        />
        <text
          v-for="i in capacity"
          :key="'t' + i"
          :x="(i - 1) * 32 + 21"
          y="28"
          text-anchor="middle"
          dominant-baseline="central"
          :fill="i - 1 < tokens ? '#fff' : 'var(--viz-muted)'"
          font-size="11"
          font-weight="700"
          font-family="var(--vp-font-family-mono)"
        >{{ i - 1 < tokens ? '●' : '○' }}</text>
      </svg>
    </div>

    <!-- Request log -->
    <div v-if="requestLog.length > 0" class="rl-log">
      <span class="viz-label">Requests:&nbsp;</span>
      <span
        v-for="(req, i) in requestLog.slice(-12)"
        :key="i"
        class="rl-log-dot"
        :class="req.accepted ? 'rl-dot-ok' : 'rl-dot-reject'"
        :title="req.accepted ? 'Accepted' : 'Rejected'"
      >{{ req.accepted ? '✓' : '✗' }}</span>
    </div>

    <div class="viz-controls">
      <button class="viz-btn viz-btn--primary" @click="sendRequest">Send Request</button>
      <button class="viz-btn" @click="sendBurst">Burst (×5)</button>
      <button v-if="!running" class="viz-btn" @click="startRefill">Start Refill</button>
      <button v-else class="viz-btn viz-btn--danger" @click="stopRefill">Stop Refill</button>
      <button class="viz-btn viz-btn--danger" @click="reset">Reset</button>
    </div>

    <div class="viz-status">{{ message }}</div>
  </div>
</template>

<style scoped>
.rl-bucket-wrap {
  text-align: center;
  margin: 0.5rem 0;
}

.rl-bucket-label {
  font-size: 0.8rem;
  font-weight: 600;
  font-family: var(--vp-font-family-mono);
  color: var(--viz-text);
  margin-bottom: 0.25rem;
}

.rl-svg {
  width: 100%;
  max-width: 320px;
  height: auto;
  display: block;
  margin: 0 auto;
}

.rl-token-active {
  animation: rl-fill 0.2s ease;
}

.rl-log {
  display: flex;
  align-items: center;
  gap: 3px;
  flex-wrap: wrap;
  padding: 0.5rem 0;
}

.rl-log-dot {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  font-size: 0.65rem;
  font-weight: 700;
}

.rl-dot-ok {
  background: var(--viz-success);
  color: #fff;
}

.rl-dot-reject {
  background: var(--viz-danger);
  color: #fff;
}

@keyframes rl-fill {
  from { opacity: 0.5; transform: scale(0.8); }
  to { opacity: 1; transform: scale(1); }
}
</style>
