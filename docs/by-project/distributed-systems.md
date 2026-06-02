# Patterns from Distributed Systems

High-throughput messaging and trading systems push throughput patterns to the extreme.

| Pattern | Project | Where | What It Does |
|---------|---------|-------|--------------|
| [Ring Buffer](/patterns/ring-buffer/) | LMAX Disruptor | `RingBuffer.java` | Core data structure — 6M orders/sec at LMAX Exchange |
| [Batch Processing](/patterns/batch-processing/) | Apache Kafka | `RecordAccumulator.java` | Accumulate records into batches per partition for throughput |

## Further Reading

- [LMAX Disruptor (GitHub)](https://github.com/LMAX-Exchange/disruptor) · [Apache Kafka (GitHub)](https://github.com/apache/kafka)
