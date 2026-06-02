<script setup lang="ts">
import { ref, onMounted, watch, shallowRef, onBeforeUnmount, nextTick, computed } from 'vue';

const props = withDefaults(
  defineProps<{
    code?: string;
    lang?: string;
    title?: string;
    languages?: Record<string, string>;
  }>(),
  { code: '', lang: 'typescript', title: 'Playground' },
);

const editorContainer = ref<HTMLDivElement>();
const output = ref('');
const isRunning = ref(false);
const hasError = ref(false);
const activeLang = ref(props.lang);
const editorInstance = shallowRef<any>(null);
const monacoRef = shallowRef<any>(null);
const pyodideRef = shallowRef<any>(null);
const pyodideLoading = ref(false);

const langLabels: Record<string, string> = {
  typescript: 'TypeScript',
  python: 'Python',
  go: 'Go',
  rust: 'Rust',
  c: 'C',
};

const monacoLangMap: Record<string, string> = {
  typescript: 'javascript',
  python: 'python',
  go: 'go',
  rust: 'rust',
  c: 'c',
};

const availableLangs = computed(() => {
  if (props.languages) return Object.keys(props.languages);
  return [props.lang];
});

function getInitialCode(): string {
  return props.languages?.[activeLang.value] || props.code;
}

async function initMonaco() {
  if (typeof window === 'undefined') return;
  try {
    const loader = await import('@monaco-editor/loader');
    const monaco = await loader.default.init();
    monacoRef.value = monaco;
    if (!editorContainer.value) return;

    const editor = monaco.editor.create(editorContainer.value, {
      value: getInitialCode(),
      language: monacoLangMap[activeLang.value] || 'plaintext',
      theme: 'vs-dark',
      minimap: { enabled: false },
      fontSize: 14,
      lineNumbers: 'on',
      scrollBeyondLastLine: false,
      automaticLayout: true,
      tabSize: 2,
      padding: { top: 12, bottom: 12 },
      overviewRulerLanes: 0,
      scrollbar: { vertical: 'hidden', horizontal: 'auto' },
      renderLineHighlight: 'none',
    });

    editorInstance.value = editor;

    const updateHeight = () => {
      const lines = editor.getModel()?.getLineCount() || 8;
      editorContainer.value!.style.height = `${Math.min(Math.max(lines * 20 + 24, 180), 500)}px`;
      editor.layout();
    };
    editor.onDidChangeModelContent(updateHeight);
    updateHeight();
  } catch {
    // Monaco failed to load — fallback handled by template
  }
}

function switchLang(lang: string) {
  activeLang.value = lang;
  output.value = '';
  hasError.value = false;
  if (editorInstance.value && monacoRef.value) {
    editorInstance.value.setValue(props.languages?.[lang] || props.code);
    const model = editorInstance.value.getModel();
    if (model) monacoRef.value.editor.setModelLanguage(model, monacoLangMap[lang] || 'plaintext');
  }
}

function runTypeScript(code: string): string {
  const logs: string[] = [];
  const mockConsole = {
    log: (...args: unknown[]) => logs.push(args.map(String).join(' ')),
    error: (...args: unknown[]) => logs.push('ERROR: ' + args.map(String).join(' ')),
  };
  const assert = (cond: boolean, msg = 'Assertion failed') => {
    if (!cond) throw new Error(msg);
    logs.push(`✓ ${msg}`);
  };
  const assertEquals = (actual: unknown, expected: unknown, msg?: string) => {
    const pass = JSON.stringify(actual) === JSON.stringify(expected);
    if (!pass) throw new Error(msg || `Expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
    logs.push(`✓ ${msg || `${JSON.stringify(actual)} === ${JSON.stringify(expected)}`}`);
  };

  const fn = new Function('console', 'assert', 'assertEquals', code);
  fn(mockConsole, assert, assertEquals);
  return logs.join('\n');
}

async function loadPyodide() {
  if (pyodideRef.value) return pyodideRef.value;
  pyodideLoading.value = true;
  try {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/pyodide/v0.27.7/full/pyodide.js';
    document.head.appendChild(script);
    await new Promise<void>((resolve, reject) => {
      script.onload = () => resolve();
      script.onerror = () => reject(new Error('Failed to load Pyodide'));
    });
    const pyodide = await (window as any).loadPyodide();
    pyodideRef.value = pyodide;
    return pyodide;
  } finally {
    pyodideLoading.value = false;
  }
}

async function runPython(code: string): Promise<string> {
  const pyodide = await loadPyodide();
  const logs: string[] = [];
  pyodide.setStdout({ batched: (text: string) => logs.push(text) });
  pyodide.setStderr({ batched: (text: string) => logs.push('ERROR: ' + text) });
  await pyodide.runPythonAsync(code);
  return logs.join('\n');
}

async function handleRun() {
  isRunning.value = true;
  hasError.value = false;
  output.value = '';
  try {
    const code = editorInstance.value?.getValue() || getInitialCode();
    if (activeLang.value === 'typescript') {
      output.value = runTypeScript(code);
    } else if (activeLang.value === 'python') {
      output.value = pyodideLoading.value ? '⏳ Loading Python runtime...' : '';
      output.value = await runPython(code);
    } else {
      output.value = `⚠ Browser execution not available for ${langLabels[activeLang.value] || activeLang.value}.\nRun locally with the appropriate toolchain.`;
    }
  } catch (e: unknown) {
    hasError.value = true;
    output.value = `✗ ${(e as Error).message}`;
  } finally {
    isRunning.value = false;
  }
}

function handleReset() {
  editorInstance.value?.setValue(props.languages?.[activeLang.value] || props.code);
  output.value = '';
  hasError.value = false;
}

onMounted(() => nextTick(initMonaco));
onBeforeUnmount(() => editorInstance.value?.dispose());
</script>

<template>
  <div class="playground">
    <div class="playground-header">
      <span class="playground-title">{{ title }}</span>
      <select
        v-if="availableLangs.length > 1"
        class="playground-select"
        :value="activeLang"
        @change="switchLang(($event.target as HTMLSelectElement).value)"
      >
        <option v-for="l in availableLangs" :key="l" :value="l">
          {{ langLabels[l] || l }}
        </option>
      </select>
      <span v-else class="playground-lang">{{ langLabels[activeLang] || activeLang }}</span>
      <div class="playground-actions">
        <button class="btn-reset" @click="handleReset" title="Reset">↺</button>
        <button class="btn-run" @click="handleRun" :disabled="isRunning">
          {{ isRunning ? (pyodideLoading ? '⏳ Loading...' : '⏳ Running...') : '▶ Run' }}
        </button>
      </div>
    </div>
    <div class="playground-body">
      <div ref="editorContainer" class="playground-editor" />
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
  flex-wrap: wrap;
}
.playground-title { font-weight: 600; font-size: 14px; }
.playground-select {
  padding: 3px 8px;
  border-radius: 6px;
  border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 13px;
  cursor: pointer;
}
.playground-lang {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand-1);
}
.playground-actions { margin-left: auto; display: flex; gap: 6px; }
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
.btn-run:hover { opacity: 0.9; }
.btn-run:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-reset {
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid var(--vp-c-divider);
  background: transparent;
  cursor: pointer;
  font-size: 16px;
}
.playground-body { display: flex; flex-direction: column; }
.playground-editor { width: 100%; min-height: 180px; max-height: 500px; }
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
.playground-output.error { color: var(--vp-c-danger-1); }
</style>
