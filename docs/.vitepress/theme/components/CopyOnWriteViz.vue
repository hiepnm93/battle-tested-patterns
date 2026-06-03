<script setup lang="ts">
import { ref } from 'vue';

interface DataBlock {
  id: number;
  value: string;
  refCount: number;
}

interface Reader {
  name: string;
  dataId: number;
  color: string;
}

let nextId = 0;

const blocks = ref<DataBlock[]>([{ id: nextId++, value: 'Hello', refCount: 3 }]);
const readers = ref<Reader[]>([
  { name: 'A', dataId: 0, color: 'var(--viz-primary)' },
  { name: 'B', dataId: 0, color: 'var(--viz-success)' },
  { name: 'C', dataId: 0, color: 'var(--viz-warning)' },
]);

const message = ref('All readers share the same data. Click "Write" to trigger CoW.');
const lastAction = ref('');

function writeFromReader(readerIdx: number) {
  const reader = readers.value[readerIdx];
  const block = blocks.value.find(b => b.id === reader.dataId)!;

  if (block.refCount === 1) {
    block.value = block.value + '!';
    lastAction.value = `direct-${reader.name}`;
    message.value = `${reader.name} has exclusive ownership — modified in place`;
  } else {
    block.refCount--;
    const newBlock: DataBlock = { id: nextId++, value: block.value + '*', refCount: 1 };
    blocks.value.push(newBlock);
    reader.dataId = newBlock.id;
    lastAction.value = `cow-${reader.name}`;
    message.value = `Copy-on-Write: ${reader.name} got a private copy "${newBlock.value}"`;
  }
}

function reset() {
  nextId = 0;
  blocks.value = [{ id: nextId++, value: 'Hello', refCount: 3 }];
  readers.value = [
    { name: 'A', dataId: 0, color: 'var(--viz-primary)' },
    { name: 'B', dataId: 0, color: 'var(--viz-success)' },
    { name: 'C', dataId: 0, color: 'var(--viz-warning)' },
  ];
  lastAction.value = '';
  message.value = 'Reset — all readers share the same data again';
}

function getBlock(id: number) {
  return blocks.value.find(b => b.id === id);
}
</script>

<template>
  <div class="viz-container">
    <div class="viz-title">Interactive Copy-on-Write</div>

    <div class="cow-layout">
      <!-- Readers -->
      <div class="cow-readers">
        <div
          v-for="(r, i) in readers"
          :key="r.name"
          class="cow-reader"
          :style="{ borderColor: r.color }"
        >
          <div class="cow-reader-name" :style="{ color: r.color }">{{ r.name }}</div>
          <button class="viz-btn cow-write-btn" @click="writeFromReader(i)">Write</button>
        </div>
      </div>

      <!-- Connection lines (conceptual) -->
      <div class="cow-arrows">
        <div v-for="r in readers" :key="'arr-' + r.name" class="cow-arrow">→</div>
      </div>

      <!-- Data blocks -->
      <div class="cow-blocks">
        <div
          v-for="block in blocks"
          :key="block.id"
          class="cow-block"
          :class="{ 'cow-block-new': lastAction.startsWith('cow') && block.id === blocks[blocks.length - 1]?.id }"
        >
          <div class="cow-block-value">"{{ block.value }}"</div>
          <div class="cow-block-refs">
            <span
              v-for="r in readers.filter(rd => rd.dataId === block.id)"
              :key="r.name"
              class="cow-ref-dot"
              :style="{ background: r.color }"
            >{{ r.name }}</span>
          </div>
          <div class="cow-block-rc">rc={{ block.refCount }}</div>
        </div>
      </div>
    </div>

    <div class="viz-controls">
      <button class="viz-btn viz-btn--danger" @click="reset">Reset</button>
    </div>

    <div class="viz-status">{{ message }}</div>
  </div>
</template>

<style scoped>
.cow-layout {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem 0;
}

@media (max-width: 640px) {
  .cow-layout { flex-direction: column; align-items: stretch; }
}

.cow-readers {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.cow-reader {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0.4rem 0.6rem;
  border: 2px solid;
  border-radius: 6px;
  background: var(--vp-c-bg);
}

.cow-reader-name {
  font-size: 0.8rem;
  font-weight: 700;
  font-family: var(--vp-font-family-mono);
  min-width: 20px;
}

.cow-write-btn {
  padding: 0.2rem 0.5rem;
  font-size: 0.7rem;
}

.cow-arrows {
  display: flex;
  flex-direction: column;
  gap: 14px;
  color: var(--viz-muted);
  font-size: 1rem;
  padding-top: 8px;
}

.cow-blocks {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.cow-block {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--viz-border);
  border-radius: 6px;
  background: var(--vp-c-bg);
}

.cow-block-new {
  animation: cow-appear 0.3s ease;
}

.cow-block-value {
  font-size: 0.85rem;
  font-weight: 700;
  font-family: var(--vp-font-family-mono);
  color: var(--viz-text);
}

.cow-block-refs {
  display: flex;
  gap: 3px;
}

.cow-ref-dot {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  font-size: 0.6rem;
  font-weight: 700;
  color: #fff;
}

.cow-block-rc {
  font-size: 0.7rem;
  color: var(--viz-muted);
  font-family: var(--vp-font-family-mono);
  margin-left: auto;
}

@keyframes cow-appear {
  from { opacity: 0; transform: translateX(10px); }
  to { opacity: 1; transform: translateX(0); }
}
</style>
