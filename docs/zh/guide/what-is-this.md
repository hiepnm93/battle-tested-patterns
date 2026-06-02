# 这是什么？

**Battle-Tested Patterns** 收集的编程模式具有以下特点：

1. **经过生产验证** — 在 React、Linux 内核、Go 运行时、Chromium 等顶级项目中使用
2. **跨语言通用** — 适用于 TypeScript、Rust、Go、C 及更多语言
3. **代码级技巧** — 可以立即应用的具体技术，而非抽象的架构概念

## 为什么做这个

市面上有大量"设计模式"书籍和"算法"仓库，但存在一个空白：

| 现有资源 | 缺失的部分 |
|---------|-----------|
| 设计模式 (GoF) | 太抽象，过于面向对象 |
| 算法仓库 | 脱离工程实践 |
| 系统设计指南 | 架构层面，不涉及代码级技巧 |
| "Awesome" 列表 | 链接集合，没有教学内容 |

本项目填补这个空白：**从生产源码中提取的代码级技巧，附带可验证的精确引用**。

## 什么是"经过实战检验"？

本集合中的每个模式必须满足：

- **≥ 2 个生产验证** — 精确到行号的 GitHub 链接，展示模式的实际使用
- **多语言实现** — TypeScript + 至少一种其他语言的地道代码
- **可运行练习** — 渐进式难度，配套测试用例

我们绝不编造源码链接。如果找不到可验证的引用，就不收录该模式。

## 如何使用

- **浏览模式** — 阅读概念，研究生产验证，然后尝试练习
- **本地运行练习** — TypeScript: `pnpm test` · Rust: `cargo test` · Go: `go test`
- **在线尝试** — 将代码示例复制到官方 Playground 运行：
  - [TypeScript Playground](https://www.typescriptlang.org/play) · [Go Playground](https://go.dev/play/) · [Rust Playground](https://play.rust-lang.org/) · [Python Online](https://www.online-python.com/)
- **参与贡献** — 参见[如何贡献](./how-to-contribute)
