<script setup lang="ts">
import { ref, onUnmounted } from 'vue';

const QUEUE_CAP = 12;
const queue = ref<number[]>([]);
const produced = ref(0);
const consumed = ref(0);
const dropped = ref(0);
const producerRate = ref(3);
const consumerRate = ref(1);
const message = ref('Start producer & consumer to see backpressure in action');
const producerTimer = ref<ReturnType<typeof setInterval> | null>(null);
const consumerTimer = ref<ReturnType<typeof setInterval> | null>(null);
let nextItem = 1;

function startProducer() {
  if (producerTimer.value) return;
  producerTimer.value = setInterval(() => {
    if (queue.value.length >= QUEUE_CAP) {
      dropped.value++;
      message.value = `Backpressure! Item #${nextItem} DROPPED (queue full)`;
      nextItem++;
    } else {
      queue.value.push(nextItem);
      produced.value++;
      message.value = `Produced #${nextItem}`;
      nextItem++;
    }
  }, 1000 / producerRate.value);
}

function startConsumer() {
  if (consumerTimer.value) return;
  consumerTimer.value = setInterval(() => {
    if (queue.value.length > 0) {
      const item = queue.value.shift()!;
      consumed.value++;
      message.value = `Consumed #${item}`;
    }
  }, 1000 / consumerRate.value);
}

function stopAll() {
  if (producerTimer.value) { clearInterval(producerTimer.value); producerTimer.value = null; }
  if (consumerTimer.value) { clearInterval(consumerTimer.value); consumerTimer.value = null; }
  message.value = 'Stopped';
}

function reset() {
  stopAll();
  queue.value = [];
  produced.value = 0;
  consumed.value = 0;
  dropped.value = 0;
  nextItem = 1;
  message.value = 'Reset';
}

onUnmounted(() => {
  if (producerTimer.value) clearInterval(producerTimer.value);
  if (consumerTimer.value) clearInterval(consumerTimer.value);
});

function fillPercent() {
  return (queue.value.length / QUEUE_CAP) * 100;
}

function fillColor() {
  const pct = fillPercent();
  if (pct >= 80) return 'var(--viz-danger)';
  if (pct >= 50) return 'var(--viz-warning)';
  return 'var(--viz-primary)';
}
</script>

<template>
  <div class="viz-container">
    <div class="viz-title">Interactive Backpressure</div>

    <div class="bp-flow">
      <!-- Producer -->
      <div class="bp-actor bp-producer">
        <div class="bp-actor-label">Producer</div>
        <div class="bp-actor-rate">{{ producerRate }}/s</div>
      </div>

      <div class="bp-arrow">→</div>

      <!-- Queue -->
      <div class="bp-queue-wrap">
        <div class="bp-queue-label">Queue ({{ queue.length }}/{{ QUEUE_CAP }})</div>
        <div class="bp-queue">
          <div
            v-for="i in QUEUE_CAP"
            :key="i"
            class="bp-slot"
            :class="{ 'bp-slot-filled': i <= queue.length }"
            :style="{ background: i <= queue.length ? fillColor() : undefined }"
          ></div>
        </div>
        <div class="bp-queue-bar">
          <div class="bp-queue-fill" :style="{ width: fillPercent() + '%', background: fillColor() }"></div>
        </div>
      </div>

      <div class="bp-arrow">→</div>

      <!-- Consumer -->
      <div class="bp-actor bp-consumer">
        <div class="bp-actor-label">Consumer</div>
        <div class="bp-actor-rate">{{ consumerRate }}/s</div>
      </div>
    </div>

    <!-- Stats -->
    <div class="bp-stats">
      <span class="bp-stat">Produced: <strong>{{ produced }}</strong></span>
      <span class="bp-stat">Consumed: <strong>{{ consumed }}</strong></span>
      <span class="bp-stat bp-stat-drop">Dropped: <strong>{{ dropped }}</strong></span>
    </div>

    <div class="viz-controls">
      <button class="viz-btn viz-btn--primary" @click="startProducer" :disabled="!!producerTimer">Start Producer</button>
      <button class="viz-btn" @click="startConsumer" :disabled="!!consumerTimer">Start Consumer</button>
      <button class="viz-btn" @click="stopAll">Stop All</button>
      <button class="viz-btn viz-btn--danger" @click="reset">Reset</button>
    </div>

    <div class="viz-status">{{ message }}</div>
  </div>
</template>

<style scoped>
.bp-flow {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 0;
  justify-content: center;
}

@media (max-width: 640px) {
  .bp-flow {
    flex-direction: column;
  }
}

.bp-actor {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 0.6rem 1rem;
  border-radius: 8px;
  border: 2px solid var(--viz-border);
  background: var(--vp-c-bg);
  min-width: 70px;
}

.bp-producer { border-color: var(--viz-primary); }
.bp-consumer { border-color: var(--viz-success); }

.bp-actor-label {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--viz-text);
}

.bp-actor-rate {
  font-size: 0.75rem;
  font-family: var(--vp-font-family-mono);
  color: var(--viz-muted);
}

.bp-arrow {
  font-size: 1.2rem;
  color: var(--viz-muted);
}

.bp-queue-wrap {
  text-align: center;
}

.bp-queue-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--viz-muted);
  margin-bottom: 4px;
}

.bp-queue {
  display: flex;
  gap: 2px;
}

.bp-slot {
  width: 16px;
  height: 24px;
  border-radius: 3px;
  background: var(--viz-cell-empty);
  transition: background 0.15s;
}

.bp-slot-filled {
  animation: bp-pop 0.15s ease;
}

.bp-queue-bar {
  margin-top: 4px;
  height: 4px;
  border-radius: 2px;
  background: var(--viz-cell-empty);
  overflow: hidden;
}

.bp-queue-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.2s, background 0.2s;
}

.bp-stats {
  display: flex;
  gap: 1rem;
  padding: 0.5rem 0;
  flex-wrap: wrap;
}

.bp-stat {
  font-size: 0.75rem;
  color: var(--viz-text);
  font-family: var(--vp-font-family-mono);
}

.bp-stat-drop {
  color: var(--viz-danger);
}

@keyframes bp-pop {
  from { transform: scaleY(0.5); }
  to { transform: scaleY(1); }
}
</style>
