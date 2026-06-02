# 模式：写时复制 (Copy-on-Write)

## 一句话

通过引用共享数据，直到有人修改时才创建私有副本——为读多写少的场景节省内存和分配开销。

## 核心思想

写时复制将复制的开销推迟到实际发生修改时。多个读取方可以共享同一份数据。当写入方需要修改时，系统为该写入方创建副本，其他引用不受影响。

```mermaid
flowchart LR
    A["读取方 A"] --> D["共享数据"]
    B["读取方 B"] --> D
    C["写入方 C"] -->|"要修改"| D
    D -->|"写时复制"| E["C 的副本"]
    C --> E
```

核心洞察：**大多数数据被读取的次数远多于被写入的次数**。CoW 利用这种不对称——读取免费共享，写入按需付费。

## 生产验证

| 项目 | 源码 | 用途 |
|------|------|------|
| Git | [object-file.c#L719-L730](https://github.com/git/git/blob/master/object-file.c#L719-L730) | Git 对象是不可变的内容寻址 blob。分支时不复制文件——共享相同对象。新 commit 只为变更的文件创建新对象。 |
| Rust 标准库 | [borrow.rs#L169-L220](https://github.com/rust-lang/rust/blob/main/library/alloc/src/borrow.rs#L169-L220) | `Cow<'a, B>` — 持有 `Borrowed` 引用或 `Owned` 值的枚举。`to_mut()` 仅在当前是借用时才克隆。广泛用于零拷贝解析。 |

## 实现

::: code-group

```typescript [TypeScript]
class Cow<T extends object> {
  private data: T;
  private shared: boolean;

  constructor(data: T) { this.data = data; this.shared = false; }

  static from<T extends object>(data: T): Cow<T> {
    const cow = new Cow(data);
    cow.shared = true;
    return cow;
  }

  read(): Readonly<T> { return this.data; }

  write(): T {
    if (this.shared) {
      this.data = structuredClone(this.data);
      this.shared = false;
    }
    return this.data;
  }
}
```

```python [Python]
import copy

class Cow:
    def __init__(self, data, shared=False):
        self._data = data
        self._shared = shared

    @classmethod
    def share(cls, data):
        return cls(data, shared=True)

    def read(self):
        return self._data

    def write(self):
        if self._shared:
            self._data = copy.deepcopy(self._data)
            self._shared = False
        return self._data
```

:::

## 练习

| 难度 | 练习 | 文件 |
|------|------|------|
| 基础 | 实现写时复制包装器 | `exercises/typescript/copy-on-write/01-basic.test.ts` |

## 何时使用

- **读多写少** — 配置对象、解析后的 AST、缓存响应
- **分支/版本控制** — Git 对象模型、数据库快照
- **零拷贝解析** — Rust 的 `Cow<str>` 在输入已有效时避免分配
- **撤销系统** — 共享状态快照，仅在修改时复制

## 何时不用

- **写多读少** — 每次写入触发复制，抵消收益
- **小数据** — 复制小结构比 CoW 记账更便宜
- **并发写入** — CoW 不解决并发修改问题

## 更多生产案例

Linux `fork()` (page table CoW), Swift value types, PHP strings (before PHP 7), Redis `BGSAVE`, ZFS/Btrfs filesystem snapshots.
