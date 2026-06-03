<script setup lang="ts">
import { ref } from 'vue';

interface Subscriber {
  id: number;
  name: string;
  messages: string[];
}

let nextId = 0;

const subscribers = ref<Subscriber[]>([
  { id: nextId++, name: 'Logger', messages: [] },
  { id: nextId++, name: 'UI', messages: [] },
  { id: nextId++, name: 'Analytics', messages: [] },
]);

const events = ['click', 'submit', 'error', 'login'];
const lastEvent = ref('');
const broadcasting = ref(false);
const message = ref('Click "Emit Event" to broadcast to all subscribers');

function delay(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function emitEvent() {
  if (broadcasting.value) return;
  broadcasting.value = true;
  const event = events[Math.floor(Math.random() * events.length)];
  lastEvent.value = event;
  message.value = `Broadcasting "${event}" to ${subscribers.value.length} subscribers...`;

  for (const sub of subscribers.value) {
    sub.messages = [...sub.messages, event];
    if (sub.messages.length > 5) sub.messages = sub.messages.slice(-5);
    await delay(200);
  }

  message.value = `"${event}" delivered to all subscribers`;
  await delay(400);
  lastEvent.value = '';
  broadcasting.value = false;
}

function addSubscriber() {
  const names = ['DB Writer', 'Cache', 'Notifier', 'Metrics', 'Auditor'];
  const name = names[subscribers.value.length % names.length];
  if (subscribers.value.length >= 6) {
    message.value = 'Maximum 6 subscribers';
    return;
  }
  subscribers.value.push({ id: nextId++, name, messages: [] });
  message.value = `${name} subscribed`;
}

function removeSubscriber() {
  if (subscribers.value.length <= 1) {
    message.value = 'Need at least 1 subscriber';
    return;
  }
  const removed = subscribers.value.pop()!;
  message.value = `${removed.name} unsubscribed`;
}

function reset() {
  nextId = 0;
  subscribers.value = [
    { id: nextId++, name: 'Logger', messages: [] },
    { id: nextId++, name: 'UI', messages: [] },
    { id: nextId++, name: 'Analytics', messages: [] },
  ];
  lastEvent.value = '';
  broadcasting.value = false;
  message.value = 'Observer reset';
}
</script>

<template>
  <div class="viz-container">
    <div class="viz-title">Interactive Observer Pattern</div>

    <div class="obs-layout">
      <!-- Publisher -->
      <div class="obs-publisher" :class="{ 'obs-active': broadcasting }">
        <div class="obs-pub-label">Publisher</div>
        <div v-if="lastEvent" class="obs-event-badge">{{ lastEvent }}</div>
      </div>

      <!-- Fan-out arrows -->
      <div class="obs-arrows">
        <div v-for="sub in subscribers" :key="sub.id" class="obs-arrow">
          <span class="obs-arrow-line" :class="{ 'obs-arrow-active': broadcasting }">→</span>
        </div>
      </div>

      <!-- Subscribers -->
      <div class="obs-subscribers">
        <div
          v-for="sub in subscribers"
          :key="sub.id"
          class="obs-subscriber"
          :class="{ 'obs-sub-receiving': broadcasting }"
        >
          <div class="obs-sub-name">{{ sub.name }}</div>
          <div class="obs-sub-msgs">
            <span
              v-for="(m, i) in sub.messages.slice(-3)"
              :key="i"
              class="obs-msg-tag"
            >{{ m }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="viz-controls">
      <button class="viz-btn viz-btn--primary" @click="emitEvent" :disabled="broadcasting">Emit Event</button>
      <button class="viz-btn" @click="addSubscriber" :disabled="broadcasting">+ Subscribe</button>
      <button class="viz-btn" @click="removeSubscriber" :disabled="broadcasting">- Unsubscribe</button>
      <button class="viz-btn viz-btn--danger" @click="reset">Reset</button>
    </div>

    <div class="viz-status">{{ message }}</div>
  </div>
</template>

<style scoped>
.obs-layout {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 0;
}

@media (max-width: 640px) {
  .obs-layout {
    flex-direction: column;
  }
}

.obs-publisher {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 1rem 1.5rem;
  border: 2px solid var(--viz-primary);
  border-radius: 8px;
  background: var(--vp-c-bg);
  min-width: 90px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.obs-active {
  border-color: var(--viz-warning);
  box-shadow: 0 0 12px rgba(245, 158, 11, 0.3);
}

.obs-pub-label {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--viz-primary);
}

.obs-event-badge {
  padding: 2px 8px;
  border-radius: 10px;
  background: var(--viz-warning);
  color: #fff;
  font-size: 0.7rem;
  font-weight: 700;
  font-family: var(--vp-font-family-mono);
  animation: obs-pulse 0.3s ease;
}

.obs-arrows {
  display: flex;
  flex-direction: column;
  gap: 6px;
  color: var(--viz-muted);
  font-size: 1.2rem;
}

.obs-arrow-active {
  color: var(--viz-warning);
}

.obs-subscribers {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.obs-subscriber {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0.4rem 0.6rem;
  border: 1px solid var(--viz-border);
  border-radius: 6px;
  background: var(--vp-c-bg);
  transition: border-color 0.2s;
}

.obs-sub-receiving {
  border-color: var(--viz-success);
}

.obs-sub-name {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--viz-text);
  min-width: 70px;
}

.obs-sub-msgs {
  display: flex;
  gap: 3px;
  flex-wrap: wrap;
}

.obs-msg-tag {
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 0.65rem;
  font-family: var(--vp-font-family-mono);
  background: var(--viz-primary);
  color: #fff;
}

@keyframes obs-pulse {
  from { transform: scale(0.8); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}
</style>
