import type MarkdownIt from 'markdown-it';

/**
 * Custom markdown-it plugin that converts ```mermaid code blocks
 * into <pre class="mermaid">...</pre> elements for client-side rendering.
 *
 * This replaces vitepress-plugin-mermaid's markdown processing while
 * allowing conditional loading of the mermaid library.
 */
export function mermaidMarkdownPlugin(md: MarkdownIt) {
  const defaultFence = md.renderer.rules.fence!.bind(md.renderer.rules);

  md.renderer.rules.fence = (tokens, idx, options, env, self) => {
    const token = tokens[idx]!;
    if (token.info.trim() === 'mermaid') {
      const content = token.content.trim();
      return `<pre class="mermaid">${md.utils.escapeHtml(content)}</pre>\n`;
    }
    return defaultFence(tokens, idx, options, env, self);
  };
}
