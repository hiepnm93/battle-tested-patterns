# Git 中的模式

| 模式 | 位置 | 作用 |
|------|------|------|
| [写时复制](/zh/patterns/copy-on-write/) | `object-file.c` | 内容寻址不可变对象，分支共享数据 |
| [差异/补丁](/zh/patterns/diff-patch/) | `diff.c`, `xdiff/` | Myers 差异算法 |
