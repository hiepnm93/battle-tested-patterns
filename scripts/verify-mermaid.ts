/**
 * Mermaid syntax validation script.
 *
 * Usage:
 *   tsx scripts/verify-mermaid.ts              # scan all docs/
 *   tsx scripts/verify-mermaid.ts file1.md ... # validate specific files
 *
 * Exit code: 0 = all valid, 1 = syntax errors found
 *
 * Design mirrors verify-source-links.ts and verify-code-blocks.ts.
 */

import { JSDOM } from 'jsdom';
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';

// ─── DOM shim (mermaid.parse() requires minimal DOM) ───
const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>', {
  url: 'http://localhost',
  pretendToBeVisual: true,
});

Object.defineProperty(globalThis, 'document', { value: dom.window.document, writable: true });
Object.defineProperty(globalThis, 'window', { value: dom.window, writable: true });
Object.defineProperty(globalThis, 'navigator', { value: dom.window.navigator, writable: true, configurable: true });
Object.defineProperty(globalThis, 'DOMParser', { value: dom.window.DOMParser, writable: true });
Object.defineProperty(globalThis, 'XMLSerializer', { value: dom.window.XMLSerializer, writable: true });
Object.defineProperty(globalThis, 'HTMLElement', { value: dom.window.HTMLElement, writable: true });
Object.defineProperty(globalThis, 'SVGElement', { value: dom.window.SVGElement, writable: true });

// ─── File discovery ───
const ROOT = join(import.meta.dirname, '..');
const DOCS_DIR = join(ROOT, 'docs');

function findMarkdownFiles(dir: string): string[] {
  const results: string[] = [];
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (entry === 'node_modules' || entry === '.vitepress') continue;
    if (statSync(full).isDirectory()) {
      results.push(...findMarkdownFiles(full));
    } else if (entry.endsWith('.md')) {
      results.push(full);
    }
  }
  return results;
}

interface MermaidError {
  file: string;
  line: number;
  blockIndex: number;
  error: string;
}

async function main() {
  // Dynamic import mermaid AFTER DOM shim is in place
  const mermaid = (await import('mermaid')).default;
  mermaid.initialize({ startOnLoad: false });

  const files =
    process.argv.length > 2
      ? process.argv.slice(2)
      : findMarkdownFiles(DOCS_DIR);

  const errors: MermaidError[] = [];
  let totalBlocks = 0;

  for (const file of files) {
    const content = readFileSync(file, 'utf-8');
    const regex = /```mermaid\n([\s\S]*?)```/g;
    let match: RegExpExecArray | null;
    let blockIndex = 0;

    while ((match = regex.exec(content)) !== null) {
      blockIndex++;
      totalBlocks++;
      const diagram = match[1]!;

      const result = await mermaid.parse(diagram, { suppressErrors: true });

      if (!result) {
        const line = content.substring(0, match.index).split('\n').length;
        let errorMsg = 'Unknown syntax error';
        try {
          await mermaid.parse(diagram);
        } catch (e: unknown) {
          errorMsg = e instanceof Error ? e.message : String(e);
        }
        errors.push({ file, line, blockIndex, error: errorMsg });
      }
    }
  }

  // ─── Report ───
  console.log(
    `\nMermaid syntax check: ${totalBlocks} block(s) in ${files.length} file(s)\n`,
  );

  if (errors.length === 0) {
    console.log('✓ All mermaid diagrams have valid syntax.');
    process.exit(0);
  } else {
    console.error(`✗ Found ${errors.length} syntax error(s):\n`);
    for (const err of errors) {
      const rel = relative(ROOT, err.file);
      console.error(`  ${rel}:${err.line} — block #${err.blockIndex}`);
      console.error(`    ${err.error}\n`);
    }
    process.exit(1);
  }
}

main();
