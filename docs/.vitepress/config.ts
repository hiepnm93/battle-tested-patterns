import { defineConfig } from 'vitepress';
import { withMermaid } from 'vitepress-plugin-mermaid';

export default withMermaid(defineConfig({
  title: 'Battle-Tested Patterns',
  description:
    'Battle-tested programming patterns from production codebases. Multi-language examples, precise source links, interactive playground.',

  base: '/battle-tested-patterns/',

  locales: {
    root: {
      label: 'English',
      lang: 'en',
      themeConfig: {
        nav: [
          { text: 'Guide', link: '/guide/what-is-this' },
          { text: 'Patterns', link: '/patterns/bitmask/' },
          { text: 'By Project', link: '/by-project/react' },
        ],
        sidebar: {
          '/guide/': [
            {
              text: 'Introduction',
              items: [
                { text: 'What is This?', link: '/guide/what-is-this' },
                { text: 'Pattern Connections', link: '/guide/pattern-connections' },
                { text: 'How to Contribute', link: '/guide/how-to-contribute' },
              ],
            },
          ],
          '/patterns/': [
            {
              text: 'Patterns',
              items: [
                { text: 'Bitmask', link: '/patterns/bitmask/' },
                { text: 'Double Buffering', link: '/patterns/double-buffering/' },
                { text: 'Cooperative Scheduling', link: '/patterns/cooperative-scheduling/' },
                { text: 'Min Heap', link: '/patterns/min-heap/' },
                { text: 'Diff / Patch', link: '/patterns/diff-patch/' },
                { text: 'Object Pool', link: '/patterns/object-pool/' },
                { text: 'Ring Buffer', link: '/patterns/ring-buffer/' },
                { text: 'State Machine', link: '/patterns/state-machine/' },
                { text: 'Copy-on-Write', link: '/patterns/copy-on-write/' },
                { text: 'Observer / Pub-Sub', link: '/patterns/observer/' },
                { text: 'Iterator / Lazy Eval', link: '/patterns/iterator/' },
                { text: 'Semaphore', link: '/patterns/semaphore/' },
                { text: 'Batch Processing', link: '/patterns/batch-processing/' },
                { text: 'Retry with Backoff', link: '/patterns/retry-backoff/' },
                { text: 'Flyweight / Interning', link: '/patterns/flyweight/' },
              ],
            },
          ],
          '/by-project/': [
            {
              text: 'By Source Project',
              items: [
                { text: 'React', link: '/by-project/react' },
                { text: 'Linux Kernel', link: '/by-project/linux' },
                { text: 'Go', link: '/by-project/go-runtime' },
                { text: 'Git', link: '/by-project/git' },
                { text: 'Node.js Ecosystem', link: '/by-project/nodejs' },
                { text: 'Rust', link: '/by-project/rust' },
                { text: 'Game Engines', link: '/by-project/game-engines' },
                { text: 'Distributed Systems', link: '/by-project/distributed-systems' },
              ],
            },
          ],
        },
      },
    },
    zh: {
      label: '简体中文',
      lang: 'zh-CN',
      themeConfig: {
        nav: [
          { text: '指南', link: '/zh/guide/what-is-this' },
          { text: '模式', link: '/zh/patterns/bitmask/' },
          { text: '按项目', link: '/zh/by-project/react' },
        ],
        sidebar: {
          '/zh/guide/': [
            {
              text: '入门',
              items: [
                { text: '这是什么？', link: '/zh/guide/what-is-this' },
                { text: '模式如何协作', link: '/zh/guide/pattern-connections' },
                { text: '如何贡献', link: '/zh/guide/how-to-contribute' },
              ],
            },
          ],
          '/zh/patterns/': [
            {
              text: '编程模式',
              items: [
                { text: '位掩码 (Bitmask)', link: '/zh/patterns/bitmask/' },
                { text: '双缓冲 (Double Buffering)', link: '/zh/patterns/double-buffering/' },
                { text: '协作调度 (Cooperative Scheduling)', link: '/zh/patterns/cooperative-scheduling/' },
                { text: '最小堆 (Min Heap)', link: '/zh/patterns/min-heap/' },
                { text: '差异/补丁 (Diff/Patch)', link: '/zh/patterns/diff-patch/' },
                { text: '对象池 (Object Pool)', link: '/zh/patterns/object-pool/' },
                { text: '环形缓冲区 (Ring Buffer)', link: '/zh/patterns/ring-buffer/' },
                { text: '状态机 (State Machine)', link: '/zh/patterns/state-machine/' },
                { text: '写时复制 (Copy-on-Write)', link: '/zh/patterns/copy-on-write/' },
                { text: '观察者 (Observer)', link: '/zh/patterns/observer/' },
                { text: '迭代器 (Iterator)', link: '/zh/patterns/iterator/' },
                { text: '信号量 (Semaphore)', link: '/zh/patterns/semaphore/' },
                { text: '批处理 (Batch Processing)', link: '/zh/patterns/batch-processing/' },
                { text: '指数退避重试 (Retry)', link: '/zh/patterns/retry-backoff/' },
                { text: '享元/驻留 (Flyweight)', link: '/zh/patterns/flyweight/' },
              ],
            },
          ],
          '/zh/by-project/': [
            {
              text: '按来源项目',
              items: [
                { text: 'React', link: '/zh/by-project/react' },
                { text: 'Linux 内核', link: '/zh/by-project/linux' },
                { text: 'Go', link: '/zh/by-project/go-runtime' },
                { text: 'Git', link: '/zh/by-project/git' },
                { text: 'Node.js 生态', link: '/zh/by-project/nodejs' },
                { text: 'Rust', link: '/zh/by-project/rust' },
                { text: '游戏引擎', link: '/zh/by-project/game-engines' },
                { text: '分布式系统', link: '/zh/by-project/distributed-systems' },
              ],
            },
          ],
        },
      },
    },
  },

  themeConfig: {
    socialLinks: [
      { icon: 'github', link: 'https://github.com/Totoro-jam/battle-tested-patterns' },
    ],

    search: {
      provider: 'local',
    },

    editLink: {
      pattern: 'https://github.com/Totoro-jam/battle-tested-patterns/edit/main/docs/:path',
      text: 'Edit this page on GitHub',
    },

    footer: {
      message: 'Released under the MIT License.',
      copyright: 'Copyright © 2026 Totoro-jam',
    },
  },

  mermaid: {},
}));
