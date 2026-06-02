# 分布式系统中的模式

| 模式 | 项目 | 位置 | 作用 |
|------|------|------|------|
| [环形缓冲区](/zh/patterns/ring-buffer/) | LMAX Disruptor | `RingBuffer.java` | 每秒 600 万笔订单的核心数据结构 |
| [批处理](/zh/patterns/batch-processing/) | Apache Kafka | `RecordAccumulator.java` | 按分区累积记录为批次提升吞吐 |
