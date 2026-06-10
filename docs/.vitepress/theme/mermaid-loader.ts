/**
 * Mermaid conditional loader.
 *
 * - Only loads the mermaid library on pages that contain .mermaid elements
 * - Listens for VitePress theme toggle (.dark class) and re-renders with correct theme
 * - Handles VitePress SPA navigation (re-checks on route change)
 */
export function initMermaidLoader(): () => Promise<void> {
  if (typeof window === 'undefined') return async () => {};

  let mermaidModule: typeof import('mermaid') | null = null;

  async function renderMermaid() {
    const elements = document.querySelectorAll<HTMLPreElement>('pre.mermaid');
    if (elements.length === 0) return;

    // Lazy load mermaid only when needed
    if (!mermaidModule) {
      mermaidModule = await import('mermaid');
    }

    const isDark = document.documentElement.classList.contains('dark');
    mermaidModule.default.initialize({
      startOnLoad: false,
      theme: isDark ? 'dark' : 'default',
    });

    // Preserve original source for re-rendering on theme change
    elements.forEach((el) => {
      if (!el.dataset.mermaidSource) {
        el.dataset.mermaidSource = el.textContent || '';
      }
    });

    // Restore original definitions before re-rendering
    elements.forEach((el) => {
      if (el.dataset.mermaidSource) {
        el.textContent = el.dataset.mermaidSource;
        el.removeAttribute('data-processed');
      }
    });

    await mermaidModule.default.run({ nodes: elements });
  }

  // Watch for theme changes (.dark class toggle on <html>)
  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (mutation.attributeName === 'class') {
        renderMermaid();
        break;
      }
    }
  });
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['class'],
  });

  return renderMermaid;
}
