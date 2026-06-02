<div align="center">

# Battle-Tested Patterns

**从 React、Linux、Go、Chromium 等顶级开源项目源码中提炼的编程模式。**

精确源码链接 · 多语言实现 · 可运行练习

[📖 Documentation](https://totoro-jam.github.io/battle-tested-patterns/) · [📖 中文文档](https://totoro-jam.github.io/battle-tested-patterns/zh/)

[English](README.md) | 简体中文

[![CI](https://github.com/Totoro-jam/battle-tested-patterns/actions/workflows/ci.yml/badge.svg)](https://github.com/Totoro-jam/battle-tested-patterns/actions/workflows/ci.yml)
[![Deploy](https://github.com/Totoro-jam/battle-tested-patterns/actions/workflows/deploy.yml/badge.svg)](https://github.com/Totoro-jam/battle-tested-patterns/actions/workflows/deploy.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

</div>

---

## 为什么做这个

设计模式的书太抽象，算法仓库脱离工程实践，系统设计指南不涉及代码级技巧。

本项目填补这个空白：**从生产源码中提取的代码级模式**，每一个都有可验证的 GitHub 链接作为证明。

## 有什么不同

- **🔗 生产验证** — 每个模式链接到 React、Linux、Go 或 Chromium 中使用它的精确行号。不是空口白话。
- **🌍 多语言实现** — TypeScript、Rust、Go 的地道实现。不是逐行机械翻译。
- **🧪 可运行练习** — 渐进式难度（基础 → 进阶 → 高级），配套测试用例。
- **🎮 官方 Playground** — 一键跳转 TypeScript、Go、Rust、Python 官方在线环境，直接运行每个模式的代码。

## 编程模式

| 模式 | 核心洞察 | 来源项目 | 语言 |
|------|---------|---------|------|
| [位掩码 (Bitmask)](https://totoro-jam.github.io/battle-tested-patterns/zh/patterns/bitmask/) | 将多个标志打包到一个整数中 | React, Linux, Go | TS, Rust, Go, Python |
| 双缓冲 (Double Buffering) | 在两份副本间切换以实现原子更新 | React Fiber, PostgreSQL | TS, Rust, Go, Python |
| 协作调度 (Cooperative Scheduling) | 主动让出控制权以保持响应 | React, Go Runtime | TS, Rust, Go, Python |
| 最小堆 (Min Heap) | O(1) 访问最高优先级元素 | React Scheduler, Linux CFS | TS, Rust, Go, Python |
| 差异/补丁 (Diff/Patch) | 计算两个状态之间的最小变更 | React Reconciler, Git | TS, Rust, Go, Python |

## 快速开始

```bash
# 克隆和安装
git clone https://github.com/Totoro-jam/battle-tested-patterns.git
cd battle-tested-patterns
pnpm install

# 运行练习
pnpm test                              # TypeScript (Vitest)
cd exercises/rust && cargo test        # Rust
cd exercises/go && go test ./...       # Go

# 启动文档站
pnpm dev
```

## 项目结构

```text
battle-tested-patterns/
├── docs/                 # VitePress 文档站（中英文）
│   ├── patterns/         #   模式页面（每个模式一个目录）
│   └── zh/               #   中文翻译
├── exercises/            # 可运行练习
│   ├── typescript/       #   Vitest 测试文件
│   ├── rust/             #   Cargo 项目
│   └── go/               #   Go 模块
├── .sop/                 # 标准作业流程
├── .claude/skills/       # AI Agent Skills
└── .github/workflows/    # CI/CD 流水线
```

## 源码链接标准

每个生产验证必须是精确到行号的 GitHub URL：

```text
✅ https://github.com/facebook/react/blob/main/.../ReactFiberFlags.js#L14-L36
✅ https://github.com/torvalds/linux/blob/master/.../stat.h#L25-L33
❌ 目录级链接（不够精确）
❌ 未经验证的 URL
```

CI 每周自动检查链接有效性，失效链接会自动创建 Issue。

## 参与贡献

欢迎贡献！详见 [CONTRIBUTING.md](.github/CONTRIBUTING.md)（[中文版](.github/CONTRIBUTING.zh-CN.md)）。

**简要要求：**
1. 每个模式需要 ≥ 2 个生产验证，附带已验证的源码链接
2. 必须有 TypeScript 实现 + 至少一种其他语言
3. 至少 2 个练习测试文件，标注难度等级
4. 所有测试通过，无 lint 错误

## 技术栈

| 层级 | 工具 |
|------|------|
| Monorepo | pnpm workspace |
| 文档 | VitePress → GitHub Pages |
| 测试 | Vitest · cargo test · go test |
| 提交规范 | Conventional Commits + commitlint |
| 变更日志 | changelogen（自动生成） |
| CI/CD | GitHub Actions（6 个 workflow） |
| AI | Claude Code skills + git 守护钩子 |

## 许可证

[MIT](LICENSE) © Totoro-jam
