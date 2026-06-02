# 模式：环形缓冲区 (Ring Buffer)

## 一句话

固定大小的缓冲区通过模运算实现循环，提供常数时间的入队出队且无需内存分配。

## 核心思想

环形缓冲区使用固定数组加两个指针——`head`（下次读取位置）和 `tail`（下次写入位置）。当指针到达末尾时回绕到开头。无移位、无扩容、无分配。

```text
  容量: 8       head=2, tail=6

  ┌───┬───┬───┬───┬───┬───┬───┬───┐
  │   │   │ A │ B │ C │ D │   │   │
  └───┴───┴─▲─┴───┴───┴─▲─┴───┴───┘
            │            │
          head         tail

  写入 'E' 到 tail (索引 6)，然后 tail = (6+1) % 8 = 7
  读取 'A' 从 head (索引 2)，然后 head = (2+1) % 8 = 3
```

`index % capacity` 的回绕使其成为"环"——永远不会用完数组空间。

## 生产验证

| 项目 | 源码 | 用途 |
|------|------|------|
| LMAX Disruptor | [RingBuffer.java#L84-L130](https://github.com/LMAX-Exchange/disruptor/blob/master/src/main/java/com/lmax/disruptor/RingBuffer.java#L84-L130) | Disruptor 的核心数据结构，支撑 LMAX 交易所每秒处理 600 万笔订单。使用 2 的幂大小以位运算取模。 |
| Linux 内核 | [ring_buffer.h#L12-L70](https://github.com/torvalds/linux/blob/master/include/linux/ring_buffer.h#L12-L70) | 内核 tracing 子系统 (ftrace) 使用环形缓冲区进行无锁事件记录，per-CPU 缓冲区实现零竞争。 |

## 实现

::: code-group

```typescript [TypeScript]
class RingBuffer<T> {
  private buffer: (T | undefined)[];
  private head = 0;
  private tail = 0;
  private count = 0;
  private capacity: number;

  constructor(capacity: number) {
    this.capacity = capacity;
    this.buffer = new Array(capacity);
  }

  enqueue(item: T): boolean {
    if (this.count === this.capacity) return false;
    this.buffer[this.tail] = item;
    this.tail = (this.tail + 1) % this.capacity;
    this.count++;
    return true;
  }

  dequeue(): T | undefined {
    if (this.count === 0) return undefined;
    const item = this.buffer[this.head];
    this.head = (this.head + 1) % this.capacity;
    this.count--;
    return item;
  }
}
```

```python [Python]
class RingBuffer:
    def __init__(self, capacity):
        self._buf = [None] * capacity
        self._head = self._tail = self._count = 0
        self._cap = capacity

    def enqueue(self, item):
        if self._count == self._cap: return False
        self._buf[self._tail] = item
        self._tail = (self._tail + 1) % self._cap
        self._count += 1
        return True

    def dequeue(self):
        if self._count == 0: return None
        item = self._buf[self._head]
        self._head = (self._head + 1) % self._cap
        self._count -= 1
        return item
```

:::

## 练习

| 难度 | 练习 | 文件 |
|------|------|------|
| 基础 | 实现环形缓冲区 enqueue/dequeue | `exercises/typescript/ring-buffer/01-basic.test.ts` |

## 何时使用

- **固定大小队列** — 有界生产者-消费者缓冲区
- **流数据** — 日志缓冲、音视频帧、网络包
- **无锁并发** — 原子 head/tail 实现 wait-free SPSC 队列
- **覆盖最旧** — 遥测数据、最近 N 条缓存

## 何时不用

- **无界增长** — 无法预测最大大小时用链表或 deque
- **按 key 随机访问** — 环形缓冲区是顺序的，用哈希表

## 更多生产案例

Linux `io_uring`, ZeroMQ, Kafka (log segments), audio DSP buffers, UART serial communication, Chrome trace event buffer.
