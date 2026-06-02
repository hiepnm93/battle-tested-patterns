<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';

const props = withDefaults(
  defineProps<{
    code?: string;
    lang?: 'typescript' | 'python';
    title?: string;
  }>(),
  {
    code: '',
    lang: 'typescript',
    title: 'Playground',
  },
);

const editorCode = ref(props.code);
const output = ref('');
const isRunning = ref(false);
const hasError = ref(false);

watch(
  () => props.code,
  (newCode) => {
    editorCode.value = newCode;
  },
);

function runTypeScript(code: string): string {
  const logs: string[] = [];
  const mockConsole = {
    log: (...args: unknown[]) => logs.push(args.map(String).join(' ')),
    error: (...args: unknown[]) => logs.push('ERROR: ' + args.map(String).join(' ')),
  };

  // Mini assertion library
  const assert = (condition: boolean, msg = 'Assertion failed') => {
    if (!condition) throw new Error(msg);
    logs.push(`✓ ${msg}`);
  };
  const assertEquals = (actual: unknown, expected: unknown, msg?: string) => {
    const pass = JSON.stringify(actual) === JSON.stringify(expected);
    if (!pass) throw new Error(msg || `Expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
    logs.push(`✓ ${msg || `${JSON.stringify(actual)} === ${JSON.stringify(expected)}`}`);
  };

  // Strip TypeScript type annotations for browser execution
  const jsCode = code
    .replace(/:\s*\w+(\[\])?\s*(?=[=,;\)\n\{])/g, '') // simple type annotations
    .replace(/\btype\s+\w+\s*=\s*[^;]+;/g, '')        // type aliases
    .replace(/\binterface\s+\w+\s*\{[^}]*\}/gs, '')    // interfaces
    .replace(/<\w+(\s*,\s*\w+)*>/g, '')                 // generics
    .replace(/\bas\s+\w+/g, '')                         // type assertions
    .replace(/!\./g, '.')                                // non-null assertions
    .replace(/\bexport\s+/g, '')                        // export keywords
    .replace(/\bconst\s+(\w+)\s*=\s*\{([^}]*)\}\s*as\s*const/g, 'const $1 = {$2}'); // as const

  try {
    const fn = new Function('console', 'assert', 'assertEquals', jsCode);
    fn(mockConsole, assert, assertEquals);
  } catch (e: unknown) {
    const err = e as Error;
    logs.push(`✗ ${err.message}`);
    throw e;
  }

  return logs.join('\n');
}

function runPython(code: string): string {
  return '⚠ Python execution requires Pyodide.\nThis feature is coming soon.\n\nCode preview:\n' + code;
}

async function handleRun() {
  isRunning.value = true;
  hasError.value = false;
  output.value = '';

  try {
    if (props.lang === 'typescript') {
      output.value = runTypeScript(editorCode.value);
    } else {
      output.value = runPython(editorCode.value);
    }
  } catch {
    hasError.value = true;
  } finally {
    isRunning.value = false;
  }
}

function handleReset() {
  editorCode.value = props.code;
  output.value = '';
  hasError.value = false;
}

onMounted(() => {
  editorCode.value = props.code;
});
</script>

<template>
  <div class="playground">
    <div class="playground-header">
      <span class="playground-title">{{ title }}</span>
      <span class="playground-lang">{{ lang }}</span>
      <div class="playground-actions">
        <button class="btn-reset" @click="handleReset" title="Reset">↺</button>
        <button class="btn-run" @click="handleRun" :disabled="isRunning">
          {{ isRunning ? '...' : '▶ Run' }}
        </button>
      </div>
    </div>
    <div class="playground-body">
      <textarea
        v-model="editorCode"
        class="playground-editor"
        spellcheck="false"
        :rows="Math.max(editorCode.split('\n').length, 8)"
      />
      <pre v-if="output" :class="['playground-output', { error: hasError }]">{{ output }}</pre>
    </div>
  </div>
</template>

<style scoped>
.playground {
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  overflow: hidden;
  margin: 16px 0;
}

.playground-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--vp-c-bg-soft);
  border-bottom: 1px solid var(--vp-c-divider);
}

.playground-title {
  font-weight: 600;
  font-size: 14px;
}

.playground-lang {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand-1);
}

.playground-actions {
  margin-left: auto;
  display: flex;
  gap: 6px;
}

.btn-run {
  padding: 4px 12px;
  border-radius: 6px;
  border: none;
  background: var(--vp-c-brand-1);
  color: var(--vp-c-white);
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
}

.btn-run:hover {
  opacity: 0.9;
}

.btn-run:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-reset {
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid var(--vp-c-divider);
  background: transparent;
  cursor: pointer;
  font-size: 16px;
}

.playground-body {
  display: flex;
  flex-direction: column;
}

.playground-editor {
  width: 100%;
  padding: 12px 16px;
  font-family: var(--vp-font-family-mono);
  font-size: 14px;
  line-height: 1.6;
  border: none;
  outline: none;
  resize: vertical;
  background: var(--vp-code-block-bg);
  color: var(--vp-c-text-1);
  tab-size: 2;
}

.playground-output {
  padding: 12px 16px;
  margin: 0;
  font-family: var(--vp-font-family-mono);
  font-size: 13px;
  line-height: 1.6;
  background: var(--vp-c-bg-soft);
  border-top: 1px solid var(--vp-c-divider);
  white-space: pre-wrap;
  color: var(--vp-c-text-2);
}

.playground-output.error {
  color: var(--vp-c-danger-1);
}
</style>
