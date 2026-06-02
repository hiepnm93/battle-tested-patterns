<div align="center">

# Battle-Tested Patterns

**Production-proven programming patterns from React, Linux, Go, and Chromium.**

Precise source links · Multi-language examples · Interactive playground

[📖 Documentation](https://totoro-jam.github.io/battle-tested-patterns/) · [📖 中文文档](https://totoro-jam.github.io/battle-tested-patterns/zh/)

English | [简体中文](README.zh-CN.md)

[![CI](https://github.com/Totoro-jam/battle-tested-patterns/actions/workflows/ci.yml/badge.svg)](https://github.com/Totoro-jam/battle-tested-patterns/actions/workflows/ci.yml)
[![Deploy](https://github.com/Totoro-jam/battle-tested-patterns/actions/workflows/deploy.yml/badge.svg)](https://github.com/Totoro-jam/battle-tested-patterns/actions/workflows/deploy.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

</div>

---

## Why This Exists

Design patterns books are too abstract. Algorithm repos are disconnected from engineering. System design guides don't touch code-level techniques.

This project fills the gap: **code-level patterns extracted from production source code**, each backed by verifiable GitHub links.

## What Makes This Different

- **🔗 Production Proof** — Every pattern links to the exact lines in React, Linux, Go, or Chromium where it's used. No hand-waving.
- **🌍 Multi-Language** — Idiomatic implementations in TypeScript, Rust, and Go. Not line-by-line translations.
- **🧪 Runnable Exercises** — Progressive difficulty (basic → intermediate → advanced) with test suites.
- **🎮 Interactive Playground** — Edit and run code in the browser. No local setup required.

## Patterns

| Pattern | Key Insight | Source Projects | Languages |
|---------|------------|-----------------|-----------|
| [Bitmask](https://totoro-jam.github.io/battle-tested-patterns/patterns/bitmask/) | Pack multiple flags into a single integer | React, Linux, Go | TS, Rust, Go, Python |
| Double Buffering | Swap between two copies for atomic updates | React Fiber, PostgreSQL | TS, Rust, Go, Python |
| Cooperative Scheduling | Voluntarily yield control to stay responsive | React, Go Runtime | TS, Rust, Go, Python |
| Min Heap | O(1) access to the highest-priority item | React Scheduler, Linux CFS | TS, Rust, Go, Python |
| Diff / Patch | Compute minimal changes between two states | React Reconciler, Git | TS, Rust, Go, Python |

## Quick Start

```bash
# Clone and install
git clone https://github.com/Totoro-jam/battle-tested-patterns.git
cd battle-tested-patterns
pnpm install

# Run exercises
pnpm test                              # TypeScript (Vitest)
cd exercises/rust && cargo test        # Rust
cd exercises/go && go test ./...       # Go

# Start docs site locally
pnpm dev
```

## Project Structure

```
battle-tested-patterns/
├── docs/                 # VitePress documentation site
│   ├── patterns/         #   English pattern pages
│   ├── zh/               #   Chinese translation
│   └── .vitepress/       #   Site configuration
├── exercises/            # Runnable exercises
│   ├── typescript/       #   Vitest test files
│   ├── rust/             #   Cargo project
│   └── go/               #   Go module
├── .sop/                 # Standard Operating Procedures
├── .claude/skills/       # AI agent skills
└── .github/workflows/    # CI/CD pipelines
```

## Source Link Standard

Every production proof must be a precise GitHub URL to specific lines:

```
✅ https://github.com/facebook/react/blob/main/.../ReactFiberFlags.js#L14-L36
✅ https://github.com/torvalds/linux/blob/master/.../stat.h#L25-L33
❌ Directory-level links (not precise enough)
❌ Unverified URLs
```

Links are automatically checked weekly via CI. Broken links trigger an Issue.

## Contributing

We welcome contributions! See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for details.

**In short:**
1. Every pattern needs ≥ 2 production proofs with verified source links
2. TypeScript implementation required + at least one other language
3. At least 2 exercise test files with difficulty labels
4. All tests pass, no lint errors

## Tech Stack

| Layer | Tool |
|-------|------|
| Monorepo | pnpm workspace |
| Docs | VitePress → GitHub Pages |
| Tests | Vitest · cargo test · go test |
| Commits | Conventional Commits + commitlint |
| Changelog | changelogen (auto-generated) |
| CI/CD | GitHub Actions (6 workflows) |
| AI | Claude Code skills + git guardrails |

## License

[MIT](LICENSE) © Totoro-jam
